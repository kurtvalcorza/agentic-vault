<#
.SYNOPSIS
    Fans out adversarial-read prompts to multiple AI CLIs (Gemini, Codex,
    Cursor) for Council Mode of the tools-for-thought Interrogation protocol.

.DESCRIPTION
    Council Mode delegates ONLY the adversarial read (Interrogation Report
    Section 5) to multiple models so that different model lineages attack the
    same artifact from different angles. Everything else in the Interrogation
    protocol — preliminary scan, core-claim distillation, assumption surfacing,
    silence hunting, evidence calibration, convergence synthesis, decision
    menu — stays with the orchestrating agent.

    This script reads a JSON job spec describing the shared context and the
    persona/runner assignments, dispatches one headless call per persona to the
    correct CLI, captures each response, and writes a single markdown results
    file plus a JSON status sidecar. Per-runner failures are NON-FATAL: a failed
    persona is recorded as UNAVAILABLE and the run proceeds (the "proceed, note"
    failure rule).

.PARAMETER JobSpec
    Path to a JSON job spec. Schema:
    {
      "artifact":   "<full artifact text OR a summary of key claims>",
      "coreClaim":  "<orchestrator-distilled core claim>",
      "assumptions":["<load-bearing assumption>", ...],
      "personas": [
        {
          "label":  "Investigative tech journalist (Rappler/PDI)",
          "lens":   "external public / accountability",
          "runner": "gemini" | "codex" | "cursor",
          "model":  "<optional; runner default used if omitted>",
          "brief":  "<persona instructions: who they are, what they hunt>",
          "voiceAsk":"<what the closing 'What you would say' should produce>"
        }
      ]
    }

.PARAMETER OutFile
    Path to write the markdown results file. A sibling "<OutFile>.status.json"
    is also written with per-persona status for the orchestrator to parse.

.PARAMETER TimeoutSec
    Per-runner timeout in seconds. Default 360.

.EXAMPLE
    .\council-adversary-read.ps1 -JobSpec ".agent/outputs/council-job.json" `
        -OutFile ".agent/outputs/2026-05-30_council-reads.md"

.NOTES
    Part of the Example Org vault agent tooling (tools-for-thought skill).

    Runner invocation quirks (learned from prototyping — do not "simplify" away):
      gemini  : prompt passed as -p argument. Emits noisy stderr (local Gemma
                router 500s, ripgrep warnings) that is harmless; we capture
                stdout only and discard stderr.
      codex   : prompt MUST be piped via stdin ('$p | codex exec'); passing it
                as an argument makes 'codex exec' block waiting on stdin EOF.
                Has a usage cap that surfaces as "hit your usage limit".
      cursor  : long-form flags only ('--print', NOT '-p', on the PowerShell
                shim). Model name is e.g. 'gpt-5.1-codex' (run
                'cursor-agent --list-models'). Requires 'cursor-agent login'.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$JobSpec,

    [Parameter(Mandatory = $true)]
    [string]$OutFile,

    [int]$TimeoutSec = 360
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Runner defaults
# ---------------------------------------------------------------------------
$RunnerDefaults = @{
    gemini = @{ Model = $null }            # gemini uses account default model
    codex  = @{ Model = $null }            # codex uses its configured model
    cursor = @{ Model = "gpt-5.1-codex" }  # cursor-agent technical default
}

# ---------------------------------------------------------------------------
# Prompt assembly — the "standard" context depth: artifact + persona brief +
# core claim + load-bearing assumptions. Deliberately NOT including the
# orchestrator's silences/evidence reads, to keep each persona's attack
# independent rather than anchored to the orchestrator's reading.
# ---------------------------------------------------------------------------
function Build-Prompt {
    param($Spec, $Persona)

    $assumptions = ($Spec.assumptions | ForEach-Object { "- $_" }) -join "`n"

    @"
You are conducting an adversarial review of an institutional artifact. Return
ONLY the requested output. Do not explore files, do not use tools, do not ask
questions — produce the adversarial read directly.

# YOUR PERSONA
$($Persona.brief)

# ARTIFACT
$($Spec.artifact)

# CORE CLAIM (distilled by the orchestrator)
$($Spec.coreClaim)

# LOAD-BEARING ASSUMPTIONS (orchestrator surfacing)
$assumptions

# OUTPUT FORMAT — return ONLY these four sections. No preamble, no validation
of what works, no proposed fixes.

**What you care about (1 sentence):**

**Primary attack vector (2-3 sentences — the single most vulnerable point from your perspective):**

**Secondary vulnerabilities (2-3 short bullets):**

**What you would say ($($Persona.voiceAsk)):**
"@
}

# ---------------------------------------------------------------------------
# Failure detection — runner exits 0 even when the model refused / hit a cap,
# so we also scan output text for known failure signatures.
# ---------------------------------------------------------------------------
function Test-RunnerFailure {
    param([string]$Text, [int]$ExitCode)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return "empty response"
    }
    $signatures = @(
        @{ Pattern = "hit your usage limit";        Reason = "usage limit / rate limited" },
        @{ Pattern = "Authentication required";      Reason = "not authenticated" },
        @{ Pattern = "No models available";          Reason = "no models for account" },
        @{ Pattern = "Retry attempts exhausted";     Reason = "API retries exhausted" },
        @{ Pattern = "usage limit";                  Reason = "usage limit / rate limited" }
    )
    foreach ($s in $signatures) {
        if ($Text -match $s.Pattern) { return $s.Reason }
    }
    # A valid read contains the required headers; if none present, treat as junk.
    if ($Text -notmatch "Primary attack vector") {
        return "response missing expected sections"
    }
    return $null
}

# ---------------------------------------------------------------------------
# Dispatch one persona to its runner. Returns a hashtable result.
# Uses Start-Job for a hard timeout boundary per call.
# ---------------------------------------------------------------------------
function Invoke-Persona {
    param($Spec, $Persona, [int]$TimeoutSec)

    $runner = ($Persona.runner).ToLower()
    if (-not $RunnerDefaults.ContainsKey($runner)) {
        return @{ Status = "UNAVAILABLE"; Reason = "unknown runner '$runner'"; Text = ""; Runner = $runner; Model = "" }
    }

    $model = $Persona.model
    if ([string]::IsNullOrWhiteSpace($model)) { $model = $RunnerDefaults[$runner].Model }

    $prompt = Build-Prompt -Spec $Spec -Persona $Persona

    $job = Start-Job -ScriptBlock {
        param($runner, $model, $prompt)

        switch ($runner) {
            "gemini" {
                # stdout only; stderr (Gemma router noise) discarded
                if ($model) { gemini -m $model -p $prompt 2>$null }
                else        { gemini -p $prompt 2>$null }
            }
            "codex" {
                # prompt via stdin — arg form hangs on stdin EOF
                $prompt | codex exec --skip-git-repo-check 2>&1
            }
            "cursor" {
                cursor-agent --print --output-format text --force --trust --model $model $prompt 2>&1
            }
        }
    } -ArgumentList $runner, $model, $prompt

    $completed = Wait-Job -Job $job -Timeout $TimeoutSec
    if (-not $completed) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
        return @{ Status = "UNAVAILABLE"; Reason = "timeout after ${TimeoutSec}s"; Text = ""; Runner = $runner; Model = $model }
    }

    $raw = (Receive-Job -Job $job -ErrorAction SilentlyContinue) -join "`n"
    Remove-Job -Job $job -Force -ErrorAction SilentlyContinue

    $text = Get-CleanRead -Raw $raw
    $fail = Test-RunnerFailure -Text $text -ExitCode 0
    if ($fail) {
        return @{ Status = "UNAVAILABLE"; Reason = $fail; Text = $text; Runner = $runner; Model = $model }
    }
    return @{ Status = "OK"; Reason = ""; Text = $text; Runner = $runner; Model = $model }
}

# ---------------------------------------------------------------------------
# Strip runner banners / stderr that leaks into stdout, keep from the first
# expected section header onward.
# ---------------------------------------------------------------------------
function Get-CleanRead {
    param([string]$Raw)
    if ([string]::IsNullOrWhiteSpace($Raw)) { return "" }
    $idx = $Raw.IndexOf("**What you care about")
    if ($idx -ge 0) { return $Raw.Substring($idx).Trim() }
    return $Raw.Trim()
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if (-not (Test-Path $JobSpec)) { throw "Job spec not found: $JobSpec" }
$spec = Get-Content -Raw -Path $JobSpec | ConvertFrom-Json

$outDir = Split-Path -Parent $OutFile
if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }

$results = @()
$letters = [char[]]([char]'A'..[char]'Z')
$i = 0

$md = New-Object System.Text.StringBuilder
[void]$md.AppendLine("# Council Adversarial Reads")
[void]$md.AppendLine("")
[void]$md.AppendLine("**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$md.AppendLine("**Personas dispatched:** $($spec.personas.Count)")
[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")

foreach ($persona in $spec.personas) {
    $letter = $letters[$i]; $i++
    Write-Host "[council] Dispatching Adversary $letter -> $($persona.runner) ($($persona.label))..."
    $r = Invoke-Persona -Spec $spec -Persona $persona -TimeoutSec $TimeoutSec
    $r.Label  = $persona.label
    $r.Lens   = $persona.lens
    $r.Letter = $letter
    $results += $r

    [void]$md.AppendLine("## Adversary $($letter) — $($persona.label)")
    [void]$md.AppendLine("**Lens:** $($persona.lens) | **Runner:** $($r.Runner)$(if($r.Model){" ($($r.Model))"}) | **Status:** $($r.Status)")
    [void]$md.AppendLine("")
    if ($r.Status -eq "OK") {
        [void]$md.AppendLine($r.Text)
    } else {
        [void]$md.AppendLine("> [UNAVAILABLE] $($r.Reason). Per the council failure rule, the report proceeds without this read. This lens is a KNOWN GAP in this run — re-run before treating the report as complete.")
    }
    [void]$md.AppendLine("")
    [void]$md.AppendLine("---")
    [void]$md.AppendLine("")
}

$ok = ($results | Where-Object { $_.Status -eq "OK" }).Count
[void]$md.AppendLine("**Council completeness:** $ok of $($results.Count) personas returned a usable read.")
if ($ok -lt $results.Count) {
    [void]$md.AppendLine("")
    [void]$md.AppendLine("> Convergence analysis below is based on the available reads only. Treat convergence as provisional until all lenses report.")
}

Set-Content -Path $OutFile -Value $md.ToString() -Encoding UTF8

# Status sidecar for the orchestrator
$status = @{
    generated = (Get-Date -Format 'o')
    total     = $results.Count
    ok        = $ok
    personas  = @($results | ForEach-Object {
        @{ letter = $_.Letter; label = $_.Label; runner = $_.Runner; model = $_.Model; status = $_.Status; reason = $_.Reason }
    })
}
$status | ConvertTo-Json -Depth 5 | Set-Content -Path "$OutFile.status.json" -Encoding UTF8

Write-Host ""
Write-Host "[council] Wrote $OutFile ($ok/$($results.Count) personas OK)"
Write-Host "[council] Status sidecar: $OutFile.status.json"
