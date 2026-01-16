# Ebook to Static Site Generator

Convert monolithic HTML ebooks (exported from Calibre) into modern, responsive, and aesthetically pleasing static websites.

## Features

- **Dependency-Free**: Uses only Python's built-in libraries (no pip install required)
- **Premium Design**: Clean, paper-like reading interface with beautiful Chinese typography
- **Responsive Layout**: Desktop sidebar + mobile hamburger menu
- **Offline-First**: Uses system fonts, no CDN dependencies
- **Visual Enhancements**: Breakout images, lightbox, and smooth animations

## Project Structure

```
ebook-helper/
├── public/              # Place your ebook source files here
│   ├── index.html       # Calibre-exported HTML
│   └── images/          # Images folder
├── scripts/
│   ├── generate_site.py # Main generation script
│   └── theme.css        # Styling for generated site
├── dist/                # Generated output (auto-created)
└── README.md
```

## Quick Start

### 1. Prepare Your Ebook

Export your ebook as HTML from Calibre, then place the files in the `public/` directory:

```bash
public/
├── index.html    # Main HTML file
└── images/       # Images folder (if any)
```

### 2. Generate the Static Site

```bash
python3 scripts/generate_site.py
```

### 3. View the Result

The generated site will be in the `dist/` folder. Open `dist/index.html` in your browser, or serve it locally:

```bash
# Using Python's built-in server
cd dist && python3 -m http.server 8080
```

## Technical Details

### Content Processing

- Uses regex-based parsing to split the source HTML
- Identifies chapter headers (`<h1 class="calibre4">`) as split points
- Generates individual `chapter_XX.html` files

### Design Features

- **Typography**: Noto Serif TC / System Font Stack (Songti, PMingLiU, Source Han Serif)
- **Layout**: Fixed sidebar navigation with card-style content area
- **Images**: "Breakout" styling with deep shadows for visual impact
- **Interaction**: Click-to-zoom lightbox for images

### Navigation

- Auto-generated table of contents with volume/section headers
- Active chapter highlighting in sidebar

## License

MIT License
