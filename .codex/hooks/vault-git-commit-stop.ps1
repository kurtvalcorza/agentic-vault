<#
.SYNOPSIS
    Codex Stop hook wrapper for session logging and local-git auto-snapshot.

.DESCRIPTION
    Codex Stop hooks must emit valid JSON on stdout. The shared vault session
    log and commit scripts write human-readable status lines, so this wrapper
    runs them sequentially, mirrors their output into .git\codex-stop-hook.log,
    and emits only the JSON control response that Codex expects.
#>

$ErrorActionPreference = 'Stop'

try {
    $null = [Console]::In.ReadToEnd()

    $HookDir = $PSScriptRoot
    $VaultRoot = (Resolve-Path (Join-Path $HookDir '..\..')).Path
    $SessionLogScript = Join-Path $VaultRoot '.agent\scripts\vault-session-log.ps1'
    $CommitScript = Join-Path $VaultRoot '.agent\scripts\vault-git-commit.ps1'
    $GitDir = Join-Path $VaultRoot '.git'
    $HookLog = Join-Path $GitDir 'codex-stop-hook.log'

    if (-not (Test-Path $SessionLogScript)) {
        throw "Missing session log script: $SessionLogScript"
    }

    if (-not (Test-Path $CommitScript)) {
        throw "Missing commit script: $CommitScript"
    }

    if ($env:CODEX_HOOK_DRY_RUN -eq '1') {
        [ordered]@{
            continue = $true
        } | ConvertTo-Json -Compress
        exit 0
    }

    $sessionOutput = @(& pwsh -NoProfile -ExecutionPolicy Bypass -File $SessionLogScript -Agent codex 2>&1)
    $sessionExitCode = $LASTEXITCODE

    $commitOutput = @(& pwsh -NoProfile -ExecutionPolicy Bypass -File $CommitScript 2>&1)
    $commitExitCode = $LASTEXITCODE

    if (Test-Path $GitDir) {
        $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        Add-Content -Path $HookLog -Value "[$stamp] Codex Stop hook ran."
        foreach ($line in $sessionOutput) {
            Add-Content -Path $HookLog -Value $line.ToString()
        }
        foreach ($line in $commitOutput) {
            Add-Content -Path $HookLog -Value $line.ToString()
        }
    }

    $text = (($sessionOutput + $commitOutput) | ForEach-Object { $_.ToString() }) -join "`n"
    if ($sessionExitCode -ne 0) {
        [ordered]@{
            decision = 'block'
            reason = "Vault session log returned exit $sessionExitCode. Check .git\codex-stop-hook.log."
        } | ConvertTo-Json -Compress
        exit 0
    }

    if ($commitExitCode -ne 0) {
        [ordered]@{
            decision = 'block'
            reason = "Vault auto-commit returned exit $commitExitCode. Check .git\codex-stop-hook.log."
        } | ConvertTo-Json -Compress
        exit 0
    }

    if ($text -match 'WARNING') {
        [ordered]@{
            decision = 'block'
            reason = 'Vault auto-commit reported a possible secret. Check .git\codex-stop-hook.log and notify the owner.'
        } | ConvertTo-Json -Compress
        exit 0
    }

    [ordered]@{
        continue = $true
    } | ConvertTo-Json -Compress
    exit 0
}
catch {
    [ordered]@{
        decision = 'block'
        reason = "Codex vault auto-commit hook failed: $($_.Exception.Message)"
    } | ConvertTo-Json -Compress
    exit 0
}
