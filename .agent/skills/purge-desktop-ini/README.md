# Purge Desktop.ini

Recursively removes all desktop.ini files from the workspace.

## What It Does

Simple utility that scans the entire vault and deletes Windows desktop.ini files that clutter directory views and version control.

## When to Use

- Desktop.ini files appearing in vault
- Before committing to version control
- Cleaning up after Windows Explorer customizations
- Workspace hygiene maintenance

## Quick Start

**Triggers**:
- "Purge desktop.ini"
- "Clean up desktop.ini files"
- "Remove desktop.ini from vault"

Runs a PowerShell script that:
1. Recursively scans from vault root
2. Finds all desktop.ini files
3. Deletes them with confirmation
4. Reports count of removed files

## Related Skills

- `optimize-workspace` - Comprehensive vault cleanup
- `optimize-assets` - Image file optimization
