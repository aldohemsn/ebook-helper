# Design Principles for Static Ebook Websites

## Handling Long Sidebar Navigation

For content-heavy ebooks (like dictionaries or comprehensive collections) with thousands of entries, a standard flat list or simple nested list in the sidebar can become unwieldy and slow. We implemented the following design principles to ensure usability and performance:

### 1. Multi-Level Hierarchy
Instead of a flat list, structure the navigation into logical levels. For *Tang Shi Song Ci Yuan Qu Gu Wen*, we used a three-level hierarchy:
- **Volume Level** (Top): e.g., *Tang Shi*, *Song Ci*, *Gu Wen*. These serve as the main containers.
- **Author Level** (Middle): e.g., *Li Bai*, *Du Fu*. This groups individual works.
- **Work Level** (Bottom): The actual poems or essays.

### 2. Initial State: Collapse All
To prevent overwhelming the user and the browser:
- On initial load (index page), only the top-level Volume headers are visible.
- All Author and Work lists are collapsed (hidden) by default.
- This creates a clean, "book-shelf" like appearance.

### 3. Active Path Expansion
When a user navigates to a specific page (e.g., a specific poem), the sidebar automation logic:
- Identifies the current active link.
- Expands *only* the specific parent hierarchy (Author -> Volume) for that link.
- Keeps all other branches collapsed.
- Scrolls the sidebar to center the active link.

### 4. Accordion-Style Interaction
To maintain a manageable sidebar length during navigation:
- **Sibling Collapse**: When opening a new section (Volume or Author), automatically close any other open siblings at the same level.
- **Deep Collapse**: When closing a parent item, validly collapse all its descendants so that re-opening it starts fresh (or preserves state if that's the preferred UX, but currently we reset).
- This ensures that typically only one "path" is fully open at a time, mimicking a physical book where you can only be in one chapter at a time.

### 5. Visual Hierarchy
Use distinct visual cues to differentiate levels:
- **Volume Headers**: Prominent styling (e.g., larger font, distinct background color, colored accents/borders) to act as visual anchors.
- **Author Headers**: Subtle indentation and background differentiation.
- **Works**: Standard link styling with deep indentation.

## Technical Implementation Notes

- **CSS Classes**: Use semantic classes like `.volume-level`, `.author-level`, `.has-children`, and `.nested.collapsed` to control visibility and styling.
- **JavaScript**: Use concise event delegation or specific event listeners on toggle buttons. Avoid heavy DOM manipulation; simply toggle CSS classes (`.collapsed`, `.expanded`).
- **Performance**: For 5000+ items, using CSS `display: none` (via class) is much faster than adding/removing DOM nodes.
