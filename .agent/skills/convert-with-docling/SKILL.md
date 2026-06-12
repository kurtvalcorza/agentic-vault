---
name: convert-with-docling
description: Convert documents to Markdown using IBM Docling with AI-powered layout analysis, table structure recognition, and optional OCR/VLM. Use when converting complex PDFs with tables/figures, multi-format batch conversion, or when markitdown produces suboptimal results.
---

# convert-with-docling

Convert documents to structured Markdown using Docling's AI-powered document understanding pipeline. Handles complex layouts, tables, figures, formulas, and multi-format input with high fidelity.

## Trigger Phrases

- "Convert this with docling"
- "Parse this PDF with docling"
- "Use docling for this document"
- "Convert with AI layout analysis"
- "This PDF has complex tables"

## Usage

### Via Script (Recommended)

Default conversion with vault-compatible frontmatter:

```bash
python .agent/scripts/convert-with-docling.py "Inbox/document.pdf"
```

Output: `Inbox/document.md` (same directory, same name)

### With Custom Output Path

```bash
python .agent/scripts/convert-with-docling.py "Inbox/document.pdf" "01_Projects/Project Atlas/document.md"
```

### With OCR (Scanned Documents)

```bash
python .agent/scripts/convert-with-docling.py "Inbox/scanned.pdf" --ocr
```

### With VLM Pipeline (Charts, Images, Complex Visuals)

```bash
python .agent/scripts/convert-with-docling.py "Inbox/charts.pdf" --vlm
```

### Via CLI (Quick/Fallback)

```bash
docling "Inbox/document.pdf" --to md
```

For JSON output:
```bash
docling "Inbox/document.pdf" --to json
```

Batch convert a directory:
```bash
docling "Inbox/corpus/" --to md
```

## Output Format

```markdown
---
source: "original-filename.pdf"
converted_with: "docling"
extracted: true
---

# Document Title

[Structured content with preserved headings, tables, figures, formulas...]
```

## Supported Input Formats

| Category | Formats |
|:---------|:--------|
| PDF | `.pdf` (native + scanned with OCR) |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Spreadsheets | `.xlsx` |
| HTML | `.html` |
| Images | `.png`, `.jpg`, `.jpeg`, `.tiff` |
| LaTeX | `.tex` |
| Plain text | `.txt`, `.text` |
| Markdown | `.md`, `.qmd`, `.Rmd` |
| Audio | `.wav`, `.mp3` (with ASR) |
| Subtitles | `.vtt` (WebVTT) |
| XML schemas | USPTO patents, JATS articles, XBRL financial reports |

## Supported Output Formats

Markdown (default), JSON, YAML, HTML, text, DocTags, WebVTT.

## CLI Options Reference

| Option | Description |
|:-------|:------------|
| `--from <format>` | Restrict input format (e.g., `--from pdf`) |
| `--to <format>` | Output format: `md`, `json`, `yaml`, `html`, `text`, `doctags`, `vtt` |
| `--ocr` | Enable OCR for scanned documents |
| `--vlm` | Use VLM pipeline (GraniteDocling) |
| `--num-threads <n>` | Thread count (default: 4) |
| `--device <dev>` | Accelerator: `auto`, `cpu`, `cuda`, `mps` |
| `--document-timeout <s>` | Per-document timeout in seconds |
| `--page-batch-size <n>` | Pages per batch (default: 4) |
| `--show-layout` | Visualize bounding boxes on page images |

## Decision Rules: When to Use Docling

| Condition | Route to |
|:----------|:---------|
| Simple text-heavy PDF, speed priority | `convert-pdf-to-md` (MarkItDown) — fastest |
| Complex tables, figures, formulas in PDF | `convert-with-docling` — AI layout analysis |
| Multi-format batch (PDF + DOCX + PPTX mixed) | `convert-with-docling` — unified pipeline |
| MarkItDown fails or output is poor | `convert-with-docling` — fallback tier |
| Charts/diagrams needing visual understanding | `convert-with-docling --vlm` |
| Scanned PDF needing OCR | `convert-with-docling --ocr` |

## Dependencies

- Python 3.10+
- `docling` (`pip install docling`)
- GPU optional but recommended for large batches (`--device cuda` or `--device mps`)

## Performance Tuning

The script defaults to the `pypdfium2` PDF backend, which is significantly more memory-efficient than the default `docling-parse` backend. This eliminates `std::bad_alloc` errors on image-heavy pages.

| Flag | Effect |
|:-----|:-------|
| `--no-ocr` | Skip OCR entirely (fastest for PDFs with embedded text) |
| `--fast` | No OCR + no table structure + no enrichment (maximum speed) |
| `--ocr` | Force OCR on (for scanned documents) |
| `--backend pypdfium2` | Default. Memory-efficient, handles large images well |
| `--backend docling-parse` | Original C++ backend. Faster text extraction but may OOM on image-heavy pages |
| `--timeout <seconds>` | Per-document timeout (returns partial results on expiry) |

## Related Skills

- `convert-pdf-to-md` — MarkItDown-based PDF extraction (fast, simple)
- `compile-wiki` — Compiles converted markdown into an interlinked wiki
