<#
.SYNOPSIS
    One-time setup for the agentic vault template.

.DESCRIPTION
    Run this once after cloning / "Use this template":
      1. Creates the skills junctions — every agent's skills/ directory points
         at the single canonical .agent/skills/ (git cannot store junctions,
         so they must be created locally).
      2. Initializes the vault as a LOCAL git repository (no remote) so the
         session-end auto-commit hooks have something to commit to.
      3. Sets core.longpaths (Windows MAX_PATH protection — needed if the
         vault lives in a cloud-synced folder with deep paths).
      4. Prints the remaining manual steps.

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File setup.ps1
#>

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

Write-Host "Agentic Vault Template - setup" -ForegroundColor Cyan
Write-Host "Vault root: $Root`n"

# --- 1. Skills junctions (single canonical skill directory) ---
$canonical = Join-Path $Root '.agent\skills'
foreach ($agent in @('.claude', '.codex', '.kiro', '.gemini')) {
    $agentDir = Join-Path $Root $agent
    if (-not (Test-Path $agentDir)) { New-Item -ItemType Directory -Path $agentDir | Out-Null }
    $link = Join-Path $agentDir 'skills'
    if (Test-Path $link) { Write-Host "  $agent\skills already exists - skipping" }
    else {
        New-Item -ItemType Junction -Path $link -Target $canonical | Out-Null
        Write-Host "  created junction $agent\skills -> .agent\skills" -ForegroundColor Green
    }
}

# --- 2. Local git repo (undo safety net; hooks auto-commit at session end) ---
if (Get-Command git -ErrorAction SilentlyContinue) {
    if (-not (Test-Path (Join-Path $Root '.git'))) {
        git -C $Root init -q
        git -C $Root config core.longpaths true
        git -C $Root add -A
        git -C $Root commit -q -m "Initial vault snapshot (template)"
        Write-Host "  initialized local git repo + first snapshot" -ForegroundColor Green
    } else {
        git -C $Root config core.longpaths true
        Write-Host "  git repo already present - ensured core.longpaths"
    }
} else {
    Write-Warning "git not found on PATH - the auto-snapshot hooks will skip until git is installed."
}

# --- 3. What's left for you ---
Write-Host @"

Done. Remaining manual steps:
  1. Open this folder as a vault in Obsidian (it will create .obsidian/).
     Recommended community plugins: Kanban, Templater, Calendar, Excalidraw, Bases.
  2. Personalize AGENTS.md - fill in the {{OWNER_NAME}} / focus / projects
     placeholders (and mirror them in GEMINI.md + .agent/steering/memory-hot-cache.md).
  3. If you use Claude Code: hooks in .claude/settings.json fire on SessionEnd.
     If you use Kiro/Codex: their hook configs are in .kiro/hooks/ and .codex/.
  4. Optional: edit the `$BackupDir default in .agent/scripts/vault-git-bundle.ps1
     if you want history backups somewhere other than
     %USERPROFILE%\OneDrive\VaultBackups (or pass -BackupDir when running manually).
"@ -ForegroundColor Cyan
