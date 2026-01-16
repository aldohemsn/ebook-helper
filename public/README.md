# Public Directory

This folder is for placing your ebook source files.

## Required Files

Place the following files exported from Calibre here:

```
public/
├── index.html    # Main HTML file exported from Calibre
└── images/       # Images folder (if any)
    ├── image1.jpg
    ├── image2.png
    └── ...
```

## How to Use

1. Export your ebook as HTML from Calibre
2. Copy `index.html` and the `images/` folder into this directory
3. Run the generation script from the project root:
   ```bash
   python3 scripts/generate_site.py
   ```
4. The generated static site will be created in the `dist/` folder
