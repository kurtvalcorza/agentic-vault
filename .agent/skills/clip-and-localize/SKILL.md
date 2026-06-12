---
name: clip-and-localize
description: Clip web articles into the vault as offline-readable Markdown with localized images and structured frontmatter. Use when clipping a web article, saving a URL to the vault, batch-clipping multiple URLs, or ingesting web content for later compilation.
---

# clip-and-localize

Fetches web content, restructures it into well-formatted Markdown, downloads all images to local storage, rewrites image references to Obsidian `![[embed]]` syntax, and writes the result with structured YAML frontmatter.

## Trigger Phrases

- "Clip this URL"
- "Save this article to the vault"
- "Clip and localize this page"
- "Batch clip these URLs"
- "Ingest this web article"
- "Download this page with images"

## Modes

| Mode | Input | Description |
|------|-------|-------------|
| **Single URL** | One URL (provided in conversation) | Clip one article |
| **Batch** | Text file path (one URL per line) | Clip multiple articles sequentially with crash recovery |

---

## Single-URL Mode

### Step 1 — Deduplication Check

Before fetching, check if this URL has already been clipped:

1. **Primary check** — vault-search index (if available):
   ```
   **Tool:** command-exec
   python .agent/scripts/vault-search.py --source "{URL}" --json
   ```
   If results are returned, report "Already clipped: {path}" and **skip**.

2. **Fallback check** — grep frontmatter (if index not built):
   ```
   **Tool:** content-search
   Search for `source: "{URL}"` across `Inbox/` and `03_Resources/` directories.
   ```
   If a match is found, report "Already clipped: {path}" and **skip**.

### Step 2 — Fetch

```
**Tool:** web-fetch
Fetch the URL. WebFetch returns pre-cleaned text/markdown (nav, ads, boilerplate stripped).
```

- If fetch fails (404, paywall, timeout): report the error and suggest alternatives:
  - "Try clipping from a cached version (Google Cache, Wayback Machine)"
  - "Try fetching with `mode: rendered` for JavaScript-heavy pages"
- If the page is mostly empty or navigation-only, retry with `mode: rendered`.

### Step 3 — Restructure & Extract Metadata

From the fetched content:

1. **Extract metadata:**
   - `title` — from page heading or first `# ` line
   - `author` — look for byline patterns ("By {name}", "Author: {name}", meta attribution)
   - `date` — publication date if present (ISO format)
   - `description` — meta description or first paragraph summary

2. **Academic paper detection** — if the content appears to be a research paper or preprint:
   - Extract `doi` (look for `doi.org/` URLs or "DOI:" labels)
   - Extract `publication` (journal/conference name)
   - Extract `year` from publication date
   - Extract `abstract` if present

3. **Restructure the markdown:**
   - Normalize heading hierarchy (ensure single `#` title, sequential levels)
   - Clean up list formatting, code blocks, and tables
   - Remove redundant whitespace and empty sections
   - Preserve blockquotes, emphasis, and inline code

### Step 4 — Localize Images

1. **Extract image URLs** from the markdown:
   - Standard markdown: `![alt](url)`
   - HTML img tags: `<img src="url">`
   - Raw URLs ending in image extensions (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`)

   **Rendered-fetch fallback for images:** If the article text references figures/charts (e.g. "Figure 1", "Fig. 2") but no image URLs were found in the initial fetch, many modern sites load images via JavaScript (Next.js image optimization, lazy loading, etc.). In this case:
   - Re-fetch the URL with `mode: rendered` to get the fully rendered DOM
   - Extract image URLs from the rendered content (look for `![Image](url)`, `<img src="url">`, and Next.js `/_next/image?url=` patterns)
   - Filter out decorative/navigation images (icons, logos, avatars) — keep only content images that correspond to referenced figures
   - Use the rendered content only for image URL extraction; continue using the cleaner text-mode content for the article body
   - If a direct CDN URL returns an error (e.g. 502), retry via the site's image proxy URL (e.g. `/_next/image?url={encoded_cdn_url}&w=3840&q=75`)

2. **Derive paths:**
   - Date: today's date as `YYYY-MM-DD`
   - Article slug: slugified title (lowercase, hyphens, max 60 chars)
   - Image directory: `03_Resources/Attachments/clips/{YYYY-MM-DD}/{article-slug}/`
   - Image filenames: `{article-slug}-{01..NN}.{ext}`

3. **Build download manifest** — JSON array:
   ```json
   [
     {"url": "https://example.com/img1.png", "out_path": "03_Resources/Attachments/clips/2026-04-03/article-slug/article-slug-01.png"},
     {"url": "https://example.com/img2.jpg", "out_path": "03_Resources/Attachments/clips/2026-04-03/article-slug/article-slug-02.jpg"}
   ]
   ```

4. **Download images:**
   ```
   **Tool:** command-exec
   Write manifest to a temp file, then run:
   python .agent/scripts/download-image.py --manifest {manifest_path}
   ```

5. **Rewrite image references** in the markdown:
   - Successful downloads: replace with `![[{filename}]]` (Obsidian embed syntax)
   - Failed downloads: keep original URL, add inline comment `<!-- download failed: {error} -->`

6. **Clean up** the temporary manifest file.

### Step 5 — Auto-Tag

Generate 2-4 content tags by:

1. **Consult existing tags** (prefer reuse over invention):
   ```
   **Tool:** command-exec
   python .agent/scripts/vault-search.py --list-tags --json
   ```
   If the index is not available, skip this step and generate reasonable tags.

2. **Match content** against existing tags. If no good match, create descriptive kebab-case tags.

3. Always include `web-clip` as the first tag.

### Step 6 — Write Output

1. **Build frontmatter** using the template at `templates/web-clip-template.md`:
   ```yaml
   ---
   title: "{extracted title}"
   type: web-clip
   source: "{original URL}"
   author: "{extracted author or empty string}"
   clipped: {YYYY-MM-DD}
   tags:
     - web-clip
     - {auto-tag-1}
     - {auto-tag-2}
   ---
   ```

   For academic papers, add extra fields:
   ```yaml
   doi: "{extracted DOI}"
   publication: "{journal/conference}"
   year: {publication year}
   abstract: "{extracted abstract}"
   ```

2. **Determine output path:**
   - Default: `Inbox/{YYYY-MM-DD}_{slugified-title}.md`
   - If user specified a path: use that path instead
   - Filename pattern: `{YYYY-MM-DD}_{slugified-title}.md`

3. **Write the file:**
   ```
   **Tool:** file-write
   Write frontmatter + restructured markdown body to the output path.
   ```

4. **Report result:**
   - Output file path
   - Number of images localized
   - Any warnings (failed image downloads, missing metadata)

---

## Batch Mode

### Activation

User provides a text file path containing URLs (one per line). Lines starting with `#` are comments and skipped. Empty lines are skipped.

### Batch Progress Tracking

Track progress for crash recovery at `.agent/search-index/clip-progress/{batch-name}.json`:

```json
{
  "batch_name": "research-clips-2026-04",
  "source_file": "path/to/urls.txt",
  "started": "2026-04-03T10:00:00Z",
  "urls": {
    "https://example.com/article-1": {"status": "clipped", "output": "Inbox/2026-04-03_article-1.md", "images": 3},
    "https://example.com/article-2": {"status": "failed", "error": "404 Not Found"},
    "https://example.com/article-3": {"status": "pending"}
  }
}
```

- `batch-name`: derived from the source filename (slugified, without extension)
- On re-invocation: read progress file, skip URLs with status `clipped`, retry `failed` only if user requests

### Batch Processing Steps

1. **Read URL list:**
   ```
   **Tool:** file-read
   Read the text file. Parse one URL per line, skip comments (#) and blanks.
   ```

2. **Load or create progress file:**
   ```
   **Tool:** file-read
   Check `.agent/search-index/clip-progress/{batch-name}.json`
   If exists: load and resume from pending URLs.
   If not: create new progress tracker with all URLs as "pending".
   ```

3. **Process each URL sequentially:**
   For each pending URL, execute the full Single-URL Mode pipeline (Steps 1–6).
   After each URL completes (success or failure), update the progress file:
   ```
   **Tool:** file-write
   Update `.agent/search-index/clip-progress/{batch-name}.json` with current status.
   ```

4. **Generate summary report** after all URLs are processed:
   ```
   ## Batch Clip Report: {batch-name}

   **Processed:** {N} URLs
   **Clipped:** {success_count} articles
   **Failed:** {fail_count} ({reasons})
   **Skipped (duplicate):** {dup_count}
   **Images downloaded:** {total_images}

   ### Successful Clips
   - {path1} ← {url1}
   - {path2} ← {url2}

   ### Failed
   - {url3}: {error reason}

   ### Skipped (already clipped)
   - {url4}: existing at {existing_path}
   ```

---

## Output Conventions

### File Naming
- Pattern: `{YYYY-MM-DD}_{slugified-title}.md`
- Slug rules: lowercase, replace spaces/special chars with hyphens, collapse multiple hyphens, max 60 characters, strip trailing hyphens
- Example: `2026-04-03_federated-learning-practical-guide.md`

### Image Storage
- Directory: `03_Resources/Attachments/clips/{YYYY-MM-DD}/{article-slug}/`
- Filenames: `{article-slug}-{01..NN}.{original-extension}`
- Example: `03_Resources/Attachments/clips/2026-04-03/federated-learning-practical-guide/federated-learning-practical-guide-01.png`

### Frontmatter Template
Located at: `.agent/skills/clip-and-localize/templates/web-clip-template.md`

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `web-fetch` | Fetch URL content (pre-cleaned markdown) |
| `command-exec` | Run `download-image.py` for image batch download; run `vault-search.py` for dedup and tag lookup |
| `file-read` | Read batch URL files, progress trackers |
| `file-write` | Write clipped markdown, progress trackers, image manifests |
| `content-search` | Fallback dedup check (grep for `source:` in frontmatter) |

### External Scripts

| Script | Path | Purpose |
|:-------|:-----|:--------|
| `download-image.py` | `.agent/scripts/download-image.py` | Batch image download with manifest support |
| `vault-search.py` | `.agent/scripts/vault-search.py` | Dedup check (`--source`), tag lookup (`--list-tags`) |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| URL returns 404/5xx | Log error, report to user, continue batch |
| URL is paywalled | Report failure, suggest cached alternatives |
| Image download fails | Keep original URL in markdown, add `<!-- download failed -->` comment. If CDN URL returns 502/403, retry via the site's image proxy URL before giving up |
| No image URLs in text fetch | If article references figures but no image URLs found, re-fetch with `mode: rendered` to extract JS-loaded images |
| Duplicate URL detected | Skip, report "already clipped" with existing path |
| Batch interrupted | Progress saved per-URL; resume on re-invocation |
| vault-search index missing | Fall back to `content-search` grep for dedup; skip tag lookup |

---

## Examples

### Single URL

**Agent:** I'll clip that article for you.

1. Checking for duplicates... not found.
2. Fetching content from `https://example.com/federated-learning-guide`...
3. Extracted: title="A Practical Guide to Federated Learning", author="Jane Smith"
4. Found 4 images — downloading to `03_Resources/Attachments/clips/2026-04-03/federated-learning-guide/`
5. All 4 images downloaded successfully.
6. Written to `Inbox/2026-04-03_a-practical-guide-to-federated-learning.md`

### Batch Mode

**Agent:** Processing batch file `research-urls.txt` (5 URLs)...

- [1/5] `https://example.com/article-1` → Clipped (3 images)
- [2/5] `https://example.com/article-2` → Clipped (0 images)
- [3/5] `https://example.com/article-3` → Failed: 404 Not Found
- [4/5] `https://example.com/article-4` → Skipped: already clipped at `Inbox/2026-04-01_article-4.md`
- [5/5] `https://example.com/article-5` → Clipped (1 image)

**Summary:** 3 clipped, 1 failed, 1 skipped, 4 images downloaded.
