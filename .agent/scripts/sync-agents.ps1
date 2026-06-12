<#
.SYNOPSIS
    Verify CLAUDE.md and GEMINI.md are consistent with AGENTS.md.

.DESCRIPTION
    AGENTS.md is the canonical protocol file. The two satellite files relate to
    it differently, and this script enforces each relationship WITHOUT copying
    AGENTS.md over either of them (the old behavior, which would have clobbered
    CLAUDE.md's @AGENTS.md directive and GEMINI.md's digest):

      CLAUDE.md — must contain the literal "@AGENTS.md" import directive.
                  If missing, the directive is restored (file rewritten as the
                  minimal pointer).
      GEMINI.md — a hand-maintained digest carrying a marker line:
                  "Synced with AGENTS.md version: X.Y"
                  This script compares that marker against AGENTS.md's own
                  "**Version:** X.Y" footer and WARNS on mismatch. It does NOT
                  auto-regenerate the digest — that's an authoring task.

    Exit code 0 = consistent; 1 = drift detected or a file missing.

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File .agent\scripts\sync-agents.ps1
#>

$ErrorActionPreference = 'Stop'

$vaultRoot  = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$agentsFile = Join-Path $vaultRoot 'AGENTS.md'
$claudeFile = Join-Path $vaultRoot 'CLAUDE.md'
$geminiFile = Join-Path $vaultRoot 'GEMINI.md'
$drift = $false

if (-not (Test-Path $agentsFile)) { Write-Error "AGENTS.md not found at: $agentsFile"; exit 1 }

# --- AGENTS.md version (footer: **Version:** X.Y (...)) ---
$agentsVersion = $null
if ((Get-Content $agentsFile -Raw) -match '\*\*Version:\*\*\s*([0-9]+\.[0-9]+)') { $agentsVersion = $Matches[1] }
if (-not $agentsVersion) { Write-Warning 'Could not parse AGENTS.md version footer.'; $drift = $true }
else { Write-Host "AGENTS.md version: $agentsVersion" }

# --- CLAUDE.md: must reference @AGENTS.md ---
if (-not (Test-Path $claudeFile)) {
    Set-Content -Path $claudeFile -Value '@AGENTS.md' -Encoding UTF8
    Write-Host 'CLAUDE.md was missing - restored @AGENTS.md pointer.'
} elseif ((Get-Content $claudeFile -Raw) -notmatch '@AGENTS\.md') {
    Write-Warning 'CLAUDE.md does not reference @AGENTS.md - restoring pointer (old content preserved as CLAUDE.md.bak).'
    Copy-Item $claudeFile "$claudeFile.bak" -Force
    Set-Content -Path $claudeFile -Value '@AGENTS.md' -Encoding UTF8
    $drift = $true
} else {
    Write-Host 'CLAUDE.md: @AGENTS.md directive present.'
}

# --- GEMINI.md: digest version marker must match ---
if (-not (Test-Path $geminiFile)) {
    Write-Warning 'GEMINI.md missing - the derived digest needs to be authored from AGENTS.md.'
    $drift = $true
} else {
    $gemini = Get-Content $geminiFile -Raw
    if ($gemini -match 'Synced with AGENTS\.md version:\*{0,2}\s*([0-9]+\.[0-9]+)') {
        $geminiVersion = $Matches[1]
        if ($geminiVersion -eq $agentsVersion) {
            Write-Host "GEMINI.md: digest in sync (v$geminiVersion)."
        } else {
            Write-Warning "GEMINI.md digest is STALE: synced to v$geminiVersion but AGENTS.md is v$agentsVersion. Regenerate the digest."
            $drift = $true
        }
    } else {
        Write-Warning 'GEMINI.md has no "Synced with AGENTS.md version" marker - add one when regenerating.'
        $drift = $true
    }
}

if ($drift) { exit 1 } else { Write-Host 'All agent pointer files consistent.'; exit 0 }
