import os
import re
import shutil

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'dist')

# Book Specific Config
SOURCE_DIR_NAME = 'ren-lei-da-li-shi'
SOURCE_FILE = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'index.html')
IMAGES_DIR_NAME = 'images'
THEME_CSS_NAME = 'theme_renlei.css' # Using the specific theme for Renlei

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 人類大歷史</title>
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
            <span class="mobile-title">人類大歷史</span>
        </div>

        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="index.html" class="book-title">人類大歷史</a>
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

    # Split into blocks based on top-level divs with class 'calibre'
    # Pattern: <div class="calibre" id="calibre_link-36">
    parts = re.split(r'(<div class="calibre"[^>]*>)', full_body_content)
    
    blocks = []
    if len(parts) > 1:
        # parts[0] is usually empty or whitespace before first div
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                block = parts[i] + parts[i+1]
                blocks.append(block)
    else:
        # Fallback
        blocks = [full_body_content]

    print(f"Found {len(blocks)} content blocks.")

    chapters = []
    
    # Check first block, usually cover or title page.
    # We will assume:
    # 1. Front matter pages (like '誌謝') have <h1 class="calibre3">
    # 2. Part headers (like '第一部') have <h1 class="p">
    # 3. Chapters (like '第01章') have <h2 class="p1">
    
    # Regex patterns
    # Matches <h1 class="..."> <span class="num">...</span> ... </h1>
    re_part = re.compile(r'<h1[^>]*><span class="num">([^<]+)</span>([^<]+)</h1>', re.IGNORECASE)
    
    # Matches <h2 class="..."> <span class="num">...</span> ... </h2>
    # Note: text might be immediately after span or have some whitespace
    re_chapter = re.compile(r'<h2[^>]*><span class="num">([^<]+)</span>((?:(?!</h2>).)+)</h2>', re.IGNORECASE)
    
    # Front matter: <h1 class="calibre3">Title</h1> - class might change too, so match h1 without num span?
    # But Parts also use h1. Part has span.num, Front matter doesn't.
    re_front = re.compile(r'<h1[^>]*>(?!<span)([^<]+)</h1>', re.IGNORECASE)

    current_chapter = None
    
    for i, block in enumerate(blocks):
        # Determine title
        title = None
        is_part_header = False
        
        # Search for headers in priority
        # Part headers are high level
        match_part = re_part.search(block)
        
        # Chapter headers
        match_chapter = re_chapter.search(block)
        
        # Front matter
        match_front = re_front.search(block)

        if match_part:
            # e.g. 第一部 認知革命
            title = f"{match_part.group(1)} {match_part.group(2)}"
            is_part_header = True
        elif match_chapter:
            # e.g. 第01章 人類: ...
            title = f"{match_chapter.group(1)} {match_chapter.group(2)}"
        elif match_front:
            title = match_front.group(1)
        
        # If no explicit header, maybe it's just following usage of previous chapter or it's a cover/misc page
        if title:
             # Start new chapter
             filename = f"chapter_{len(chapters):02d}.html"
             # Special case for first one
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
            # Append to latest chapter if exists, otherwise create a dummy start
            if chapters:
                chapters[-1]["content_blocks"].append(block)
            else:
                # Likely cover or initial empty pages
                # Check if it has content meaningful?
                # For now let's create a "Cover" chapter
                chapters.append({
                    "title": "封面 / 前言",
                    "filename": "index.html",
                    "content_blocks": [block],
                    "is_part_header": False
                })

    # Generate TOC HTML
    toc_html = ""
    for ch in chapters:
        title = ch["title"]
        filename = ch["filename"]
        
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
            prev_btn = f'<a href="{prev_ch["filename"]}" class="nav-btn prev">← 上一章</a>'
            
        next_btn = ""
        if i < len(chapters) - 1:
            next_ch = chapters[i+1]
            next_btn = f'<a href="{next_ch["filename"]}" class="nav-btn next">下一章 →</a>'

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

    print("Done.")

if __name__ == "__main__":
    main()
