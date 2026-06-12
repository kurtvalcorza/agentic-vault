---
name: transcribe-audio
description: "Transcribe audio and video files to text using OpenAI Whisper. Use when transcribing recordings, meetings, lectures, or any audio/video file to text."
---

# transcribe-audio

## Purpose

Transcribe audio and video files to text using the local OpenAI Whisper installation. This skill wraps the `transcribe-audio.ps1` PowerShell script, which activates the Whisper virtual environment, runs the transcription, and produces raw Whisper output files (`.txt`, `.srt`, `.vtt`, `.json`, `.tsv`, or all formats).

This skill is transcription-only. It does NOT summarize, restructure, or create notes from the transcript. Downstream processing is handled by dedicated skills:

- `write-note` — distill key points, decisions, and action items into atomic notes
- `universal-triager` — file the transcript into the vault (PARA routing + enrichment)

## Trigger Patterns

- "Transcribe this recording"
- "Transcribe this audio" / "Transcribe this video"
- "Convert audio to text"
- "Run whisper on this file"
- "Transcribe this meeting"
- "Get a transcript of this file"

## Required Capabilities

- `command-exec` — Execute the PowerShell transcription script
- `file-read` — Read and verify the source audio/video file exists
- `user-interact` — Prompt the user for missing parameters (file path, model preference, language)

## Parameters

| Parameter | Default | Description |
|:----------|:--------|:------------|
| `FilePath` | *(required)* | Path to the source audio or video file |
| `Model` | `turbo` | Whisper model to use for transcription |
| `Language` | *(auto-detect)* | Language of the audio; omit to let Whisper detect automatically |
| `InitialPrompt` | *(none)* | Domain-specific terms and acronyms to improve transcription accuracy |
| `OutputFormat` | `txt` | Format of the transcript output file |
| `OutputDir` | Source file directory | Directory where the transcript file is written |

### Valid Models

| Model | Notes |
|:------|:------|
| `turbo` | Default. Fastest inference, good general quality |
| `large-v3` | Best quality. Recommended for code-switched speech and mixed-language audio |
| `medium` | Balanced speed and quality |
| `small` | Lightest model, fastest but lowest accuracy |

### Valid Output Formats

| Format | Notes |
|:-------|:------|
| `txt` | Default. Plain text transcript |
| `srt` | SubRip subtitle format |
| `vtt` | WebVTT subtitle format |
| `json` | Full Whisper JSON output with timestamps and metadata |
| `tsv` | Tab-separated values |
| `all` | Produces all formats at once |

## Agent Recommendation Rules

Apply these recommendations when resolving parameters for the user:

1. **Model selection**
   - If the user requests high-quality transcription or the audio contains code-switched or non-English speech, recommend `large-v3`.
   - Otherwise, use the default `turbo` model.

2. **Language**
   - If the user mentions non-English or code-switched content, suggest adding `-Language <name>`.
   - If the language is unknown or mixed, omit the parameter and let Whisper auto-detect.

3. **Initial prompt**
   - If the transcription context involves Example Org, government, or institutional work, suggest the default institutional prompt:
     ```
     "Example Org, Project Atlas, Project Cedar, the funding agency, Project Dawn, Project Beacon, COARE"
     ```
   - If the user provides their own domain terms, use those instead.

4. **Unrecognized file extensions**
   - Accepted extensions: `.mp3`, `.mp4`, `.wav`, `.m4a`, `.webm`, `.ogg`, `.flac`
   - If the source file has an extension not in the list above, warn the user that the format is unrecognized but offer to attempt transcription anyway — FFmpeg may still support it. Use `user-interact` to confirm before proceeding.

## Script Invocation

Invoke the transcription script via `command-exec`:

```
pwsh .agent/scripts/transcribe-audio.ps1 -FilePath "<path>" [-Model <model>] [-Language <lang>] [-InitialPrompt "<prompt>"] [-OutputFormat <fmt>] [-OutputDir "<dir>"]
```

All parameters except `-FilePath` are optional and fall back to their defaults.

## Output Parsing

The transcription script outputs structured messages prefixed with `[INFO]` or `[ERROR]`. Parse these to determine the result.

### Info Messages

| Message | Meaning |
|:--------|:--------|
| `[INFO] Source file found: <path>` | Input file validated successfully |
| `[INFO] Whisper environment activated` | Whisper venv activated and ready |
| `[INFO] Transcription started: model=<model>, format=<format>` | Whisper CLI invoked with the shown parameters |
| `[INFO] Transcription complete: <output_path>` | Transcript written to the indicated path |

### Error Messages

| Message | Exit Code | Meaning |
|:--------|:----------|:--------|
| `[ERROR] Source file not found: <path>` | 1 | The provided file path does not exist |
| `[ERROR] Whisper environment not found: <path>` | 2 | The Whisper venv is missing at the expected location |
| `[ERROR] Whisper failed: <stderr>` | 4 | Whisper CLI returned a non-zero exit code |
| `[ERROR] Failed to create output directory: <path>` | 5 | Could not create the specified output directory |

### Exit Codes

| Code | Meaning |
|:-----|:--------|
| 0 | Success — transcript file produced |
| 1 | Source file not found |
| 2 | Whisper virtual environment not found |
| 3 | Invalid parameter (e.g., bad model or format value) |
| 4 | Whisper execution failed |
| 5 | Output directory creation failed |

When the script exits with code 0, extract the output path from the `[INFO] Transcription complete: <output_path>` message and report it to the user. For any non-zero exit code, relay the corresponding `[ERROR]` message.

## Source File Cleanup

Do NOT delete the source file by default after transcription.

If the user requests cleanup after transcription:

1. Confirm the file path and name with the user before deletion. Use `user-interact` to ask:
   > "Delete the source file `<filename>` at `<path>`? This cannot be undone."
2. If the user confirms: delete the file and report the result.
3. If deletion fails: report the error and leave the file intact. Do not retry automatically.

## Downstream Handoff

After transcription completes, the transcript file is available for downstream skills. This skill does NOT invoke downstream skills automatically — the user or agent decides the next step.

| Downstream Skill | Use Case |
|:-----------------|:---------|
| `write-note` | Distill key points, decisions, and action items into atomic notes |
| `universal-triager` | File the transcript into the vault (PARA routing + enrichment) |

## Example Dialogue

**User:** Transcribe the recording at `01_Projects/Project Atlas/meetings/2026-06-15-standup.mp3`. It's a code-switched speech meeting.

**Agent:** The file is a code-switched speech meeting recording, so I'll use the `large-v3` model for best mixed-language accuracy and add the Example Org institutional prompt. Running transcription now.

```
pwsh .agent/scripts/transcribe-audio.ps1 -FilePath "01_Projects/Project Atlas/meetings/2026-06-15-standup.mp3" -Model large-v3 -Language <name> -InitialPrompt "Example Org, Project Atlas, Project Cedar, the funding agency, Project Dawn, Project Beacon, COARE" -OutputFormat txt
```

Transcription complete. The transcript is at `01_Projects/Project Atlas/meetings/2026-06-15-standup.txt`. Would you like me to distill the key decisions and action items into an atomic note with `write-note`?
