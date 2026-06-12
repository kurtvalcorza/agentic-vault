# Local Security Audit

Comprehensive local security audit for your development environment. Scans repositories, running services, agent workspaces, credentials, and system configuration for vulnerabilities.

## Quick Start

Tell any agent:
- "Audit this repo for security issues" (Module 1 — repo triage)
- "Scan for open ports" (Module 2 — running services)
- "Check my agent workspace security" (Module 3 — workspace integrity)
- "Find leaked secrets" (Module 4 — credential hygiene)
- "Check my system security" (Module 5 — system posture)
- "Run a full security audit" (all modules)

## Modules

| # | Module | What It Checks | When to Run |
|:--|:-------|:---------------|:------------|
| 1 | **Repository Triage** | Secrets in code, post-install scripts, network bindings, CSWSH, dependencies, .gitignore | After cloning a new repo or installing a new tool |
| 2 | **Running Services & Ports** | Open ports, MCP server transports, stale dev servers | Periodically or when suspecting exposure |
| 3 | **Agent Workspace Security** | MCP config secrets, symlink integrity, skill modifications, cross-agent isolation | After workspace changes or when troubleshooting |
| 4 | **Credential Hygiene** | Git credential storage, scattered .env files, tokens in shell profiles, SSH keys | Periodically or after setting up a new machine |
| 5 | **System Posture** | Firewall, Defender, scheduled tasks, RDP/SSH, recently installed software | Periodically or after system changes |

## Output

Reports are saved to `.agent/outputs/YYYY-MM-DD_security-audit.md` using the template in `templates/audit-report.md`.

Findings are tagged by severity:
- `[CRITICAL]` — Immediate action required
- `[HIGH]` — Fix soon
- `[MEDIUM]` — Should fix
- `[LOW]` — Informational

## Origin

Assimilated from a Gemini workspace skill focused on CSWSH and open port detection. Expanded to cover the full local security surface relevant to a multi-agent PKM development environment.

## Platform

Currently Windows-focused (PowerShell commands). The static analysis modules (1.1–1.6, parts of 3 and 4) are platform-agnostic.
