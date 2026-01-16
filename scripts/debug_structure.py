import re

SOURCE_FILE = 'index_backup.html'

def main():
    print(f"Reading {SOURCE_FILE}...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if not body_match:
        print("No body found")
        return
    
    full_body_content = body_match.group(1)
    # Split by the calibre div same as before
    parts = re.split(r'(<div class="calibre"[^>]*>)', full_body_content)
    
    blocks = []
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            blocks.append(parts[i] + parts[i+1])

    print(f"Found {len(blocks)} blocks.")
    
    # Look for patterns
    # Matches <h1, <h2, <h3 etc.
    header_pattern = re.compile(r'<(h[1-6])[^>]*>(.*?)</\1>', re.DOTALL | re.IGNORECASE)
    
    for idx, block in enumerate(blocks):
        matches = header_pattern.findall(block)
        for tag, text in matches:
            # Clean tags from text
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            print(f"Block {idx}: <{tag}> {clean_text}")

if __name__ == "__main__":
    main()
