# Transcribe Audio

Transcribe audio and video files to text using a local OpenAI Whisper installation. Wraps the `transcribe-audio.ps1` PowerShell script, which activates the Whisper virtual environment, runs the transcription, and produces raw Whisper output.

## What It Does

- Transcribes audio and video files (MP3, MP4, WAV, M4A, WEBM, OGG, FLAC) to text
- Supports multiple Whisper models for speed/quality tradeoffs
- Accepts domain-specific initial prompts to improve accuracy on acronyms and proper nouns
- Outputs in multiple formats: plain text, SRT, VTT, JSON, TSV, or all at once
- Runs entirely locally — no cloud API calls

## What It Doesn't Do

- Does NOT summarize, restructure, or reformat the transcript
- Does NOT create Obsidian notes, add frontmatter, or apply templates
- Does NOT invoke downstream skills automatically

Downstream processing is handled by dedicated skills:

| Skill | Use Case |
|:------|:---------|
| `write-note` | Distill key points, decisions, and action items into atomic notes |
| `universal-triager` | File the transcript into the vault (PARA routing + enrichment) |

## Prerequisites

| Requirement | Details |
|:------------|:--------|
| Whisper venv | Installed at `%USERPROFILE%\whisper\` |
| FFmpeg | Installed and available on PATH (required by Whisper for audio decoding) |
| Python | Python 3.x (used by the Whisper venv) |
| PowerShell | `pwsh` for running the automation script |

## Parameter Reference

| Parameter | Type | Required | Default | Validation |
|:----------|:-----|:---------|:--------|:-----------|
| `FilePath` | string | Yes | — | File must exist on disk |
| `Model` | enum | No | `turbo` | `turbo`, `large-v3`, `medium`, `small` |
| `Language` | string | No | *(auto-detect)* | Passed to Whisper `--language` flag |
| `InitialPrompt` | string | No | *(none)* | Passed to Whisper `--initial_prompt` flag |
| `OutputFormat` | enum | No | `txt` | `txt`, `srt`, `vtt`, `json`, `tsv`, `all` |
| `OutputDir` | string | No | Source file directory | Created automatically if missing |

### Model Guide

| Model | Speed | Quality | Notes |
|:------|:------|:--------|:------|
| `turbo` | Fastest | Good | Default. Best for general English audio |
| `large-v3` | Slowest | Best | Recommended for code-switched speech and mixed-language audio |
| `medium` | Moderate | Good | Balanced speed and quality |
| `small` | Fast | Lower | Lightest model, lowest accuracy |

## Usage Examples

### Basic — Transcribe with defaults

```powershell
pwsh .agent/scripts/transcribe-audio.ps1 -FilePath "path/to/audio.mp3"
```

Uses the `turbo` model, auto-detects language, outputs `.txt` to the same directory as the source file.

### With model selection

```powershell
pwsh .agent/scripts/transcribe-audio.ps1 -FilePath "meeting.mp3" -Model large-v3
```

### Full options

```powershell
pwsh .agent/scripts/transcribe-audio.ps1 -FilePath "meeting.mp3" -Model large-v3 -Language <name> -InitialPrompt "Example Org, Project Atlas, Project Cedar, the funding agency" -OutputFormat srt -OutputDir "output/"
```

### Agent-invoked

When a user says "Transcribe this recording", the agent:

1. Reads `SKILL.md` to identify required parameters
2. Resolves parameters (file path, model, language, etc.) — prompting the user if needed
3. Invokes the script via `command-exec` with the resolved parameters
4. Parses the structured `[INFO]`/`[ERROR]` output and reports the result

## Downstream Integration

This skill produces raw transcripts only. Downstream skills consume the output:

- **`write-note`** — Distill key points, decisions, and action items into atomic notes
- **`universal-triager`** — File the transcript into the vault (PARA routing + Zettelkasten enrichment)

The transcript file path is reported on completion and can be passed directly to downstream skills.

## Troubleshooting

| Exit Code | Error | Cause | Fix |
|:----------|:------|:------|:----|
| 1 | `Source file not found` | The provided file path does not exist | Check the file path for typos; verify the file is accessible |
| 2 | `Whisper environment not found` | Whisper venv missing at expected path | Verify the venv exists at `%USERPROFILE%\whisper\` |
| 3 | Invalid parameter | Bad model name or output format value | Check that `-Model` and `-OutputFormat` use valid values (see Parameter Reference) |
| 4 | `Whisper failed` | Whisper CLI returned a non-zero exit code | Check the stderr output for details; verify FFmpeg is installed and on PATH |
| 5 | `Output dir creation failed` | Could not create the specified output directory | Check write permissions on the target path |

## Script Location

The automation script lives at `.agent/scripts/transcribe-audio.ps1` and can be run independently without an AI agent.
