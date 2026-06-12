---
name: convert-pdf-to-md
description: Extract text from PDF files and convert to searchable Markdown using Microsoft MarkItDown. Use when importing PDFs into the vault, extracting text from research papers, or converting PDF to Markdown.
---

# convert-pdf-to-md

Extracts text content from PDF files and outputs clean, LLM-optimized Markdown with preserved structure (headings, lists, tables, links) and frontmatter.

## Trigger Phrases

- "Convert this PDF to markdown"
- "Extract text from PDF"
- "Make this PDF searchable"
- "Process PDF"

## Usage

### Via Script (Recommended)

Default method with custom frontmatter for vault integration:

```powershell
python .agent/scripts/convert-pdf-to-md.py "Inbox/document.pdf"
```

Output: `Inbox/document.md` (same directory, same name)

### With Custom Output Path

```powershell
python .agent/scripts/convert-pdf-to-md.py "Inbox/document.pdf" "01_Projects/Project Atlas/document.md"
```

### Via CLI (Fallback)

Quick conversion without custom frontmatter:

```powershell
python -m markitdown "Inbox/document.pdf" -o "Inbox/document.md"
```

Or with stdout:
```powershell
python -m markitdown "Inbox/document.pdf" > "Inbox/document.md"
```

## Output Format

```markdown
---
source: "original-filename.pdf"
converted_with: "markitdown"
extracted: true
---

# Document Title

[Structured content with preserved headings, lists, tables, and links...]
```

## Features

- **Structure preservation**: Maintains headings, lists, tables, and links
- **LLM-optimized**: Designed for consumption by GPT-4o and similar models
- **Frontmatter**: Source file and conversion metadata
- **UTF-8 encoding**: Handles international characters
- **Token-efficient**: Uses Markdown conventions understood by LLMs

## Limitations

- **Scanned PDFs**: No OCR in basic mode (use Azure Document Intelligence for OCR)
- **Images**: Not extracted by default (text only)
- **Complex layouts**: Best-effort conversion for complex formatting

## Dependencies

- Python 3.10+
- MarkItDown (`pip install 'markitdown[pdf]'`)

## Script vs CLI

**Use Script** (`convert-pdf-to-md.py`) - Default:
- Custom YAML frontmatter for vault integration
- Consistent metadata across all converted documents
- Tracks conversion method and source file
- Best for documents staying in the vault

**Use CLI** (`python -m markitdown`) - Fallback:
- Quick, one-off conversions
- When frontmatter isn't needed
- Piping or batch processing
- Fastest for temporary conversions

## Advanced Usage

### Azure Document Intelligence (OCR Support)

For better PDF extraction with OCR support:
```powershell
python -m markitdown document.pdf -o output.md -d -e "<azure_endpoint>"
```

### Batch Processing

Process multiple PDFs:
```powershell
Get-ChildItem "Inbox/*.pdf" | ForEach-Object {
    python -m markitdown $_.FullName -o ($_.BaseName + ".md")
}
```

### Reading from Stdin

```powershell
cat document.pdf | python -m markitdown -x pdf > output.md
```

## Related Skills

- `convert-with-docling` — AI layout analysis/OCR for complex or scanned PDFs
- `compile-wiki` — Compiles converted markdown into an interlinked wiki
