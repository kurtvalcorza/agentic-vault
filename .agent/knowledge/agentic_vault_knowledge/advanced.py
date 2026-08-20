from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import yaml

from .core import KnowledgeIndex, ValidationIssue, load_relation_registry, parse_note, iter_markdown, validate_note

EXTENDED_SQL = """
CREATE TABLE IF NOT EXISTS claims(
  id TEXT PRIMARY KEY,
  subject_id TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_value TEXT NOT NULL,
  derivation TEXT NOT NULL,
  status TEXT NOT NULL,
  event_time TEXT,
  transaction_time TEXT,
  confidence REAL,
  path TEXT NOT NULL,
  ordinal INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS claim_evidence(
  claim_id TEXT NOT NULL,
  source TEXT NOT NULL,
  locator_type TEXT NOT NULL,
  locator_value TEXT,
  authority TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS claims_subject ON claims(subject_id);
CREATE INDEX IF NOT EXISTS claims_predicate ON claims(predicate);
CREATE INDEX IF NOT EXISTS claims_object ON claims(object_value);
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


class ExtendedKnowledgeIndex(KnowledgeIndex):
    """Adds first-class claim projection and higher-level graph analytics."""

    def __init__(self, db_path: Path):
        super().__init__(db_path)
        self.conn.executescript(EXTENDED_SQL)

    def build(self, vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
        issues = super().build(vault_root, schema_root)
        registry = load_relation_registry_with_extensions(schema_root)
        # Re-validate semantic notes against merged extension registry.
        issues = [i for i in issues if i.code != "unknown-relation"]
        for path in iter_markdown(vault_root):
            try:
                note = parse_note(path, vault_root)
            except Exception:
                continue
            issues.extend(i for i in validate_note(note, registry) if i.code == "unknown-relation")
        self._project_claims(vault_root)
        return issues

    def _project_claims(self, vault_root: Path) -> None:
        self.conn.execute("DELETE FROM claim_evidence")
        self.conn.execute("DELETE FROM claims")
        for row in self.conn.execute("SELECT id,path,frontmatter_json FROM objects"):
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
                self.conn.execute(
                    "INSERT OR REPLACE INTO claims(id,subject_id,predicate,object_value,derivation,status,event_time,transaction_time,confidence,path,ordinal) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (claim_id, subject, str(predicate), str(obj), str(claim.get("derivation") or "asserted"), str(claim.get("status") or "accepted"), claim.get("event_time"), claim.get("transaction_time"), claim.get("confidence"), row["path"], ordinal),
                )
                ev = claim.get("evidence") or []
                if not isinstance(ev, list): ev=[ev]
                for item in ev:
                    if isinstance(item, str):
                        self.conn.execute("INSERT INTO claim_evidence VALUES(?,?,?,?,?)",(claim_id,item,"file",None,"unknown"))
                    elif isinstance(item, dict) and item.get("source"):
                        loc=item.get("locator") if isinstance(item.get("locator"),dict) else {}
                        self.conn.execute("INSERT INTO claim_evidence VALUES(?,?,?,?,?)",(claim_id,str(item["source"]),str(item.get("locator_type") or loc.get("type") or "file"),str(item.get("locator_value") or loc.get("value")) if (item.get("locator_value") or loc.get("value")) is not None else None,str(item.get("authority") or "unknown")))
        self.conn.commit()

    def claims(self, object_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        sql="SELECT * FROM claims WHERE 1=1"; args=[]
        if object_id is not None: sql += " AND (subject_id=? OR object_value=?)"; args += [object_id,object_id]
        if status is not None: sql += " AND status=?"; args.append(status)
        return [dict(r) for r in self.conn.execute(sql,args)]

    def claim_sources(self, claim_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM claim_evidence WHERE claim_id=?",(claim_id,))]

    def query(self, object_type: str | None=None, predicate: str | None=None, target: str | None=None, status: str="accepted", limit: int=100) -> list[dict[str,Any]]:
        sql="SELECT r.*,o.type AS source_type,o.title AS source_title FROM relations r JOIN objects o ON o.id=r.source_id WHERE 1=1"; args=[]
        if status: sql += " AND r.status=?"; args.append(status)
        if object_type: sql += " AND o.type=?"; args.append(object_type)
        if predicate: sql += " AND r.predicate=?"; args.append(predicate)
        if target: sql += " AND r.target_id=?"; args.append(target)
        sql += " LIMIT ?"; args.append(limit)
        return [dict(r) for r in self.conn.execute(sql,args)]

    def impact(self, object_id: str, max_depth: int=3) -> list[dict[str,Any]]:
        """Return accepted downstream dependency impact using depends_on/dependency_of/part_of edges."""
        q=deque([(object_id,0)]); seen={object_id}; out=[]
        while q:
            node,depth=q.popleft()
            if depth>=max_depth: continue
            for r in self.conn.execute("SELECT * FROM relations WHERE status='accepted' AND (source_id=? OR target_id=?)",(node,node)):
                if r["predicate"] not in {"depends_on","dependency_of","part_of","has_part"}: continue
                nxt=r["target_id"] if r["source_id"]==node else r["source_id"]
                if nxt in seen: continue
                seen.add(nxt); out.append({"id":nxt,"depth":depth+1,"via":r["predicate"]}); q.append((nxt,depth+1))
        return out

    def communities(self) -> list[dict[str,Any]]:
        """Deterministic connected components over accepted semantic edges; no external graph dependency."""
        adj: dict[str,set[str]]=defaultdict(set)
        for r in self.conn.execute("SELECT source_id,target_id FROM relations WHERE status='accepted'"):
            adj[r["source_id"]].add(r["target_id"]); adj[r["target_id"]].add(r["source_id"])
        for r in self.conn.execute("SELECT id FROM objects"): adj.setdefault(r["id"],set())
        seen=set(); groups=[]
        for node in sorted(adj):
            if node in seen: continue
            q=[node]; seen.add(node); members=[]
            while q:
                cur=q.pop(); members.append(cur)
                for nxt in sorted(adj[cur]):
                    if nxt not in seen: seen.add(nxt); q.append(nxt)
            groups.append({"community":len(groups)+1,"size":len(members),"members":sorted(members)})
        return sorted(groups,key=lambda x:(-x["size"],x["community"]))

    def central_objects(self, limit: int=20) -> list[dict[str,Any]]:
        degree=Counter()
        for r in self.conn.execute("SELECT source_id,target_id FROM relations WHERE status='accepted'"):
            degree[r["source_id"]]+=1; degree[r["target_id"]]+=1
        return [{"id":oid,"degree":deg} for oid,deg in degree.most_common(limit)]

    def health(self) -> dict[str,Any]:
        out=super().health()
        out["claims"]=self.conn.execute("SELECT count(*) FROM claims").fetchone()[0]
        out["candidate_claims"]=self.conn.execute("SELECT count(*) FROM claims WHERE status IN ('candidate','proposed')").fetchone()[0]
        out["communities"]=len(self.communities())
        return out
