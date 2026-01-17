
import os
import re
import shutil

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'dist_silkroads')

# Book Specific Config
SOURCE_DIR_NAME = 'The Silk Roads_ A New History of the World - Peter Frankopan'
SOURCE_FILE = os.path.join(PROJECT_ROOT, SOURCE_DIR_NAME, 'index.html')
IMAGES_DIR_NAME = 'images'
THEME_CSS_NAME = 'theme_silkroads.css'

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - The Silk Roads</title>
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
            <span class="mobile-title">The Silk Roads</span>
        </div>

        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="index.html" class="book-title">The Silk Roads</a>
                <span class="book-subtitle">A New History of the World</span>
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
                
                <div class="navigation-footer">
                    {prev_button}
                    {next_button}
                </div>
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
    Targeting the TOC block: <div class="calibre" id="calibre_link-5">
    Returns a dictionary: { "calibre_link-X": "Title" } where X is the anchor ID.
    """
    toc_map = {}
    
    # Locate the TOC block
    # Based on file inspection, it's roughly lines 72-141, id="calibre_link-5"
    
    start_marker = '<div class="calibre" id="calibre_link-5">'
    # We can look for the next div class="calibre" to end the block
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Warning: Could not find strict TOC block start. Using loose regex.")
        search_area = content 
    else:
        # Find next div that is a sibling or subsequent block
        # A simple way is to find the next <div class="calibre" after the start
        # but we need to be careful about nesting.
        # Actually, let's just grab a chunk of text or use regex to find the end div
        end_idx = content.find('<div class="calibre"', start_idx + len(start_marker))
        if end_idx == -1:
             search_area = content[start_idx:]
        else:
             search_area = content[start_idx:end_idx]
    
    # Extract links
    # <a href="#calibre_link-13" class="calibre1">Chapter 1: ...</a>
    link_pattern = re.compile(r'<a href="#(calibre_link-\d+)"[^>]*>(.*?)</a>', re.DOTALL)
    
    matches = link_pattern.findall(search_area)
    for link_id, link_inner in matches:
        # Strip spans/tags to get clean text
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
    
    # Extract Body Content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if not body_match:
        print("Could not find body tag.")
        return
    full_body_content = body_match.group(1)

    # Split into blocks
    # Pattern: <div class="calibre" id="calibre_link-36">
    parts = re.split(r'(<div class="calibre"[^>]*>)', full_body_content)
    
    blocks = []
    # parts[0] is usually empty or whitespace
    # parts[1] is delim, parts[2] is content, parts[3] is delim...
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            header = parts[i]
            body = parts[i+1]
            
            # Note: We don't rely on the Div ID for the chapter mapping directly, 
            # but on the anchor ID inside the block.
            
            full_block = header + body
            blocks.append({
                "content": full_block
            })

    print(f"Found {len(blocks)} content blocks.")

    chapters = []
    
    # Start with a front-matter chapter
    current_chapter = {
        "title": "Front Matter",
        "filename": "index.html",
        "content_blocks": []
    }
    chapters.append(current_chapter)
    
    # Regex to find anchors or IDs: id="calibre_link-XXX"
    anchor_pattern = re.compile(r'id="(calibre_link-\d+)"')

    for block in blocks:
        block_content = block["content"]
        
        # Check if this block contains an anchor that is in our TOC map
        anchors = anchor_pattern.findall(block_content)
        
        # Determine if we need to start a new chapter
        is_new_chapter = False
        new_chapter_title = ""
        
        for anchor in anchors:
            if anchor in toc_map:
                is_new_chapter = True
                new_chapter_title = toc_map[anchor]
                break
        
        if is_new_chapter:
            print(f"Starting chapter: {new_chapter_title}")
            
            # Determine filename
            safe_title = re.sub(r'[^\w\s-]', '', new_chapter_title).strip().replace(' ', '_')
            # Shorten if too long
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
                
            filename = f"chapter_{len(chapters):02d}_{safe_title}.html"
            
            # If it's the very first match (Cover/Images/Title Page), we might want to keep it in index.html
            # But usually index.html is the "Front Matter".
            # If the TOC has "Cover", that might be the fast one.
            
            new_chapter = {
                "title": new_chapter_title,
                "filename": filename,
                "content_blocks": [block_content]
            }
            chapters.append(new_chapter)
            current_chapter = new_chapter
        else:
            # Append to current
            current_chapter["content_blocks"].append(block_content)

    # Build Anchor Map
    # Map anchor ID to filename: { 'calibre_link-123': 'chapter_01.html', ... }
    anchor_id_to_filename = {}
    
    # Also capture generic IDs if possible, but calibre mostly uses calibre_link-XXX
    # We'll use the same anchor_pattern regex
    
    for ch in chapters:
        filename = ch["filename"]
        for block in ch["content_blocks"]:
            # Find all IDs in this block
            ids = anchor_pattern.findall(block)
            for aid in ids:
                anchor_id_to_filename[aid] = filename

    print(f"Mapped {len(anchor_id_to_filename)} anchors to files.")

    # Fix Links in Content
    # Regex to find links: href="#calibre_link-XXX"
    link_replace_pattern = re.compile(r'href="#(calibre_link-\d+)"')

    def replace_link(match, current_filename):
        link_id = match.group(1)
        if link_id in anchor_id_to_filename:
            target_filename = anchor_id_to_filename[link_id]
            # If target is different file, rewrite link
            if target_filename != current_filename:
                return f'href="{target_filename}#{link_id}"'
        # Otherwise keep as is
        return match.group(0)

    # Process all chapters to update links
    for ch in chapters:
        current_filename = ch["filename"]
        new_blocks = []
        for block in ch["content_blocks"]:
            # Use partial/lambda to pass current context if needed, but simple iteration works
            # We need to pass current_filename to the replacer
            # re.sub with a function: func(match_obj)
            
            updated_block = link_replace_pattern.sub(lambda m: replace_link(m, current_filename), block)
            new_blocks.append(updated_block)
        ch["content_blocks"] = new_blocks

    # Generate TOC HTML for sidebar
    toc_html = ""
    for ch in chapters:
        title = ch["title"]
        filename = ch["filename"]
        # Skip empty front matter if it has no title or weird title
        if title == "Front Matter" and len(ch["content_blocks"]) == 0:
            continue
            
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
            prev_title = "Previous"
            prev_btn = f'<a href="{prev_ch["filename"]}" class="nav-btn">← {prev_title}</a>'
            
        next_btn = ""
        if i < len(chapters) - 1:
            next_ch = chapters[i+1]
            next_title = "Next"
            next_btn = f'<a href="{next_ch["filename"]}" class="nav-btn">{next_title} →</a>'

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
