import os
import re
import shutil
from bs4 import BeautifulSoup, Tag, NavigableString

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR_NAME = 'dist_tangshisongci'
OUTPUT_DIR = os.path.join(PROJECT_ROOT, OUTPUT_DIR_NAME)

# Book Specific Config
SOURCE_DIR_NAME = 'Tang Shi Song Ci Yuan Qu Gu Wen (Gong 6Ce - Shang Hai Ci Shu Chu Ban She Wen Xue Jian '
SOURCE_FILE = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'index.html')
IMAGES_DIR_NAME = 'images'
THEME_CSS_NAME = 'theme_tangshisongci.css'

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 唐诗宋词元曲古文</title>
    <!-- Local CSS only for offline access -->
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="{theme_css}">
</head>
<body>
    <div class="app-container">
        <!-- Mobile Header -->
        <div class="mobile-header">
            <button id="menu-toggle" class="menu-toggle" aria-label="Toggle Navigation">
                ☰ 
            </button>
            <span class="mobile-title">唐诗宋词元曲古文</span>
        </div>

        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="index.html" class="book-title">唐诗宋词元曲古文</a>
                <button id="menu-close" class="menu-close" aria-label="Close Navigation">×</button>
            </div>
            <nav class="toc">
                <ul>
                    {toc_items}
                </ul>
            </nav>
        </aside>
        
        <!-- Main Content -->
        <main class="content-area">
            <div class="chapter-content">
                {content}
            </div>
            
            <div class="navigation-footer">
                {prev_button}
                {next_button}
            </div>
        </main>
        
        <!-- Overlay -->
        <div class="sidebar-overlay" id="sidebar-overlay"></div>

        <!-- Lightbox -->
        <div id="lightbox" class="lightbox">
            <img id="lightbox-img" src="" alt="Enlarged image">
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // Highlight active TOC item & Auto-expand
            const currentObj = window.location.pathname.split('/').pop();
            const links = document.querySelectorAll('.toc a');
            let activeLink = null;

            links.forEach(link => {{
                if (link.getAttribute('href') === currentObj) {{
                    link.classList.add('active');
                    activeLink = link;
                }}
            }});

            // Expand parents of active link
            if (activeLink) {{
                // 1. If active link is a parent itself, expand it
                const selfLi = activeLink.closest('li.has-children');
                // Check if the link is actually inside the toggle part (header), not a child in the nested list
                // (Though standard querySelectorAll('.toc a') gets all. activeLink is the specific one.)
                // If activeLink is the Header link, it is immediate child of .toc-item
                if (selfLi && activeLink.closest('.toc-item')) {{
                     selfLi.classList.add('expanded');
                     const childUl = selfLi.querySelector('ul.nested');
                     if (childUl) childUl.classList.remove('collapsed');
                }}

                // 2. Expand ancestors
                let parent = activeLink.closest('ul.nested');
                while (parent) {{
                    parent.classList.remove('collapsed');
                    const li = parent.closest('li');
                    if (li) {{
                        li.classList.add('expanded');
                        li.classList.add('active-parent');
                    }}
                    parent = li ? li.closest('ul.nested') : null;
                }}
                
                // Scroll into view after expansion
                setTimeout(() => {{
                    activeLink.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                }}, 100);
            }}

            // Sidebar Toggles
            const toggles = document.querySelectorAll('.toc-toggle');
            toggles.forEach(toggle => {{
                toggle.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    const li = toggle.closest('li');
                    const nested = li.querySelector('.nested');
                    if (nested) {{
                        nested.classList.toggle('collapsed');
                        li.classList.toggle('expanded');
                    }}
                }});
            }});
            
            // Mobile Menu
            const toggleBtn = document.getElementById('menu-toggle');
            const closeBtn = document.getElementById('menu-close');
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            
            function toggleMenu() {{
                sidebar.classList.toggle('open');
                overlay.classList.toggle('active');
            }}
            
            function closeMenu() {{
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }}
            
            if(toggleBtn) toggleBtn.addEventListener('click', toggleMenu);
            if(closeBtn) closeBtn.addEventListener('click', closeMenu);
            if(overlay) overlay.addEventListener('click', closeMenu);

            // Lightbox
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightbox-img');
            const contentImages = document.querySelectorAll('.chapter-content img');

            contentImages.forEach(img => {{
                img.style.cursor = 'zoom-in';
                img.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    lightboxImg.src = img.src;
                    lightbox.classList.add('active');
                }});
            }});

            lightbox.addEventListener('click', () => {{
                lightbox.classList.remove('active');
            }});
        }});
    </script>
</body>
</html>
"""

def clean_title(title_text):
    if not title_text:
        return "Untitled"
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title_text).strip()
    return title

def is_header(tag):
    if not isinstance(tag, Tag):
        return False
    
    # We only care about specific headers
    classes = tag.get('class', [])
    if not classes:
        # Check if it's an H1 or H2 without class? 
        # Source uses classes heavily.
        return False
    
    # H1
    if tag.name == 'h1': 
        if 'calibre5' in classes: return True
        if 'calibre8' in classes: return True
        if 'calibre26' in classes: return True
        if 'kindle-cn-heading' in classes: return True
    
    # H2
    if tag.name == 'h2':
        if 'calibre18' in classes: return True
        if 'biaoti' in classes: return True
        if 'calibre3' in classes: return True
        if 'kindle-cn-heading1' in classes: return True

    # H3
    if tag.name == 'h3':
        if 'kindle-cn-heading2' in classes: return True

    # Div (TOC)
    if tag.name == 'div':
        if 'sgc-toc-title' in classes: return True
        if 'kindle-cn-toc-title' in classes: return True
        
    # P (Poems - specifically requested)
    if tag.name == 'p':
        if 'title-poem-k-zhong' in classes: return True
        
    return False

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    print(f"Reading {SOURCE_FILE}...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Parsing HTML with BeautifulSoup...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    chapters = []
    
    # Initialize first chapter (Cover/Preface)
    current_chapter = {
        "title": "封面",
        "elements": [],
        "is_header": False
    }
    
    body = soup.find('body')
    if not body:
        print("No body tag found")
        return

    print("Processing content...")
    
    # Heuristic: The ebook seems to use top-level divs with id="calibre_link-X" as containers.
    # Inside these divs, we have the content.
    # We will iterate through these top-level divs, and then iterate through their children.
    # If we find a header, we split.
    
    # Find all direct children of body
    # We use find_all recursive=False to get top level elements
    top_elements = body.find_all(recursive=False)
    
    for element in top_elements:
        # If it's a NavigableString (just text between divs), add it to current
        if isinstance(element, NavigableString):
            txt = str(element).strip()
            if txt:
                current_chapter['elements'].append(str(element))
            continue
            
        # If it's a div (likely calibre_link wrapper), iterate ITS children
        if element.name == 'div':
            # Check if this div ITSELF is a header (like TOC div)
            if is_header(element):
                 # Split here
                 chapters.append(current_chapter)
                 title = clean_title(element.get_text())
                 current_chapter = {
                    "title": title,
                    "elements": [str(element)],
                    "is_header": True # TOC divs are usually structural
                 }
                 continue

            # Iterate children of the div
            # Note: If the div has NO ID or specific class, it might just be wrapper.
            # We treat it as a container.
            for child in element.children:
                if isinstance(child, NavigableString):
                    if str(child).strip():
                        current_chapter['elements'].append(str(child))
                    continue
                
                if is_header(child):
                    # Found a header inside the div -> Split
                    chapters.append(current_chapter)
                    
                    title = clean_title(child.get_text())
                    
                    # Determine styling
                    is_major = False
                    classes = child.get('class', [])
                    if child.name == 'h1': is_major = True
                    if 'calibre5' in classes: is_major = True
                    if 'kindle-cn-toc-title' in classes: is_major = True
                    
                    if len(title) > 50: 
                        title = title[:50] + "..."
                        
                    current_chapter = {
                        "title": title,
                        "elements": [str(child)],
                        "is_header": is_major
                    }
                else:
                    # Regular content
                    current_chapter['elements'].append(str(child))
        else:
            # element is not a div (maybe h1 directly in body?)
            if is_header(element):
                chapters.append(current_chapter)
                title = clean_title(element.get_text())
                is_major = (element.name == 'h1')
                current_chapter = {
                    "title": title,
                    "elements": [str(element)],
                    "is_header": is_major
                }
            else:
                current_chapter['elements'].append(str(element))

    # Add the last chapter
    chapters.append(current_chapter)
    
    # Remove empty chapters if any (except maybe the first one or valid ones)
    final_chapters = []
    for ch in chapters:
        # If title is empty/Unknown or content is empty, maybe skip?
        # But allow "Untitled" if it has content.
        if not ch['elements'] and ch['title'] == 'Untitled':
            continue
        # Dedupe titles? No, poems can have same title.
        
        # Override untitled if logical
        if ch['title'] == 'Untitled' or ch['title'] == 'Unknown':
             if "封面" in str(ch['elements']):
                 ch['title'] = "封面"
        
        # Assign filename
        idx = len(final_chapters)
        if idx == 0:
            ch['filename'] = "index.html"
            ch['title'] = "封面" # Ensure first is cover
        else:
            ch['filename'] = f"chapter_{idx:04d}.html"
            
        final_chapters.append(ch)

    print(f"Identified {len(final_chapters)} chapters.")

    # Generate Output
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Copy Assets
    src_images = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, IMAGES_DIR_NAME)
    dst_images = os.path.join(OUTPUT_DIR, IMAGES_DIR_NAME)
    if os.path.exists(src_images):
        shutil.copytree(src_images, dst_images)
        print("Copied images.")

    src_style = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'style.css')
    if os.path.exists(src_style):
        shutil.copy(src_style, os.path.join(OUTPUT_DIR, 'style.css'))
        print("Copied style.css")

    # Create theme file (assuming it exists in dist or scripts, copying from scripts)
    theme_src = os.path.join(SCRIPT_DIR, THEME_CSS_NAME)
    if os.path.exists(theme_src):
         shutil.copy(theme_src, os.path.join(OUTPUT_DIR, THEME_CSS_NAME))
         print("Copied theme css.")

    # Generate TOC HTML with nesting
    toc_tree = []
    current_parent = None
    
    # Pre-process chapters to build tree
    for ch in final_chapters:
        if ch["is_header"]:
            # New section
            current_parent = {
                "chapter": ch,
                "children": []
            }
            toc_tree.append(current_parent)
        else:
            if current_parent:
                current_parent["children"].append(ch)
            else:
                # Root level item (e.g. cover/preface)
                toc_tree.append({
                    "chapter": ch,
                    "children": []
                })

    toc_html = ""
    for node in toc_tree:
        parent_ch = node["chapter"]
        children = node["children"]
        
        title = parent_ch['title']
        filename = parent_ch['filename']
        
        if children:
            # It's a folder/section with children
            toc_html += f'<li class="has-children">\n'
            toc_html += f'    <div class="toc-item">\n'
            toc_html += f'        <span class="toc-toggle">▶</span>\n'
            toc_html += f'        <a href="{filename}">{title}</a>\n'
            toc_html += f'    </div>\n'
            toc_html += f'    <ul class="nested collapsed">\n'
            for child in children:
                c_title = child['title']
                c_file = child['filename']
                toc_html += f'        <li><a href="{c_file}">{c_title}</a></li>\n'
            toc_html += f'    </ul>\n'
            toc_html += f'</li>\n'
        else:
            # Leaf node at root level
            cls = "book-section-header" if parent_ch["is_header"] else ""
            toc_html += f'<li class="{cls}"><a href="{filename}">{title}</a></li>\n'

    # Write Pages
    print(f"Writing {len(final_chapters)} pages...")
    for i, ch in enumerate(final_chapters):
        prev_btn = ""
        if i > 0:
            prev_ch = final_chapters[i-1]
            prev_btn = f'<a href="{prev_ch["filename"]}" class="nav-btn prev">← {prev_ch["title"][:10]}</a>'
            
        next_btn = ""
        if i < len(final_chapters) - 1:
            next_ch = final_chapters[i+1]
            next_btn = f'<a href="{next_ch["filename"]}" class="nav-btn next">{next_ch["title"][:10]} →</a>'
        
        content_str = "\n".join(ch['elements'])
        
        html = HTML_TEMPLATE.format(
            title=ch["title"],
            theme_css=THEME_CSS_NAME,
            toc_items=toc_html,
            content=content_str,
            prev_button=prev_btn,
            next_button=next_btn
        )
        
        with open(os.path.join(OUTPUT_DIR, ch["filename"]), 'w', encoding='utf-8') as f:
            f.write(html)

    print("Done.")

if __name__ == "__main__":
    main()
