from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

from .core import iter_markdown, parse_note, split_frontmatter

RESERVED = {"index.md", "log.md"}
IGNORE_MARKER = ".knowledge-ignore"


def _safe_rel(path: Path) -> Path:
    parts = [p for p in path.parts if p not in {".agent", ".git"}]
    return Path(*parts)


def _is_within(path: Path, parent: Path) -> bool:
    path = path.resolve()
    parent = parent.resolve()
    return path == parent or parent in path.parents


def export_okf_bundle(vault_root: Path, output_dir: Path) -> dict[str, Any]:
    """Export semantic notes as an OKF v0.2-compatible Markdown bundle.

    Source paths are snapshotted before output creation. In-vault exports carry
    a `.knowledge-ignore` marker so future runtime scans never re-ingest the
    projection as canonical knowledge.
    """
    root = vault_root.resolve()
    destination = output_dir.resolve()

    # Snapshot canonical source paths before creating or replacing destination.
    source_paths = [
        path for path in iter_markdown(root)
        if not _is_within(path, destination)
    ]

    if destination.exists():
        marker = destination / IGNORE_MARKER
        if not marker.exists():
            raise ValueError(
                f"refusing to replace existing export directory without {IGNORE_MARKER}: {destination}"
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=destination.name + ".staging.", dir=str(destination.parent)))
    try:
        (staging / IGNORE_MARKER).write_text(
            "Generated knowledge projection. Excluded from canonical vault indexing.\n",
            encoding="utf-8",
        )
        exported: list[str] = []
        for path in source_paths:
            note = parse_note(path, root)
            if not note.semantic:
                continue
            rel = _safe_rel(note.path)
            if rel.name.lower() in RESERVED:
                rel = rel.with_name(rel.stem + "-concept.md")
            target = staging / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            fm = dict(note.frontmatter)
            fm["type"] = note.object_type
            fm.setdefault("title", note.title)
            text = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip() + "\n---\n" + note.body
            target.write_text(text, encoding="utf-8")
            exported.append(str(rel).replace("\\", "/"))

        root_index = staging / "index.md"
        index_fm = {"okf_version": "0.2", "type": "Index", "title": "agentic-vault knowledge export"}
        body = (
            "# Knowledge Bundle\n\n"
            "Generated from semantic knowledge objects. Canonical state remains in the source vault.\n\n"
            + "\n".join(f"- [{p}]({p})" for p in sorted(exported))
            + "\n"
        )
        root_index.write_text(
            "---\n" + yaml.safe_dump(index_fm, sort_keys=False).rstrip() + "\n---\n" + body,
            encoding="utf-8",
        )

        if destination.exists():
            shutil.rmtree(destination)
        os.replace(staging, destination)
        staging = None
        return {"okf_version": "0.2", "concepts": len(exported), "output": str(destination)}
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)


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
    graph = []
    for row in index.conn.execute("SELECT id,type,title,status FROM objects ORDER BY id"):
        node = {"@id": row["id"], "@type": row["type"], "name": row["title"], "status": row["status"]}
        rels = []
        for rel in index.conn.execute(
            "SELECT predicate,target_id,status,derivation FROM relations WHERE source_id=?", (row["id"],)
        ):
            rels.append({
                "predicate": rel["predicate"],
                "target": {"@id": rel["target_id"]},
                "status": rel["status"],
                "derivation": rel["derivation"],
            })
        if rels:
            node["relations"] = rels
        graph.append(node)
    data = {"@context": {"name": "https://schema.org/name", "status": "https://schema.org/status"}, "@graph": graph}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"objects": len(graph), "output": str(output)}


def _urn(kind: str, value: str) -> str:
    return f"<urn:agentic-vault:{kind}:{quote(value, safe='')}>"


def _literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def export_rdf_ntriples(index, output: Path) -> dict[str, Any]:
    rdf_type = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
    rdfs_label = "<http://www.w3.org/2000/01/rdf-schema#label>"
    av_status = _urn("property", "status")
    av_derivation = _urn("property", "derivation")
    lines: list[str] = []
    for row in index.conn.execute("SELECT id,type,title,status FROM objects ORDER BY id"):
        subject = _urn("object", row["id"])
        lines.append(f"{subject} {rdf_type} {_urn('class', row['type'])} .")
        lines.append(f"{subject} {rdfs_label} {_literal(row['title'])} .")
        lines.append(f"{subject} {av_status} {_literal(row['status'] or '')} .")
    for rel in index.conn.execute(
        "SELECT source_id,predicate,target_id,status,derivation FROM relations "
        "WHERE status='accepted' ORDER BY source_id,predicate,target_id"
    ):
        subject = _urn("object", rel["source_id"])
        predicate = _urn("relation", rel["predicate"])
        target = _urn("object", rel["target_id"])
        lines.append(f"{subject} {predicate} {target} .")
        edge = _urn("edge", f"{rel['source_id']}|{rel['predicate']}|{rel['target_id']}")
        lines.append(f"{edge} {av_derivation} {_literal(rel['derivation'])} .")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return {"triples": len(lines), "output": str(output), "format": "application/n-triples"}
