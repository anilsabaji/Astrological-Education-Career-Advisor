# Standalone (browser) edition

A fully client-side version of the adviser. It runs entirely in the browser
using the [astronomy-engine](https://github.com/cosinekitty/astronomy) model for
sidereal planetary positions (validated against Swiss Ephemeris to ~0.004 deg).
Rahu/Ketu use the mean lunar node.

## Source files
- `engine.js`  - the full KP + Parashara + Vimshottari + Varga engine (no DOM).
- `ui.js`      - form handling, tabbed rendering and print-to-PDF.
- `styles.css` - screen + colourful print stylesheet.
- `build.js`   - inlines astronomy-engine + engine + ui + css into one HTML file.

## Rebuild `docs/index.html`
```bash
cd standalone
npm install
npm run build        # writes ../docs/index.html
```
The generated `docs/index.html` is a single self-contained file (no network
required) and is what GitHub Pages serves.
