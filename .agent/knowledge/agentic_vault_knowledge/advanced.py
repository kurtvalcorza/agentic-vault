from __future__ import annotations

import datetime as dt
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import yaml

from .core import KnowledgeIndex, ValidationIssue, load_relation_registry

EXTENDED_SQL = """
CREATE TABLE IF NOT EXISTS claims(
  id TEXT PRIMARY KEY,
  subject_id TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_value TEXT NOT NULL,
  derivation TEXT NOT NULL,
  status TEXT NOT NULL,
  valid_from TEXT,
  valid_to TEXT,
  recorded_at TEXT,
  extraction_confidence REAL,
  claim_confidence REAL,
  review_status TEXT,
  created_by TEXT,
  reviewed_by_json TEXT NOT NULL DEFAULT '[]',
  path TEXT NOT NULL,
  ordinal INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS claim_evidence(
  claim_id TEXT NOT NULL,
  source TEXT NOT NULL,
  locator_type TEXT NOT NULL,
  locator_value TEXT,
  source_authority TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS claims_subject ON claims(subject_id);
CREATE INDEX IF NOT EXISTS claims_predicate ON claims(predicate);
CREATE INDEX IF NOT EXISTS claims_object ON claims(object_value);
CREATE INDEX IF NOT EXISTS claims_status ON claims(status);
"""


def load_relation_registry_with_extensions(schema_root: Path) -> dict[str, dict[str, Any]]:
    registry = load_relation_registry(schema_root)
    ext = schema_root / "extensions"
    if ext.exists():
        for path in sorted(ext.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for name, spec in (data.get("relations") or {}).items():
                if name in registry:
                    raise ValueError(f"extension relation shadows core relation: {name}")
                registry[str(name)] = dict(spec or {})
    return registry


def _interval_overlaps(a_from: str | None, a_to: str | None, b_from: str | None, b_to: str | None) -> bool:
    low_a = a_from or "0001-01-01"
    low_b = b_from or "0001-01-01"
    high_a = a_to or "9999-12-31"
    high_b = b_to or "9999-12-31"
    return low_a <= high_b and low_b <= high_a


def _instant(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


class ExtendedKnowledgeIndex(KnowledgeIndex):
    """First-class claims, extension relations, temporal reasoning, and graph analytics."""

    def __init__(self, db_path: Path, initialize_extended: bool = True):
        super().__init__(db_path)
        if initialize_extended:
            self.conn.executescript(EXTENDED_SQL)

    def build(self, vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
        """Validate once, then incrementally project only a valid vault state."""
        from .validation import scan_vault_semantics

        issues, notes = scan_vault_semantics(vault_root, schema_root)
        if any(i.severity == "error" for i in issues):
            return issues

        seen_paths: set[str] = set()
        changed = False
        for note in notes:
            p = str(note.path).replace("\\", "/")
            seen_paths.add(p)
            row = self.conn.execute("SELECT content_hash FROM files WHERE path=?", (p,)).fetchone()
            if not row or row["content_hash"] != note.content_hash:
                self.upsert(note)
                changed = True

        stale = [r["path"] for r in self.conn.execute("SELECT path FROM files") if r["path"] not in seen_paths]
        for path in stale:
            self._remove_path(path)
            changed = True
        self.conn.commit()

        if changed:
            self._project_claims()
            self._repoint_merged_relations()
        return issues

    def _repoint_merged_relations(self) -> None:
        """Repoint relation endpoints that reference a merged object to its
        canonical redirect target, so neighbors()/trace()/analytics keep the edge
        attached to the surviving node instead of the obsolete id."""
        redirects: dict[str, str] = {}
        for row in self.conn.execute("SELECT id,frontmatter_json FROM objects WHERE status='merged'"):
            target = json.loads(row["frontmatter_json"]).get("redirect_to")
            if target:
                redirects[row["id"]] = str(target)
        if not redirects:
            return

        def _final(oid: str) -> str:
            seen: set[str] = set()
            while oid in redirects and oid not in seen:
                seen.add(oid)
                oid = redirects[oid]
            return oid

        for old in redirects:
            dest = _final(old)
            if dest != old:
                self.conn.execute("UPDATE relations SET source_id=? WHERE source_id=?", (dest, old))
                self.conn.execute("UPDATE relations SET target_id=? WHERE target_id=?", (dest, old))
        self.conn.commit()

    def _project_claims(self) -> None:
        self.conn.execute("DELETE FROM claim_evidence")
        self.conn.execute("DELETE FROM claims")
        self.conn.execute("DELETE FROM relations WHERE path LIKE '__claim__:%'")
        object_ids = {r[0] for r in self.conn.execute("SELECT id FROM objects")}
        rows = list(self.conn.execute("SELECT id,path,frontmatter_json FROM objects"))
        for row in rows:
            fm = json.loads(row["frontmatter_json"])
            raw_claims = fm.get("claims") or []
            if not isinstance(raw_claims, list):
                continue
            for ordinal, claim in enumerate(raw_claims):
                if not isinstance(claim, dict):
                    continue
                subject = str(claim.get("subject") or row["id"])
                predicate = claim.get("predicate")
                obj = claim.get("object")
                if not predicate or obj is None:
                    continue
                claim_id = str(claim.get("id") or f"claim:{row['id']}:{ordinal}")
                derivation = str(claim.get("derivation") or "asserted")
                status = str(claim.get("status") or "accepted")
                valid_from = claim.get("valid_from") or claim.get("event_time")
                valid_to = claim.get("valid_to")
                recorded_at = claim.get("recorded_at") or claim.get("transaction_time")
                reviewed_by = claim.get("reviewed_by") or []
                if isinstance(reviewed_by, str):
                    reviewed_by = [reviewed_by]
                self.conn.execute(
                    "INSERT INTO claims(id,subject_id,predicate,object_value,derivation,status,valid_from,valid_to,recorded_at,extraction_confidence,claim_confidence,review_status,created_by,reviewed_by_json,path,ordinal) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        claim_id, subject, str(predicate), str(obj), derivation, status, valid_from, valid_to,
                        recorded_at, claim.get("extraction_confidence"), claim.get("claim_confidence", claim.get("confidence")),
                        claim.get("review_status"), claim.get("created_by"), json.dumps(reviewed_by), row["path"], ordinal,
                    ),
                )
                evidence_rows: list[tuple[str, str, str, str | None, str]] = []
                ev = claim.get("evidence") or []
                if not isinstance(ev, list):
                    ev = [ev]
                for item in ev:
                    if isinstance(item, str):
                        evidence_rows.append((claim_id, item, "file", None, "unknown"))
                    elif isinstance(item, dict) and item.get("source"):
                        loc = item.get("locator") if isinstance(item.get("locator"), dict) else {}
                        locator_value = item.get("locator_value")
                        if locator_value is None:
                            locator_value = loc.get("value")
                        evidence_rows.append((
                            claim_id,
                            str(item["source"]),
                            str(item.get("locator_type") or loc.get("type") or "file"),
                            str(locator_value) if locator_value is not None else None,
                            str(item.get("source_authority") or item.get("authority") or "unknown"),
                        ))
                self.conn.executemany(
                    "INSERT INTO claim_evidence(claim_id,source,locator_type,locator_value,source_authority) VALUES(?,?,?,?,?)",
                    evidence_rows,
                )

                if status == "accepted" and subject in object_ids and str(obj) in object_ids:
                    cur = self.conn.execute(
                        "INSERT INTO relations(source_id,predicate,target_id,derivation,status,event_time,transaction_time,valid_from,valid_to,recorded_at,confidence,extraction_confidence,claim_confidence,review_status,created_by,reviewed_by_json,path) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            subject, str(predicate), str(obj), derivation, status, valid_from, recorded_at,
                            valid_from, valid_to, recorded_at,
                            claim.get("claim_confidence", claim.get("confidence")),
                            claim.get("extraction_confidence"),
                            claim.get("claim_confidence", claim.get("confidence")),
                            claim.get("review_status"), claim.get("created_by"), json.dumps(reviewed_by),
                            f"__claim__:{row['path']}:{claim_id}",
                        ),
                    )
                    rid = int(cur.lastrowid)
                    self.conn.executemany(
                        "INSERT INTO evidence(relation_id,source,locator_type,locator_value,authority) VALUES(?,?,?,?,?)",
                        [(rid, source, locator_type, locator_value, authority)
                         for _, source, locator_type, locator_value, authority in evidence_rows],
                    )
        self.conn.commit()

    def resolve(self, ref: str) -> list[dict[str, Any]]:
        result = super().resolve(ref)
        if len(result) == 1 and result[0].get("match") == "id":
            row = self.conn.execute("SELECT status,frontmatter_json FROM objects WHERE id=?", (result[0]["id"],)).fetchone()
            if row and row["status"] == "merged":
                fm = json.loads(row["frontmatter_json"])
                target = fm.get("redirect_to")
                if target:
                    resolved = super().resolve(str(target))
                    if resolved:
                        resolved[0] = {**resolved[0], "match": "redirect", "redirected_from": result[0]["id"]}
                        return resolved
        return result

    def claims(self, object_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM claims WHERE 1=1"
        args: list[Any] = []
        if object_id is not None:
            sql += " AND (subject_id=? OR object_value=?)"
            args += [object_id, object_id]
        if status is not None:
            sql += " AND status=?"
            args.append(status)
        return [dict(r) for r in self.conn.execute(sql, args)]

    def claim_sources(self, claim_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM claim_evidence WHERE claim_id=?", (claim_id,))]

    def query(self, object_type: str | None = None, predicate: str | None = None, target: str | None = None, status: str = "accepted", limit: int = 100) -> list[dict[str, Any]]:
        sql = "SELECT r.*,o.type AS source_type,o.title AS source_title FROM relations r JOIN objects o ON o.id=r.source_id WHERE 1=1"
        args: list[Any] = []
        if status:
            sql += " AND r.status=?"
            args.append(status)
        if object_type:
            sql += " AND o.type=?"
            args.append(object_type)
        if predicate:
            sql += " AND r.predicate=?"
            args.append(predicate)
        if target:
            sql += " AND r.target_id=?"
            args.append(target)
        sql += " LIMIT ?"
        args.append(limit)
        return [dict(r) for r in self.conn.execute(sql, args)]

    def contradiction_candidates(self) -> list[dict[str, Any]]:
        rows = list(self.conn.execute("SELECT * FROM claims WHERE status='accepted' ORDER BY subject_id,predicate,id"))
        out: list[dict[str, Any]] = []
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                # Rows are ordered by (subject_id, predicate, id); once either
                # differs the group is over, so break instead of scanning the
                # rest (keeps contradiction detection linear per group).
                if a["subject_id"] != b["subject_id"] or a["predicate"] != b["predicate"]:
                    break
                if a["object_value"] == b["object_value"]:
                    continue
                if _interval_overlaps(a["valid_from"], a["valid_to"], b["valid_from"], b["valid_to"]):
                    out.append({
                        "subject_id": a["subject_id"], "predicate": a["predicate"],
                        "left_claim": a["id"], "left_object": a["object_value"],
                        "right_claim": b["id"], "right_object": b["object_value"],
                        "left_valid_from": a["valid_from"], "left_valid_to": a["valid_to"],
                        "right_valid_from": b["valid_from"], "right_valid_to": b["valid_to"],
                    })
        out.extend(super().contradiction_candidates())
        return out

    def state_as_of(self, object_id: str, as_of: str) -> dict[str, Any]:
        as_of_instant = _instant(as_of)
        as_of_date = as_of_instant.date().isoformat()
        claims: list[dict[str, Any]] = []
        for row in self.conn.execute("SELECT * FROM claims WHERE subject_id=?", (object_id,)):
            valid = (
                (row["valid_from"] is None or row["valid_from"] <= as_of_date)
                and (row["valid_to"] is None or row["valid_to"] >= as_of_date)
            )
            recorded = row["recorded_at"] is None or _instant(str(row["recorded_at"])) <= as_of_instant
            if valid and recorded:
                claims.append(dict(row))
        timeline = [
            item for item in self.timeline(object_id)
            if item["event_time"] <= as_of_date and item["transaction_time"] <= as_of_date
        ]
        return {"object_id": object_id, "as_of": as_of, "claims": claims, "timeline": timeline}

    def impact(self, object_id: str, max_depth: int = 3, include_derived: bool = False) -> list[dict[str, Any]]:
        derived_clause = "" if include_derived else " AND derivation!='inferred'"
        queue = deque([(object_id, 0)])
        seen = {object_id}
        out = []
        while queue:
            node, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for row in self.conn.execute(
                "SELECT * FROM relations WHERE status='accepted'" + derived_clause + " AND (source_id=? OR target_id=?)", (node, node)
            ):
                if row["predicate"] not in {"depends_on", "dependency_of", "part_of", "has_part"}:
                    continue
                nxt = row["target_id"] if row["source_id"] == node else row["source_id"]
                if nxt in seen:
                    continue
                seen.add(nxt)
                out.append({"id": nxt, "depth": depth + 1, "via": row["predicate"]})
                queue.append((nxt, depth + 1))
        return out

    def communities(self) -> list[dict[str, Any]]:
        adj: dict[str, set[str]] = defaultdict(set)
        for row in self.conn.execute("SELECT source_id,target_id FROM relations WHERE status='accepted' AND derivation!='inferred'"):
            adj[row["source_id"]].add(row["target_id"])
            adj[row["target_id"]].add(row["source_id"])
        for row in self.conn.execute("SELECT id FROM objects"):
            adj.setdefault(row["id"], set())
        seen = set()
        groups = []
        for node in sorted(adj):
            if node in seen:
                continue
            stack = [node]
            seen.add(node)
            members = []
            while stack:
                current = stack.pop()
                members.append(current)
                for nxt in sorted(adj[current]):
                    if nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)
            groups.append({"community": len(groups) + 1, "size": len(members), "members": sorted(members)})
        return sorted(groups, key=lambda item: (-item["size"], item["community"]))

    def central_objects(self, limit: int = 20) -> list[dict[str, Any]]:
        degree = Counter()
        for row in self.conn.execute("SELECT source_id,target_id FROM relations WHERE status='accepted' AND derivation!='inferred'"):
            degree[row["source_id"]] += 1
            degree[row["target_id"]] += 1
        return [{"id": oid, "degree": value} for oid, value in degree.most_common(limit)]

    def health(self) -> dict[str, Any]:
        out = super().health()
        out["claims"] = self.conn.execute("SELECT count(*) FROM claims").fetchone()[0]
        out["candidate_claims"] = self.conn.execute("SELECT count(*) FROM claims WHERE status IN ('candidate','proposed')").fetchone()[0]
        out["accepted_claims"] = self.conn.execute("SELECT count(*) FROM claims WHERE status='accepted'").fetchone()[0]
        out["communities"] = len(self.communities())
        out["contradiction_candidates"] = self.contradiction_candidates()
        return out
