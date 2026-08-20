from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

from agentic_vault_knowledge.core import KnowledgeIndex, apply_patch, propose_frontmatter_patch, validate_patch, vault_roots

VAULT_ROOT = Path(os.environ.get("AGENTIC_VAULT_ROOT", ".")).resolve()
READ_ONLY = os.environ.get("AGENTIC_VAULT_KNOWLEDGE_READ_ONLY", "1").lower() not in {"0", "false", "no"}
_, SCHEMA_ROOT, DB_PATH = vault_roots(VAULT_ROOT)
mcp = MCPServer("agentic-vault-knowledge")


def _with_index(fn):
    with KnowledgeIndex(DB_PATH) as idx:
        idx.build(VAULT_ROOT, SCHEMA_ROOT)
        return fn(idx)


@mcp.tool()
def knowledge_resolve_entity(ref: str) -> list[dict[str, Any]]:
    """Resolve a stable ID, alias, or normalized title. Ambiguous matches remain candidates."""
    return _with_index(lambda idx: idx.resolve(ref))


@mcp.tool()
def knowledge_search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Full-text search over semantic knowledge objects."""
    return _with_index(lambda idx: idx.search(query, limit))


@mcp.tool()
def knowledge_get(object_id: str) -> dict[str, Any] | None:
    """Get one semantic knowledge object by stable ID."""
    return _with_index(lambda idx: idx.get(object_id))


@mcp.tool()
def knowledge_neighbors(object_id: str, predicate: str | None = None, include_derived: bool = False) -> list[dict[str, Any]]:
    """Return typed semantic relations adjacent to an object."""
    return _with_index(lambda idx: idx.neighbors(object_id, predicate, include_derived))


@mcp.tool()
def knowledge_trace_path(start_id: str, end_id: str, max_depth: int = 6) -> list[str]:
    """Trace a shortest accepted semantic path between two objects."""
    return _with_index(lambda idx: idx.trace(start_id, end_id, max_depth))


@mcp.tool()
def knowledge_timeline(object_id: str) -> list[dict[str, Any]]:
    """Return bi-temporal timeline entries ordered by event/transaction time."""
    return _with_index(lambda idx: idx.timeline(object_id))


@mcp.tool()
def knowledge_sources(object_id: str) -> list[dict[str, Any]]:
    """Return evidence locators attached to relations involving an object."""
    return _with_index(lambda idx: idx.sources(object_id))


@mcp.tool()
def knowledge_contradictions() -> list[dict[str, Any]]:
    """Return deterministic contradiction candidates for same subject/predicate/time with differing targets."""
    return _with_index(lambda idx: idx.contradiction_candidates())


@mcp.tool()
def knowledge_health() -> dict[str, Any]:
    """Return index counts, unresolved relation targets, and contradiction candidates."""
    return _with_index(lambda idx: idx.health())


@mcp.tool()
def knowledge_propose_patch(relative_path: str, patch: dict[str, Any]) -> dict[str, Any]:
    """Create a hash-bound frontmatter patch proposal without mutating the vault."""
    path = (VAULT_ROOT / relative_path).resolve()
    if VAULT_ROOT not in path.parents:
        raise ValueError("path escapes vault root")
    proposal = propose_frontmatter_patch(path, patch)
    proposal["path"] = str(path)
    proposal["validation"] = [i.__dict__ for i in validate_patch(proposal, VAULT_ROOT)]
    return proposal


@mcp.tool()
def knowledge_validate_patch(proposal_json: str) -> list[dict[str, Any]]:
    """Validate a previously generated patch proposal."""
    proposal = json.loads(proposal_json)
    return [i.__dict__ for i in validate_patch(proposal, VAULT_ROOT)]


@mcp.tool()
def knowledge_apply_patch(proposal_json: str) -> dict[str, Any]:
    """Apply a validated hash-bound patch atomically. Disabled by default unless read-only mode is explicitly off."""
    if READ_ONLY:
        raise PermissionError("knowledge runtime is read-only; set AGENTIC_VAULT_KNOWLEDGE_READ_ONLY=0 to enable writes")
    proposal = json.loads(proposal_json)
    path = Path(proposal["path"]).resolve()
    if VAULT_ROOT not in path.parents:
        raise ValueError("path escapes vault root")
    apply_patch(proposal, VAULT_ROOT)
    return {"applied": True, "path": str(path.relative_to(VAULT_ROOT))}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
