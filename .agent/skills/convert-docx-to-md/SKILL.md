---
name: convert-docx-to-md
description: Convert Microsoft Word documents (.docx) to Markdown (.md) using Pandoc for seamless integration into the Obsidian vault. Use when importing Word documents into the vault, converting .docx files, or preparing documents for Obsidian.
---

# SKILL: Convert DOCX to Markdown
*(Word Documents → Obsidian-Ready Markdown)*

**Type:** Utility Skill (File Conversion)
**Domain:** Document Processing
**Audience:** Anyone needing to import Word documents into the vault

---

## Purpose

Convert `.docx` files to clean Markdown using Pandoc, making Word documents immediately usable in Obsidian. The skill:

- Converts single files or batch processes entire directories
- Preserves document structure (headings, lists, tables, links)
- Extracts embedded images to a media folder
- Outputs vault-ready `.md` files

---

## When to Invoke

**Trigger patterns:**
- "Convert this docx to markdown"
- "Import Word document to vault"
- "Convert docx files in this folder"
- User provides a `.docx` file path

**Do NOT invoke when:**
- File is already in Markdown format
- User wants PDF conversion (different tool needed)
- Document requires complex formatting preservation (tables with merged cells, etc.)

---

## Dependencies

### Required Tools
- **Pandoc** - Must be installed and available in PATH
- PowerShell script at `.agent/scripts/convert-docx-to-md.ps1`

### Required Inputs
- **Source**: Path to `.docx` file or directory containing `.docx` files

### Optional Inputs
- **Output Directory**: Where to save converted files (defaults to same location)
- **Extract Media**: Whether to extract images (default: true)
- **Overwrite**: Whether to overwrite existing `.md` files (default: false)

---

## Script Location

`.agent/scripts/convert-docx-to-md.ps1`

---

## Usage Examples

### Single File Conversion
```powershell
# Convert a single file
.\.agent\scripts\convert-docx-to-md.ps1 -Source "Inbox\report.docx"

# Convert with custom output location
.\.agent\scripts\convert-docx-to-md.ps1 -Source "Inbox\report.docx" -OutputDir "01_Projects\Project Atlas"
```

### Batch Conversion
```powershell
# Convert all docx files in a directory
.\.agent\scripts\convert-docx-to-md.ps1 -Source "Inbox" -Recursive

# Convert without extracting media
.\.agent\scripts\convert-docx-to-md.ps1 -Source "Inbox" -ExtractMedia:$false
```

---

## Conversion Behavior

### What Gets Converted
- Headings → `#`, `##`, `###`, etc.
- Bold/Italic → `**bold**`, `*italic*`
- Bullet lists → `-` items
- Numbered lists → `1.` items
- Tables → Markdown tables
- Hyperlinks → `[text](url)`
- Images → Extracted to `media/` subfolder with `![[image.png]]` references

### What May Need Manual Cleanup
- Complex nested tables
- Text boxes and shapes
- Track changes / comments (stripped)
- Custom styles (converted to plain text)

---

## Output

- `.md` file(s) in the specified output directory
- `media/` subfolder containing extracted images (if any)
- Console summary of converted files

---

## Error Handling

The script will:
- Skip files that already have a `.md` counterpart (unless `-Overwrite` is set)
- Report Pandoc errors for individual files without stopping batch processing
- Warn if Pandoc is not installed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-04 | Initial implementation |
