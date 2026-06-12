---
name: download-media
description: "Download audio or video from YouTube, Facebook, and other supported sites using yt-dlp. Use when downloading media, extracting audio from videos, saving recordings for transcription, or capturing online lectures and meetings."
---

# download-media

## Purpose

Download audio or video from online platforms (YouTube, Facebook, Streamable, Vimeo, and 1000+ yt-dlp-supported sites). The primary use case is extracting audio (MP3) for downstream transcription via `transcribe-audio`. Video download is supported as a secondary mode.

This skill is download-only. It does NOT transcribe, summarize, or process the downloaded media. Downstream processing is handled by dedicated skills:

- `transcribe-audio` — transcribe the downloaded audio to text
- `write-note` — distill the transcript into atomic notes
- `universal-triager` — file the download into the vault

## Trigger Patterns

- "Download this video"
- "Download audio from this YouTube link"
- "Save this recording"
- "Extract audio from this URL"
- "Download this Facebook video"
- "Get the audio from this lecture"
- "Download this for transcription"

## Required Capabilities

- `command-exec` — Execute yt-dlp via shell
- `file-read` — Verify the downloaded file exists; read the yt-dlp guide if needed
- `user-interact` — Prompt the user for missing parameters (URL, mode preference)

## Reference

The vault's yt-dlp & FFmpeg guide lives at `02_Areas/Tools/Media/yt-dlp and FFmpeg Guide.md`. Consult it for advanced flags, cookie handling, and troubleshooting.

## Parameters

| Parameter | Default | Description |
|:----------|:--------|:------------|
| `URL` | *(required)* | URL of the media to download |
| `Mode` | `audio` | `audio` (MP3 extraction) or `video` (full MP4) |
| `OutputDir` | `Inbox/` | Directory where the downloaded file is saved |
| `OutputTemplate` | `%(title)s.%(ext)s` | yt-dlp output template for the filename |
| `CookieSource` | *(none)* | Browser name for cookie auth (`chrome`, `firefox`, `edge`) or path to `cookies.txt` |
| `TimeRange` | *(none)* | Download only a segment, e.g. `*00:15:00-00:25:00` |
| `EmbedMetadata` | `true` | Embed thumbnail and metadata into the output file |

## Mode Details

### Audio Mode (default)

Extracts best-quality audio and converts to MP3. Embeds thumbnail and metadata by default. This is the recommended mode for transcription workflows.

```
yt-dlp -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata -o "<OutputDir>/%(title)s.%(ext)s" "<URL>"
```

### Video Mode

Downloads best video + audio and merges to MP4.

```
yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --embed-metadata -o "<OutputDir>/%(title)s.%(ext)s" "<URL>"
```

## Agent Decision Rules

1. **Default to audio mode.** Most downloads in this vault are for transcription. Unless the user explicitly asks for video, use audio mode.

2. **Cookie handling.** If yt-dlp returns a "Sign in to confirm you're not a bot" error or the download fails with an HTTP 403/429:
   - First retry with `--cookies-from-browser chrome`
   - If that fails, inform the user and suggest exporting `cookies.txt` manually

3. **Time range segments.** If the user specifies a time range, add `--download-sections "<TimeRange>"` to the command. This works in both audio and video modes.

4. **Playlist detection.** If the URL points to a playlist:
   - Confirm with the user before downloading all items
   - Add `%(playlist_index)s - ` to the output template prefix
   - Suggest adding `--sleep-interval 3` to avoid rate limiting

5. **Output directory.** Default to `Inbox/`. If the user specifies a project context or destination, use that instead.

6. **Filename conflicts.** Add `--no-overwrites` to skip files that already exist rather than overwriting.

7. **Performance.** Add `-N 4` for concurrent fragment downloads on large files.

## Invocation

Construct the yt-dlp command based on resolved parameters and execute via `command-exec`.

### Audio (typical)

```
yt-dlp -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata --no-overwrites -N 4 -o "Inbox/%(title)s.%(ext)s" "https://www.youtube.com/watch?v=XXXXX"
```

### Video

```
yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --embed-metadata --no-overwrites -N 4 -o "Inbox/%(title)s.%(ext)s" "https://www.youtube.com/watch?v=XXXXX"
```

### With cookies

```
yt-dlp --cookies-from-browser chrome -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata -o "Inbox/%(title)s.%(ext)s" "URL"
```

### With time range

```
yt-dlp --download-sections "*00:15:00-00:25:00" -f bestaudio -x --audio-format mp3 -o "Inbox/%(title)s.%(ext)s" "URL"
```

## Output Parsing

yt-dlp outputs progress and status messages to stdout/stderr. Key patterns to watch for:

| Pattern | Meaning |
|:--------|:--------|
| `[download] Destination: <path>` | Download target path |
| `[download] 100% of <size>` | Download complete |
| `[ExtractAudio] Destination: <path>` | Audio extraction output path |
| `[Merger] Merging formats into "<path>"` | Video merge output path |
| `ERROR:` or `[error]` | Download failed — relay message to user |
| `Sign in to confirm` | Bot detection — retry with cookies |
| `HTTP Error 403` / `HTTP Error 429` | Access denied or rate limited — retry with cookies or wait |

On success, report the output file path and size to the user. On failure, relay the error and suggest fixes per the troubleshooting section of the yt-dlp guide.

## Downstream Handoff

After download completes, the file is available for downstream skills. This skill does NOT invoke downstream skills automatically.

| Downstream Skill | Use Case |
|:-----------------|:---------|
| `transcribe-audio` | Transcribe the downloaded audio to text |
| `write-note` | Distill the transcript into atomic notes |
| `universal-triager` | File the download into the vault |

If the download was audio and the user's intent was transcription, suggest running `transcribe-audio` as the next step.

## Example Dialogues

### Audio download (most common)

**User:** Download the audio from https://www.youtube.com/watch?v=XXXXX

**Agent:** Downloading audio-only as MP3 to Inbox.

```
yt-dlp -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata --no-overwrites -N 4 -o "Inbox/%(title)s.%(ext)s" "https://www.youtube.com/watch?v=XXXXX"
```

Done — saved to `Inbox/Video Title.mp3` (24.5 MB). Want me to transcribe it with `transcribe-audio`?

### Video download

**User:** Download this Facebook video: https://www.facebook.com/USER/videos/ID — I need the full video.

**Agent:** Downloading full video as MP4 to Inbox.

```
yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --embed-metadata --no-overwrites -N 4 -o "Inbox/%(title)s.%(ext)s" "https://www.facebook.com/USER/videos/ID"
```

Done — saved to `Inbox/Video Title.mp4` (150 MB).

### Segment download

**User:** Download just the 15:00 to 25:00 segment from this lecture: URL

**Agent:** Downloading the 15:00–25:00 segment as audio.

```
yt-dlp --download-sections "*00:15:00-00:25:00" -f bestaudio -x --audio-format mp3 --embed-thumbnail --embed-metadata -o "Inbox/%(title)s.%(ext)s" "URL"
```
