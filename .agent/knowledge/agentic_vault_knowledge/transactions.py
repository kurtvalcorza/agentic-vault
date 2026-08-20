from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path
from typing import Any

from .core import ConflictError, KnowledgeError, sha256_text, validate_patch


def validate_batch(proposals: list[dict[str, Any]], vault_root: Path) -> list[dict[str, Any]]:
    """Validate every proposal and detect duplicate paths before any write."""
    seen: set[Path] = set()
    out: list[dict[str, Any]] = []
    for proposal in proposals:
        path = Path(proposal["path"]).resolve()
        if path == vault_root or vault_root not in path.parents:
            out.append({"path": str(path), "code": "path-escape", "message": "path escapes vault root", "severity": "error"}); continue
        if path in seen:
            out.append({"path": str(path), "code": "duplicate-path", "message": "batch contains multiple writes to same path", "severity": "error"}); continue
        seen.add(path)
        out.extend(i.__dict__ for i in validate_patch(proposal, vault_root))
        if not path.exists():
            out.append({"path": str(path), "code": "missing-source", "message": "source file does not exist", "severity": "error"}); continue
        if sha256_text(path.read_text(encoding="utf-8")) != proposal.get("base_hash"):
            out.append({"path": str(path), "code": "conflict", "message": "source changed since proposal", "severity": "error"})
    return out


def apply_batch(proposals: list[dict[str, Any]], vault_root: Path) -> list[str]:
    """Apply a validated multi-file batch with rollback on replacement failure.

    POSIX/Windows do not provide a single transaction across arbitrary files, so
    this implementation stages all candidate bytes first, snapshots originals,
    then replaces files. If a replacement fails, already-replaced files are
    restored from their backups before the error is re-raised.
    """
    issues = validate_batch(proposals, vault_root)
    errors = [x for x in issues if x.get("severity", "error") == "error"]
    if errors:
        if any(x["code"] == "conflict" for x in errors):
            raise ConflictError("batch has concurrent modification conflicts")
        raise KnowledgeError("batch validation failed: " + "; ".join(x["message"] for x in errors))

    staged: dict[Path, Path] = {}
    backups: dict[Path, bytes] = {}
    replaced: list[Path] = []
    try:
        for proposal in proposals:
            path = Path(proposal["path"]).resolve()
            backups[path] = path.read_bytes()
            fd, tmp = tempfile.mkstemp(prefix=path.name + ".knowledge-stage.", dir=str(path.parent))
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                fh.write(str(proposal["content"])); fh.flush(); os.fsync(fh.fileno())
            staged[path] = Path(tmp)
        for path, tmp in staged.items():
            os.replace(tmp, path); replaced.append(path)
        return [str(p.relative_to(vault_root)) for p in replaced]
    except Exception:
        for path in reversed(replaced):
            with contextlib.suppress(Exception):
                fd, tmp = tempfile.mkstemp(prefix=path.name + ".knowledge-rollback.", dir=str(path.parent))
                with os.fdopen(fd, "wb") as fh:
                    fh.write(backups[path]); fh.flush(); os.fsync(fh.fileno())
                os.replace(tmp, path)
        raise
    finally:
        for tmp in staged.values():
            with contextlib.suppress(FileNotFoundError): tmp.unlink()
