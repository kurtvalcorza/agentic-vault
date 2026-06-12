# clip-and-localize

Clip web articles into the vault as offline-readable Markdown with localized images and structured YAML frontmatter. Supports single-URL and batch modes with deduplication and crash recovery.

## Purpose

Converts web content into vault-native Markdown files that are:
- **Offline-readable** — all images downloaded locally
- **LLM-parseable** — clean structure with proper headings and metadata
- **Searchable** — YAML frontmatter with title, source URL, author, tags
- **Compilation-ready** — output is compatible with `compile-wiki` ingestion

## Usage

### Single URL

Tell the agent to clip a URL:

```
Clip this article: https://example.com/federated-learning-guide
```

Output: `Inbox/2026-04-03_federated-learning-guide.md` with images in `03_Resources/Attachments/clips/2026-04-03/federated-learning-guide/`

### With Custom Output Path

```
Clip https://example.com/article and save it to 01_Projects/Project Atlas/references/
```

### Batch Mode

Create a text file with one URL per line:

```text
# research-urls.txt
https://example.com/article-1
https://example.com/article-2
# This is a comment — skipped
https://example.com/article-3
```

Then:

```
Batch clip the URLs in research-urls.txt
```

The agent processes each URL sequentially, tracks progress for crash recovery, and produces a summary report.

## Output Examples

### Frontmatter (Standard Article)

```yaml
---
title: "A Practical Guide to Federated Learning"
type: web-clip
source: "https://example.com/federated-learning-guide"
author: "Jane Smith"
clipped: 2026-04-03
tags:
  - web-clip
  - ai
  - federated-learning
---
```

### Frontmatter (Academic Paper)

```yaml
---
title: "Communication-Efficient Learning of Deep Networks"
type: web-clip
source: "https://arxiv.org/abs/1602.05629"
author: "McMahan et al."
clipped: 2026-04-03
doi: "10.48550/arXiv.1602.05629"
publication: "arXiv"
year: 2016
abstract: "Modern mobile devices have access to a wealth of data..."
tags:
  - web-clip
  - research-paper
  - federated-learning
---
```

### File Structure

```
Inbox/
└── 2026-04-03_federated-learning-guide.md

03_Resources/Attachments/clips/
└── 2026-04-03/
    └── federated-learning-guide/
        ├── federated-learning-guide-01.png
        ├── federated-learning-guide-02.jpg
        └── federated-learning-guide-03.svg
```

### Batch Progress File

Stored at `.agent/search-index/clip-progress/{batch-name}.json` for crash recovery:

```json
{
  "batch_name": "research-urls",
  "source_file": "research-urls.txt",
  "started": "2026-04-03T10:00:00Z",
  "urls": {
    "https://example.com/article-1": {"status": "clipped", "output": "Inbox/2026-04-03_article-1.md", "images": 3},
    "https://example.com/article-2": {"status": "failed", "error": "404 Not Found"},
    "https://example.com/article-3": {"status": "pending"}
  }
}
```

## Features

| Feature | Description |
|---------|-------------|
| **Image localization** | Downloads all images to `03_Resources/Attachments/clips/` and rewrites to `![[embed]]` syntax. Falls back to rendered fetch for JS-loaded images (Next.js, lazy-load, etc.) |
| **Deduplication** | Checks vault-search index (or grep fallback) before clipping |
| **Academic detection** | Extracts DOI, publication, year for research papers |
| **Auto-tagging** | Consults existing vault tags to prefer reuse over invention |
| **Batch mode** | Process a text file of URLs with per-URL progress tracking |
| **Crash recovery** | Batch progress saved after each URL; resume on re-invocation |

## Prerequisites

| Dependency | Path | Required |
|:-----------|:-----|:---------|
| `vault-search.py` | `.agent/scripts/vault-search.py` | Recommended (dedup + tag lookup; falls back to grep if missing) |
| `download-image.py` | `.agent/scripts/download-image.py` | Required (image batch download) |
| Python 3.9+ | System | Required |

## Error Handling

- **Fetch failures** (404, paywall, timeout): reported with suggestions for cached alternatives
- **Image download failures**: original URL kept in markdown with `<!-- download failed -->` comment; CDN 502/403 errors retried via site image proxy
- **No image URLs in text fetch**: if article references figures but text fetch found no images, automatic rendered-fetch fallback extracts JS-loaded image URLs
- **Duplicate URLs**: skipped with "already clipped" message and path to existing file
- **Batch interruption**: progress saved per-URL; re-invocation resumes from last pending URL

## Test Scenarios

### Test 1: Single URL with Images
- **Input:** A URL pointing to an article with embedded images
- **Expected:** `.md` file in `Inbox/` with `type: web-clip` frontmatter; images downloaded to `03_Resources/Attachments/clips/{date}/{slug}/`; image references rewritten to `![[filename]]`

### Test 2: Duplicate Detection
- **Input:** Clip the same URL twice
- **Expected:** Second run reports "already clipped" and skips without creating a duplicate file

### Test 3: Batch Mode (Mixed Results)
- **Input:** Text file with 3 URLs — 1 valid, 1 returning 404, 1 already clipped
- **Expected:** 1 clipped successfully, 1 reported as failed (404), 1 reported as skipped (duplicate); summary report with counts

### Test 4: Agent Skills Standard Compliance
- **Validate:** `SKILL.md` has proper YAML frontmatter with `name` and `description`
- **Validate:** Uses agent-agnostic tool names from `.agent/TOOL-TAXONOMY.md`
- **Validate:** Dual documentation pattern (SKILL.md + README.md)
- **Validate:** Directory structure follows `skill-name/{SKILL.md, README.md, templates/}`

## Related Skills

- `compile-wiki` — Compiles clipped articles into structured wiki (downstream consumer)
- `convert-pdf-to-md` — PDF extraction (for non-web sources)
- `write-note` — Atomic note creation (used by query-vault for filing answers)
