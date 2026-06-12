<#
.SYNOPSIS
    Auto-write a session log entry for the Obsidian vault.

.DESCRIPTION
    Command-hook equivalent of Kiro's "Auto-Log Session Activity" agentStop
    hook. Because Claude and Codex lifecycle hooks run commands, this log is
    deterministic: it records the timestamp and the files changed since the
    last commit (i.e. this session's working-tree changes), with a task line
    derived from which top-level directories were touched. It does NOT produce
    the LLM-inferred prose summary that Kiro's askAgent hook does.

    Designed to run before vault-git-commit.ps1, so the log file it writes is
    itself picked up by that commit.

    Steps:
      1. Resolve vault root from this script's own location (no hardcoded paths).
      2. Skip cleanly if git is missing or this isn't a repo.
      3. Read working-tree changes (git status --porcelain). Skip if none
         (trivial interaction => no log, matching the Kiro hook's behaviour).
      4. Derive a task hint + filename slug from the dominant changed directory.
      5. Write System/session-logs/YYYY-MM-DD/HH-MM-SS_<slug>.md with provenance
         frontmatter per AGENTS.md Session Continuity.

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File .agent\scripts\vault-session-log.ps1 -Agent codex
#>

param([string]$Agent = 'claude')

$ErrorActionPreference = 'Stop'

$Agent = ($Agent.ToLowerInvariant() -replace '[^a-z0-9_-]', '-').Trim('-')
if (-not $Agent) { $Agent = 'unknown' }

$VaultRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$GitDir    = Join-Path $VaultRoot '.git'
$Now       = Get-Date
$Stamp     = $Now.ToString('yyyy-MM-dd HH:mm:ss')
$DateDir   = $Now.ToString('yyyy-MM-dd')
$TimeName  = $Now.ToString('HH-mm-ss')

# --- Preconditions ---
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { return }
if (-not (Test-Path $GitDir)) { return }

# --- Collect this session's working-tree changes ---
$porcelain = @(git -C $VaultRoot status --porcelain 2>$null)
if ($porcelain.Count -eq 0) { return }   # nothing changed => trivial, skip

# Parse "XY path" rows into status + clean relative path (handles quotes/renames).
$changes = foreach ($row in $porcelain) {
    if ($row.Length -lt 4) { continue }
    $path = $row.Substring(3).Trim()
    if ($path -like '* -> *') { $path = ($path -split ' -> ')[-1] }  # rename: keep dest
    $path = $path.Trim('"')
    [pscustomobject]@{ Status = $row.Substring(0, 2).Trim(); Path = $path }
}

# Never let the log itself be the only "change" we report on a rerun.
$changes = @($changes | Where-Object { $_.Path -notmatch '^System/session-logs/' })
if ($changes.Count -eq 0) { return }

# --- Derive task hint + slug from the dominant top-level directory ---
$topDirs = $changes | ForEach-Object { ($_.Path -split '[\\/]')[0] }
$dominant = ($topDirs | Group-Object | Sort-Object Count, Name -Descending | Select-Object -First 1).Name
$distinctTop = @($topDirs | Sort-Object -Unique)
$taskHint = "Vault session — changes in $($distinctTop -join ', ')"

$slugSource = if ($dominant) { $dominant } else { 'vault' }
$slug = ($slugSource.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
if (-not $slug) { $slug = 'vault' }

# --- Build the log body ---
$fileList = ($changes | Select-Object -First 20 | ForEach-Object { "- ``$($_.Path)``" }) -join "`n"
if ($changes.Count -gt 20) { $fileList += "`n- …and $($changes.Count - 20) more" }

$content = @"
---
agent: $Agent
timestamp: $Stamp
task: $taskHint
status: auto-logged
---

**Task:** $taskHint
**Files Modified ($($changes.Count)):**
$fileList

> Deterministic SessionEnd log (file list from git; no LLM task inference).
"@

# --- Write it ---
$outDir  = Join-Path $VaultRoot "System/session-logs/$DateDir"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
$outFile = Join-Path $outDir "${TimeName}_session-$slug.md"
Set-Content -Path $outFile -Value $content -Encoding UTF8
Write-Host "vault-session-log: wrote $outFile ($($changes.Count) change(s))."
