# convert-with-docling

Convert documents to Markdown using [Docling](https://github.com/docling-project/docling) — IBM Research's AI-powered document understanding library.

## What It Does

Parses PDFs, DOCX, PPTX, XLSX, HTML, images, LaTeX, and more into clean Markdown with preserved structure. Uses deep learning models for layout analysis and table structure recognition, producing higher-fidelity output than rule-based parsers on complex documents.

## When to Use

- PDFs with complex tables, figures, or formulas
- Mixed-format batch conversions
- When MarkItDown or LiteParse produce suboptimal results
- Documents needing AI-powered layout understanding
- Charts/diagrams requiring visual language model (VLM) processing

## Quick Start

```bash
# Basic conversion
python .agent/scripts/convert-with-docling.py "Inbox/document.pdf"

# With OCR for scanned docs
python .agent/scripts/convert-with-docling.py "Inbox/scanned.pdf" --ocr

# With VLM for charts/images
python .agent/scripts/convert-with-docling.py "Inbox/charts.pdf" --vlm

# CLI shortcut (no frontmatter)
docling "Inbox/document.pdf" --to md
```

## How It Fits in the Vault

This is the escalation tier in the PDF conversion pipeline:

1. **MarkItDown** (`convert-pdf-to-md`) — fast, simple text extraction
2. **Docling** (`convert-with-docling`) — AI layout analysis, OCR, complex tables/figures, multi-format

## Requirements

- Python 3.10+
- `pip install docling`
- GPU optional (speeds up large batches)
