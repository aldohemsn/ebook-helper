import os
import re
import shutil

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR_NAME = 'dist_renlei_jian_shi'
OUTPUT_DIR = os.path.join(PROJECT_ROOT, OUTPUT_DIR_NAME)

# Book Specific Config
SOURCE_DIR_NAME = 'Ren Lei Jian Shi _Cong Dong Wu Dao Shang D - Yuval Noah Harari'
SOURCE_FILE = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'index.html')
IMAGES_DIR_NAME = 'images'
THEME_CSS_NAME = 'theme_renlei_jian_shi.css'

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 人类简史</title>
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
            <span class="mobile-title">人类简史</span>
        </div>

        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="index.html" class="book-title">人类简史</a>
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
            // Highlight active TOC item
            const currentObj = window.location.pathname.split('/').pop();
            const links = document.querySelectorAll('.toc a');
            links.forEach(link => {{
                if (link.getAttribute('href') === currentObj) {{
                    link.classList.add('active');
                    link.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                }}
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

def clean_title(title_html):
    """
    Cleans tags from title string and handles breaks.
    e.g. 第一章<br class="calibre9" />Title -> 第一章 Title
    """
    if not title_html:
        return ""
    # Replace <br...> with space
    title = re.sub(r'<br[^>]*>', ' ', title_html, flags=re.IGNORECASE)
    # Remove other tags
    title = re.sub(r'<[^>]+>', '', title)
    title = title.strip()
    return title

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    print(f"Reading {SOURCE_FILE}...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Body Content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if not body_match:
        print("Could not find body tag.")
        return
    full_body_content = body_match.group(1)

    # Split into blocks based on top-level divs with id 'calibre_link-X'
    # This covers both <div class="calibre" id="..."> and <div class="brownll" id="...">
    parts = re.split(r'(<div[^>]+id="calibre_link-\d+"[^>]*>)', full_body_content)
    
    blocks = []
    if len(parts) > 1:
        # parts[0] is usually empty or whitespace before first div
        # The split keeps delimiters, so parts[1] is delimiter, parts[2] is content.
        # We need to Combine Delimiter + Content
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                block = parts[i] + parts[i+1]
                blocks.append(block)
    else:
        # Fallback
        blocks = [full_body_content]

    print(f"Found {len(blocks)} content blocks.")

    chapters = []
    
    # Regex patterns
    
    # 1. Part Headers: <h1 class="calibre8" ...>
    re_part = re.compile(r'<h1[^>]*class="[^"]*calibre8[^"]*"[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL)
    
    # 2. Chapter Headers: <h2 class="biaoti" ...> or <h2 class="calibre3" ...>
    # Removed typo 'bisoti'
    re_chapter = re.compile(r'<h2[^>]*class="[^"]*(calibre3|biaoti)[^"]*"[^>]*>(.*?)</h2>', re.IGNORECASE | re.DOTALL)
                          
    
    current_chapter = None
    
    for i, block in enumerate(blocks):
        # Determine title
        title = None
        is_part_header = False
        
        # Search for headers in priority
        match_part = re_part.search(block)
        match_chapter = re_chapter.search(block)
        
        if match_part:
            raw_title = match_part.group(1)
            title = clean_title(raw_title)
            is_part_header = True
        elif match_chapter:
            raw_title = match_chapter.group(2)
            title = clean_title(raw_title)
            
        # Ignore empty titles (like the dummy header <h2 hidden... title="扉页" ...></h2> which has empty content
        if title == "":
            title = None

        if title:
             # Start new chapter
             filename = f"chapter_{len(chapters):02d}.html"
             if len(chapters) == 0:
                 filename = "index.html"
             
             chapter_data = {
                 "title": title,
                 "filename": filename,
                 "content_blocks": [block],
                 "is_part_header": is_part_header
             }
             chapters.append(chapter_data)
        else:
            # Append to latest chapter if exists
            if chapters:
                chapters[-1]["content_blocks"].append(block)
            else:
                # Cover / Initial content
                chapters.append({
                    "title": "封面 / 信息",
                    "filename": "index.html",
                    "content_blocks": [block],
                    "is_part_header": False
                })

    # Generate TOC HTML
    toc_html = ""
    for ch in chapters:
        title = ch["title"]
        filename = ch["filename"]
        
        # Skip "目录" from sidebar
        if "目录" in title and len(title) < 5:
            continue
            
        if ch["is_part_header"]:
            toc_html += f'<li class="book-section-header"><a href="{filename}">{title}</a></li>\n'
        else:
            toc_html += f'<li><a href="{filename}">{title}</a></li>\n'

    # Prepare Output
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    # Copy Assets
    src_images = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, IMAGES_DIR_NAME)
    dst_images = os.path.join(OUTPUT_DIR, IMAGES_DIR_NAME)
    if os.path.exists(src_images):
        shutil.copytree(src_images, dst_images)
        print(f"Copied images from {src_images}")
    else:
        print(f"Warning: Image directory not found at {src_images}")

    src_style = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'style.css')
    if os.path.exists(src_style):
        shutil.copy(src_style, os.path.join(OUTPUT_DIR, 'style.css'))
        print("Copied original style.css")
        
    theme_src = os.path.join(SCRIPT_DIR, THEME_CSS_NAME)
    if os.path.exists(theme_src):
        shutil.copy(theme_src, os.path.join(OUTPUT_DIR, THEME_CSS_NAME))
        print(f"Copied {THEME_CSS_NAME}")

    # Write Pages
    print(f"Generating {len(chapters)} pages...")
    for i, ch in enumerate(chapters):
        # Navigation
        prev_btn = ""
        if i > 0:
            prev_ch = chapters[i-1]
            prev_btn = f'<a href="{prev_ch["filename"]}" class="nav-btn prev">← {prev_ch["title"]}</a>'
            
        next_btn = ""
        if i < len(chapters) - 1:
            next_ch = chapters[i+1]
            next_btn = f'<a href="{next_ch["filename"]}" class="nav-btn next">{next_ch["title"]} →</a>'
        
        # Truncate long button text
        if len(prev_btn) > 40:
             prev_btn = f'<a href="{chapters[i-1]["filename"]}" class="nav-btn prev">← 上一章</a>'
        if len(next_btn) > 40:
             next_btn = f'<a href="{chapters[i+1]["filename"]}" class="nav-btn next">下一章 →</a>'

        content = "\n".join(ch["content_blocks"])
        
        html = HTML_TEMPLATE.format(
            title=ch["title"],
            theme_css=THEME_CSS_NAME,
            toc_items=toc_html,
            content=content,
            prev_button=prev_btn,
            next_button=next_btn
        )
        
        with open(os.path.join(OUTPUT_DIR, ch["filename"]), 'w', encoding='utf-8') as f:
            f.write(html)

    print(f"Done. Output in {OUTPUT_DIR_NAME}")

if __name__ == "__main__":
    main()
