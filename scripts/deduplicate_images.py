#!/usr/bin/env python3
"""
Deduplicate images in the public/images directory.
This script:
1. Finds duplicate images (files with " (1)" suffix that match originals)
2. Updates references in public/index.html to use the original filename
3. Removes the duplicate files
"""

import os
import re
import hashlib

# Get the project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'public')
IMAGES_DIR = os.path.join(PUBLIC_DIR, 'images')
INDEX_HTML = os.path.join(PUBLIC_DIR, 'index.html')


def get_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()


def find_duplicates(images_dir):
    """
    Find duplicate images based on the " (1)" naming pattern.
    Returns a dict mapping duplicate filename -> original filename
    """
    duplicates = {}
    
    # Pattern: "filename (1).ext" -> "filename.ext"
    pattern = re.compile(r'^(.+) \(1\)(\.[^.]+)$')
    
    for filename in os.listdir(images_dir):
        match = pattern.match(filename)
        if match:
            base, ext = match.groups()
            original = base + ext
            original_path = os.path.join(images_dir, original)
            duplicate_path = os.path.join(images_dir, filename)
            
            # Verify original exists
            if os.path.exists(original_path):
                # Optional: verify they're actually the same file
                if get_file_hash(original_path) == get_file_hash(duplicate_path):
                    duplicates[filename] = original
                else:
                    print(f"Warning: {filename} differs from {original}, keeping both")
            else:
                # Original doesn't exist, rename duplicate to original
                print(f"Original missing, renaming: {filename} -> {original}")
                os.rename(duplicate_path, original_path)
    
    return duplicates


def update_html_references(html_path, duplicates):
    """Update HTML file to reference original images instead of duplicates."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for dup_name, orig_name in duplicates.items():
        # Handle URL-encoded spaces: " " -> "%20"
        dup_encoded = dup_name.replace(' ', '%20')
        orig_encoded = orig_name.replace(' ', '%20')
        
        # Replace both forms
        content = content.replace(f'images/{dup_name}', f'images/{orig_name}')
        content = content.replace(f'images/{dup_encoded}', f'images/{orig_encoded}')
    
    if content != original_content:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def remove_duplicates(images_dir, duplicates):
    """Remove duplicate image files."""
    removed = 0
    for dup_name in duplicates:
        dup_path = os.path.join(images_dir, dup_name)
        if os.path.exists(dup_path):
            os.remove(dup_path)
            removed += 1
    return removed


def main():
    print(f"Scanning {IMAGES_DIR} for duplicates...")
    
    if not os.path.exists(IMAGES_DIR):
        print(f"Error: Images directory not found: {IMAGES_DIR}")
        return
    
    # Count before
    before_count = len(os.listdir(IMAGES_DIR))
    
    # Find duplicates
    duplicates = find_duplicates(IMAGES_DIR)
    print(f"Found {len(duplicates)} duplicate images")
    
    if not duplicates:
        print("No duplicates to remove.")
        return
    
    # Update HTML references
    if os.path.exists(INDEX_HTML):
        if update_html_references(INDEX_HTML, duplicates):
            print(f"Updated references in {INDEX_HTML}")
        else:
            print("No references needed updating in index.html")
    
    # Remove duplicates
    removed = remove_duplicates(IMAGES_DIR, duplicates)
    print(f"Removed {removed} duplicate files")
    
    # Count after
    after_count = len(os.listdir(IMAGES_DIR))
    print(f"Images: {before_count} -> {after_count} (saved {before_count - after_count} files)")


if __name__ == "__main__":
    main()
