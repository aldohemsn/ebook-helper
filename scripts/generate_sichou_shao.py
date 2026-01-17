
import os
import re
import shutil

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'dist_sichou_shao')

# Book Specific Config
SOURCE_DIR_NAME = 'si-chou-zhi-lu-shao-xu-dong'
SOURCE_FILE = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'index.html')
IMAGES_DIR_NAME = 'images'
THEME_CSS_NAME = 'theme_sichou_shao.css'

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

def remove_ads(content):
    """
    Remove ads and promotional content added by ebook piracy sites.
    """
    # Pattern for the specific ad text - match the whole paragraph
    # 本書由"行行"整理，如果你不知道讀什麼書或者想獲得更多免費電子書...
    ad_patterns = [
        r'<p[^>]*>\s*本書由"行行"整理[^<]*</p>',
        r'<p[^>]*>[^<]*行行[^<]*整理[^<]*微信[^<]*QQ[^<]*</p>',
        r'<p[^>]*>[^<]*ireadweek\.com[^<]*</p>',
        r'<p class="calibre_5">[^<]*本書由"行行"整理[^<]*</p>',
        r'<p class="calibre_6">[^<]*本書由"行行"整理[^<]*</p>',
    ]
    
    cleaned = content
    for pattern in ad_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    
    return cleaned

def extract_toc_list(content):
    """
    Extracts the TOC mapping from the HTML.
    Returns a list of tuples: [("anchor_id", "Title"), ...]
    """
    toc_list = []
    
    # Locate the TOC block
    # It seems to be in the first block or specifically in <div class="calibre" id="calibre_link-0">
    start_marker = '<div class="calibre" id="calibre_link-0">'
    end_marker = '<div class="calibre" id="calibre_link-31">' # Based on file view, TOC ends before this image block
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Warning: Could not find TOC block start.")
        search_area = content[0:20000] # Look at the beginning
    else:
        # Just look at the first block basically
        # Or look until the next big div
        end_idx = content.find('<div class="calibre" id="calibre_link-31">', start_idx)
        if end_idx == -1: 
             end_idx = start_idx + 10000
        search_area = content[start_idx:end_idx]
    
    # Extract links
    # <a href="#calibre_link-1">前 言</a>
    link_pattern = re.compile(r'<a href="#(calibre_link-\d+)">([^<]+)</a>', re.DOTALL)
    
    matches = link_pattern.findall(search_area)
    for link_id, link_text in matches:
        clean_text = re.sub(r'<[^>]+>', '', link_text).strip()
        clean_text = ' '.join(clean_text.split())
        toc_list.append((link_id, clean_text))
        
    print(f"Extracted {len(toc_list)} TOC entries.")
    return toc_list

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    print(f"Reading {SOURCE_FILE}...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get TOC List
    toc_list = extract_toc_list(content)
    
    # Extract Body Content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if not body_match:
        print("Could not find body tag.")
        return
    full_body_content = body_match.group(1)

    # Split into blocks
    # Pattern: <div class="calibre" id="calibre_link-36">
    parts = re.split(r'(<div class="calibre" id="[^"]+">)', full_body_content)
    
    blocks = []
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            header = parts[i]
            body = parts[i+1]
            full_block = header + body
            blocks.append(full_block)

    print(f"Found {len(blocks)} content blocks.")

    chapters = []
    
    # Special handling for "Front Matter" (Cover, TOC itself)
    # The first few blocks before the first TOC anchor (calibre_link-1) should be "Cover"
    # Wait, the TOC logic: The first logical chapter corresponds to 'calibre_link-1' (Preface).
    # Blocks before that one should be "Cover".
    
    current_chapter = {
        "title": "封面 / 目錄",
        "filename": "index.html",
        "content_blocks": []
    }
    chapters.append(current_chapter)
    
    # We need a way to check if a block contains a start anchor
    # The anchors look like <a id="calibre_link-1"></a> or <a name="calibre_link-1"></a>
    
    # Convert toc_list to a map for easy lookup of index
    toc_map_title = { t[0]: t[1] for t in toc_list }
    toc_order = [t[0] for t in toc_list]
    
    # We want to maintain order.
    # next_expected_anchor_idx = 0
    
    found_anchors = set()
    
    for block in blocks:
        # Check if this block contains any of the TOC anchors
        # Find which anchor appears first in this block (if multiple?)
        # Actually usually one chapter per block or multiple blocks per chapter
        
        block_start_anchor = None
        for anchor_id in toc_order:
            if anchor_id in found_anchors:
                continue
            # Check if this anchor is present in the block
            # Regex for anchor tag
            if re.search(f'id="{anchor_id}"|name="{anchor_id}"', block):
                block_start_anchor = anchor_id
                break
        
        if block_start_anchor:
            # Start new chapter
            title = toc_map_title[block_start_anchor]
            found_anchors.add(block_start_anchor)
            print(f"Starting chapter: {title} ({block_start_anchor})")
            
            filename = f"chapter_{len(chapters):02d}.html"
            
            new_chapter = {
                "title": title,
                "filename": filename,
                "content_blocks": [block]
            }
            chapters.append(new_chapter)
            current_chapter = new_chapter
        else:
            # Continue current chapter
            current_chapter["content_blocks"].append(block)

    # Generate TOC HTML for sidebar
    toc_html = f'<li><a href="index.html">封面 / 目錄</a></li>\n'
    for i, ch in enumerate(chapters):
        if i == 0: continue # Skip cover
        title = ch["title"]
        filename = ch["filename"]
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
            prev_btn = f'<a href="{prev_ch["filename"]}" class="nav-btn prev">← {prev_ch["title"]}</a>'
            
        next_btn = ""
        if i < len(chapters) - 1:
            next_ch = chapters[i+1]
            next_btn = f'<a href="{next_ch["filename"]}" class="nav-btn next">{next_ch["title"]} →</a>'

        content = "\n".join(ch["content_blocks"])
        # Remove ads from content
        content = remove_ads(content)
        
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
