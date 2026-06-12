<#
.SYNOPSIS
    Auto-snapshot the Obsidian vault to LOCAL git (notes + config scope).

.DESCRIPTION
    Hands-off, idempotent, safe-to-rerun. Designed to run unattended from a
    session-end hook (Claude SessionEnd / Kiro agentStop), so the owner — who
    is not a git user — never has to touch git.

    Steps:
      1. Resolve vault root from this script's own location (no hardcoded paths).
      2. Skip cleanly if git is missing or this isn't a repo.
      3. Ensure core.longpaths (a note path exceeds Windows MAX_PATH).
      4. Purge desktop.ini that Google Drive injects into .git (breaks gc/repack).
      5. Stage everything (.gitignore filters secrets, binaries, nested repos).
      6. SECRET GATE: unstage any file containing an AWS key or private key.
      7. Commit with a timestamped message only when something changed.

    Audit trail is appended to .git\auto-commit.log (never tracked).

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File .agent\scripts\vault-git-commit.ps1
#>

$ErrorActionPreference = 'Stop'

$VaultRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$GitDir    = Join-Path $VaultRoot '.git'
$Stamp     = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

function Write-Log($msg) {
    $line = "[$Stamp] $msg"
    Write-Host "vault-git-commit: $line"
    try { Add-Content -Path (Join-Path $GitDir 'auto-commit.log') -Value $line -ErrorAction SilentlyContinue } catch {}
}

# --- Preconditions ---
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Log 'git not found on PATH - skipping.'; return }
if (-not (Test-Path $GitDir)) { Write-Log 'no .git here - not a repo, skipping.'; return }

# --- Ensure long-path support (idempotent) ---
git -C $VaultRoot config core.longpaths true | Out-Null

# --- Purge desktop.ini that Drive injects (vault-wide; in .git it breaks gc/repack) ---
$inis = @(Get-ChildItem -Path $VaultRoot -Recurse -Force -Filter 'desktop.ini' -ErrorAction SilentlyContinue)
if ($inis.Count -gt 0) {
    $inis | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Log "removed $($inis.Count) desktop.ini file(s) vault-wide"
}

# --- Stage everything (.gitignore does the filtering) ---
git -C $VaultRoot add -A 2>$null

$staged = @(git -C $VaultRoot diff --cached --name-only)
if ($staged.Count -eq 0) { Write-Log 'no changes to commit.'; return }

# --- SECRET GATE: never commit cloud keys, API tokens, or private keys ---
# Patterns tuned 2026-06-12 against the full index: sk- must not match word tails
# (risk-/task-/desk-...) so it requires a non-letter boundary + a long unbroken
# alphanumeric run; Google keys always start AIzaSy (bare AIza matches base64 noise).
$leak = @(git -C $VaultRoot grep --cached -lE 'AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,}|(^|[^A-Za-z])sk-(proj-|ant-api[0-9]{2}-)?[A-Za-z0-9_]{32,}|AIzaSy[A-Za-z0-9_-]{33}|xox[baprs]-[A-Za-z0-9-]{10,}')
if ($leak.Count -gt 0) {
    foreach ($f in $leak) { git -C $VaultRoot reset --quiet -- $f | Out-Null }
    Write-Log "WARNING - excluded possible secret(s) from commit: $($leak -join '; '). Add them to .gitignore."
    $staged = @(git -C $VaultRoot diff --cached --name-only)
    if ($staged.Count -eq 0) { Write-Log 'nothing left to commit after excluding secrets.'; return }
}

# --- Commit ---
$msg = "Vault auto-snapshot $Stamp ($($staged.Count) file change(s))"
git -C $VaultRoot commit -q -m $msg
if ($LASTEXITCODE -eq 0) { Write-Log "committed $($staged.Count) change(s)." }
else { Write-Log "git commit returned exit $LASTEXITCODE." }

# --- Off-root history backup (self-throttling: bundles at most monthly) ---
try { & (Join-Path $PSScriptRoot 'vault-git-bundle.ps1') } catch { Write-Log "bundle step failed: $($_.Exception.Message)" }
