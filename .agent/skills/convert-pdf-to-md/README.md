---
name: convert-pdf-to-md
description: Extract text from PDF files and convert to searchable Markdown using Microsoft MarkItDown
---

# Convert PDF to Markdown

Extracts text from PDF files into searchable, LLM-optimized Markdown format with preserved structure (headings, lists, tables, links).

## Quick Start

**Script (recommended):**
```powershell
python .agent/scripts/convert-pdf-to-md.py "Inbox/your-file.pdf"
```

**CLI (fallback):**
```powershell
python -m markitdown "Inbox/your-file.pdf" -o "Inbox/your-file.md"
```

Creates `Inbox/your-file.md` alongside the original PDF with custom frontmatter (script) or standard output (CLI).

## When to Use

- Making PDFs searchable in Obsidian
- Preparing documents for literature review workflows
- Extracting content for note-taking or synthesis
- Converting research papers, guides, or documentation

## Output

- Markdown file with preserved document structure
- Headings, lists, tables, and links maintained
- YAML frontmatter (when using script)
- LLM-optimized formatting

## Advanced Features

**Azure Document Intelligence (OCR):**
```powershell
python -m markitdown document.pdf -o output.md -d -e "<azure_endpoint>"
```

**Batch Processing:**
```powershell
Get-ChildItem "Inbox/*.pdf" | ForEach-Object {
    python -m markitdown $_.FullName -o ($_.BaseName + ".md")
}
```

## Notes

- Works best on text-based PDFs
- For scanned PDFs, use Azure Document Intelligence option for OCR
- MarkItDown is optimized for LLM consumption (GPT-4o, and other AI assistants)
- Supports many formats beyond PDF (DOCX, PPTX, XLSX, images, audio)
