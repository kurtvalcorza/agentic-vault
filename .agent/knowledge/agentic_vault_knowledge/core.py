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
DERIVATIONS = {"asserted", "extracted", "inferred", "ambiguous"}
STATUSES = {"candidate", "proposed", "accepted", "active", "superseded", "retracted", "retired", "archived"}


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
    confidence: float | None = None


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter while accepting LF, CRLF, or CR line endings."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return {}, normalized
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return {}, normalized
    raw = normalized[4:end]
    body = normalized[end + 5 :]
    data = yaml.safe_load(raw) or {}
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
        out.append(Relation(
            predicate=str(raw["predicate"]),
            target=str(raw["target"]),
            derivation=str(raw.get("derivation") or "asserted"),
            status=str(raw.get("status") or "accepted"),
            evidence=_parse_evidence(raw.get("evidence")),
            event_time=str(raw["event_time"]) if raw.get("event_time") is not None else None,
            transaction_time=str(raw["transaction_time"]) if raw.get("transaction_time") is not None else None,
            confidence=confidence,
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
    excluded = {".git", ".venv", "node_modules", "generated", "export", "__pycache__"}
    root = vault_root.resolve()
    for path in root.rglob("*.md"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(part in excluded for part in rel.parts):
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
CREATE TABLE IF NOT EXISTS relations(id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, predicate TEXT NOT NULL, target_id TEXT NOT NULL, derivation TEXT NOT NULL, status TEXT NOT NULL, event_time TEXT, transaction_time TEXT, confidence REAL, path TEXT NOT NULL);
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
        self.conn = sqlite3.connect(db_path)
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
                    "INSERT INTO relations(source_id,predicate,target_id,derivation,status,event_time,transaction_time,confidence,path) VALUES(?,?,?,?,?,?,?,?,?)",
                    (note.object_id, rel.predicate, rel.target, rel.derivation, rel.status,
                     rel.event_time, rel.transaction_time, rel.confidence, path),
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
        self.conn = sqlite3.connect(self.db_path)
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
                "SELECT id,title,snippet(objects_fts,2,'[',']',' … ',12) AS snippet FROM objects_fts WHERE objects_fts MATCH ? LIMIT ?",
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
        sql = "SELECT * FROM relations WHERE (source_id=? OR target_id=?)"
        args: list[Any] = [object_id, object_id]
        if predicate:
            sql += " AND predicate=?"
            args.append(predicate)
        if not include_derived:
            sql += " AND status='accepted' AND derivation!='inferred'"
        return [dict(r) for r in self.conn.execute(sql, args)]

    def trace(self, start: str, end: str, max_depth: int = 6) -> list[str]:
        if start == end:
            return [start]
        q = deque([(start, [start])])
        seen = {start}
        while q:
            node, path = q.popleft()
            if len(path) > max_depth + 1:
                continue
            rows = self.conn.execute(
                "SELECT source_id,target_id FROM relations WHERE status='accepted' AND (source_id=? OR target_id=?)",
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
        rows = self.conn.execute(
            "SELECT a.source_id,a.predicate,a.target_id AS left_target,b.target_id AS right_target,"
            "a.event_time,a.id AS left_id,b.id AS right_id FROM relations a JOIN relations b "
            "ON a.source_id=b.source_id AND a.predicate=b.predicate AND a.id<b.id "
            "WHERE a.status='accepted' AND b.status='accepted' AND a.target_id<>b.target_id "
            "AND COALESCE(a.event_time,'')=COALESCE(b.event_time,'')"
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


def propose_frontmatter_patch(path: Path, patch: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    before_hash = sha256_text(text)
    fm, body = split_frontmatter(text)
    candidate = dict(fm)
    candidate.update(patch)
    rendered = "---\n" + yaml.safe_dump(candidate, sort_keys=False, allow_unicode=True).rstrip() + "\n---\n" + body
    return {"path": str(path), "base_hash": before_hash, "frontmatter": candidate, "content": rendered}


def validate_patch(proposal: dict[str, Any], vault_root: Path) -> list[ValidationIssue]:
    """Validate a candidate in the complete vault context and extension schema."""
    path = _resolve_vault_path(proposal["path"], vault_root)
    from .validation import validate_candidate_semantics
    return validate_candidate_semantics(str(proposal["content"]), path, vault_root)


def apply_patch(proposal: dict[str, Any], vault_root: Path) -> None:
    path = _resolve_vault_path(proposal["path"], vault_root)
    if not path.exists():
        raise KnowledgeError(f"source file does not exist: {path}")
    current = path.read_text(encoding="utf-8")
    if sha256_text(current) != proposal["base_hash"]:
        raise ConflictError(f"source changed since proposal: {path}")
    issues = validate_patch(proposal, vault_root)
    if any(i.severity == "error" for i in issues):
        raise KnowledgeError("candidate patch failed validation: " + "; ".join(i.message for i in issues))
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(str(proposal["content"]))
            fh.flush()
            os.fsync(fh.fileno())
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
