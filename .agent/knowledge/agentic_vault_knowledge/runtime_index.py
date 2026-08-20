from __future__ import annotations

import contextlib
import json
import sqlite3
from pathlib import Path

from .advanced import EXTENDED_SQL, ExtendedKnowledgeIndex
from .core import KnowledgeIndex, SCHEMA_SQL, ValidationIssue

NORMAL_FTS_SQL = "CREATE VIRTUAL TABLE objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags)"
EXPECTED_CLAIM_COLUMNS = {
    "id", "subject_id", "predicate", "object_value", "derivation", "status",
    "valid_from", "valid_to", "recorded_at", "extraction_confidence",
    "claim_confidence", "review_status", "created_by", "reviewed_by_json",
    "path", "ordinal",
}


class RuntimeIndex(ExtendedKnowledgeIndex):
    """Production index wrapper with storage migrations and correct full rebuild semantics."""

    def __init__(self, db_path: Path):
        super().__init__(db_path)
        self._ensure_mutable_fts()
        self._ensure_extended_schema()
        self.conn.executescript(EXTENDED_SQL)

    def _ensure_mutable_fts(self) -> None:
        row = self.conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='objects_fts'").fetchone()
        sql = row[0] if row else ""
        if "content=''" not in sql.replace(" ", ""):
            return
        # One-time migration from the early contentless projection. Mark every
        # file dirty so the ordinary incremental build repopulates search rows.
        self.conn.execute("DROP TABLE objects_fts")
        self.conn.execute(NORMAL_FTS_SQL)
        self.conn.execute("DELETE FROM files")
        self.conn.commit()

    def _ensure_extended_schema(self) -> None:
        """Recreate incompatible *derived* claim tables in place.

        The runtime database is disposable, so a schema mismatch is repaired by
        dropping only derived claim projections and their generated relation
        edges. Canonical Markdown is never migrated through this path.
        """
        exists = self.conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='claims'").fetchone()
        if not exists:
            return
        columns = {r["name"] for r in self.conn.execute("PRAGMA table_info(claims)")}
        if columns == EXPECTED_CLAIM_COLUMNS:
            return
        self.conn.execute("DELETE FROM relations WHERE path LIKE '__claim__:%'")
        self.conn.execute("DROP TABLE IF EXISTS claim_evidence")
        self.conn.execute("DROP TABLE IF EXISTS claims")
        self.conn.commit()

    def resolve(self, ref: str) -> list[dict]:
        """Resolve IDs/aliases and follow explicit merge redirects safely."""
        results = KnowledgeIndex.resolve(self, ref)
        if len(results) != 1:
            return results
        current = results[0]
        seen: set[str] = set()
        while current.get("id") and current["id"] not in seen:
            seen.add(current["id"])
            row = self.conn.execute("SELECT status,frontmatter_json FROM objects WHERE id=?", (current["id"],)).fetchone()
            if not row or row["status"] != "merged":
                return current if isinstance(current, list) else [current]
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
        """Delete every derived byte, recreate all runtime schemas, and rebuild from Markdown."""
        db_path = self.db_path
        self.close()
        with contextlib.suppress(FileNotFoundError):
            db_path.unlink()
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        # Use mutable FTS on fresh databases rather than the legacy contentless definition.
        base = SCHEMA_SQL.replace(
            "CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags, content='');",
            "CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags);",
        )
        self.conn.executescript(base)
        self.conn.executescript(EXTENDED_SQL)
        return self.build(vault_root, schema_root)
