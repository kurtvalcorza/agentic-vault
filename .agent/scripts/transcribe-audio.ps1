<#
.SYNOPSIS
    Transcribe an audio/video file to text with a local OpenAI Whisper install.

.DESCRIPTION
    Wrapper used by the transcribe-audio skill. Activates the Whisper virtual
    environment (expected at %USERPROFILE%\whisper\), runs the Whisper CLI on
    the source file, and writes the transcript to the requested format.

    Output contract (parsed by agents — see the skill's Output Parsing tables):
      [INFO]/[ERROR]-prefixed status lines on stdout.
      Exit codes: 0 success, 1 source file not found, 2 Whisper venv not
      found, 3 invalid parameter, 4 Whisper execution failed, 5 output
      directory creation failed.

.EXAMPLE
    pwsh .agent/scripts/transcribe-audio.ps1 -FilePath "meeting.mp3" -Model large-v3
#>

param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [string]$Model = 'turbo',
    [string]$Language,
    [string]$InitialPrompt,
    [string]$OutputFormat = 'txt',
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'

# --- Parameter validation (exit 3) — done manually so the documented
# ---  [ERROR]/exit-code contract holds instead of a PowerShell binding error
$ValidModels  = @('turbo', 'large-v3', 'medium', 'small')
$ValidFormats = @('txt', 'srt', 'vtt', 'json', 'tsv', 'all')
if ($ValidModels -notcontains $Model) {
    Write-Host "[ERROR] Invalid parameter: -Model '$Model' (valid: $($ValidModels -join ', '))"
    exit 3
}
if ($ValidFormats -notcontains $OutputFormat) {
    Write-Host "[ERROR] Invalid parameter: -OutputFormat '$OutputFormat' (valid: $($ValidFormats -join ', '))"
    exit 3
}

# --- Source file (exit 1) ---
if (-not (Test-Path $FilePath)) {
    Write-Host "[ERROR] Source file not found: $FilePath"
    exit 1
}
$FilePath = (Resolve-Path $FilePath).Path
Write-Host "[INFO] Source file found: $FilePath"

# --- Whisper venv (exit 2) — Windows layout first, then POSIX layout ---
$HomeDir  = if ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }
$VenvRoot = Join-Path $HomeDir 'whisper'
$Activate = Join-Path $VenvRoot 'Scripts\Activate.ps1'
if (-not (Test-Path $Activate)) { $Activate = Join-Path $VenvRoot 'bin/Activate.ps1' }
if (-not (Test-Path $Activate)) {
    Write-Host "[ERROR] Whisper environment not found: $VenvRoot"
    exit 2
}
. $Activate
Write-Host "[INFO] Whisper environment activated"

# --- Output directory (exit 5) ---
if (-not $OutputDir) { $OutputDir = Split-Path -Parent $FilePath }
if (-not (Test-Path $OutputDir)) {
    try { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }
    catch {
        Write-Host "[ERROR] Failed to create output directory: $OutputDir"
        exit 5
    }
}
$OutputDir = (Resolve-Path $OutputDir).Path

# --- Run Whisper (exit 4) ---
$WhisperArgs = @($FilePath, '--model', $Model, '--output_format', $OutputFormat, '--output_dir', $OutputDir)
if ($Language)      { $WhisperArgs += @('--language', $Language) }
if ($InitialPrompt) { $WhisperArgs += @('--initial_prompt', $InitialPrompt) }

Write-Host "[INFO] Transcription started: model=$Model, format=$OutputFormat"
$WhisperOutput = & whisper @WhisperArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    $Tail = ($WhisperOutput | ForEach-Object { $_.ToString() } | Select-Object -Last 5) -join ' '
    Write-Host "[ERROR] Whisper failed: $Tail"
    exit 4
}

# --- Report the transcript path ---
$BaseName = [IO.Path]::GetFileNameWithoutExtension($FilePath)
$OutPath  = if ($OutputFormat -eq 'all') { $OutputDir } else { Join-Path $OutputDir "$BaseName.$OutputFormat" }
Write-Host "[INFO] Transcription complete: $OutPath"
exit 0
