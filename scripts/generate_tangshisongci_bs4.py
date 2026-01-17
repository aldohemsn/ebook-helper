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

            // Helper function: collapse all items at a given level (siblings of the target)
            function collapseSiblings(targetLi) {{
                const parentUl = targetLi.parentElement;
                if (!parentUl) return;
                
                const siblings = parentUl.querySelectorAll(':scope > li.has-children');
                siblings.forEach(sibling => {{
                    if (sibling !== targetLi) {{
                        sibling.classList.remove('expanded');
                        const nestedUl = sibling.querySelector(':scope > ul.nested');
                        if (nestedUl) {{
                            nestedUl.classList.add('collapsed');
                            // Also collapse all descendants
                            const descendantLis = nestedUl.querySelectorAll('li.has-children');
                            descendantLis.forEach(desc => {{
                                desc.classList.remove('expanded');
                                const descNested = desc.querySelector(':scope > ul.nested');
                                if (descNested) descNested.classList.add('collapsed');
                            }});
                        }}
                    }}
                }});
            }}

            // Expand parents of active link (only the path to active, not siblings)
            if (activeLink) {{
                // Build path from active link to root
                let pathItems = [];
                let current = activeLink.closest('li');
                while (current) {{
                    if (current.classList.contains('has-children')) {{
                        pathItems.push(current);
                    }}
                    const parentUl = current.parentElement;
                    current = parentUl ? parentUl.closest('li') : null;
                }}

                // Expand only items in the path
                pathItems.forEach(li => {{
                    li.classList.add('expanded');
                    li.classList.add('active-parent');
                    const nested = li.querySelector(':scope > ul.nested');
                    if (nested) nested.classList.remove('collapsed');
                }});
                
                // Scroll into view after expansion
                setTimeout(() => {{
                    activeLink.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                }}, 100);
            }}

            // Sidebar Toggles - Accordion behavior
            const toggles = document.querySelectorAll('.toc-toggle');
            toggles.forEach(toggle => {{
                toggle.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    const li = toggle.closest('li');
                    const nested = li.querySelector(':scope > .nested');
                    
                    if (!nested) return;
                    
                    const isExpanding = nested.classList.contains('collapsed');
                    
                    if (isExpanding) {{
                        // Collapse siblings first (accordion behavior)
                        collapseSiblings(li);
                        
                        // Then expand this one
                        nested.classList.remove('collapsed');
                        li.classList.add('expanded');
                    }} else {{
                        // Collapsing - also collapse all children
                        nested.classList.add('collapsed');
                        li.classList.remove('expanded');
                        
                        // Collapse all descendant items
                        const descendantLis = nested.querySelectorAll('li.has-children');
                        descendantLis.forEach(desc => {{
                            desc.classList.remove('expanded');
                            const descNested = desc.querySelector(':scope > ul.nested');
                            if (descNested) descNested.classList.add('collapsed');
                        }});
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

    # Generate TOC HTML with THREE-LEVEL nesting: Volume → Author → Works
    # Volume markers are specific chapters for each major dictionary
    
    def is_volume_header(title):
        """Check if this chapter is a volume header (e.g. 唐诗鉴赏辞典)"""
        # Specific volume titles - must contain these specific patterns
        volume_patterns = [
            '唐诗鉴赏辞典',
            '宋词鉴赏辞典', 
            '元曲鉴赏辞典',
            '古文鉴赏辞典'
        ]
        for pattern in volume_patterns:
            if pattern in title:
                return True
        return False
    
    def is_volume_aux(title):
        """Check if this is auxiliary content for a volume (出版说明, 凡例, 序言, etc.)"""
        aux_keywords = ['出版说明', '凡例', '序言', '前言', '目录', '后记', '附录', 
                        '书目', '索引', '简释', '词学', '词牌']
        for kw in aux_keywords:
            if kw in title:
                return True
        return False
    
    # Build three-level tree structure
    volumes = []  # List of {volume_chapter, authors: [{author_chapter, works: []}], aux_items: []}
    current_volume = None
    current_author = None
    
    for ch in final_chapters:
        title = ch['title']
        
        # Check if this is a new volume
        if is_volume_header(title):
            # Save previous volume
            if current_volume:
                if current_author:
                    current_volume['authors'].append(current_author)
                    current_author = None
                volumes.append(current_volume)
            
            current_volume = {
                'chapter': ch,
                'authors': [],
                'aux_items': []  # For 出版说明, 凡例, 序言 etc.
            }
            continue
        
        # If we don't have a volume yet, create a default one
        if not current_volume:
            # First few items before first volume - create 唐诗鉴赏辞典 as default
            current_volume = {
                'chapter': {'title': '唐诗鉴赏辞典', 'filename': 'index.html', 'is_header': True},
                'authors': [],
                'aux_items': []
            }
        
        # Check if this is auxiliary content (出版说明, 凡例, etc.)
        if is_volume_aux(title):
            current_volume['aux_items'].append(ch)
            continue
        
        # Check if this is an author header (is_header=True)
        if ch['is_header']:
            # Save previous author
            if current_author:
                current_volume['authors'].append(current_author)
            
            current_author = {
                'chapter': ch,
                'works': []
            }
        else:
            # This is a work
            if current_author:
                current_author['works'].append(ch)
            else:
                # Orphan work without author - add as aux item
                current_volume['aux_items'].append(ch)
    
    # Don't forget the last author and volume
    if current_author:
        current_volume['authors'].append(current_author)
    if current_volume:
        volumes.append(current_volume)
    
    # Generate TOC HTML
    toc_html = ""
    
    for vol in volumes:
        vol_ch = vol['chapter']
        vol_title = vol_ch['title']
        vol_file = vol_ch['filename']
        authors = vol['authors']
        aux_items = vol['aux_items']
        
        has_content = authors or aux_items
        
        if has_content:
            # Volume with content - create expandable section
            toc_html += f'<li class="has-children volume-level">\n'
            toc_html += f'    <div class="toc-item">\n'
            toc_html += f'        <span class="toc-toggle">▶</span>\n'
            toc_html += f'        <a href="{vol_file}">{vol_title}</a>\n'
            toc_html += f'    </div>\n'
            toc_html += f'    <ul class="nested collapsed">\n'
            
            # Add auxiliary items first (出版说明, 凡例, etc.)
            for aux in aux_items:
                toc_html += f'        <li class="book-section-header"><a href="{aux["filename"]}">{aux["title"]}</a></li>\n'
            
            # Add authors
            for author in authors:
                auth_ch = author['chapter']
                auth_title = auth_ch['title']
                auth_file = auth_ch['filename']
                works = author['works']
                
                if works:
                    # Author with works
                    toc_html += f'        <li class="has-children author-level">\n'
                    toc_html += f'            <div class="toc-item">\n'
                    toc_html += f'                <span class="toc-toggle">▶</span>\n'
                    toc_html += f'                <a href="{auth_file}">{auth_title}</a>\n'
                    toc_html += f'            </div>\n'
                    toc_html += f'            <ul class="nested collapsed">\n'
                    for work in works:
                        toc_html += f'                <li><a href="{work["filename"]}">{work["title"]}</a></li>\n'
                    toc_html += f'            </ul>\n'
                    toc_html += f'        </li>\n'
                else:
                    # Author without works (just a standalone header)
                    toc_html += f'        <li><a href="{auth_file}">{auth_title}</a></li>\n'
            
            toc_html += f'    </ul>\n'
            toc_html += f'</li>\n'
        else:
            # Volume without content (standalone)
            cls = "book-section-header" if vol_ch.get("is_header", False) else ""
            toc_html += f'<li class="{cls}"><a href="{vol_file}">{vol_title}</a></li>\n'

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
