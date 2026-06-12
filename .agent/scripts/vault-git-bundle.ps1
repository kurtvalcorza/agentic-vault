<#
.SYNOPSIS
    Monthly off-root backup of the vault's git history via `git bundle`.

.DESCRIPTION
    The vault repo is local-only (no remote), often inside a cloud-synced
    folder — a single point of failure for the entire version history. This
    script writes a full-repo bundle to a DIFFERENT storage root (default:
    %USERPROFILE%\OneDrive\VaultBackups, override with -BackupDir), so
    history survives a sync-account or disk-folder catastrophe.

    Hands-off and self-throttling — designed to be called at the end of
    vault-git-commit.ps1 (i.e., on every session end across all harnesses):
      - Runs only when the newest existing bundle is older than 30 days
        (or none exists). Otherwise exits immediately.
      - Keeps the 3 newest bundles, deletes older ones (rolling window).
      - Verifies the bundle with `git bundle verify` before trusting it.

    Restore (an agent task, never the owner's):
      git clone "<bundle path>" restored-vault

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File .agent\scripts\vault-git-bundle.ps1
#>

param(
    [int]$MaxAgeDays = 30,
    [int]$Keep = 3,
    [string]$BackupDir = (Join-Path $env:USERPROFILE 'OneDrive\VaultBackups')
)

$ErrorActionPreference = 'Stop'

$VaultRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$GitDir    = Join-Path $VaultRoot '.git'
$Stamp     = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

function Write-Log($msg) {
    $line = "[$Stamp] bundle: $msg"
    Write-Host "vault-git-bundle: $line"
    try { Add-Content -Path (Join-Path $GitDir 'auto-commit.log') -Value $line -ErrorAction SilentlyContinue } catch {}
}

# --- Preconditions ---
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Log 'git not found - skipping.'; return }
if (-not (Test-Path $GitDir)) { Write-Log 'not a repo - skipping.'; return }
if (-not (Test-Path (Split-Path $BackupDir))) { Write-Log "backup root parent not found ($(Split-Path $BackupDir)) - skipping."; return }

# --- Throttle: only bundle when the newest one is stale ---
if (-not (Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null }
$existing = @(Get-ChildItem $BackupDir -Filter 'vault-*.bundle' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
if ($existing.Count -gt 0 -and $existing[0].LastWriteTime -gt (Get-Date).AddDays(-$MaxAgeDays)) { return }

# --- Create + verify ---
$target = Join-Path $BackupDir ("vault-{0}.bundle" -f (Get-Date -Format 'yyyy-MM-dd'))
git -C $VaultRoot bundle create $target --all 2>$null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $target)) { Write-Log "bundle create FAILED (exit $LASTEXITCODE)."; return }

git -C $VaultRoot bundle verify $target 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Log 'bundle verify FAILED - deleting bad bundle.'; Remove-Item $target -Force; return }

$sizeMB = '{0:N0}' -f ((Get-Item $target).Length / 1MB)
Write-Log "created + verified $(Split-Path $target -Leaf) ($sizeMB MB)."

# --- Rolling window: keep newest $Keep ---
$all = @(Get-ChildItem $BackupDir -Filter 'vault-*.bundle' | Sort-Object LastWriteTime -Descending)
if ($all.Count -gt $Keep) {
    $all | Select-Object -Skip $Keep | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Log "pruned old bundle $($_.Name)."
    }
}
