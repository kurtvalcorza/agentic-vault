from __future__ import annotations

import contextlib
import hashlib
import json
import sqlite3
from pathlib import Path

from .advanced import EXTENDED_SQL, ExtendedKnowledgeIndex
from .core import KnowledgeIndex, SCHEMA_SQL, ValidationIssue, iter_markdown

NORMAL_FTS_SQL = "CREATE VIRTUAL TABLE objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags)"
EXPECTED_CLAIM_COLUMNS = {
    "id", "subject_id", "predicate", "object_value", "derivation", "status",
    "valid_from", "valid_to", "recorded_at", "extraction_confidence",
    "claim_confidence", "review_status", "created_by", "reviewed_by_json",
    "path", "ordinal",
}


class RuntimeIndex(ExtendedKnowledgeIndex):
    """Production index wrapper with storage migrations and warm incremental refresh."""

    def __init__(self, db_path: Path):
        KnowledgeIndex.__init__(self, db_path)
        self._last_fingerprint: tuple | None = None
        self._ensure_mutable_fts()
        self._ensure_relations_schema()
        self._ensure_extended_schema()
        self.conn.executescript(EXTENDED_SQL)

    def _ensure_mutable_fts(self) -> None:
        row = self.conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='objects_fts'").fetchone()
        sql = row[0] if row else ""
        if "content=''" not in sql.replace(" ", ""):
            return
        self.conn.execute("DROP TABLE objects_fts")
        self.conn.execute(NORMAL_FTS_SQL)
        self.conn.execute("DELETE FROM files")
        self.conn.commit()

    def _ensure_relations_schema(self) -> None:
        columns = {r["name"] for r in self.conn.execute("PRAGMA table_info(relations)")}
        if {"valid_from", "valid_to", "recorded_at"} <= columns:
            return
        # An older disposable DB predates the canonical relation validity columns.
        # Relations are fully rebuildable from Markdown, so drop and recreate the
        # table (and its dependent evidence rows) and force a reprojection.
        self.conn.execute("DROP TABLE IF EXISTS evidence")
        self.conn.execute("DROP TABLE IF EXISTS relations")
        self.conn.executescript(SCHEMA_SQL)
        self.conn.execute("DELETE FROM files")
        self.conn.commit()

    def _ensure_extended_schema(self) -> None:
        exists = self.conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='claims'").fetchone()
        if not exists:
            # A pre-claims runtime may already have a populated file hash table.
            # Mark it dirty so the newly introduced claim projection is filled.
            self.conn.execute("DELETE FROM files")
            self.conn.commit()
            return
        columns = {r["name"] for r in self.conn.execute("PRAGMA table_info(claims)")}
        if columns == EXPECTED_CLAIM_COLUMNS:
            return
        self.conn.execute("DELETE FROM relations WHERE path LIKE '__claim__:%'")
        self.conn.execute("DROP TABLE IF EXISTS claim_evidence")
        self.conn.execute("DROP TABLE IF EXISTS claims")
        self.conn.execute("DELETE FROM files")
        self.conn.commit()

    def _fingerprint(self, vault_root: Path, schema_root: Path) -> tuple:
        # Include a content digest, not just (mtime, size): a sync tool or editor
        # can preserve mtime and byte length across a real edit, and a
        # metadata-only fingerprint would then skip the rebuild and serve stale
        # objects. The digest cannot stay equal when canonical bytes change.
        files = []
        for path in iter_markdown(vault_root):
            stat = path.stat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            files.append((str(path.relative_to(vault_root)).replace("\\", "/"), stat.st_mtime_ns, stat.st_size, digest))
        schema_files = []
        for path in sorted(schema_root.rglob("*.yaml")):
            stat = path.stat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            schema_files.append((str(path.relative_to(schema_root)), stat.st_mtime_ns, stat.st_size, digest))
        version = schema_root / "VERSION"
        if version.exists():
            stat = version.stat()
            digest = hashlib.sha256(version.read_bytes()).hexdigest()
            schema_files.append(("VERSION", stat.st_mtime_ns, stat.st_size, digest))
        return tuple(sorted(files)), tuple(schema_files)

    def refresh(self, vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
        fingerprint = self._fingerprint(vault_root, schema_root)
        if self._last_fingerprint == fingerprint:
            return []
        issues = self.build(vault_root, schema_root)
        if not any(i.severity == "error" for i in issues):
            self._last_fingerprint = fingerprint
        return issues

    def resolve(self, ref: str) -> list[dict]:
        results = KnowledgeIndex.resolve(self, ref)
        if len(results) != 1:
            return results
        current = results[0]
        seen: set[str] = set()
        while current.get("id") and current["id"] not in seen:
            seen.add(current["id"])
            row = self.conn.execute("SELECT status,frontmatter_json FROM objects WHERE id=?", (current["id"],)).fetchone()
            if not row or row["status"] != "merged":
                return [current]
            fm = json.loads(row["frontmatter_json"])
            target = fm.get("redirect_to")
            if not target:
                return [current]
            redirected = KnowledgeIndex.resolve(self, str(target))
            if len(redirected) != 1:
                return [{**current, "match": "redirect-unresolved", "redirect_to": target}]
            current = {**redirected[0], "match": "redirect", "redirected_from": results[0]["id"]}
        if current.get("id") in seen:
            return [{**current, "match": "redirect-cycle"}]
        return [current]

    def rebuild(self, vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
        db_path = self.db_path
        self.close()
        with contextlib.suppress(FileNotFoundError):
            db_path.unlink()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        base = SCHEMA_SQL.replace(
            "CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags, content='');",
            "CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags);",
        )
        self.conn.executescript(base)
        self.conn.executescript(EXTENDED_SQL)
        self._last_fingerprint = None
        issues = self.build(vault_root, schema_root)
        if not any(i.severity == "error" for i in issues):
            self._last_fingerprint = self._fingerprint(vault_root, schema_root)
        return issues
