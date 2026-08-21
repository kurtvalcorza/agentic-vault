from __future__ import annotations

import dataclasses
import datetime as dt
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .advanced import load_relation_registry_with_extensions
from .core import (
    DERIVATIONS,
    SEMANTIC_TYPES,
    STATUSES,
    ParsedNote,
    ValidationIssue,
    _norm,
    iter_markdown,
    parse_note,
    sha256_text,
    validate_note,
    vault_roots,
)

LOCATOR_TYPES = {"file", "heading", "obsidian-block", "line-range", "url", "pdf-page", "timestamp", "commit"}
REVIEW_STATUSES = {"unreviewed", "pending", "accepted", "rejected"}
SOURCE_AUTHORITIES = {"primary", "secondary", "tertiary", "unknown"}
SCHEMA_VERSION_RE = re.compile(r"^\d+\.\d+(?:\.\d+)?$")


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def load_class_specs(schema_root: Path) -> dict[str, dict[str, Any]]:
    core = yaml.safe_load((schema_root / "core.yaml").read_text(encoding="utf-8")) or {}
    classes = {str(name): dict(spec or {}) for name, spec in (core.get("classes") or {}).items()}
    ext = schema_root / "extensions"
    if ext.exists():
        for path in sorted(ext.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for name, spec in (data.get("classes") or {}).items():
                if name in classes:
                    raise ValueError(f"extension class shadows/duplicates existing class: {name}")
                classes[str(name)] = dict(spec or {})
    return classes


def load_extension_classes(schema_root: Path) -> dict[str, dict[str, Any]]:
    classes = load_class_specs(schema_root)
    return {name: spec for name, spec in classes.items() if name not in SEMANTIC_TYPES}


def _ancestors(class_name: str, class_specs: dict[str, dict[str, Any]]) -> set[str]:
    out = {class_name}
    stack = [class_name]
    while stack:
        current = stack.pop()
        parent = class_specs.get(current, {}).get("is_a")
        if parent and str(parent) not in out:
            out.add(str(parent))
            stack.append(str(parent))
    return out


def _type_allowed(actual: str, allowed: set[str], class_specs: dict[str, dict[str, Any]]) -> bool:
    if not allowed:
        return True
    return bool(_ancestors(actual, class_specs) & allowed)


def _date(value: Any) -> bool:
    if value in (None, ""):
        return True
    try:
        dt.date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def _datetime(value: Any) -> bool:
    if value in (None, ""):
        return True
    text = str(value).replace("Z", "+00:00")
    try:
        dt.datetime.fromisoformat(text)
        return True
    except ValueError:
        return False


def _confidence(value: Any) -> bool:
    if value is None:
        return True
    try:
        n = float(value)
    except (TypeError, ValueError):
        return False
    return 0 <= n <= 1


def _validate_evidence(path: str, raw: Any, prefix: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if raw is None:
        return issues
    items = raw if isinstance(raw, list) else [raw]
    for i, item in enumerate(items):
        if isinstance(item, str):
            if not item.strip():
                issues.append(ValidationIssue(path, "invalid-evidence", f"{prefix}.evidence[{i}] is empty"))
            continue
        if not isinstance(item, dict) or not item.get("source"):
            issues.append(ValidationIssue(path, "invalid-evidence", f"{prefix}.evidence[{i}] requires source"))
            continue
        locator = item.get("locator") if isinstance(item.get("locator"), dict) else {}
        lt = item.get("locator_type") or locator.get("type") or "file"
        if lt not in LOCATOR_TYPES:
            issues.append(ValidationIssue(path, "invalid-locator", f"{prefix}.evidence[{i}] locator type {lt!r} is not registered"))
        authority = item.get("source_authority") or item.get("authority") or "unknown"
        if authority not in SOURCE_AUTHORITIES:
            issues.append(ValidationIssue(path, "invalid-source-authority", f"{prefix}.evidence[{i}] source authority {authority!r} is invalid"))
    return issues


def _validate_statement(path: str, raw: dict[str, Any], prefix: str, registry: dict[str, Any], require_target_key: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not raw.get("predicate"):
        issues.append(ValidationIssue(path, "missing-predicate", f"{prefix} requires predicate"))
    elif str(raw["predicate"]) not in registry:
        issues.append(ValidationIssue(path, "unknown-relation", f"{prefix} uses unknown predicate: {raw['predicate']}"))
    if raw.get(require_target_key) is None:
        issues.append(ValidationIssue(path, "missing-object", f"{prefix} requires {require_target_key}"))
    derivation = str(raw.get("derivation") or "asserted")
    if derivation not in DERIVATIONS | {"imported"}:
        issues.append(ValidationIssue(path, "invalid-derivation", f"{prefix} derivation {derivation!r} is invalid"))
    status = str(raw.get("status") or "accepted")
    if status not in STATUSES | {"merged"}:
        issues.append(ValidationIssue(path, "invalid-status", f"{prefix} status {status!r} is invalid"))
    review = raw.get("review_status")
    if review is not None and str(review) not in REVIEW_STATUSES:
        issues.append(ValidationIssue(path, "invalid-review-status", f"{prefix} review_status {review!r} is invalid"))
    for field in ("extraction_confidence", "claim_confidence", "confidence"):
        if field in raw and not _confidence(raw.get(field)):
            issues.append(ValidationIssue(path, "invalid-confidence", f"{prefix}.{field} must be within [0,1]"))
    for field in ("valid_from", "valid_to", "event_time", "transaction_time"):
        if field in raw and not _date(raw.get(field)):
            issues.append(ValidationIssue(path, "invalid-time", f"{prefix}.{field} must be ISO YYYY-MM-DD"))
    if raw.get("recorded_at") is not None and not _datetime(raw.get("recorded_at")):
        issues.append(ValidationIssue(path, "invalid-time", f"{prefix}.recorded_at must be ISO datetime"))
    if raw.get("valid_from") and raw.get("valid_to") and str(raw["valid_from"]) > str(raw["valid_to"]):
        issues.append(ValidationIssue(path, "invalid-validity-interval", f"{prefix}.valid_from is after valid_to"))
    issues.extend(_validate_evidence(path, raw.get("evidence"), prefix))
    return issues


def _scan_notes(
    vault_root: Path,
    replacements: list[tuple[Path, str]] | None = None,
) -> tuple[list[ValidationIssue], list[ParsedNote]]:
    issues: list[ValidationIssue] = []
    notes: list[ParsedNote] = []
    replacements = list(replacements or [])
    targets = {target.resolve() for target, _ in replacements}
    for path in iter_markdown(vault_root):
        if path.resolve() in targets:
            continue
        try:
            notes.append(parse_note(path, vault_root))
        except Exception as exc:
            issues.append(ValidationIssue(str(path.relative_to(vault_root)), "parse-error", str(exc)))
    for target_path, content in replacements:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                temp = Path(tmp) / target_path.name
                temp.write_text(content, encoding="utf-8")
                candidate = parse_note(temp)
                candidate = dataclasses.replace(
                    candidate,
                    path=target_path.resolve().relative_to(vault_root.resolve()),
                    content_hash=sha256_text(content),
                )
                notes.append(candidate)
        except Exception as exc:
            issues.append(ValidationIssue(str(target_path), "parse-error", str(exc)))
    return issues, notes


def scan_vault_semantics(
    vault_root: Path,
    schema_root: Path,
    replacements: list[tuple[Path, str]] | None = None,
) -> tuple[list[ValidationIssue], list[ParsedNote]]:
    registry = load_relation_registry_with_extensions(schema_root)
    class_specs = load_class_specs(schema_root)
    extension_classes = {name for name in class_specs if name not in SEMANTIC_TYPES}
    version_file = schema_root / "VERSION"
    supported_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else None
    issues, notes = _scan_notes(vault_root, replacements)
    ids: dict[str, ParsedNote] = {}
    aliases: dict[str, set[str]] = {}
    claim_ids: dict[str, str] = {}

    for note in notes:
        p = str(note.path)
        base = validate_note(note, registry)
        issues.extend(i for i in base if i.code != "unknown-relation")
        if not note.semantic:
            continue
        oid = note.object_id or ""
        if oid in ids:
            issues.append(ValidationIssue(p, "duplicate-id", f"{oid} also used by {ids[oid].path}"))
        ids[oid] = note
        if note.object_type not in SEMANTIC_TYPES and note.object_type not in extension_classes:
            issues.append(ValidationIssue(p, "unknown-type", f"semantic type {note.object_type!r} is not core or declared extension"))
        ks = note.frontmatter.get("knowledge_schema")
        if ks is not None and not SCHEMA_VERSION_RE.match(str(ks)):
            issues.append(ValidationIssue(p, "invalid-schema-version", "knowledge_schema must be a dotted numeric version"))
        elif ks is not None and supported_version and _version_tuple(str(ks)) > _version_tuple(supported_version):
            issues.append(ValidationIssue(
                p, "unsupported-schema-version",
                f"knowledge_schema {ks} is newer than supported {supported_version}; a migration is required",
            ))
        if note.object_type == "Source":
            sa = note.frontmatter.get("source_authority")
            if sa is not None and str(sa) not in SOURCE_AUTHORITIES:
                issues.append(ValidationIssue(p, "invalid-source-authority", f"source_authority {sa!r} is not a valid value"))
        for field in ("created", "updated"):
            if field in note.frontmatter and not _date(note.frontmatter.get(field)):
                issues.append(ValidationIssue(p, "invalid-object-time", f"{field} must be ISO YYYY-MM-DD"))
        status = str(note.frontmatter.get("status") or "accepted")
        if status not in STATUSES | {"merged"}:
            issues.append(ValidationIssue(p, "invalid-object-status", f"object status {status!r} is not a valid lifecycle value"))
        if status == "merged" and not note.frontmatter.get("redirect_to"):
            issues.append(ValidationIssue(p, "missing-redirect", "merged object requires redirect_to"))
        for alias in (note.title, *note.aliases):
            normalized = _norm(alias)
            if normalized:
                aliases.setdefault(normalized, set()).add(oid)
        for i, rel in enumerate(note.frontmatter.get("relations") or []):
            if isinstance(rel, dict):
                issues.extend(_validate_statement(p, rel, f"relations[{i}]", registry, "target"))
        claims = note.frontmatter.get("claims") or []
        if claims and not isinstance(claims, list):
            issues.append(ValidationIssue(p, "invalid-claims", "claims must be a list"))
        elif isinstance(claims, list):
            for i, claim in enumerate(claims):
                if not isinstance(claim, dict):
                    issues.append(ValidationIssue(p, "invalid-claim", f"claims[{i}] must be a mapping"))
                    continue
                if not claim.get("id"):
                    issues.append(ValidationIssue(
                        p, "missing-claim-id",
                        f"claims[{i}] requires an explicit stable id; list-position ids are unstable across edits",
                    ))
                cid = str(claim.get("id") or f"claim:{oid}:{i}")
                if cid in claim_ids:
                    issues.append(ValidationIssue(p, "duplicate-claim-id", f"claim id {cid} also used by {claim_ids[cid]}"))
                else:
                    claim_ids[cid] = p
                issues.extend(_validate_statement(p, claim, f"claims[{i}]", registry, "object"))

    for note in notes:
        if not note.semantic:
            continue
        p = str(note.path)
        fm = note.frontmatter
        redirect = fm.get("redirect_to")
        if redirect and str(redirect) not in ids:
            issues.append(ValidationIssue(p, "unresolved-redirect", f"redirect target not found: {redirect}"))
        statements: list[tuple[str, dict[str, Any], str]] = []
        statements.extend((f"relations[{i}]", rel, "target") for i, rel in enumerate(fm.get("relations") or []) if isinstance(rel, dict))
        statements.extend((f"claims[{i}]", claim, "object") for i, claim in enumerate(fm.get("claims") or []) if isinstance(claim, dict))
        for prefix, statement, target_key in statements:
            if not statement.get("predicate") or statement.get(target_key) is None:
                continue
            pred = str(statement["predicate"])
            target = str(statement[target_key])
            spec = registry.get(pred) or {}
            # A claim may declare an explicit subject distinct from its containing
            # note; domain must be checked against the subject object's type.
            if target_key == "object":
                subject_ref = str(statement.get("subject") or note.object_id or "")
            else:
                subject_ref = str(note.object_id or "")
            subject_note = ids.get(subject_ref)
            src_type = subject_note.object_type if subject_note else None
            tgt_type = ids[target].object_type if target in ids else None
            domain = set(spec.get("domain") or [])
            range_ = set(spec.get("range") or [])
            if src_type and domain and not _type_allowed(src_type, domain, class_specs):
                issues.append(ValidationIssue(p, "relation-domain", f"{prefix}: {pred} does not allow source type {src_type}"))
            if tgt_type and range_ and not _type_allowed(tgt_type, range_, class_specs):
                issues.append(ValidationIssue(p, "relation-range", f"{prefix}: {pred} does not allow target type {tgt_type}"))

    # Detect self-links and cycles in the merged-object redirect graph: these
    # build cleanly (all targets exist) but leave every id/alias in the cycle
    # unresolvable at query time.
    redirect_edges: dict[str, str] = {}
    for note in notes:
        if note.semantic and note.object_id and str(note.frontmatter.get("status") or "") == "merged":
            target = note.frontmatter.get("redirect_to")
            if target:
                redirect_edges[note.object_id] = str(target)
    for start in redirect_edges:
        seen: set[str] = set()
        current = start
        while current in redirect_edges:
            if current in seen:
                p = str(ids[start].path) if start in ids else "<vault>"
                issues.append(ValidationIssue(p, "redirect-cycle", f"merged redirect cycle starting at {start}"))
                break
            seen.add(current)
            current = redirect_edges[current]

    for alias, object_ids in sorted(aliases.items()):
        if len(object_ids) > 1:
            issues.append(ValidationIssue("<vault>", "ambiguous-alias", f"alias/title {alias!r} resolves to {sorted(object_ids)}", severity="warning"))
    return issues, notes


def validate_vault_semantics(vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
    return scan_vault_semantics(vault_root, schema_root)[0]


def validate_candidate_semantics(content: str, target_path: Path, vault_root: Path) -> list[ValidationIssue]:
    _, schema_root, _ = vault_roots(vault_root)
    return scan_vault_semantics(vault_root, schema_root, [(target_path, content)])[0]


def validate_batch_semantics(replacements: list[tuple[Path, str]], vault_root: Path) -> list[ValidationIssue]:
    """Validate the combined final state of a multi-file batch applied simultaneously."""
    _, schema_root, _ = vault_roots(vault_root)
    return scan_vault_semantics(vault_root, schema_root, replacements)[0]
