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
│   ├── generate_site.py           # Generator for Chinese ebooks (e.g., 講談社中國史)
│   ├── generate_sapiens.py        # Generator for Sapiens (English)
│   ├── generate_renlei.py         # Generator for 人類大歷史 (Traditional Chinese Sapiens)
│   ├── generate_sichou.py         # Generator for 絲綢之路 (Taiwan Edition)
│   ├── generate_sichou_shao.py    # Generator for 絲綢之路 (Shao Xudong Translation)
│   ├── generate_silkroads.py      # Generator for The Silk Roads (Peter Frankopan)
│   ├── theme.css                  # Theme for Chinese books
│   ├── theme_sapiens.css          # Theme for English books  
│   ├── theme_renlei.css           # Theme for Traditional Chinese history books
│   ├── theme_sichou.css           # Theme for Silk Roads (Taiwan)
│   ├── theme_sichou_shao.css      # Theme for Silk Roads (Shao Xudong)
│   ├── theme_silkroads.css        # Theme for Silk Roads (Peter Frankopan)
│   └── deduplicate_images.py      # Utility to remove duplicate images
├── public/                        # Place Chinese ebook source files here
├── ren-lei-da-li-shi/             # 人類大歷史 source (gitignored)
├── si-chou-zhi-lu/                # 絲綢之路 Taiwan edition source (gitignored)
├── si-chou-zhi-lu-shao-xu-dong/   # 絲綢之路 Shao Xudong translation source (gitignored)
├── The Silk Roads_ A New History of the World - Peter Frankopan/ # Silk Roads English source (gitignored)
├── dist/                          # Generated output for 人類大歷史 (auto-created)
├── dist_sichou/                   # Generated output for 絲綢之路 Taiwan edition
├── dist_sichou_shao/              # Generated output for 絲綢之路 Shao Xudong edition
├── dist_silkroads/                # Generated output for Silk Roads (Peter Frankopan)
└── README.md
```

## Supported Books

| Book | Generator Script | Theme | Output Directory |
|------|------------------|-------|------------------|
| 講談社中國史 | `generate_site.py` | `theme.css` | `dist/` |
| Sapiens (English) | `generate_sapiens.py` | `theme_sapiens.css` | `dist/` |
| 人類大歷史 (Traditional Chinese Sapiens) | `generate_renlei.py` | `theme_renlei.css` | `dist/` |
| 絲綢之路 (Taiwan Edition) | `generate_sichou.py` | `theme_sichou.css` | `dist_sichou/` |
| 絲綢之路 (Shao Xudong Translation) | `generate_sichou_shao.py` | `theme_sichou_shao.css` | `dist_sichou_shao/` |
| The Silk Roads (Original English) | `generate_silkroads.py` | `theme_silkroads.css` | `dist_silkroads/` |

### Quick Start (The Silk Roads - English)

1. Ensure the ebook source is at `The Silk Roads_ A New History of the World - Peter Frankopan/index.html`
2. Run the generator:
   ```bash
   python3 scripts/generate_silkroads.py
   ```
3. Open `dist_silkroads/index.html` to read.

### Quick Start (Silk Roads - Shao Xudong Edition)

1. Ensure the ebook source is at `si-chou-zhi-lu-shao-xu-dong/index.html`
2. Run the generator:
   ```bash
   python3 scripts/generate_sichou_shao.py
   ```
3. Open `dist_sichou_shao/index.html` to read.

**Note**: The script automatically removes ads and promotional content inserted by ebook piracy sites.

### Quick Start (Traditional Chinese Sapiens)

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
