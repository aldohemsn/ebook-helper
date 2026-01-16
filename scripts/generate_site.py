import os
import re
import shutil

# Get the project root directory (parent of scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Configuration - paths relative to project root
PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'public')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'dist')
SOURCE_FILE = os.path.join(PUBLIC_DIR, 'index.html')
IMAGES_DIR = 'images'
THEME_CSS = os.path.join(SCRIPT_DIR, 'theme.css')

# HTML Template with offline compatibility and mobile menu support
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 中國・歷史的長河</title>
    <!-- Local CSS only for offline access -->
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="theme.css">
</head>
<body>
    <div class="app-container">
        <!-- Mobile Header (Visible only on small screens via CSS) -->
        <div class="mobile-header">
            <button id="menu-toggle" class="menu-toggle" aria-label="Toggle Navigation">
                ☰ 
            </button>
            <span class="mobile-title">中國・歷史的長河</span>
        </div>

        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="index.html" class="book-title">中國・歷史的長河</a>
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
        
        <!-- Overlay for mobile sidebar -->
        <div class="sidebar-overlay" id="sidebar-overlay"></div>

        <!-- Lightbox for Images -->
        <div id="lightbox" class="lightbox">
            <img id="lightbox-img" src="" alt="Enlarged image">
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // highlight active TOC item
            const currentObj = window.location.pathname.split('/').pop();
            const links = document.querySelectorAll('.toc a');
            links.forEach(link => {{
                if (link.getAttribute('href') === currentObj) {{
                    link.classList.add('active');
                    link.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                }}
            }});
            
            // Mobile Menu Logic
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

            // Lightbox Logic
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightbox-img');
            const contentImages = document.querySelectorAll('.chapter-content img');

            contentImages.forEach(img => {{
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
    # Check if source file exists
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        print(f"Please place your Calibre-exported index.html in the public/ directory.")
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
    parts = re.split(r'(<div class="calibre"[^>]*>)', full_body_content)
    
    blocks = []
    current_block = parts[0]
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            block = parts[i] + parts[i+1]
            blocks.append(block)
    
    print(f"Found {len(blocks)} content blocks.")
    
    # Book Title Mapping (Filename -> Title)
    BOOK_MAP = {
        "index.html": "第一卷：從神話到歷史：神話時代與夏王朝",
        "chapter_11.html": "第二卷：從城市國家到中華：殷商與春秋戰國時代",
        "chapter_22.html": "第三卷：始皇帝的遺產：秦漢帝國",
        "chapter_33.html": "第四卷：三國志的世界：東漢與三國時代",
        "chapter_44.html": "第五卷：中華的崩潰與擴大：魏晉南北朝",
        "chapter_54.html": "第六卷：絢爛的世界帝國：隋唐時代",
        "chapter_66.html": "第七卷：中國思想與宗教的奔流：宋朝",
        "chapter_76.html": "第八卷：疾馳的草原征服者：遼、西夏、金、元",
        "chapter_83.html": "第九卷：海與帝國：明清時代",
        "chapter_93.html": "第十卷：末代王朝與近代中國：晚清與中華民國",
        "chapter_104.html": "第十一卷：巨龍的胎動：毛澤東、鄧小平與中華人民共和國",
        "chapter_114.html": "第十二卷：日本人眼中的中國：過去與現在"
    }

    chapters = []
    current_chapter = {
        "title": "前言/封面",
        "filename": "index.html",
        "content_blocks": []
    }
    
    # Regex to find Chapter Title
    # <h1 class="calibre4" title="【第一章】神話與考古學">
    h1_pattern = re.compile(r'<h1[^>]*class="calibre4"[^>]*title="([^"]*)"[^>]*>', re.IGNORECASE)
    # Alternative pattern if title attr is missing, check text content
    h1_text_pattern = re.compile(r'<h1[^>]*class="calibre4"[^>]*>(.*?)</h1>', re.DOTALL | re.IGNORECASE)

    chapter_count = 0
    
    for block in blocks:
        # Check if this block starts a new chapter
        match = h1_pattern.search(block)
        if match:
            # Save previous chapter
            chapters.append(current_chapter)
            
            # Start new chapter
            chapter_count += 1
            title = match.group(1)
            filename = f"chapter_{chapter_count:02d}.html"
            current_chapter = {
                "title": title,
                "filename": filename,
                "content_blocks": [block]
            }
        else:
            # Only start new chapter if h1 found, otherwise append
            text_match = h1_text_pattern.search(block)
            if text_match and "【" in text_match.group(1): # Heuristic for chapter start
                 # Save previous chapter
                chapters.append(current_chapter)
                
                # Start new chapter
                chapter_count += 1
                # Clean title: remove tags
                raw_title = re.sub(r'<[^>]+>', '', text_match.group(1)).strip()
                # Basic cleanup
                title = raw_title.replace('\n', ' ')
                
                filename = f"chapter_{chapter_count:02d}.html"
                current_chapter = {
                    "title": title,
                    "filename": filename,
                    "content_blocks": [block]
                }
            else:
                current_chapter["content_blocks"].append(block)
    
    # Add last chapter
    if current_chapter:
        chapters.append(current_chapter)
    
    # Prepare Output Directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Copy Images from public/
    src_images = os.path.join(PUBLIC_DIR, IMAGES_DIR)
    dst_images = os.path.join(OUTPUT_DIR, IMAGES_DIR)
    if os.path.exists(src_images):
        if os.path.exists(dst_images):
            shutil.rmtree(dst_images)
        shutil.copytree(src_images, dst_images)
        print("Images copied.")

    # Copy Style.css from public/ if exists
    src_style = os.path.join(PUBLIC_DIR, 'style.css')
    if os.path.exists(src_style):
        shutil.copy(src_style, os.path.join(OUTPUT_DIR, 'style.css'))
    
    # Copy theme.css from scripts/
    if os.path.exists(THEME_CSS):
        shutil.copy(THEME_CSS, os.path.join(OUTPUT_DIR, 'theme.css'))
        print("Theme CSS copied.")
    
    # Generate TOC HTML with Book Headers
    toc_html = ""
    for ch in chapters:
        fname = ch["filename"]
        if fname in BOOK_MAP:
            toc_html += f'<li class="book-section-header">{BOOK_MAP[fname]}</li>\n'
        toc_html += f'<li><a href="{fname}">{ch["title"]}</a></li>\n'
    
    # Write Chapters
    for i, ch in enumerate(chapters):
        # Nav buttons
        prev_btn = ""
        if i > 0:
            prev_ch = chapters[i-1]
            prev_btn = f'<a href="{prev_ch["filename"]}" class="nav-btn prev">← {prev_ch["title"]}</a>'
            
        next_btn = ""
        if i < len(chapters) - 1:
            next_ch = chapters[i+1]
            next_btn = f'<a href="{next_ch["filename"]}" class="nav-btn next">{next_ch["title"]} →</a>'
        
        full_content = "\n".join(ch["content_blocks"])
        
        final_html = HTML_TEMPLATE.format(
            title=ch["title"],
            toc_items=toc_html,
            content=full_content,
            prev_button=prev_btn,
            next_button=next_btn
        )
        
        out_path = os.path.join(OUTPUT_DIR, ch["filename"])
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
    print(f"Generated {len(chapters)} pages in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
