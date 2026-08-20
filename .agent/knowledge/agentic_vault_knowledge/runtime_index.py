from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path
from typing import Any

from .advanced import EXTENDED_SQL, ExtendedKnowledgeIndex
from .core import SCHEMA_SQL, ValidationIssue

NORMAL_FTS_SQL = "CREATE VIRTUAL TABLE objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags)"


class RuntimeIndex(ExtendedKnowledgeIndex):
    """Production index wrapper with storage migrations and correct full rebuild semantics."""

    def __init__(self, db_path: Path):
        super().__init__(db_path)
        self._ensure_mutable_fts()
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

    def rebuild(self, vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
        """Delete every derived byte, recreate all runtime schemas, and rebuild from Markdown."""
        db_path = self.db_path
        self.close()
        with contextlib.suppress(FileNotFoundError):
            db_path.unlink()
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        # Use mutable FTS on fresh databases rather than the legacy contentless definition.
        base = SCHEMA_SQL.replace("CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags, content='');", "CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags);")
        self.conn.executescript(base)
        self.conn.executescript(EXTENDED_SQL)
        return self.build(vault_root, schema_root)
