---
name: convert-docx-to-md
description: Convert Microsoft Word documents (.docx) to Markdown (.md) using Pandoc for seamless integration into the Obsidian vault
---

# Convert DOCX to Markdown

A utility skill for converting Word documents to Obsidian-ready Markdown files.

## Quick Start

```powershell
# Single file
.\.agent\scripts\convert-docx-to-md.ps1 -Source "path\to\document.docx"

# Entire folder
.\.agent\scripts\convert-docx-to-md.ps1 -Source "Inbox" -Recursive
```

## Requirements

- **Pandoc** must be installed ([pandoc.org](https://pandoc.org/installing.html))
- PowerShell 5.1+ or PowerShell Core

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-Source` | String | Required | Path to `.docx` file or directory |
| `-OutputDir` | String | Same as source | Where to save `.md` files |
| `-Recursive` | Switch | False | Process subdirectories |
| `-ExtractMedia` | Bool | True | Extract embedded images |
| `-Overwrite` | Switch | False | Overwrite existing `.md` files |

## Examples

### Import a meeting transcript
```powershell
.\.agent\scripts\convert-docx-to-md.ps1 -Source "Downloads\meeting-notes.docx" -OutputDir "Journal"
```

### Batch convert project documents
```powershell
.\.agent\scripts\convert-docx-to-md.ps1 -Source "01_Projects\Project Beacon\docs" -Recursive
```

### Force overwrite existing conversions
```powershell
.\.agent\scripts\convert-docx-to-md.ps1 -Source "Inbox\report.docx" -Overwrite
```

## Output Structure

```
OutputDir/
├── document.md          # Converted markdown
└── media/               # Extracted images (if any)
    ├── image1.png
    └── image2.jpg
```

## Troubleshooting

**"Pandoc not found"**
- Install Pandoc: `winget install pandoc` or download from [pandoc.org](https://pandoc.org)

**Tables look broken**
- Complex Word tables may need manual cleanup
- Consider simplifying the source table structure

**Images missing**
- Ensure `-ExtractMedia` is not set to `$false`
- Check the `media/` subfolder in output directory

## Related Skills

- [[universal-triager/SKILL|Universal Triager]] - Organize and file imported content
- [[compile-wiki/SKILL|Compile Wiki]] - Compile converted documents into a wiki
