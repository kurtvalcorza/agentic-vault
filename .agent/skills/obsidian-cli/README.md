# Obsidian CLI

Universal agent skill for interacting with the Obsidian vault via its command-line interface.

## Purpose

Perform vault-level operations — search, file management, task queries, property/tag manipulation, template execution, plugin management, link analysis, and more — directly from the command line. Useful for batch operations, automation, and when MCP tools are insufficient.

## When to Use

- "Search vault for...", "Find notes matching..."
- "List files in...", "Show orphan notes"
- "Check open tasks", "Mark task as done"
- "Set property on...", "List tags"
- "Run template...", "Append to daily note"
- "List plugins", "Enable/disable plugin"
- "Check backlinks to...", "Find unresolved links"
- Any batch or scripted vault operation

## Prerequisites

1. **Obsidian CLI** installed and on PATH (`obsidian --help` to verify)
2. **Obsidian desktop app** running (CLI communicates with the running instance)

## Quick Start

```bash
# Basic usage
obsidian <command> [key=value ...] [flags]

# Examples
obsidian search:context query="TODO" path="01_Projects"
obsidian tasks todo verbose
obsidian tags counts sort=count
obsidian orphans total
obsidian property:set name="status" value="done" file="My Note"
obsidian daily:append content="- Quick capture"
```

## Command Categories

| Category | Commands | Examples |
|:---|:---|:---|
| Search | `search`, `search:context`, `search:open` | Full-text search with context |
| Files | `files`, `file`, `create`, `read`, `append`, `prepend`, `move`, `rename`, `delete` | CRUD operations |
| Links | `backlinks`, `links`, `orphans`, `deadends`, `unresolved`, `aliases` | Graph analysis |
| Tasks | `tasks`, `task` | List, toggle, filter tasks |
| Properties | `properties`, `property:read`, `property:set`, `property:remove` | Frontmatter management |
| Tags | `tags`, `tag` | Tag listing and info |
| Daily | `daily`, `daily:read`, `daily:append`, `daily:prepend`, `daily:path` | Daily note operations |
| Templates | `templates`, `template:read`, `template:insert` | Template management |
| Bookmarks | `bookmarks`, `bookmark` | Bookmark management |
| Plugins | `plugins`, `plugin`, `plugin:enable/disable/install/uninstall` | Plugin management |
| Bases | `bases`, `base:query`, `base:create`, `base:views` | Database views |
| Themes | `theme`, `themes`, `snippets` | Appearance management |
| Vault | `vault`, `vaults`, `workspace`, `workspaces`, `reload`, `restart` | Vault management |
| Navigation | `open`, `recents`, `random`, `outline`, `wordcount`, `tabs` | Navigation and info |
| History | `history`, `diff`, `history:read`, `history:restore` | Version history |
| Dev | `devtools`, `dev:screenshot`, `dev:dom`, `eval` | Developer tools |

See `SKILL.md` for the full command reference with all options.

## Key Conventions

- `file=<name>` resolves like wikilinks; `path=<path>` is exact
- Most commands default to the active file when file/path is omitted
- Quote values with spaces: `name="My Note"`
- Target a specific vault: `vault=<name>`
- Output formats: `format=json|tsv|csv|md|yaml` (varies by command)

## Migration Note (v2.0)

This skill was reworked from v1.0 which routed commands through PowerShell wrapper scripts (`obsidian-search.ps1`, etc.). The CLI is now called directly — simpler, faster, and covers the full command set. The legacy wrapper scripts in `.agent/scripts/` are no longer referenced by this skill.
