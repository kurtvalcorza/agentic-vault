from __future__ import annotations

import atexit
import json
import os
import threading
from pathlib import Path
from typing import Any, Callable, TypeVar

from mcp.server import MCPServer

from agentic_vault_knowledge.core import KnowledgeError, apply_patch, propose_frontmatter_patch, validate_patch, vault_roots
from agentic_vault_knowledge.retrieval import fused_search
from agentic_vault_knowledge.runtime_index import RuntimeIndex
from agentic_vault_knowledge.transactions import apply_batch, validate_batch
from agentic_vault_knowledge.validation import validate_vault_semantics

VAULT_ROOT = Path(os.environ.get("AGENTIC_VAULT_ROOT", ".")).resolve()
READ_ONLY = os.environ.get("AGENTIC_VAULT_KNOWLEDGE_READ_ONLY", "1").lower() not in {"0", "false", "no"}
_, SCHEMA_ROOT, DB_PATH = vault_roots(VAULT_ROOT)
mcp = MCPServer("agentic-vault-knowledge")
_INDEX: RuntimeIndex | None = None
_INDEX_LOCK = threading.RLock()
T = TypeVar("T")


def _index() -> RuntimeIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = RuntimeIndex(DB_PATH)
    return _INDEX


def _close_index() -> None:
    global _INDEX
    with _INDEX_LOCK:
        if _INDEX is not None:
            _INDEX.close()
            _INDEX = None


atexit.register(_close_index)


def _with_index(fn: Callable[[RuntimeIndex], T]) -> T:
    with _INDEX_LOCK:
        idx = _index()
        issues = idx.refresh(VAULT_ROOT, SCHEMA_ROOT)
        errors = [item for item in issues if item.severity == "error"]
        if errors:
            diagnostics = [item.__dict__ for item in errors]
            raise KnowledgeError(
                "knowledge index validation failed; refusing to serve queries: "
                + json.dumps(diagnostics, ensure_ascii=False)
            )
        return fn(idx)


def _safe_path(relative_path: str) -> Path:
    path = (VAULT_ROOT / relative_path).resolve()
    if path == VAULT_ROOT or VAULT_ROOT not in path.parents:
        raise ValueError("path escapes vault root")
    return path


@mcp.tool()
def knowledge_validate() -> list[dict[str, Any]]:
    """Validate semantic objects, extensions, claims, relations, redirects, provenance, and temporal fields."""
    return [item.__dict__ for item in validate_vault_semantics(VAULT_ROOT, SCHEMA_ROOT)]


@mcp.tool()
def knowledge_resolve_entity(ref: str) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.resolve(ref))


@mcp.tool()
def knowledge_search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.search(query, limit))


@mcp.tool()
def knowledge_retrieve(query: str, limit: int = 20, graph_expand: bool = True) -> list[dict[str, Any]]:
    """Fused lexical + graph retrieval with optional adapter-based semantic retrieval."""
    return _with_index(lambda idx: fused_search(idx, query, limit, graph_expand=graph_expand))


@mcp.tool()
def knowledge_get(object_id: str) -> dict[str, Any] | None:
    return _with_index(lambda idx: idx.get(object_id))


@mcp.tool()
def knowledge_neighbors(object_id: str, predicate: str | None = None, include_derived: bool = False) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.neighbors(object_id, predicate, include_derived))


@mcp.tool()
def knowledge_trace_path(start_id: str, end_id: str, max_depth: int = 6, include_derived: bool = False) -> list[str]:
    return _with_index(lambda idx: idx.trace(start_id, end_id, max_depth, include_derived))


@mcp.tool()
def knowledge_query(object_type: str | None = None, predicate: str | None = None, target: str | None = None, status: str = "accepted", limit: int = 100) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.query(object_type, predicate, target, status, limit))


@mcp.tool()
def knowledge_timeline(object_id: str) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.timeline(object_id))


@mcp.tool()
def knowledge_state_as_of(object_id: str, as_of: str) -> dict[str, Any]:
    return _with_index(lambda idx: idx.state_as_of(object_id, as_of))


@mcp.tool()
def knowledge_sources(object_id: str) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.sources(object_id))


@mcp.tool()
def knowledge_claims(object_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.claims(object_id, status))


@mcp.tool()
def knowledge_claim_sources(claim_id: str) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.claim_sources(claim_id))


@mcp.tool()
def knowledge_contradictions() -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.contradiction_candidates())


@mcp.tool()
def knowledge_communities() -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.communities())


@mcp.tool()
def knowledge_impact(object_id: str, max_depth: int = 3, include_derived: bool = False) -> list[dict[str, Any]]:
    return _with_index(lambda idx: idx.impact(object_id, max_depth, include_derived))


@mcp.tool()
def knowledge_health() -> dict[str, Any]:
    def report(idx: RuntimeIndex) -> dict[str, Any]:
        health = idx.health()
        health["read_only"] = READ_ONLY
        health["index_fresh"] = True
        return health
    return _with_index(report)


@mcp.tool()
def knowledge_propose_patch(relative_path: str, patch: dict[str, Any]) -> dict[str, Any]:
    """Create a hash-bound candidate patch without mutating canonical Markdown."""
    path = _safe_path(relative_path)
    proposal = propose_frontmatter_patch(path, patch)
    proposal["path"] = str(path)
    proposal["validation"] = [item.__dict__ for item in validate_patch(proposal, VAULT_ROOT)]
    return proposal


@mcp.tool()
def knowledge_validate_patch(proposal_json: str) -> list[dict[str, Any]]:
    return [item.__dict__ for item in validate_patch(json.loads(proposal_json), VAULT_ROOT)]


@mcp.tool()
def knowledge_validate_batch(proposals_json: str) -> list[dict[str, Any]]:
    return validate_batch(json.loads(proposals_json), VAULT_ROOT)


@mcp.tool()
def knowledge_apply_patch(proposal_json: str) -> dict[str, Any]:
    if READ_ONLY:
        raise PermissionError("knowledge runtime is read-only; set AGENTIC_VAULT_KNOWLEDGE_READ_ONLY=0 to enable writes")
    proposal = json.loads(proposal_json)
    apply_patch(proposal, VAULT_ROOT)
    path = Path(proposal["path"]).resolve()
    return {"applied": True, "path": str(path.relative_to(VAULT_ROOT))}


@mcp.tool()
def knowledge_apply_batch(proposals_json: str) -> dict[str, Any]:
    if READ_ONLY:
        raise PermissionError("knowledge runtime is read-only; set AGENTIC_VAULT_KNOWLEDGE_READ_ONLY=0 to enable writes")
    applied = apply_batch(json.loads(proposals_json), VAULT_ROOT)
    return {"applied": applied, "count": len(applied)}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
