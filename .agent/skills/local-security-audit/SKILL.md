---
name: local-security-audit
description: Comprehensive local security audit across repos, running services, agent workspaces, credentials, and system posture. Use when auditing a new repository, checking for CSWSH or open ports, verifying MCP server security, scanning for leaked secrets, or running a full workstation security sweep.
---

# Local Security Audit

Performs a modular security audit of the local development environment. Covers repository code, running services, agent workspace integrity, credential hygiene, and system-level hardening.

## When to Use

- User downloads or sets up a new repository, tool, MCP server, or browser plugin.
- User asks to "audit security", "check for CSWSH", "scan for open ports", "find leaked secrets", or "check my system security".
- Agent suspects a tool might be running an insecure local relay or server.
- Periodic security hygiene check on the workstation.

## Invocation Modes

The skill supports **modular** or **full** invocation:

| Mode | Command Example | Modules Run |
|:-----|:----------------|:------------|
| **Targeted** | "audit this repo for security issues" | Module 1 only |
| **Targeted** | "scan for open ports" | Module 2 only |
| **Targeted** | "check my agent workspace security" | Module 3 only |
| **Targeted** | "find leaked secrets on my system" | Module 4 only |
| **Targeted** | "check my system security posture" | Module 5 only |
| **Full sweep** | "run a full security audit" | All modules |

When the user's intent is ambiguous, use `user-interact` to ask which modules to run.

## Required Capabilities

- `content-search` — Search inside file contents by pattern
- `file-read` — Read file contents
- `file-search` — Find files by name or glob pattern
- `command-exec` — Execute shell commands
- `user-interact` — Ask the user questions interactively
- `file-write` — Write the audit report

---

## Module 1 — Repository Triage

**Scope:** A single repository or project directory.
**When:** User clones a new repo, installs a new tool, or asks to check a project.

### 1.1 Secret Scanning

Search the codebase for hardcoded credentials.

- **Patterns to search:**
  - API keys: `content-search` for `(?i)(api[_-]?key|apikey)\s*[:=]\s*['"][A-Za-z0-9]`
  - Tokens: `(?i)(token|secret|password|passwd|credential)\s*[:=]\s*['"][^'"]{8,}`
  - AWS keys: `AKIA[0-9A-Z]{16}`
  - Private keys: `-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----`
  - Connection strings: `(?i)(mongodb|postgres|mysql|redis)://[^\s'"]+`
- **Exclude:** `node_modules/`, `.git/`, `*.lock`, `*.min.js`, test fixture files.
- **Severity:** `[CRITICAL]` for any match in non-test source files.
- **Remediation:** Move secrets to environment variables or a secret manager. Rotate any exposed credentials immediately.

### 1.2 Post-Install Script Analysis

Check for lifecycle scripts that execute arbitrary code on install.

- **Files to check:** `package.json`, `setup.py`, `setup.cfg`, `pyproject.toml`, `Makefile`.
- **Red flags in `package.json`:**
  - `preinstall`, `postinstall`, `prepare`, `preuninstall` scripts that run non-standard commands.
  - Scripts that `curl | sh`, download remote payloads, or reference obfuscated code.
- **Red flags in Python:**
  - `setup.py` with `subprocess`, `os.system`, or network calls in `setup()`.
  - `cmdclass` overrides that execute code during install.
- **Severity:** `[HIGH]` for any script that executes commands beyond standard build tools (tsc, esbuild, node-gyp, etc.).
- **Remediation:** Review the script contents manually before running `npm install` or `pip install`.

### 1.3 Network Binding Analysis

Search for server initializations that expose ports.

- **Patterns to search:**
  - `content-search` for `0.0.0.0`, `::`, and `.listen(` calls with no host argument.
  - Look for `host:`, `hostname:`, `bind:` in config files (`.env`, YAML, JSON, TOML).
- **Red flag:** Server binds to `0.0.0.0` or `::` — exposes to entire local network (and potentially the internet).
- **Severity:** `[HIGH]`
- **Remediation:** Bind explicitly to `127.0.0.1` or `localhost`.

### 1.4 CSWSH (Cross-Site WebSocket Hijacking)

Search for WebSocket or real-time server implementations.

- **Patterns to search:** `WebSocketServer`, `new WebSocket`, `ws(`, `socket.io`, `Server({`.
- **Red flags:**
  - `ws` library without a `verifyClient` callback.
  - `socket.io` with `cors: { origin: '*' }` or missing origin config entirely.
  - Any WebSocket server relying solely on localhost/port isolation for security.
- **Why this matters:** Any website the user visits can silently connect to an unprotected local WebSocket server, exfiltrating data or sending commands.
- **Severity:** `[CRITICAL]`
- **Remediation:** Implement origin validation, or use a cryptographic token/authorization handshake.

### 1.5 Dependency Hygiene

Check for supply chain risks in dependency declarations.

- **Checks:**
  - Unpinned versions: `"*"`, `"latest"`, or very broad ranges like `">=1.0.0"`.
  - `file:` or `git+` protocol dependencies (local path or git-based injection vector).
  - Lock file presence: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Pipfile.lock`.
  - Run `npm audit --json` or `pip-audit` if the respective package manager is available.
- **Severity:** `[MEDIUM]` for unpinned deps. `[HIGH]` for missing lock files. `[CRITICAL]` for known vulnerabilities from audit.
- **Remediation:** Pin dependency versions. Generate and commit lock files. Address audit findings.

### 1.6 .gitignore Coverage

Check that sensitive files are excluded from version control.

- **Files that MUST be in `.gitignore`:** `.env`, `.env.*`, `*.pem`, `*.key`, `credentials.json`, `secrets.*`, `*.p12`, `.npmrc` (if contains tokens).
- **Red flag:** Any of these files exist in the repo AND are not gitignored.
- **Severity:** `[HIGH]`
- **Remediation:** Add to `.gitignore` and remove from git tracking (`git rm --cached`).

---

## Module 2 — Running Services & Ports

**Scope:** Current system state.
**When:** User asks to check what's exposed, or as part of full sweep.

### 2.1 Active Port Scan

Identify processes listening on non-loopback addresses.

- **Command (PowerShell):**
  ```powershell
  Get-NetTCPConnection -State Listen |
    Where-Object { $_.LocalAddress -in '0.0.0.0', '::' } |
    ForEach-Object {
      $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
      [PSCustomObject]@{
        ProcessName  = if ($proc) { $proc.Name } else { 'Unknown' }
        PID          = $_.OwningProcess
        LocalAddress = $_.LocalAddress
        LocalPort    = $_.LocalPort
      }
    } | Sort-Object LocalPort | Format-Table -AutoSize
  ```
- **Red flag:** Unknown or unexpected processes (especially Node, Python, or Go binaries) listening on `0.0.0.0` or `::`.
- **Severity:** `[HIGH]` for dev tools exposed to network. `[CRITICAL]` for anything with no auth.

### 2.2 MCP Server Transport Check

Check MCP server configurations for transport security.

- **Files to check:** MCP config files across agent workspaces.
  - Use `file-search` for `**/mcp*.json`, `**/settings.json`, `**/.mcp*` in `.claude/`, `.gemini/`, `.kiro/`, and project roots.
- **Check each MCP server entry for:**
  - Transport type: `stdio` (sandboxed, safe) vs `sse` / `streamable-http` (network-exposed).
  - If HTTP-based: is it binding to `127.0.0.1` or `0.0.0.0`?
  - Auth configuration: does it use tokens, API keys, or is it open?
- **Severity:** `[HIGH]` for HTTP-based MCP on `0.0.0.0` without auth. `[MEDIUM]` for HTTP on localhost without auth.
- **Remediation:** Prefer `stdio` transport. If HTTP is required, bind to `127.0.0.1` and require auth tokens.

### 2.3 Stale Dev Servers

Identify likely dev servers that may have been left running.

- **Command (PowerShell):**
  ```powershell
  Get-NetTCPConnection -State Listen |
    Where-Object { $_.LocalPort -in 3000,3001,4200,5000,5173,5174,8000,8080,8888,9000 } |
    ForEach-Object {
      $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
      [PSCustomObject]@{
        ProcessName = if ($proc) { $proc.Name } else { 'Unknown' }
        PID         = $_.OwningProcess
        Port        = $_.LocalPort
        Address     = $_.LocalAddress
        StartTime   = if ($proc) { $proc.StartTime } else { 'N/A' }
      }
    } | Format-Table -AutoSize
  ```
- **Red flag:** Dev servers running for extended periods (StartTime > 24 hours ago).
- **Severity:** `[LOW]` if bound to localhost. `[MEDIUM]` if bound to `0.0.0.0`.
- **Remediation:** Terminate unused dev servers.

---

## Module 3 — Agent Workspace Security

**Scope:** `.agent/`, `.claude/`, `.gemini/`, `.kiro/` directories.
**When:** User wants to verify agent workspace integrity.

### 3.1 MCP Config Secrets

Scan agent configuration files for exposed tokens or credentials.

- **Scan targets:**
  - `file-search` for `*.json` in `.claude/`, `.gemini/`, `.kiro/`, `.agent/`.
  - Also check `.env` files in project roots that MCP servers reference.
- **Patterns:** Same secret patterns as Module 1.1, plus:
  - `"apiKey"`, `"token"`, `"authorization"` fields in JSON configs.
  - Bearer tokens or API keys in MCP server environment variable blocks.
- **Severity:** `[CRITICAL]` if secrets are in files tracked by git. `[HIGH]` if in untracked but plaintext configs.
- **Remediation:** Use environment variable references instead of inline secrets. Ensure config files are gitignored.

### 3.2 Symlink/Junction Integrity

Verify the skill-sharing symlink architecture is intact.

- **Expected state:**
  - `.claude/skills/` → junction to `.agent/skills/`
  - `.gemini/skills/` → symlink to `.agent/skills/`
  - `.kiro/skills/` → symlink to `.agent/skills/`
- **Check:** Use `command-exec` to verify each link target resolves correctly:
  ```powershell
  @('.claude/skills', '.gemini/skills', '.kiro/skills') | ForEach-Object {
    $item = Get-Item $_ -ErrorAction SilentlyContinue
    [PSCustomObject]@{
      Path   = $_
      Exists = [bool]$item
      IsLink = if ($item) { $item.LinkType -ne $null } else { $false }
      Target = if ($item -and $item.LinkType) { $item.Target } else { 'N/A' }
    }
  } | Format-Table -AutoSize
  ```
- **Red flag:** Broken symlinks, links pointing to unexpected targets, or missing links.
- **Severity:** `[MEDIUM]`
- **Remediation:** Recreate symlinks/junctions pointing to `.agent/skills/`.

### 3.3 Skill Integrity Check

Verify no unexpected modifications to shared skills.

- **Check:** If the `.agent/skills/` directory is under git, run:
  ```powershell
  git -C .agent/skills status --porcelain
  ```
  If not under git, check for recently modified files (last 24 hours):
  ```powershell
  Get-ChildItem -Path '.agent/skills' -Recurse -File |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) } |
    Select-Object FullName, LastWriteTime | Format-Table -AutoSize
  ```
- **Red flag:** Unexpected modifications to SKILL.md files, new unknown skills, or deleted skills.
- **Severity:** `[MEDIUM]` for unexplained changes. `[HIGH]` if skill content appears malicious.

### 3.4 Cross-Agent Isolation

Verify agents aren't writing outside their boundaries.

- **Check:** Look for non-standard files in agent-specific directories:
  - Files in `.claude/` not expected by Claude's config structure.
  - Files in `.gemini/` not expected by Gemini's config structure.
  - Files in `.kiro/` not expected by Kiro's config structure.
- **Red flag:** Agent A's artifacts appearing in Agent B's workspace.
- **Severity:** `[LOW]` (usually benign misconfiguration).

---

## Module 4 — Credential Hygiene

**Scope:** User's development environment.
**When:** User asks to check for leaked secrets, or as part of full sweep.

### 4.1 Git Credential Storage

Check how git credentials are stored.

- **Command:**
  ```powershell
  git config --global credential.helper
  ```
- **Red flag:** Empty result (no helper — credentials may be entered every time or cached insecurely) or `store` (plaintext file at `~/.git-credentials`).
- **Safe values:** `manager`, `manager-core`, `wincred`, `osxkeychain`.
- **Also check:** Does `~/.git-credentials` exist? If so, it contains plaintext credentials.
- **Severity:** `[CRITICAL]` if `~/.git-credentials` exists with content. `[HIGH]` if helper is `store`.
- **Remediation:** Switch to `git config --global credential.helper manager` and delete `~/.git-credentials`.

### 4.2 Scattered .env Files

Find `.env` files across project directories that may contain secrets.

- **Command:**
  ```powershell
  Get-ChildItem -Path $HOME -Filter '.env*' -Recurse -File -Depth 4 -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^\.env' } |
    Select-Object FullName, Length, LastWriteTime |
    Format-Table -AutoSize
  ```
- **For each found:** Check if the containing project's `.gitignore` covers it.
- **Severity:** `[MEDIUM]` if gitignored. `[CRITICAL]` if tracked by git.
- **Remediation:** Ensure all `.env` files are gitignored. Consider using a secret manager for sensitive values.

### 4.3 Tokens in Shell Profiles

Check shell configuration files for hardcoded tokens.

- **Files to scan:**
  - PowerShell: `$PROFILE` (usually `~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`)
  - Bash: `~/.bashrc`, `~/.bash_profile`, `~/.profile`
  - Zsh: `~/.zshrc`, `~/.zprofile`
- **Patterns:** Same secret patterns as Module 1.1.
- **Severity:** `[HIGH]`
- **Remediation:** Use environment variables set through the OS or a secret manager, not hardcoded in shell profiles.

### 4.4 SSH Key Audit

Check SSH key security.

- **Command:**
  ```powershell
  Get-ChildItem -Path "$HOME/.ssh" -File -ErrorAction SilentlyContinue |
    Select-Object Name, Length, LastWriteTime |
    Format-Table -AutoSize
  ```
- **Check for each private key:** Does a corresponding `.pub` file exist? Is the key type modern (Ed25519 preferred over RSA)?
- **Red flag:** Private keys without passphrase protection are inheritable by any process running as the user.
- **Severity:** `[MEDIUM]`
- **Note:** Agent cannot directly test if a key has a passphrase without user interaction. Flag for user review.

---

## Module 5 — System Posture

**Scope:** OS-level security configuration.
**When:** User asks for system hardening check, or as part of full sweep.

### 5.1 Windows Firewall Status

- **Command:**
  ```powershell
  Get-NetFirewallProfile | Select-Object Name, Enabled | Format-Table -AutoSize
  ```
- **Red flag:** Any profile (Domain, Private, Public) with `Enabled = False`.
- **Severity:** `[CRITICAL]` if Public profile is disabled. `[HIGH]` for others.
- **Remediation:** Enable all firewall profiles.

### 5.2 Windows Defender Status

- **Command:**
  ```powershell
  Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureAge, QuickScanAge | Format-List
  ```
- **Red flags:**
  - `AntivirusEnabled` or `RealTimeProtectionEnabled` = `False`.
  - `AntivirusSignatureAge` > 7 days.
  - `QuickScanAge` > 30 days.
- **Severity:** `[CRITICAL]` if disabled. `[MEDIUM]` for stale signatures/scans.
- **Remediation:** Enable real-time protection. Update signatures. Run a quick scan.

### 5.3 Scheduled Tasks Audit

Check for suspicious scheduled tasks (common persistence mechanism).

- **Command:**
  ```powershell
  Get-ScheduledTask |
    Where-Object { $_.State -eq 'Ready' -and $_.TaskPath -notmatch '\\Microsoft\\' } |
    Select-Object TaskName, TaskPath, @{N='Actions';E={($_.Actions | ForEach-Object { $_.Execute }) -join '; '}} |
    Format-Table -AutoSize
  ```
- **Red flags:** Tasks running unknown executables, PowerShell with encoded commands (`-enc`), or tasks in unusual paths.
- **Severity:** `[HIGH]` for suspicious tasks.
- **Remediation:** Investigate and disable unknown scheduled tasks.

### 5.4 RDP and Remote Access

- **Command:**
  ```powershell
  # RDP status
  (Get-ItemProperty 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -ErrorAction SilentlyContinue).fDenyTSConnections
  # SSH server
  Get-Service -Name sshd -ErrorAction SilentlyContinue | Select-Object Status, StartType
  ```
- **Red flag:** RDP enabled (`fDenyTSConnections = 0`) or SSH server running unexpectedly.
- **Severity:** `[MEDIUM]` if intentional. `[HIGH]` if user is unaware.
- **Remediation:** Disable if not needed. If needed, ensure strong authentication is configured.

### 5.5 Recently Installed Software

Review software installed in the last 30 days.

- **Command:**
  ```powershell
  Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Where-Object { $_.InstallDate -gt (Get-Date).AddDays(-30).ToString('yyyyMMdd') } |
    Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
    Sort-Object InstallDate -Descending | Format-Table -AutoSize
  ```
- **Red flag:** Unknown software, unexpected publishers, or tools the user doesn't recall installing.
- **Severity:** `[LOW]` for review. `[HIGH]` if suspicious.

---

## Reporting

After completing the selected modules, compile findings into a single Markdown report.

- **Output location:** `.agent/outputs/YYYY-MM-DD_security-audit.md`
- **Template:** Use `.agent/skills/local-security-audit/templates/audit-report.md`
- **Structure:** Group findings by module, then by severity within each module.
- **Severity levels:**
  - `[CRITICAL]` — Immediate action required. Active exploitation risk.
  - `[HIGH]` — Fix soon. Significant security weakness.
  - `[MEDIUM]` — Should fix. Moderate risk or hygiene issue.
  - `[LOW]` — Informational. Review when convenient.
- **Each finding must include:**
  1. What was found (specific file, port, process, or config).
  2. Why it's a risk (concrete attack scenario).
  3. How to fix it (actionable remediation step).
- **Summary:** End the report with a severity counts table and a prioritized action list.
