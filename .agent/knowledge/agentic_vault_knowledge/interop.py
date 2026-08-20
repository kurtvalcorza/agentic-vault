from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from .core import iter_markdown, parse_note, split_frontmatter

RESERVED = {"index.md", "log.md"}


def _safe_rel(path: Path) -> Path:
    parts = [p for p in path.parts if p not in {".agent", ".git"}]
    return Path(*parts)


def export_okf_bundle(vault_root: Path, output_dir: Path) -> dict[str, Any]:
    """Export semantic notes as an OKF v0.2-compatible Markdown bundle.

    The export is a projection. It never changes canonical vault files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[str] = []
    for path in iter_markdown(vault_root):
        note = parse_note(path, vault_root)
        if not note.semantic:
            continue
        rel = _safe_rel(note.path)
        if rel.name.lower() in RESERVED:
            rel = rel.with_name(rel.stem + "-concept.md")
        target = output_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        fm = dict(note.frontmatter)
        # OKF requires only type and tolerates producer-specific fields. Preserve
        # unknown metadata; stable agentic-vault id remains an extension field.
        fm["type"] = note.object_type
        fm.setdefault("title", note.title)
        text = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip() + "\n---\n" + note.body
        target.write_text(text, encoding="utf-8")
        exported.append(str(rel).replace("\\", "/"))
    root_index = output_dir / "index.md"
    index_fm = {"okf_version": "0.2", "type": "Index", "title": "agentic-vault knowledge export"}
    body = "# Knowledge Bundle\n\nGenerated from semantic knowledge objects. Canonical state remains in the source vault.\n\n" + "\n".join(f"- [{p}]({p})" for p in sorted(exported)) + "\n"
    root_index.write_text("---\n" + yaml.safe_dump(index_fm, sort_keys=False).rstrip() + "\n---\n" + body, encoding="utf-8")
    return {"okf_version": "0.2", "concepts": len(exported), "output": str(output_dir)}


def validate_okf_bundle(bundle_root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for path in bundle_root.rglob("*.md"):
        rel = path.relative_to(bundle_root)
        if path.name.lower() in RESERVED:
            if path.name.lower() == "index.md" and rel == Path("index.md"):
                fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
                if fm.get("okf_version") not in {None, "0.2"}:
                    issues.append({"path": str(rel), "code": "unsupported-okf-version", "message": str(fm.get("okf_version"))})
            continue
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        if not fm:
            issues.append({"path": str(rel), "code": "missing-frontmatter", "message": "OKF concept requires YAML frontmatter"})
        elif not str(fm.get("type") or "").strip():
            issues.append({"path": str(rel), "code": "missing-type", "message": "OKF concept requires non-empty type"})
    return issues


def import_okf_candidates(bundle_root: Path) -> list[dict[str, Any]]:
    """Read an OKF bundle into non-mutating candidate records.

    Import deliberately does not write Markdown because concept IDs in OKF are
    path-based while agentic-vault stable IDs are independent of paths. Entity
    resolution/promotion must happen through the normal proposal workflow.
    """
    issues = validate_okf_bundle(bundle_root)
    if issues:
        raise ValueError(f"invalid OKF bundle: {json.dumps(issues)}")
    out: list[dict[str, Any]] = []
    for path in bundle_root.rglob("*.md"):
        if path.name.lower() in RESERVED:
            continue
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
        out.append({
            "concept_id": str(path.relative_to(bundle_root).with_suffix("")).replace("\\", "/"),
            "frontmatter": fm,
            "body": body,
            "status": "candidate",
            "derivation": "imported",
        })
    return out


def export_jsonld(index, output: Path) -> dict[str, Any]:
    graph=[]
    for row in index.conn.execute("SELECT id,type,title,status FROM objects ORDER BY id"):
        node={"@id":row["id"],"@type":row["type"],"name":row["title"],"status":row["status"]}
        rels=[]
        for r in index.conn.execute("SELECT predicate,target_id,status,derivation FROM relations WHERE source_id=?",(row["id"],)):
            rels.append({"predicate":r["predicate"],"target":{"@id":r["target_id"]},"status":r["status"],"derivation":r["derivation"]})
        if rels: node["relations"]=rels
        graph.append(node)
    data={"@context":{"name":"https://schema.org/name","status":"https://schema.org/status"},"@graph":graph}
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    return {"objects":len(graph),"output":str(output)}
