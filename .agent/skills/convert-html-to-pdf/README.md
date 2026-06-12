---
name: convert-html-to-pdf
description: Convert HTML files to PDF using Playwright headless Chromium with auto-detection for slide decks vs document pages.
---

# Convert HTML to PDF

High-fidelity HTML-to-PDF conversion powered by Playwright (headless Chromium). Automatically detects slide decks and renders each slide as a full-page, or treats regular HTML as a paginated document.

## Quick Start

```powershell
python .agent/scripts/html-to-pdf.py "path/to/file.html"
```

Creates `path/to/file.pdf` alongside the original. The script auto-detects whether it's a slide deck or a regular page.

## When to Use

- Exporting HTML slide presentations to PDF for sharing or printing
- Converting styled HTML reports/pages to PDF
- Preserving web fonts, dark backgrounds, and CSS layouts in PDF output
- Archiving HTML content as PDF

## Examples

```powershell
# Slide deck (auto-detected)
python .agent/scripts/html-to-pdf.py "01_Projects/Project Atlas/Annual/presentation.html"

# Force document mode, A4 format
python .agent/scripts/html-to-pdf.py "report.html" --page --format=A4

# Custom output path
python .agent/scripts/html-to-pdf.py "deck.html" "exports/deck.pdf"

# Higher resolution slides
python .agent/scripts/html-to-pdf.py "deck.html" --slides --width=2560 --height=1440
```

## Requirements

```powershell
pip install playwright
playwright install chromium
```

## Notes

- Fonts are loaded via network idle detection + a configurable wait (`--wait` flag)
- All CSS animations/reveals are force-triggered so nothing is hidden in the PDF
- Interactive elements (nav dots, progress bars) are automatically stripped
- Backgrounds are always preserved (dark slides, accent colors, grid patterns)
