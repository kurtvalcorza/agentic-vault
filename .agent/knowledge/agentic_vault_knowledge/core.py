"""Deterministic knowledge runtime for agentic-vault.

Markdown/YAML is canonical. SQLite is a disposable projection.
"""
from __future__ import annotations

import contextlib
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import stat
import tempfile
from collections import deque
from pathlib import Path
from typing import Any, Iterator, Protocol

import yaml

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
BLOCK_RE = re.compile(r"(?m)^\^([A-Za-z0-9_-]+)\s*$")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*$")
SEMANTIC_TYPES = {
    "KnowledgeObject", "Entity", "Concept", "Project", "Person", "Organization",
    "Source", "Claim", "Event", "Decision", "Artifact",
}
DERIVATIONS = {"asserted", "extracted", "inferred", "ambiguous", "imported"}
STATUSES = {"candidate", "proposed", "accepted", "active", "superseded", "retracted", "retired", "archived", "merged"}


class KnowledgeError(Exception):
    pass


class ConflictError(KnowledgeError):
    pass


@dataclasses.dataclass(frozen=True)
class Evidence:
    source: str
    locator_type: str = "file"
    locator_value: str | None = None
    authority: str = "unknown"


@dataclasses.dataclass(frozen=True)
class Relation:
    predicate: str
    target: str
    derivation: str = "asserted"
    status: str = "accepted"
    evidence: tuple[Evidence, ...] = ()
    event_time: str | None = None
    transaction_time: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    recorded_at: str | None = None
    confidence: float | None = None
    extraction_confidence: float | None = None
    claim_confidence: float | None = None
    review_status: str | None = None
    created_by: str | None = None
    reviewed_by: tuple[str, ...] = ()


@dataclasses.dataclass(frozen=True)
class ParsedNote:
    path: Path
    content_hash: str
    frontmatter: dict[str, Any]
    body: str
    semantic: bool
    object_id: str | None
    object_type: str | None
    title: str
    aliases: tuple[str, ...]
    tags: tuple[str, ...]
    wikilinks: tuple[str, ...]
    headings: tuple[str, ...]
    blocks: tuple[str, ...]
    relations: tuple[Relation, ...]
    timeline: tuple[dict[str, Any], ...]


@dataclasses.dataclass(frozen=True)
class ValidationIssue:
    path: str
    code: str
    message: str
    severity: str = "error"


class SemanticEnricher(Protocol):
    """Optional adapter. Implementations return candidate records only."""

    def extract_candidates(self, note: ParsedNote) -> list[dict[str, Any]]: ...


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys instead of silently
    keeping the last occurrence (which would drop authored id/status/claims)."""


def _construct_mapping_no_dupes(loader: _UniqueKeyLoader, node: yaml.MappingNode) -> dict:
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in mapping:
            raise KnowledgeError(f"duplicate frontmatter key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=True)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping_no_dupes
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter while accepting LF, CRLF, or CR line endings."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return {}, normalized
    end = normalized.find("\n---\n", 4)
    if end >= 0:
        raw = normalized[4:end]
        body = normalized[end + 5 :]
    elif normalized.endswith("\n---"):
        # Closing delimiter at end of file with no trailing body newline.
        raw = normalized[4:-4]
        body = ""
    else:
        return {}, normalized
    data = yaml.load(raw, Loader=_UniqueKeyLoader) or {}
    if not isinstance(data, dict):
        raise KnowledgeError("YAML frontmatter must be a mapping")
    return data, body


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(str(v) for v in value if v is not None)
    return (str(value),)


def _parse_evidence(raw: Any) -> tuple[Evidence, ...]:
    if raw is None:
        return ()
    values = raw if isinstance(raw, list) else [raw]
    out: list[Evidence] = []
    for item in values:
        if isinstance(item, str):
            out.append(Evidence(source=item))
        elif isinstance(item, dict) and item.get("source"):
            locator = item.get("locator") if isinstance(item.get("locator"), dict) else {}
            locator_value = item.get("locator_value")
            if locator_value is None:
                locator_value = locator.get("value")
            out.append(Evidence(
                source=str(item["source"]),
                locator_type=str(item.get("locator_type") or locator.get("type") or "file"),
                locator_value=str(locator_value) if locator_value is not None else None,
                authority=str(item.get("source_authority") or item.get("authority") or "unknown"),
            ))
    return tuple(out)


def _parse_relations(value: Any) -> tuple[Relation, ...]:
    if not value:
        return ()
    if not isinstance(value, list):
        raise KnowledgeError("relations must be a list")
    out: list[Relation] = []
    for raw in value:
        if not isinstance(raw, dict) or not raw.get("predicate") or not raw.get("target"):
            raise KnowledgeError("each relation requires predicate and target")
        confidence = raw.get("confidence")
        if confidence is not None:
            confidence = float(confidence)

        def _opt(key: str) -> str | None:
            value = raw.get(key)
            return str(value) if value is not None else None

        def _optfloat(key: str) -> float | None:
            value = raw.get(key)
            return float(value) if value is not None else None

        reviewed_by = raw.get("reviewed_by") or []
        if isinstance(reviewed_by, str):
            reviewed_by = [reviewed_by]

        out.append(Relation(
            predicate=str(raw["predicate"]),
            target=str(raw["target"]),
            derivation=str(raw.get("derivation") or "asserted"),
            status=str(raw.get("status") or "accepted"),
            evidence=_parse_evidence(raw.get("evidence")),
            event_time=_opt("event_time"),
            transaction_time=_opt("transaction_time"),
            valid_from=_opt("valid_from"),
            valid_to=_opt("valid_to"),
            recorded_at=_opt("recorded_at"),
            confidence=confidence,
            extraction_confidence=_optfloat("extraction_confidence"),
            claim_confidence=_optfloat("claim_confidence"),
            review_status=_opt("review_status"),
            created_by=_opt("created_by"),
            reviewed_by=tuple(str(x) for x in reviewed_by),
        ))
    return tuple(out)


def parse_note(path: Path, vault_root: Path | None = None) -> ParsedNote:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    object_id = str(fm["id"]) if fm.get("id") else None
    object_type = str(fm["type"]) if fm.get("type") else None
    semantic = bool(object_id and object_type)
    title = str(
        fm.get("title")
        or next((m.group(2) for m in HEADING_RE.finditer(body) if len(m.group(1)) == 1), path.stem)
    )
    tags = _as_str_tuple(fm.get("tags"))
    aliases = _as_str_tuple(fm.get("aliases"))
    timeline = tuple(fm.get("timeline") or ()) if isinstance(fm.get("timeline") or [], list) else ()
    return ParsedNote(
        path=path if vault_root is None else path.relative_to(vault_root),
        content_hash=sha256_text(text),
        frontmatter=fm,
        body=body,
        semantic=semantic,
        object_id=object_id,
        object_type=object_type,
        title=title,
        aliases=aliases,
        tags=tags,
        wikilinks=tuple(dict.fromkeys(m.group(1).strip() for m in WIKILINK_RE.finditer(text))),
        headings=tuple(m.group(2).strip() for m in HEADING_RE.finditer(body)),
        blocks=tuple(m.group(1) for m in BLOCK_RE.finditer(body)),
        relations=_parse_relations(fm.get("relations")),
        timeline=timeline,
    )


def _has_knowledge_ignore(path: Path, vault_root: Path) -> bool:
    current = path.parent
    root = vault_root.resolve()
    while current == root or root in current.parents:
        if (current / ".knowledge-ignore").exists():
            return True
        if current == root:
            break
        current = current.parent
    return False


def iter_markdown(vault_root: Path) -> Iterator[Path]:
    # Only exclude names that are never canonical vault content. Generic names
    # like "generated"/"export" are NOT excluded globally — a real PARA folder
    # may legitimately use them; the runtime's own generated tree is excluded by
    # exact path, and OKF bundles carry a `.knowledge-ignore` marker instead.
    excluded = {".git", ".venv", "node_modules", "__pycache__"}
    runtime_generated = Path(".agent") / "knowledge" / "generated"
    root = vault_root.resolve()
    for path in root.rglob("*.md"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        # A symlink whose target escapes the vault must not be read as canonical:
        # rglob yields the link and lexical relative_to succeeds, so verify the
        # resolved target still lives under the resolved root.
        resolved = path.resolve()
        if resolved != root and root not in resolved.parents:
            continue
        if any(part in excluded for part in rel.parts):
            continue
        if runtime_generated == rel or runtime_generated in rel.parents:
            continue
        if _has_knowledge_ignore(path, root):
            continue
        yield path


def load_relation_registry(schema_root: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load((schema_root / "relations.yaml").read_text(encoding="utf-8")) or {}
    return dict(data.get("relations") or {})


def _valid_date(value: Any) -> bool:
    if value is None:
        return True
    try:
        dt.date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def validate_note(note: ParsedNote, relation_registry: dict[str, Any] | None = None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    p = str(note.path)
    if not note.semantic:
        return issues
    if not re.match(r"^[a-z][a-z0-9_-]*:[^\s:][^\s]*$", note.object_id or ""):
        issues.append(ValidationIssue(p, "invalid-id", "id must use a stable namespace:value form"))
    if note.object_type not in SEMANTIC_TYPES:
        if not re.match(r"^[A-Z][A-Za-z0-9_.-]*$", note.object_type or ""):
            issues.append(ValidationIssue(p, "invalid-type", "type must be a core or extension class name"))
    for rel in note.relations:
        if relation_registry is not None and rel.predicate not in relation_registry:
            issues.append(ValidationIssue(p, "unknown-relation", f"unknown relation predicate: {rel.predicate}"))
        if rel.derivation not in DERIVATIONS:
            issues.append(ValidationIssue(p, "invalid-derivation", f"invalid derivation: {rel.derivation}"))
        if rel.status not in STATUSES:
            issues.append(ValidationIssue(p, "invalid-status", f"invalid relation status: {rel.status}"))
        if rel.confidence is not None and not 0 <= rel.confidence <= 1:
            issues.append(ValidationIssue(p, "invalid-confidence", "confidence must be between 0 and 1"))
        if not _valid_date(rel.event_time) or not _valid_date(rel.transaction_time):
            issues.append(ValidationIssue(p, "invalid-relation-time", "relation dates must be ISO YYYY-MM-DD"))
    raw_timeline = note.frontmatter.get("timeline")
    if raw_timeline is not None and not isinstance(raw_timeline, list):
        # A single mapping (or scalar) is silently dropped during parsing; surface
        # it here so malformed canonical timeline data cannot masquerade as valid.
        issues.append(ValidationIssue(p, "invalid-timeline", "timeline must be a list of entries"))
    for i, item in enumerate(note.timeline):
        if not isinstance(item, dict):
            issues.append(ValidationIssue(p, "invalid-timeline", f"timeline[{i}] must be a mapping"))
            continue
        for key in ("event_time", "transaction_time", "claim", "source"):
            if not item.get(key):
                issues.append(ValidationIssue(p, "invalid-timeline", f"timeline[{i}] missing {key}"))
        if not _valid_date(item.get("event_time")) or not _valid_date(item.get("transaction_time")):
            issues.append(ValidationIssue(p, "invalid-timeline-time", f"timeline[{i}] dates must be ISO YYYY-MM-DD"))
    return issues


SCHEMA_SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, content_hash TEXT NOT NULL, indexed_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS objects(id TEXT PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL, path TEXT NOT NULL UNIQUE, status TEXT, body TEXT NOT NULL, frontmatter_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS aliases(alias_norm TEXT NOT NULL, object_id TEXT NOT NULL, alias TEXT NOT NULL, PRIMARY KEY(alias_norm, object_id), FOREIGN KEY(object_id) REFERENCES objects(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS navigation(source_path TEXT NOT NULL, target_ref TEXT NOT NULL, PRIMARY KEY(source_path,target_ref));
CREATE TABLE IF NOT EXISTS relations(id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, predicate TEXT NOT NULL, target_id TEXT NOT NULL, derivation TEXT NOT NULL, status TEXT NOT NULL, event_time TEXT, transaction_time TEXT, valid_from TEXT, valid_to TEXT, recorded_at TEXT, confidence REAL, extraction_confidence REAL, claim_confidence REAL, review_status TEXT, created_by TEXT, reviewed_by_json TEXT, path TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence(relation_id INTEGER NOT NULL, source TEXT NOT NULL, locator_type TEXT NOT NULL, locator_value TEXT, authority TEXT NOT NULL, FOREIGN KEY(relation_id) REFERENCES relations(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS timeline(object_id TEXT NOT NULL, ordinal INTEGER NOT NULL, event_time TEXT NOT NULL, transaction_time TEXT NOT NULL, claim TEXT NOT NULL, source TEXT NOT NULL, PRIMARY KEY(object_id,ordinal), FOREIGN KEY(object_id) REFERENCES objects(id) ON DELETE CASCADE);
CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(id UNINDEXED, title, body, aliases, tags, content='');
CREATE INDEX IF NOT EXISTS relations_source ON relations(source_id);
CREATE INDEX IF NOT EXISTS relations_target ON relations(target_id);
CREATE INDEX IF NOT EXISTS relations_predicate ON relations(predicate);
"""


class KnowledgeIndex:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # check_same_thread=False: under the MCP runtime synchronous tools run in
        # AnyIO worker threads, so the cached connection may be touched by a
        # different thread than the one that opened it. All access is serialized
        # by the caller's lock, so relaxing the same-thread guard is safe.
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_SQL)

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "KnowledgeIndex":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _remove_path(self, path: str) -> None:
        row = self.conn.execute("SELECT id FROM objects WHERE path=?", (path,)).fetchone()
        if row:
            oid = row["id"]
            self.conn.execute("DELETE FROM relations WHERE source_id=? OR path=?", (oid, path))
            self.conn.execute("DELETE FROM objects_fts WHERE id=?", (oid,))
            self.conn.execute("DELETE FROM objects WHERE id=?", (oid,))
        self.conn.execute("DELETE FROM navigation WHERE source_path=?", (path,))
        self.conn.execute("DELETE FROM files WHERE path=?", (path,))

    def upsert(self, note: ParsedNote) -> None:
        path = str(note.path).replace("\\", "/")
        if note.semantic and note.object_id:
            prior = self.conn.execute("SELECT path FROM objects WHERE id=?", (note.object_id,)).fetchone()
            if prior and prior["path"] != path:
                self._remove_path(prior["path"])
        self._remove_path(path)
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        self.conn.execute("INSERT INTO files(path,content_hash,indexed_at) VALUES(?,?,?)", (path, note.content_hash, now))
        self.conn.executemany(
            "INSERT OR IGNORE INTO navigation(source_path,target_ref) VALUES(?,?)",
            [(path, x) for x in note.wikilinks],
        )
        if note.semantic:
            status = str(note.frontmatter.get("status") or "accepted")
            self.conn.execute(
                "INSERT INTO objects(id,type,title,path,status,body,frontmatter_json) VALUES(?,?,?,?,?,?,?)",
                (note.object_id, note.object_type, note.title, path, status, note.body,
                 json.dumps(note.frontmatter, default=str, sort_keys=True)),
            )
            for alias in (note.title, *note.aliases):
                self.conn.execute(
                    "INSERT OR IGNORE INTO aliases(alias_norm,object_id,alias) VALUES(?,?,?)",
                    (_norm(alias), note.object_id, alias),
                )
            self.conn.execute(
                "INSERT INTO objects_fts(id,title,body,aliases,tags) VALUES(?,?,?,?,?)",
                (note.object_id, note.title, note.body, " ".join(note.aliases), " ".join(note.tags)),
            )
            for rel in note.relations:
                cur = self.conn.execute(
                    "INSERT INTO relations(source_id,predicate,target_id,derivation,status,event_time,transaction_time,valid_from,valid_to,recorded_at,confidence,extraction_confidence,claim_confidence,review_status,created_by,reviewed_by_json,path) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (note.object_id, rel.predicate, rel.target, rel.derivation, rel.status,
                     rel.event_time, rel.transaction_time, rel.valid_from, rel.valid_to, rel.recorded_at, rel.confidence,
                     rel.extraction_confidence, rel.claim_confidence, rel.review_status, rel.created_by,
                     json.dumps(list(rel.reviewed_by)), path),
                )
                rid = int(cur.lastrowid)
                self.conn.executemany(
                    "INSERT INTO evidence(relation_id,source,locator_type,locator_value,authority) VALUES(?,?,?,?,?)",
                    [(rid, e.source, e.locator_type, e.locator_value, e.authority) for e in rel.evidence],
                )
            for i, item in enumerate(note.timeline):
                if isinstance(item, dict) and all(item.get(k) for k in ("event_time", "transaction_time", "claim", "source")):
                    self.conn.execute(
                        "INSERT INTO timeline(object_id,ordinal,event_time,transaction_time,claim,source) VALUES(?,?,?,?,?,?)",
                        (note.object_id, i, str(item["event_time"]), str(item["transaction_time"]),
                         str(item["claim"]), str(item["source"])),
                    )
        self.conn.commit()

    def build(self, vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
        registry = load_relation_registry(schema_root)
        issues: list[ValidationIssue] = []
        seen_paths: set[str] = set()
        seen_ids: dict[str, str] = {}
        for path in iter_markdown(vault_root):
            try:
                note = parse_note(path, vault_root)
            except Exception as exc:
                issues.append(ValidationIssue(str(path.relative_to(vault_root)), "parse-error", str(exc)))
                continue
            p = str(note.path).replace("\\", "/")
            seen_paths.add(p)
            issues.extend(validate_note(note, registry))
            if note.semantic and note.object_id:
                if note.object_id in seen_ids and seen_ids[note.object_id] != p:
                    issues.append(ValidationIssue(p, "duplicate-id", f"{note.object_id} also used by {seen_ids[note.object_id]}"))
                seen_ids[note.object_id] = p
            row = self.conn.execute("SELECT content_hash FROM files WHERE path=?", (p,)).fetchone()
            if not row or row["content_hash"] != note.content_hash:
                try:
                    self.upsert(note)
                except sqlite3.IntegrityError as exc:
                    issues.append(ValidationIssue(p, "index-integrity", str(exc)))
        stale = [r["path"] for r in self.conn.execute("SELECT path FROM files") if r["path"] not in seen_paths]
        for p in stale:
            self._remove_path(p)
        self.conn.commit()
        return issues

    def rebuild(self, vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
        self.close()
        with contextlib.suppress(FileNotFoundError):
            self.db_path.unlink()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_SQL)
        return self.build(vault_root, schema_root)

    def get(self, object_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM objects WHERE id=?", (object_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["aliases"] = [r["alias"] for r in self.conn.execute("SELECT alias FROM aliases WHERE object_id=?", (object_id,))]
        result["relations"] = [dict(r) for r in self.conn.execute("SELECT * FROM relations WHERE source_id=?", (object_id,))]
        return result

    def resolve(self, ref: str) -> list[dict[str, Any]]:
        direct = self.get(ref)
        if direct:
            return [{"id": ref, "title": direct["title"], "match": "id", "score": 1.0}]
        needle = _norm(ref)
        if not needle:
            return []
        rows = self.conn.execute(
            "SELECT o.id,o.title,a.alias FROM aliases a JOIN objects o ON o.id=a.object_id WHERE a.alias_norm=?",
            (needle,),
        ).fetchall()
        if rows:
            return [{"id": r["id"], "title": r["title"], "match": "alias", "score": 1.0} for r in rows]
        candidates = []
        for r in self.conn.execute("SELECT id,title FROM objects"):
            normalized_title = _norm(r["title"])
            if normalized_title and (needle in normalized_title or normalized_title in needle):
                candidates.append({"id": r["id"], "title": r["title"], "match": "normalized", "score": 0.7})
        return candidates

    def search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        try:
            rows = self.conn.execute(
                "SELECT id,title,snippet(objects_fts,2,'[',']',' … ',12) AS snippet FROM objects_fts WHERE objects_fts MATCH ? ORDER BY rank LIMIT ?",
                (query, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            q = f"%{query.lower()}%"
            rows = self.conn.execute(
                "SELECT id,title,substr(body,1,240) AS snippet FROM objects WHERE lower(title) LIKE ? OR lower(body) LIKE ? LIMIT ?",
                (q, q, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def neighbors(self, object_id: str, predicate: str | None = None, include_derived: bool = False) -> list[dict[str, Any]]:
        # status='accepted' is unconditional (retracted/candidate edges are never
        # current neighbors); include_derived toggles only the inferred filter.
        sql = "SELECT * FROM relations WHERE status='accepted' AND (source_id=? OR target_id=?)"
        args: list[Any] = [object_id, object_id]
        if predicate:
            sql += " AND predicate=?"
            args.append(predicate)
        if not include_derived:
            sql += " AND derivation!='inferred'"
        return [dict(r) for r in self.conn.execute(sql, args)]

    def trace(self, start: str, end: str, max_depth: int = 6, include_derived: bool = False) -> list[str]:
        if start == end:
            return [start]
        derived_clause = "" if include_derived else " AND derivation!='inferred'"
        q = deque([(start, [start])])
        seen = {start}
        while q:
            node, path = q.popleft()
            # path holds nodes; edges == len(path) - 1. Stop expanding once the
            # next edge would exceed max_depth so returned paths never carry more
            # than the requested number of edges.
            if len(path) > max_depth:
                continue
            rows = self.conn.execute(
                "SELECT source_id,target_id FROM relations WHERE status='accepted'" + derived_clause + " AND (source_id=? OR target_id=?)",
                (node, node),
            )
            for r in rows:
                nxt = r["target_id"] if r["source_id"] == node else r["source_id"]
                if nxt == end:
                    return path + [nxt]
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [nxt]))
        return []

    def timeline(self, object_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM timeline WHERE object_id=? ORDER BY event_time,transaction_time,ordinal", (object_id,)
        )]

    def sources(self, object_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(
            "SELECT r.source_id,r.predicate,r.target_id,e.source,e.locator_type,e.locator_value,e.authority "
            "FROM relations r JOIN evidence e ON e.relation_id=r.id WHERE r.source_id=? OR r.target_id=?",
            (object_id, object_id),
        )]

    def contradiction_candidates(self) -> list[dict[str, Any]]:
        # Two accepted relations on the same subject/predicate with different
        # targets contradict only when their validity intervals overlap, matching
        # the claim contradiction logic. Missing bounds are treated as open.
        rows = self.conn.execute(
            "SELECT a.source_id,a.predicate,a.target_id AS left_target,b.target_id AS right_target,"
            "a.id AS left_id,b.id AS right_id,"
            "a.valid_from AS left_valid_from,a.valid_to AS left_valid_to,"
            "b.valid_from AS right_valid_from,b.valid_to AS right_valid_to "
            "FROM relations a JOIN relations b "
            "ON a.source_id=b.source_id AND a.predicate=b.predicate AND a.id<b.id "
            "WHERE a.status='accepted' AND b.status='accepted' AND a.target_id<>b.target_id "
            "AND a.path NOT LIKE '__claim__:%' AND b.path NOT LIKE '__claim__:%' "
            "AND COALESCE(a.valid_from,'0001-01-01') <= COALESCE(b.valid_to,'9999-12-31') "
            "AND COALESCE(b.valid_from,'0001-01-01') <= COALESCE(a.valid_to,'9999-12-31')"
        )
        return [dict(r) for r in rows]

    def health(self) -> dict[str, Any]:
        def count(table: str) -> int:
            return self.conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        unresolved = []
        ids = {r[0] for r in self.conn.execute("SELECT id FROM objects")}
        for r in self.conn.execute("SELECT id,source_id,predicate,target_id FROM relations"):
            if r["target_id"] not in ids:
                unresolved.append(dict(r))
        return {
            "files": count("files"),
            "objects": count("objects"),
            "relations": count("relations"),
            "navigation_edges": count("navigation"),
            "timeline_entries": count("timeline"),
            "unresolved_relation_targets": unresolved,
            "contradiction_candidates": self.contradiction_candidates(),
        }


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def vault_roots(vault_root: Path) -> tuple[Path, Path, Path]:
    knowledge = vault_root / ".agent" / "knowledge"
    return knowledge, knowledge / "schema", knowledge / "generated" / "knowledge.db"


def validate_vault(vault_root: Path) -> list[ValidationIssue]:
    _, schema, _ = vault_roots(vault_root)
    registry = load_relation_registry(schema)
    issues: list[ValidationIssue] = []
    ids: dict[str, str] = {}
    for path in iter_markdown(vault_root):
        try:
            note = parse_note(path, vault_root)
        except Exception as exc:
            issues.append(ValidationIssue(str(path.relative_to(vault_root)), "parse-error", str(exc)))
            continue
        issues.extend(validate_note(note, registry))
        if note.semantic and note.object_id:
            if note.object_id in ids:
                issues.append(ValidationIssue(str(note.path), "duplicate-id", f"also used by {ids[note.object_id]}"))
            ids[note.object_id] = str(note.path)
    return issues


def _resolve_vault_path(raw_path: str | Path, vault_root: Path) -> Path:
    root = vault_root.resolve()
    path = Path(raw_path)
    path = path.resolve() if path.is_absolute() else (root / path).resolve()
    if path == root or root not in path.parents:
        raise KnowledgeError(f"path escapes vault root: {path}")
    return path


# Directories the mutation API must never write into: version control, per-agent
# configuration workspaces, and scan-excluded / generated locations. Canonical
# knowledge lives in Markdown notes, never in these.
# Directory names that are never canonical vault content. "generated"/"export"
# are intentionally NOT here: a real PARA folder may use those names and
# iter_markdown scans them; the runtime's own tree lives under .agent, and
# export bundles are excluded via .knowledge-ignore markers instead.
PROTECTED_TARGET_DIRNAMES = {
    ".agent", ".git", ".claude", ".gemini", ".kiro", ".codex", ".obsidian",
    ".venv", "node_modules", "__pycache__",
}


def _reject_unwritable_target(path: Path, vault_root: Path) -> None:
    """Restrict the write API to canonical Markdown outside protected workspaces."""
    if path.suffix.lower() != ".md":
        raise KnowledgeError(f"patch target must be a Markdown file: {path}")
    rel = path.resolve().relative_to(vault_root.resolve())
    if any(part in PROTECTED_TARGET_DIRNAMES for part in rel.parts):
        raise KnowledgeError(f"patch target is inside a protected workspace: {path}")
    if _has_knowledge_ignore(path, vault_root):
        raise KnowledgeError(f"patch target is inside a scan-excluded (.knowledge-ignore) tree: {path}")


def propose_frontmatter_patch(path: Path, patch: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    before_hash = sha256_text(text)
    fm, body = split_frontmatter(text)
    candidate = dict(fm)
    candidate.update(patch)
    rendered = "---\n" + yaml.safe_dump(candidate, sort_keys=False, allow_unicode=True).rstrip() + "\n---\n" + body
    return {"path": str(path), "base_hash": before_hash, "frontmatter": candidate, "content": rendered}


def _parse_candidate_note(content: str) -> ParsedNote:
    with tempfile.TemporaryDirectory() as tmp:
        candidate = Path(tmp) / "candidate.md"
        candidate.write_text(content, encoding="utf-8")
        return parse_note(candidate)


# Operations exempt from the stable-ID comparison (they legitimately change the
# id). The semantic-demotion check still applies to them: an existing semantic
# note must never silently lose its frontmatter, whatever the operation.
ID_CHANGE_EXEMPT_OPERATIONS = {"migrate", "merge"}


def _identity_guard_issues(proposal: dict[str, Any], path: Path) -> list[ValidationIssue]:
    """Reject silent semantic demotion or stable-ID changes on ordinary patches."""
    operation = str(proposal.get("operation") or "update")
    # A create targets a non-existent file, so there is nothing to demote.
    if operation == "create" or not path.exists():
        return []
    try:
        current = parse_note(path)
    except Exception:
        return []
    if not (current.semantic and current.object_id):
        return []
    try:
        candidate = _parse_candidate_note(str(proposal["content"]))
    except Exception:
        return []
    p = str(path)
    if not (candidate.semantic and candidate.object_id):
        return [ValidationIssue(
            p, "semantic-demotion",
            "patch would strip id/type from a semantic object; frontmatter must be retained",
        )]
    if operation not in ID_CHANGE_EXEMPT_OPERATIONS and candidate.object_id != current.object_id:
        return [ValidationIssue(
            p, "identity-change",
            f"patch changes stable id {current.object_id} -> {candidate.object_id}; "
            "require an explicit migration or merge operation",
        )]
    return []


def validate_patch(proposal: dict[str, Any], vault_root: Path) -> list[ValidationIssue]:
    """Validate a candidate in the complete vault context and extension schema."""
    path = _resolve_vault_path(proposal["path"], vault_root)
    _reject_unwritable_target(path, vault_root)
    from .validation import validate_candidate_semantics
    issues = list(validate_candidate_semantics(str(proposal["content"]), path, vault_root))
    issues.extend(_identity_guard_issues(proposal, path))
    return issues


def _is_create(proposal: dict[str, Any]) -> bool:
    return str(proposal.get("operation") or "update") == "create" or proposal.get("base_hash") is None


def apply_patch(proposal: dict[str, Any], vault_root: Path) -> None:
    path = _resolve_vault_path(proposal["path"], vault_root)
    _reject_unwritable_target(path, vault_root)
    creating = _is_create(proposal)
    if creating:
        if path.exists():
            raise ConflictError(f"create target already exists: {path}")
    else:
        if not path.exists():
            raise KnowledgeError(f"source file does not exist: {path}")
        current = path.read_text(encoding="utf-8")
        if sha256_text(current) != proposal["base_hash"]:
            raise ConflictError(f"source changed since proposal: {path}")
    issues = validate_patch(proposal, vault_root)
    if any(i.severity == "error" for i in issues):
        raise KnowledgeError("candidate patch failed validation: " + "; ".join(i.message for i in issues))
    # Re-check the source state after validation (which scans the whole vault and
    # can race a concurrent edit) to keep the optimistic-concurrency guarantee.
    if creating:
        if path.exists():
            raise ConflictError(f"create target appeared during validation: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not path.exists():
            raise ConflictError(f"source removed during validation: {path}")
        if sha256_text(path.read_text(encoding="utf-8")) != proposal["base_hash"]:
            raise ConflictError(f"source changed during validation: {path}")
    _atomic_write_preserving_mode(path, str(proposal["content"]), creating)


def _default_file_mode() -> int:
    current = os.umask(0)
    os.umask(current)
    return 0o666 & ~current


def _atomic_write_preserving_mode(path: Path, content: str, creating: bool) -> None:
    """Atomically write `content` to `path`, preserving the existing file's
    permissions on update (mkstemp defaults to 0600, which would otherwise make
    a normal 0644 note unreadable to other users)."""
    mode = None
    if not creating and path.exists():
        mode = stat.S_IMODE(path.stat().st_mode)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, mode if mode is not None else _default_file_mode())
        os.replace(tmp, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)


def export_okf_like(index: KnowledgeIndex, output: Path) -> None:
    """Conservative OKF-oriented JSON export scaffold; not full OKF conformance."""
    objects = []
    for row in index.conn.execute("SELECT id,type,title,path,status,frontmatter_json FROM objects ORDER BY id"):
        item = dict(row)
        item["frontmatter"] = json.loads(item.pop("frontmatter_json"))
        item["relations"] = index.get(item["id"])["relations"]
        objects.append(item)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"format": "agentic-vault-okf-projection", "version": "0.1.0", "objects": objects},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
