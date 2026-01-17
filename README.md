# Ebook to Static Site Generator

Convert monolithic HTML ebooks (exported from Calibre) into modern, responsive, and aesthetically pleasing static websites.

## Features

- **Dependency-Free**: Uses only Python's built-in libraries (no pip install required)
- **Premium Design**: Clean, paper-like reading interface with beautiful typography
- **Responsive Layout**: Desktop sidebar + mobile hamburger menu
- **Offline-First**: Uses system fonts, no CDN dependencies
- **Visual Enhancements**: Breakout images, lightbox, and smooth animations

## Project Structure

```
ebook-helper/
├── scripts/
│   ├── generate_site.py       # Generator for Chinese ebooks (e.g., 講談社中國史)
│   ├── generate_sapiens.py    # Generator for Sapiens (English)
│   ├── theme.css              # Theme for Chinese books
│   ├── theme_sapiens.css      # Theme for English books  
│   └── deduplicate_images.py  # Utility to remove duplicate images
├── public/                    # Place Chinese ebook source files here
├── sapiens-.../               # Place Sapiens source files here (gitignored)
├── dist/                      # Generated output (auto-created)
└── README.md
```

## Supported Books

| Book | Generator Script | Theme |
|------|------------------|-------|
| 講談社中國史 (Chinese) | `generate_site.py` | `theme.css` |
| Sapiens: A Brief History of Humankind (English) | `generate_sapiens.py` | `theme_sapiens.css` |
| 人類大歷史 (Traditional Chinese) | `generate_renlei.py` | `theme.css` |

### Quick Start (Chinese Sapiens)

1. Ensure the ebook source is at `ren-lei-da-li-shi/index.html`
2. Run the generator:
   ```bash
   python3 scripts/generate_renlei.py
   ```
3. Open `dist/index.html` to read.

## Quick Start

### 1. Prepare Your Ebook

Export your ebook as HTML from Calibre, then place the files in the appropriate directory.

### 2. Generate the Static Site

For Chinese books:
```bash
python3 scripts/generate_site.py
```

For Sapiens:
```bash
python3 scripts/generate_sapiens.py
```

### 3. View the Result

The generated site will be in the `dist/` folder. Open `dist/index.html` in your browser, or serve it locally:

```bash
cd dist && python3 -m http.server 8080
```

## Technical Details

### Content Processing

- Uses regex-based parsing to split the source HTML
- Identifies chapter/section markers as split points
- Generates individual `chapter_XX.html` files with navigation

### Design Features

- **Chinese Typography**: Noto Serif TC / System Font Stack (Songti, Source Han Serif)
- **English Typography**: Georgia, Times New Roman (optimized line length ~75-80 chars)
- **Layout**: Fixed sidebar navigation with card-style content area
- **Images**: Breakout styling with shadows for visual impact
- **Interaction**: Click-to-zoom lightbox for images

### Navigation

- Auto-generated table of contents with volume/section headers
- Active chapter highlighting in sidebar
- Previous/Next navigation buttons

## License

MIT License
