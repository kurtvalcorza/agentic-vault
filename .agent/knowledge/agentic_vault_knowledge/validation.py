from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

import yaml

from .advanced import load_relation_registry_with_extensions
from .core import DERIVATIONS, SEMANTIC_TYPES, STATUSES, ValidationIssue, iter_markdown, parse_note, validate_note

LOCATOR_TYPES = {"file", "heading", "obsidian-block", "line-range", "url", "pdf-page", "timestamp", "commit"}
REVIEW_STATUSES = {"unreviewed", "pending", "accepted", "rejected"}
SOURCE_AUTHORITIES = {"primary", "secondary", "tertiary", "unknown"}
SCHEMA_VERSION_RE = re.compile(r"^\d+\.\d+(?:\.\d+)?$")


def load_extension_classes(schema_root: Path) -> dict[str, dict[str, Any]]:
    classes: dict[str, dict[str, Any]] = {}
    ext = schema_root / "extensions"
    if not ext.exists():
        return classes
    for path in sorted(ext.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for name, spec in (data.get("classes") or {}).items():
            if name in SEMANTIC_TYPES or name in classes:
                raise ValueError(f"extension class shadows/duplicates existing class: {name}")
            classes[str(name)] = dict(spec or {})
    return classes


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
            issues.append(ValidationIssue(path, "invalid-evidence", f"{prefix}.evidence[{i}] requires source")); continue
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


def validate_vault_semantics(vault_root: Path, schema_root: Path) -> list[ValidationIssue]:
    registry = load_relation_registry_with_extensions(schema_root)
    extension_classes = load_extension_classes(schema_root)
    issues: list[ValidationIssue] = []
    notes = []
    ids: dict[str, Any] = {}
    aliases: dict[str, set[str]] = {}

    for path in iter_markdown(vault_root):
        try:
            note = parse_note(path, vault_root)
        except Exception as exc:
            issues.append(ValidationIssue(str(path.relative_to(vault_root)), "parse-error", str(exc))); continue
        notes.append(note)
        p = str(note.path)
        base = validate_note(note, registry)
        # Unknown extension classes are handled here; avoid core's intentionally permissive type logic.
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
        for field in ("created", "updated"):
            if field in note.frontmatter and not _date(note.frontmatter.get(field)):
                issues.append(ValidationIssue(p, "invalid-object-time", f"{field} must be ISO YYYY-MM-DD"))
        status = str(note.frontmatter.get("status") or "accepted")
        if status == "merged" and not note.frontmatter.get("redirect_to"):
            issues.append(ValidationIssue(p, "missing-redirect", "merged object requires redirect_to"))
        for alias in (note.title, *note.aliases):
            aliases.setdefault(alias.casefold().strip(), set()).add(oid)
        for i, rel in enumerate(note.frontmatter.get("relations") or []):
            if isinstance(rel, dict):
                issues.extend(_validate_statement(p, rel, f"relations[{i}]", registry, "target"))
        claims = note.frontmatter.get("claims") or []
        if claims and not isinstance(claims, list):
            issues.append(ValidationIssue(p, "invalid-claims", "claims must be a list"))
        elif isinstance(claims, list):
            claim_ids: set[str] = set()
            for i, claim in enumerate(claims):
                if not isinstance(claim, dict):
                    issues.append(ValidationIssue(p, "invalid-claim", f"claims[{i}] must be a mapping")); continue
                cid = str(claim.get("id") or f"claim:{oid}:{i}")
                if cid in claim_ids:
                    issues.append(ValidationIssue(p, "duplicate-claim-id", f"duplicate claim id within note: {cid}"))
                claim_ids.add(cid)
                issues.extend(_validate_statement(p, claim, f"claims[{i}]", registry, "object"))

    # Cross-object checks require the full object map.
    for note in notes:
        if not note.semantic:
            continue
        p = str(note.path)
        fm = note.frontmatter
        redirect = fm.get("redirect_to")
        if redirect and str(redirect) not in ids:
            issues.append(ValidationIssue(p, "unresolved-redirect", f"redirect target not found: {redirect}"))
        for i, rel in enumerate(fm.get("relations") or []):
            if not isinstance(rel, dict) or not rel.get("predicate") or rel.get("target") is None:
                continue
            pred = str(rel["predicate"]); target = str(rel["target"]); spec = registry.get(pred) or {}
            src_type = note.object_type or "KnowledgeObject"
            tgt_type = ids[target].object_type if target in ids else None
            domain = set(spec.get("domain") or [])
            range_ = set(spec.get("range") or [])
            if domain and "KnowledgeObject" not in domain and src_type not in domain:
                issues.append(ValidationIssue(p, "relation-domain", f"{pred} does not allow source type {src_type}"))
            if tgt_type and range_ and "KnowledgeObject" not in range_ and tgt_type not in range_:
                issues.append(ValidationIssue(p, "relation-range", f"{pred} does not allow target type {tgt_type}"))
        # Alias collisions are not auto-merge errors, but they are surfaced for review.
    for alias, object_ids in sorted(aliases.items()):
        if alias and len(object_ids) > 1:
            issues.append(ValidationIssue("<vault>", "ambiguous-alias", f"alias/title {alias!r} resolves to {sorted(object_ids)}", severity="warning"))
    return issues
