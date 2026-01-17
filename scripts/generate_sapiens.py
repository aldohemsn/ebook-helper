import os
import re
import shutil
import argparse

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'public')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'dist')

# Book Specific Config
SOURCE_DIR_NAME = 'sapiens-a-brief-history-of-humankind'
SOURCE_FILE = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'index.html')
IMAGES_DIR_NAME = 'images'
THEME_CSS_NAME = 'theme_sapiens.css'

# HTML Template (English)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Sapiens</title>
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
            <span class="mobile-title">Sapiens</span>
        </div>

        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="index.html" class="book-title">Sapiens:<br><small>A Brief History of Humankind</small></a>
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

# Structural Mapping
# Based on analysis of index.html
# "calibre_6" class marks the start of major sections
HEADINGS_MAP = {
    "calibre_link-4": "Title Page",
    "calibre_link-5": "Copyright",
    "calibre_link-6": "Dedication",
    "calibre_link-7": "Timeline of History",
    "calibre_link-8": "Part One: The Cognitive Revolution",
    "calibre_link-9": "1. An Animal of No Significance",
    "calibre_link-10": "2. The Tree of Knowledge",
    "calibre_link-11": "3. A Day in the Life of Adam and Eve",
    "calibre_link-12": "4. The Flood",
    "calibre_link-13": "Part Two: The Agricultural Revolution",
    "calibre_link-14": "5. History's Biggest Fraud",
    "calibre_link-15": "6. Building Pyramids",
    "calibre_link-16": "7. Memory Overload",
    "calibre_link-17": "8. There is No Justice in History",
    "calibre_link-18": "Part Three: The Unification of Humankind",
    "calibre_link-19": "9. The Arrow of History",
    "calibre_link-20": "10. The Scent of Money",
    "calibre_link-21": "11. Imperial Visions",
    "calibre_link-22": "12. The Law of Religion",
    "calibre_link-23": "13. The Secret of Success",
    "calibre_link-24": "Part Four: The Scientific Revolution",
    "calibre_link-25": "14. The Discovery of Ignorance",
    "calibre_link-26": "15. The Marriage of Science and Empire",
    "calibre_link-27": "16. The Capitalist Creed",
    "calibre_link-28": "17. The Wheels of Industry",
    "calibre_link-29": "18. A Permanent Revolution",
    "calibre_link-30": "19. And They Lived Happily Ever After",
    "calibre_link-31": "20. The End of Homo Sapiens",
    "calibre_link-32": "Afterword: The Animal that Became a God",
    "calibre_link-33": "Notes",
    "calibre_link-34": "Acknowledgements",
    "calibre_link-35": "Image credits"
}

PART_HEADERS = [
    "Part One: The Cognitive Revolution",
    "Part Two: The Agricultural Revolution",
    "Part Three: The Unification of Humankind",
    "Part Four: The Scientific Revolution"
]

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
        # Fallback if no such div found (unlikely for this file)
        blocks = [full_body_content]

    print(f"Found {len(blocks)} content blocks.")

    chapters = []
    current_chapter = {
        "title": "Front Matter",
        "filename": "index.html",
        "content_blocks": [],
        "is_part_header": False
    }

    # Regex to find the Anchors that define chapters
    # We look for the <p id="calibre_link-X" class="calibre_6"> inside the block
    anchor_pattern = re.compile(r'id="(calibre_link-\d+)"', re.IGNORECASE)
    
    # Track which anchor started the current chapter to avoid duplicates
    current_anchor_id = None

    for block in blocks:
        # Check if this block contains a defining anchor
        found_new_chapter = False
        target_anchor = None
        
        # We need to find the *first* matching anchor in this block that is in our HEADINGS_MAP
        matches = anchor_pattern.findall(block)
        for anchor in matches:
            if anchor in HEADINGS_MAP:
                target_anchor = anchor
                break
        
        if target_anchor:
            # We found a start of a new section
            new_title = HEADINGS_MAP[target_anchor]
            
            # Save previous chapter if it has content
            if current_chapter["content_blocks"]:
                chapters.append(current_chapter)
            
            # Start new chapter
            safe_title = re.sub(r'[^\w\s-]', '', new_title).strip().replace(' ', '_').lower()
            if "part_" in safe_title and len(safe_title) < 20: 
                 # heuristic for part headers to keep filename simple if desired, 
                 # but numbered is better for ordering
                 pass
            
            # Determine filename
            # Special case for Index
            if new_title == "Title Page":
                 filename = "index.html"
            else:
                 # Sequential naming is safer to keep order
                 filename = f"chapter_{len(chapters):02d}.html"

            current_chapter = {
                "title": new_title,
                "filename": filename,
                "content_blocks": [block],
                "is_part_header": new_title in PART_HEADERS
            }
            current_anchor_id = target_anchor
        else:
            # Continue current chapter
            current_chapter["content_blocks"].append(block)

    # Add last chapter
    if current_chapter:
        chapters.append(current_chapter)

    # Generate TOC HTML
    toc_html = ""
    # Add explicit link to Front Matter if not covered
    # (The loop above handles it if Title Page was found, otherwise we might miss it)
    
    for ch in chapters:
        # If it's a Part Header, we can style it differently or just add it
        title = ch["title"]
        filename = ch["filename"]
        
        if ch["is_part_header"]:
            # Combine header and link to avoid duplication
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
            prev_btn = f'<a href="{prev_ch["filename"]}" class="nav-btn prev">← Previous</a>'
            
        next_btn = ""
        if i < len(chapters) - 1:
            next_ch = chapters[i+1]
            next_btn = f'<a href="{next_ch["filename"]}" class="nav-btn next">Next →</a>'

        content = "\n".join(ch["content_blocks"])
        
        # Inject IDs into links if needed ? 
        # The internal links like <a href="#calibre_link-45"> work if the target ID is on the same page.
        # But we split pages. 
        # FIX: We need to rewrite internal hrefs.
        # Map all锚点 -> Filename
        
        # NOT IMPLEMENTED YET: Complex rewrites. 
        # Implementation Plan Option A: "保留链接但转换为页内锚点" which implies if it's on same page it works. 
        # If it's on distinct page, it breaks.
        # User accepted plan which said "Proposal A: Keep as anchor".
        # However, for a better experience, basic remapping is good if simple.
        # Since we have the chapters, let's verify if we can easily map.
        
        # Not doing complex remapping now as per plan Step 1 (Implementation Phase) 
        # just focused on generation.
        
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
