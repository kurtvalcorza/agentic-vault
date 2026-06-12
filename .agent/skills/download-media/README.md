# Download Media

Download audio or video from YouTube, Facebook, and 1000+ sites using yt-dlp. Optimized for the audio-first transcription workflow — extracts MP3 by default, with full video download as a secondary mode.

## What It Does

- Downloads audio (MP3) or video (MP4) from online platforms
- Embeds thumbnail and metadata into downloaded files
- Supports time-range segment downloads
- Handles cookie-based authentication for bot detection and private content
- Supports playlists with confirmation and rate-limit protection

## What It Doesn't Do

- Does NOT transcribe, summarize, or process the downloaded media
- Does NOT create Obsidian notes or apply templates
- Does NOT invoke downstream skills automatically

Downstream processing is handled by dedicated skills:

| Skill | Use Case |
|:------|:---------|
| `transcribe-audio` | Transcribe downloaded audio to text |
| `write-note` | Distill the transcript into atomic notes |
| `universal-triager` | File the download into the vault |

## Prerequisites

| Requirement | Details |
|:------------|:--------|
| yt-dlp | Installed via pip or winget (`yt-dlp --version` to verify) |
| FFmpeg | Installed and on PATH (required for audio extraction and video merging) |

## Parameter Reference

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `URL` | string | Yes | — | URL of the media to download |
| `Mode` | enum | No | `audio` | `audio` (MP3) or `video` (MP4) |
| `OutputDir` | string | No | `Inbox/` | Destination directory |
| `OutputTemplate` | string | No | `%(title)s.%(ext)s` | yt-dlp filename template |
| `CookieSource` | string | No | *(none)* | Browser name or cookies.txt path |
| `TimeRange` | string | No | *(none)* | Segment range, e.g. `*00:15:00-00:25:00` |
| `EmbedMetadata` | bool | No | `true` | Embed thumbnail and metadata |

## Usage Examples

### Audio download (default, most common)

```
yt-dlp -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata --no-overwrites -N 4 -o "Inbox/%(title)s.%(ext)s" "URL"
```

### Video download

```
yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --embed-metadata --no-overwrites -N 4 -o "Inbox/%(title)s.%(ext)s" "URL"
```

### With browser cookies (for bot detection)

```
yt-dlp --cookies-from-browser chrome -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata -o "Inbox/%(title)s.%(ext)s" "URL"
```

### Time-range segment

```
yt-dlp --download-sections "*00:15:00-00:25:00" -f bestaudio -x --audio-format mp3 -o "Inbox/%(title)s.%(ext)s" "URL"
```

### Playlist

```
yt-dlp -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata --sleep-interval 3 -o "Inbox/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"
```

## Troubleshooting

| Problem | Solution |
|:--------|:---------|
| "Sign in to confirm you're not a bot" | Add `--cookies-from-browser chrome` (or export cookies.txt) |
| HTTP 403 / 429 | Rate limited — add `--sleep-interval 3` or use cookies |
| Merge fails / no audio | Verify FFmpeg is installed and on PATH |
| Filename too long (Windows) | Add `--restrict-filenames` |
| yt-dlp outdated | Run `yt-dlp -U` or `pip install -U yt-dlp` |

## Reference

Full yt-dlp & FFmpeg documentation: `02_Areas/Tools/Media/yt-dlp and FFmpeg Guide.md`

## Skill Location

`.agent/skills/download-media/`
