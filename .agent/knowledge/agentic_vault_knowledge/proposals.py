from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .core import KnowledgeError, propose_frontmatter_patch, sha256_text, split_frontmatter


def _safe_target(vault_root: Path, relative_path: str) -> Path:
    path = (vault_root / relative_path).resolve()
    if path == vault_root or vault_root not in path.parents:
        raise KnowledgeError("path escapes vault root")
    if path.suffix.lower() != ".md":
        raise KnowledgeError("semantic proposals must target Markdown files")
    return path


def propose_entity(vault_root: Path, relative_path: str, frontmatter: dict[str, Any], body: str = "") -> dict[str, Any]:
    """Propose creation of a new semantic Markdown object without writing it."""
    path = _safe_target(vault_root, relative_path)
    if path.exists():
        raise KnowledgeError(f"target already exists: {relative_path}")
    fm = dict(frontmatter)
    if not fm.get("id") or not fm.get("type") or not fm.get("title"):
        raise KnowledgeError("new semantic entity requires id, type, and title")
    rendered = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip() + "\n---\n"
    if body:
        rendered += body if body.startswith("\n") else "\n" + body
    return {"operation": "create", "path": str(path), "base_hash": None, "frontmatter": fm, "content": rendered}


def _read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if not fm:
        raise KnowledgeError(f"semantic proposal target has no frontmatter: {path}")
    return fm, body


def propose_relation(vault_root: Path, relative_path: str, relation: dict[str, Any]) -> dict[str, Any]:
    path = _safe_target(vault_root, relative_path)
    fm, _ = _read_frontmatter(path)
    relations = list(fm.get("relations") or [])
    candidate = dict(relation)
    # A proposal constructor never silently promotes machine/user-supplied input
    # into the accepted assertion graph (mirrors propose_claim()).
    candidate.setdefault("status", "proposed")
    relations.append(candidate)
    proposal = propose_frontmatter_patch(path, {"relations": relations})
    proposal["operation"] = "update"
    return proposal


def propose_claim(vault_root: Path, relative_path: str, claim: dict[str, Any]) -> dict[str, Any]:
    path = _safe_target(vault_root, relative_path)
    fm, _ = _read_frontmatter(path)
    claims = list(fm.get("claims") or [])
    candidate = dict(claim)
    # A proposal constructor never silently promotes machine/user-supplied input.
    candidate.setdefault("status", "proposed")
    claims.append(candidate)
    proposal = propose_frontmatter_patch(path, {"claims": claims})
    proposal["operation"] = "update"
    return proposal
