
import os
import re
import shutil

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'dist_sichou')

# Book Specific Config
SOURCE_DIR_NAME = 'si-chou-zhi-lu'
SOURCE_FILE = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'index.html')
IMAGES_DIR_NAME = 'images'
THEME_CSS_NAME = 'theme_sichou.css'

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 絲綢之路</title>
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
            <span class="mobile-title">絲綢之路</span>
        </div>

        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="index.html" class="book-title">絲綢之路</a>
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
                <h1 class="chapter-title">{title}</h1>
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

def extract_toc_map(content):
    """
    Extracts the TOC mapping from the HTML.
    Targeting the TOC block: <div class="p-text" id="calibre_link-5">
    Returns a dictionary: { "calibre_link-X": "Title" }
    """
    toc_map = {}
    
    # Locate the TOC block
    # It seems strictly between id="calibre_link-5" and the next id="calibre_link-6"
    # But since we are splitting by blocks anyway, we can just find the block that contains "目次" class="big-h"
    
    # We will iterate through blocks later. But for now, let's find the TOC in the raw content just to be sure
    # Or, we can parse it from the specific block if we can find it.
    
    # Let's use regex to find all links in the file that look like TOC entries
    # Pattern seen: <p class="calibre"><a href="#calibre_link-8" ...><span ...>第一章</span> <span ...>絲綢之路的開端</span></a></p>
    # Also: <p class="calibre"><span class="bold"><a href="#calibre_link-6" ...><span ...>關於字母轉寫</span></a></span></p>
    
    # We'll search for all <a href="#calibre_link-\d+">...</a> and extract text.
    # However, create a map only for UNIQUE links that appear in the TOC area. 
    # To be safe, let's try to identify the TOC region first.
    
    start_marker = '<div class="p-text" id="calibre_link-5">'
    end_marker = '<div class="p-text" id="calibre_link-6">' # Assumption based on file view
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Warning: Could not find strict TOC block start. Using loose regex.")
        search_area = content # Fallback to whole file? No, that might catch internal links.
    else:
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
             search_area = content[start_idx:]
        else:
             search_area = content[start_idx:end_idx]
    
    # Extract links
    # <a href="#calibre_link-8" ...> ... </a>
    link_pattern = re.compile(r'<a href="#(calibre_link-\d+)"[^>]*>(.*?)</a>', re.DOTALL)
    
    matches = link_pattern.findall(search_area)
    for link_id, link_inner in matches:
        # Strip spans to get clean text
        clean_text = re.sub(r'<[^>]+>', '', link_inner).strip()
        # Clean up whitespace
        clean_text = ' '.join(clean_text.split())
        toc_map[link_id] = clean_text
        
    print(f"Extracted {len(toc_map)} TOC entries.")
    return toc_map

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    print(f"Reading {SOURCE_FILE}...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get TOC Map
    toc_map = extract_toc_map(content)
    
    # Add manual entry for the first few pages if they are not in TOC
    # Usually link-0 to link-4 are images and foreword stuff.
    # link-5 is TOC itself.
    # link-6 is "關於字母轉寫" whish IS in TOC.
    
    # Let's ensure we cover everything.
    
    # Extract Body Content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if not body_match:
        print("Could not find body tag.")
        return
    full_body_content = body_match.group(1)

    # Split into blocks
    # Pattern: <div class="p-text" id="calibre_link-36"> or <div class="p-cover" id="...">
    # We want to keep the delimiter to know the ID
    parts = re.split(r'(<div class="(?:p-text|p-cover)"[^>]*>)', full_body_content)
    
    blocks = []
    # parts[0] is usually empty or whitespace
    # parts[1] is delim, parts[2] is content, parts[3] is delim...
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            header = parts[i]
            body = parts[i+1]
            # Extract ID from header
            id_match = re.search(r'id="(calibre_link-\d+)"', header)
            block_id = id_match.group(1) if id_match else None
            
            full_block = header + body
            blocks.append({
                "id": block_id,
                "content": full_block
            })

    print(f"Found {len(blocks)} content blocks.")

    chapters = []
    current_chapter = None
    
    # Special handling for "Front Matter" (Cover, etc)
    # We'll start a default chapter.
    front_matter_title = "封面 / 圖片"
    current_chapter = {
        "title": front_matter_title,
        "filename": "index.html",
        "content_blocks": []
    }
    chapters.append(current_chapter)
    
    # Track which IDs we have seen in TOC to switch chapters
    for block in blocks:
        bid = block["id"]
        
        # Determine if this block starts a new chapter
        if bid in toc_map:
            # New chapter
            title = toc_map[bid]
            print(f"Starting chapter: {title} ({bid})")
            
            # Determine filename
            # Use safe filename
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            filename = f"chapter_{len(chapters):02d}.html"
            
            new_chapter = {
                "title": title,
                "filename": filename,
                "content_blocks": [block["content"]]
            }
            chapters.append(new_chapter)
            current_chapter = new_chapter
        else:
            # Append to current
            current_chapter["content_blocks"].append(block["content"])

    # Generate TOC HTML for sidebar
    # We need to use the chapters list, but we should probably filter out empty ones or merge
    # Actually, relying on the TOC map order is safer for the "official" TOC, 
    # but our chapters list represents how we split the content.
    
    toc_html = ""
    for ch in chapters:
        title = ch["title"]
        filename = ch["filename"]
        
        # Simple list item
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

    print(f"Done. Output in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
