---
name: convert-html-to-pdf
description: Convert HTML files to PDF using Playwright headless Chromium, with auto-detection for slide decks vs document pages. Use when converting HTML presentations to PDF, exporting HTML slide decks, printing HTML pages to PDF, or preserving HTML formatting in PDF output.
---

# convert-html-to-pdf

Converts HTML files to high-fidelity PDF using Playwright (headless Chromium). Auto-detects whether the input is a slide deck or a regular document and applies the appropriate rendering strategy.

## Trigger Phrases

- "Convert this HTML to PDF"
- "Export this presentation to PDF"
- "Print this HTML as PDF"
- "Save this slide deck as PDF"
- "HTML to PDF"

## Modes

### Slide Deck Mode (`--slides`)
Auto-detected when the HTML contains multiple `.slide`, `.swiper-slide`, or `section[data-slide]` elements.

- Renders each slide as a full-bleed 1920×1080 page
- Triggers all reveal/animation classes so hidden content becomes visible
- Hides interactive UI (nav dots, progress bars, controls)
- Disables scroll-snap for proper page breaks

### Document Mode (`--page`)
Used for standard HTML pages, reports, articles.

- Renders as paginated Letter/A4 with 0.5in margins
- Preserves backgrounds and print styles

## Usage

### Basic (auto-detect mode)

```
**Agent:** shell-execute
python .agent/scripts/html-to-pdf.py "path/to/file.html"
```

Output: `path/to/file.pdf` (same directory, same name)

### Custom output path

```
**Agent:** shell-execute
python .agent/scripts/html-to-pdf.py "path/to/file.html" "output/result.pdf"
```

### Force slide mode

```
**Agent:** shell-execute
python .agent/scripts/html-to-pdf.py "path/to/deck.html" --slides
```

### Force document mode with A4

```
**Agent:** shell-execute
python .agent/scripts/html-to-pdf.py "path/to/page.html" --page --format=A4
```

### Custom viewport for slides

```
**Agent:** shell-execute
python .agent/scripts/html-to-pdf.py "path/to/deck.html" --slides --width=2560 --height=1440
```

### Longer wait for heavy pages

```
**Agent:** shell-execute
python .agent/scripts/html-to-pdf.py "path/to/page.html" --wait=5000
```

## CLI Arguments

| Argument     | Default  | Description                                      |
|-------------|----------|--------------------------------------------------|
| `input`     | required | Path to HTML file                                |
| `output`    | auto     | Output PDF path (defaults to same name `.pdf`)   |
| `--slides`  | auto     | Force slide deck mode                            |
| `--page`    | auto     | Force document page mode                         |
| `--width`   | 1920     | Viewport width in px (slides mode)               |
| `--height`  | 1080     | Viewport height in px (slides mode)              |
| `--format`  | Letter   | Page format for document mode (Letter, A4, etc.) |
| `--wait`    | 3000     | Wait time in ms for fonts/async rendering        |

## What It Handles

- Google Fonts and web fonts (waits for network idle + configurable delay)
- CSS animations and reveal classes (force-triggered for print)
- Dark/accent slide backgrounds (`print_background: true`)
- Scroll-snap layouts (disabled for proper pagination)
- Interactive navigation elements (hidden in output)
- `clamp()` and viewport-relative CSS units (rendered at actual viewport size)

## Dependencies

- Python 3.10+
- Playwright (`pip install playwright`)
- Chromium browser (`playwright install chromium`)

## Related Skills

- `convert-pdf-to-md` — Reverse direction: PDF to Markdown
- `convert-docx-to-md` — Word to Markdown
- `compile-wiki` — Produces the HTML-ready wiki articles this skill can render
