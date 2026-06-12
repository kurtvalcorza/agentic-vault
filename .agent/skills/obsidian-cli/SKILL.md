---
name: obsidian-cli
description: "Invoke Obsidian CLI for batch search, file ops, task queries, and template runs. Use when MCP tools are insufficient for scripted or bulk operations."
---

## Purpose

Invoke the Obsidian CLI to perform vault-level operations: search, file management, task queries, property/tag manipulation, template execution, plugin management, daily notes, backlink analysis, and more.

## Prerequisites

- Obsidian CLI installed globally and on PATH (`obsidian --help` to verify)
- Obsidian desktop app running (CLI communicates with the running instance)

## Required Capabilities

- `command-exec` (Execute shell commands)

## Invocation Pattern

Call `obsidian` directly. No wrapper scripts needed.

```
obsidian <command> [key=value ...] [flags]
```

- `file=<name>` resolves by name (like wikilinks)
- `path=<path>` resolves by exact path (e.g. `01_Projects/Project Atlas/note.md`)
- Most commands default to the active file when `file`/`path` is omitted
- Quote values with spaces: `name="My Note"`
- Use `vault=<name>` to target a specific vault

## Command Reference

### Search & Discovery

| Command | What it does | Key options |
|:---|:---|:---|
| `search query=<text>` | Full-text search | `path=`, `limit=`, `total`, `case`, `format=text\|json` |
| `search:context query=<text>` | Search with matching line context | `path=`, `limit=`, `case`, `format=text\|json` |
| `search:open query=<text>` | Open search view in Obsidian | |

### File Operations

| Command | What it does | Key options |
|:---|:---|:---|
| `files` | List vault files | `folder=`, `ext=`, `total` |
| `file file=<name>` | Show file info | `path=` |
| `create name=<name>` | Create a new file | `path=`, `content=`, `template=`, `overwrite`, `open` |
| `read file=<name>` | Read file contents | `path=` |
| `append file=<name> content=<text>` | Append to file | `path=`, `inline` |
| `prepend file=<name> content=<text>` | Prepend to file | `path=`, `inline` |
| `move file=<name> to=<path>` | Move/rename a file | `path=` |
| `rename file=<name> name=<new>` | Rename a file | `path=` |
| `delete file=<name>` | Delete a file | `path=`, `permanent` |
| `folders` | List vault folders | `folder=`, `total` |
| `folder path=<path>` | Show folder info | `info=files\|folders\|size` |

### Links & Graph Analysis

| Command | What it does | Key options |
|:---|:---|:---|
| `backlinks file=<name>` | List backlinks to a file | `counts`, `total`, `format=json\|tsv\|csv` |
| `links file=<name>` | List outgoing links | `total` |
| `orphans` | Files with no incoming links | `total`, `all` |
| `deadends` | Files with no outgoing links | `total`, `all` |
| `unresolved` | List broken/unresolved links | `total`, `counts`, `verbose`, `format=json\|tsv\|csv` |
| `aliases` | List aliases | `file=`, `total`, `verbose` |

### Tasks

| Command | What it does | Key options |
|:---|:---|:---|
| `tasks` | List vault tasks | `file=`, `path=`, `total`, `done`, `todo`, `status=`, `verbose`, `format=json\|tsv\|csv`, `daily` |
| `task ref=<path:line>` | Show/update a task | `toggle`, `done`, `todo`, `status=`, `daily` |

### Properties (Frontmatter)

| Command | What it does | Key options |
|:---|:---|:---|
| `properties` | List vault properties | `file=`, `path=`, `name=`, `total`, `sort=count`, `counts`, `format=yaml\|json\|tsv` |
| `property:read name=<prop>` | Read a property value | `file=`, `path=` |
| `property:set name=<prop> value=<val>` | Set a property | `file=`, `path=`, `type=text\|list\|number\|checkbox\|date\|datetime` |
| `property:remove name=<prop>` | Remove a property | `file=`, `path=` |

### Tags

| Command | What it does | Key options |
|:---|:---|:---|
| `tags` | List vault tags | `file=`, `path=`, `total`, `counts`, `sort=count`, `format=json\|tsv\|csv` |
| `tag name=<tag>` | Get tag info | `total`, `verbose` |

### Daily Notes

| Command | What it does | Key options |
|:---|:---|:---|
| `daily` | Open today's daily note | `paneType=tab\|split\|window` |
| `daily:read` | Read daily note contents | |
| `daily:append content=<text>` | Append to daily note | `inline`, `open` |
| `daily:prepend content=<text>` | Prepend to daily note | `inline`, `open` |
| `daily:path` | Get daily note file path | |

### Templates

| Command | What it does | Key options |
|:---|:---|:---|
| `templates` | List available templates | `total` |
| `template:read name=<tpl>` | Read template content | `resolve`, `title=` |
| `template:insert name=<tpl>` | Insert template into active file | |

### Bookmarks

| Command | What it does | Key options |
|:---|:---|:---|
| `bookmarks` | List bookmarks | `total`, `verbose`, `format=json\|tsv\|csv` |
| `bookmark` | Add a bookmark | `file=`, `folder=`, `search=`, `url=`, `title=`, `subpath=` |

### Plugins

| Command | What it does | Key options |
|:---|:---|:---|
| `plugins` | List installed plugins | `filter=core\|community`, `versions`, `format=json\|tsv\|csv` |
| `plugins:enabled` | List enabled plugins | `filter=`, `versions` |
| `plugin id=<id>` | Get plugin info | |
| `plugin:enable id=<id>` | Enable a plugin | `filter=` |
| `plugin:disable id=<id>` | Disable a plugin | `filter=` |
| `plugin:install id=<id>` | Install community plugin | `enable` |
| `plugin:uninstall id=<id>` | Uninstall community plugin | |
| `plugin:reload id=<id>` | Reload plugin (dev) | |
| `plugins:restrict` | Toggle restricted mode | `on`, `off` |

### Bases

| Command | What it does | Key options |
|:---|:---|:---|
| `bases` | List all base files | |
| `base:views` | List views in current base | |
| `base:query file=<name>` | Query a base | `view=`, `format=json\|csv\|tsv\|md\|paths` |
| `base:create file=<name>` | Create item in a base | `view=`, `name=`, `content=`, `open` |

### Themes & Snippets

| Command | What it does | Key options |
|:---|:---|:---|
| `theme` | Show active theme | `name=` for details |
| `theme:set name=<name>` | Set active theme | |
| `theme:install name=<name>` | Install community theme | `enable` |
| `theme:uninstall name=<name>` | Uninstall a theme | |
| `themes` | List installed themes | `versions` |
| `snippets` | List CSS snippets | |
| `snippets:enabled` | List enabled snippets | |
| `snippet:enable name=<name>` | Enable a snippet | |
| `snippet:disable name=<name>` | Disable a snippet | |

### Vault & Workspace

| Command | What it does | Key options |
|:---|:---|:---|
| `vault` | Show vault info | `info=name\|path\|files\|folders\|size` |
| `vaults` | List known vaults | `total`, `verbose` |
| `workspace` | Show workspace tree | `ids` |
| `workspaces` | List saved workspaces | `total` |
| `workspace:load name=<name>` | Load a workspace | |
| `workspace:save name=<name>` | Save current workspace | |
| `workspace:delete name=<name>` | Delete a workspace | |
| `reload` | Reload the vault | |
| `restart` | Restart Obsidian | |

### Navigation & History

| Command | What it does | Key options |
|:---|:---|:---|
| `open file=<name>` | Open a file | `path=`, `newtab` |
| `recents` | List recently opened files | `total` |
| `random` | Open a random note | `folder=`, `newtab` |
| `random:read` | Read a random note | `folder=` |
| `outline file=<name>` | Show headings | `format=tree\|md\|json`, `total` |
| `wordcount file=<name>` | Count words/chars | `words`, `characters` |
| `history file=<name>` | List file history | |
| `history:read file=<name>` | Read a history version | `version=` |
| `history:restore file=<name>` | Restore a version | `version=` |
| `diff file=<name>` | Diff local/sync versions | `from=`, `to=`, `filter=local\|sync` |
| `tabs` | List open tabs | `ids` |
| `hotkeys` | List hotkeys | `total`, `verbose`, `all` |
| `commands` | List Obsidian commands | `filter=` |
| `command id=<cmd-id>` | Execute an Obsidian command | |
| `version` | Show Obsidian version | |

### Developer Tools

| Command | What it does | Key options |
|:---|:---|:---|
| `devtools` | Toggle dev tools | |
| `dev:screenshot` | Take a screenshot | `path=` |
| `dev:dom selector=<css>` | Query DOM elements | `total`, `text`, `inner`, `all`, `attr=`, `css=` |
| `dev:css selector=<css>` | Inspect CSS | `prop=` |
| `dev:console` | Show console messages | `clear`, `limit=`, `level=` |
| `dev:errors` | Show captured errors | `clear` |
| `eval code=<js>` | Execute JavaScript | |
| `dev:cdp method=<method>` | Run CDP command | `params=<json>` |
| `dev:debug` | Attach/detach debugger | `on`, `off` |
| `dev:mobile` | Toggle mobile emulation | `on`, `off` |

## Common Recipes

```bash
# Search for a term with context
obsidian search:context query="Project Atlas" path="01_Projects" limit=10

# List orphan notes
obsidian orphans total

# List all open tasks from daily note
obsidian tasks daily todo

# Set a frontmatter property
obsidian property:set name="status" value="active" path="01_Projects/Project Atlas/overview.md"

# List tags sorted by frequency
obsidian tags counts sort=count

# Query a base view as JSON
obsidian base:query path="my-base.base" view="All" format=json

# Check unresolved links with source files
obsidian unresolved verbose

# Append to today's daily note
obsidian daily:append content="- Meeting with the funding agency at 2pm"

# Take a screenshot of the current view
obsidian dev:screenshot path="screenshot.png"
```

## Output Formats

Most list commands support `format=` with these options:
- `text` / `tsv` — tab-separated (default for most commands, good for piping)
- `json` — structured data (best for programmatic parsing)
- `csv` — comma-separated
- `md` — markdown table (outline, base:query)
- `yaml` — YAML (properties)

## Error Handling

- **Exit 0**: Success
- **Non-zero exit**: Check `stderr` for details. Common causes: Obsidian not running, file not found, invalid command syntax.

## Limitations

- Obsidian desktop must be running (CLI talks to the running instance)
- Interactive/GUI-opening commands (`open`, `daily`, `search:open`) are fire-and-forget from agent context
- `eval` runs JS in Obsidian's renderer — use with caution

## Related Skills

- [[obsidian-markdown]] — Obsidian-flavored Markdown syntax
- [[obsidian-bases]] — Working with .base files
- [[optimize-workspace]] — Vault health and maintenance
