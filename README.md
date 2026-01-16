# Ebook to Static Site Generator

This project contains tools and resources to convert a monolithic HTML ebook (exported from Calibre) into a modern, responsive, and aesthetically pleasing static website.

## Project Overview

The goal was to transform a heavy single-page HTML file (10MB+) into a lightweight, navigable static site structure suitable for web hosting or offline reading.

## Technical Approach

### 1. Content Processing (`generate_site.py`)
*   **Dependency-Free Parsing**: Instead of using heavy libraries like `BeautifulSoup`, the script uses Python's built-in `re` (regular expressions) to split the source HTML. This ensures the script runs in any standard Python environment without installation steps.
*   **Segmentation Strategy**:
    *   The script identifies content blocks using the `div class="calibre"` structure.
    *   It detects Chapter headers (`<h1 class="calibre4">`) to create split points.
    *   Generates individual files per chapter (e.g., `chapter_01.html`).
*   **Templating**: Uses a concise HTML5 template string to wrap extracted content with navigation, scripts, and meta tags.

### 2. Design & User Experience (`theme.css`)
*   **Premium Aesthetic**: A clean, paper-like reading interface using `Noto Serif TC` (or compatible system fonts) for body text and a dark, fixed sidebar for navigation.
*   **Responsive Layout**:
    *   **Desktop**: Persistent left sidebar with a "card-style" content area.
    *   **Mobile**: Sidebar is hidden by default and accessible via a hamburger menu (created via vanilla JS injection).
*   **Offline-First**:
    *   **Local Fonts**: Removed dependencies on Google Fonts/CDNs. The CSS uses a robust "System Font Stack" (Songti, PMingLiU, Source Han Serif) to render beautiful Chinese typography using fonts already present on the user's OS.
*   **Visual Enhancements**:
    *   **"Breakout" Images**: Content images are styled to be wider than the text column with deep shadows (3D effect), creating a "pop-out" visual rhythm (`width: calc(100% + 6rem)`).
    *   **Lightbox**: Included a vanilla JS/CSS lightbox to zoom into images when clicked.

### 3. Navigation Structure
*   **Volume Segmentation**: The processing script maps chapter filenames to their corresponding Book/Volume titles (e.g., "第一卷：從神話到歷史"), inserting them as section headers in the sidebar.
*   **Smart TOC**: The sidebar highlights the current active chapter automatically.

## Usage

1.  Place the source `index.html` and `images/` folder in the data directory.
2.  Run the generation script:
    ```bash
    python3 generate_site.py
    ```
3.  The script will:
    *   Parse `index_backup.html` (renamed source).
    *   Generate `index.html` (Cover) and `chapter_XX.html` files.
    *   Copy `images/` and `theme.css` to the output.
    *   (Optional) Move generated files to the root level.
