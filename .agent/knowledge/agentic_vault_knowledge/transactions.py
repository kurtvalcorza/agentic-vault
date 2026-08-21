from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path
from typing import Any

from .core import (
    ConflictError,
    KnowledgeError,
    _identity_guard_issues,
    _is_create,
    _reject_unwritable_target,
    _resolve_vault_path,
    parse_note,
    sha256_text,
)
from .validation import validate_batch_semantics


def _candidate_identity(proposal: dict[str, Any]) -> tuple[str | None, set[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "candidate.md"
        path.write_text(str(proposal["content"]), encoding="utf-8")
        note = parse_note(path)
    claims: set[str] = set()
    if note.semantic and note.object_id:
        for ordinal, claim in enumerate(note.frontmatter.get("claims") or []):
            if isinstance(claim, dict):
                claims.add(str(claim.get("id") or f"claim:{note.object_id}:{ordinal}"))
    return note.object_id if note.semantic else None, claims


def validate_batch(proposals: list[dict[str, Any]], vault_root: Path) -> list[dict[str, Any]]:
    """Validate the combined final batch state plus per-file identity/concurrency.

    Each candidate is checked for path safety, semantic demotion / stable-ID
    change, existence, hash-bound concurrency, and cross-proposal identity
    collisions. The whole replacement set is then validated *simultaneously* so
    that a violation only visible when the proposals are combined (for example a
    relation whose range is broken by a type change in a sibling proposal) is
    caught before any file is written.
    """
    seen_paths: set[Path] = set()
    candidate_ids: dict[str, str] = {}
    candidate_claims: dict[str, str] = {}
    out: list[dict[str, Any]] = []
    replacements: list[tuple[Path, str]] = []

    for proposal in proposals:
        try:
            path = _resolve_vault_path(proposal["path"], vault_root)
        except KnowledgeError as exc:
            out.append({"path": str(proposal.get("path")), "code": "path-escape", "message": str(exc), "severity": "error"})
            continue
        if path in seen_paths:
            out.append({"path": str(path), "code": "duplicate-path", "message": "batch contains multiple writes to same path", "severity": "error"})
            continue
        seen_paths.add(path)

        try:
            _reject_unwritable_target(path, vault_root)
        except KnowledgeError as exc:
            out.append({"path": str(path), "code": "unwritable-target", "message": str(exc), "severity": "error"})
            continue

        out.extend(item.__dict__ for item in _identity_guard_issues(proposal, path))

        creating = _is_create(proposal)
        if creating:
            if path.exists():
                out.append({"path": str(path), "code": "target-exists", "message": "create target already exists", "severity": "error"})
                continue
        else:
            if not path.exists():
                out.append({"path": str(path), "code": "missing-source", "message": "source file does not exist", "severity": "error"})
                continue
            if sha256_text(path.read_text(encoding="utf-8")) != proposal.get("base_hash"):
                out.append({"path": str(path), "code": "conflict", "message": "source changed since proposal", "severity": "error"})

        try:
            object_id, claim_ids = _candidate_identity(proposal)
        except Exception as exc:
            out.append({"path": str(path), "code": "parse-error", "message": str(exc), "severity": "error"})
            continue
        if object_id:
            if object_id in candidate_ids:
                out.append({
                    "path": str(path), "code": "duplicate-id",
                    "message": f"candidate object id {object_id} also proposed by {candidate_ids[object_id]}",
                    "severity": "error",
                })
            else:
                candidate_ids[object_id] = str(path)
        for claim_id in claim_ids:
            if claim_id in candidate_claims:
                out.append({
                    "path": str(path), "code": "duplicate-claim-id",
                    "message": f"candidate claim id {claim_id} also proposed by {candidate_claims[claim_id]}",
                    "severity": "error",
                })
            else:
                candidate_claims[claim_id] = str(path)
        replacements.append((path, str(proposal["content"])))

    out.extend(item.__dict__ for item in validate_batch_semantics(replacements, vault_root))
    return out


def apply_batch(proposals: list[dict[str, Any]], vault_root: Path) -> list[str]:
    """Apply a validated multi-file batch with rollback on replacement failure."""
    issues = validate_batch(proposals, vault_root)
    errors = [item for item in issues if item.get("severity", "error") == "error"]
    if errors:
        if any(item["code"] == "conflict" for item in errors):
            raise ConflictError("batch has concurrent modification conflicts")
        raise KnowledgeError("batch validation failed: " + "; ".join(item["message"] for item in errors))

    staged: dict[Path, Path] = {}
    backups: dict[Path, bytes] = {}
    created: set[Path] = set()
    replaced: list[Path] = []
    try:
        for proposal in proposals:
            path = _resolve_vault_path(proposal["path"], vault_root)
            if _is_create(proposal):
                path.parent.mkdir(parents=True, exist_ok=True)
                created.add(path)
            else:
                backups[path] = path.read_bytes()
            fd, tmp = tempfile.mkstemp(prefix=path.name + ".knowledge-stage.", dir=str(path.parent))
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                handle.write(str(proposal["content"]))
                handle.flush()
                os.fsync(handle.fileno())
            staged[path] = Path(tmp)
        # Post-validation, pre-commit recheck: validate_batch scanned the whole
        # vault, which can race a concurrent edit or a newly-created target. Verify
        # every source hash and every create-target absence again immediately
        # before the first replacement; abort the whole batch on any mismatch so no
        # proposal is applied over content the caller never saw.
        for proposal in proposals:
            path = _resolve_vault_path(proposal["path"], vault_root)
            if _is_create(proposal):
                if path.exists():
                    raise ConflictError(f"create target appeared during validation: {path}")
            elif not path.exists():
                raise ConflictError(f"source removed during validation: {path}")
            elif sha256_text(path.read_text(encoding="utf-8")) != proposal.get("base_hash"):
                raise ConflictError(f"source changed during validation: {path}")
        for path, tmp in staged.items():
            os.replace(tmp, path)
            replaced.append(path)
        return [str(path.relative_to(vault_root.resolve())) for path in replaced]
    except Exception:
        for path in reversed(replaced):
            with contextlib.suppress(Exception):
                if path in created:
                    path.unlink()
                    continue
                fd, tmp = tempfile.mkstemp(prefix=path.name + ".knowledge-rollback.", dir=str(path.parent))
                with os.fdopen(fd, "wb") as handle:
                    handle.write(backups[path])
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(tmp, path)
        raise
    finally:
        for tmp in staged.values():
            with contextlib.suppress(FileNotFoundError):
                tmp.unlink()
