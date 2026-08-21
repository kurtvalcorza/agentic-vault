from __future__ import annotations

from pathlib import Path

import pytest

from agentic_vault_knowledge.core import ConflictError, propose_frontmatter_patch
from agentic_vault_knowledge.migrations import plan_migrations, schema_version
from agentic_vault_knowledge.runtime_index import RuntimeIndex
from agentic_vault_knowledge.transactions import apply_batch, validate_batch
from agentic_vault_knowledge.validation import validate_vault_semantics


@pytest.fixture()
def vault(tmp_path: Path) -> Path:
    source_schema = Path(__file__).parents[1] / "schema"
    schema = tmp_path / ".agent/knowledge/schema"
    (schema / "extensions").mkdir(parents=True)
    for name in ("core.yaml", "relations.yaml", "VERSION"):
        (schema / name).write_text((source_schema / name).read_text(encoding="utf-8"), encoding="utf-8")
    (schema / "extensions/domain.yaml").write_text("""classes:
  ResearchItem:
    is_a: KnowledgeObject
relations:
  evaluates:
    domain: [KnowledgeObject]
    range: [KnowledgeObject]
""", encoding="utf-8")
    notes = tmp_path / "02_Areas/Synthetic"
    notes.mkdir(parents=True)
    (notes / "Alpha.md").write_text("""---
id: entity:alpha
knowledge_schema: 0.1.0
type: Entity
title: Alpha
aliases: [Original Alpha]
status: active
claims:
  - id: claim:accepted-edge
    subject: entity:alpha
    predicate: related_to
    object: entity:beta
    status: accepted
    derivation: asserted
    valid_from: 2026-01-01
    valid_to: 2026-06-30
    recorded_at: 2026-01-02T00:00:00+00:00
    evidence:
      - source: source:synthetic
        source_authority: primary
        locator:
          type: obsidian-block
          value: ^evidence-alpha
  - id: claim:proposed-edge
    subject: entity:alpha
    predicate: related_to
    object: entity:gamma
    status: proposed
    derivation: inferred
    valid_from: 2026-01-01
    recorded_at: 2026-01-02T00:00:00+00:00
    extraction_confidence: 0.91
    claim_confidence: 0.62
---
# Alpha
""", encoding="utf-8")
    (notes / "Beta.md").write_text("""---
id: entity:beta
knowledge_schema: 0.1.0
type: Entity
title: Beta
status: active
---
# Beta
""", encoding="utf-8")
    (notes / "Gamma.md").write_text("""---
id: entity:gamma
knowledge_schema: 0.1.0
type: Entity
title: Gamma
status: active
---
# Gamma
""", encoding="utf-8")
    return tmp_path


def test_stable_identity_survives_move_and_title_change(vault: Path) -> None:
    schema = vault / ".agent/knowledge/schema"
    db = vault / ".agent/knowledge/generated/knowledge.db"
    source = vault / "02_Areas/Synthetic/Alpha.md"
    with RuntimeIndex(db) as idx:
        assert not [i for i in idx.build(vault, schema) if i.severity == "error"]
        assert idx.get("entity:alpha")["path"].endswith("Alpha.md")
        moved = vault / "01_Projects/Renamed Alpha.md"
        moved.parent.mkdir(parents=True)
        text = source.read_text(encoding="utf-8").replace("title: Alpha", "title: Renamed Alpha")
        source.unlink(); moved.write_text(text, encoding="utf-8")
        assert not [i for i in idx.build(vault, schema) if i.severity == "error"]
        obj = idx.get("entity:alpha")
        assert obj["title"] == "Renamed Alpha"
        assert obj["path"] == "01_Projects/Renamed Alpha.md"


def test_duplicate_id_and_unknown_predicate_fail_validation(vault: Path) -> None:
    bad = vault / "02_Areas/Synthetic/Bad.md"
    bad.write_text("""---
id: entity:beta
type: Entity
title: Duplicate Beta
relations:
  - predicate: invented_relation
    target: entity:alpha
---
# Duplicate Beta
""", encoding="utf-8")
    issues = validate_vault_semantics(vault, vault / ".agent/knowledge/schema")
    codes = {i.code for i in issues if i.severity == "error"}
    assert "duplicate-id" in codes
    assert "unknown-relation" in codes


def test_extension_class_is_accepted(vault: Path) -> None:
    note = vault / "02_Areas/Synthetic/Research.md"
    note.write_text("""---
id: research:one
type: ResearchItem
title: Research One
relations:
  - predicate: evaluates
    target: entity:alpha
---
# Research One
""", encoding="utf-8")
    issues = validate_vault_semantics(vault, vault / ".agent/knowledge/schema")
    assert not [i for i in issues if i.code in {"unknown-type", "unknown-relation"}]


def test_accepted_claim_projects_to_graph_but_proposed_claim_does_not(vault: Path) -> None:
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        idx.build(vault, vault / ".agent/knowledge/schema")
        targets = {r["target_id"] for r in idx.neighbors("entity:alpha", include_derived=True) if r["source_id"] == "entity:alpha"}
        assert "entity:beta" in targets
        assert "entity:gamma" not in targets
        assert idx.claims("entity:alpha", "proposed")[0]["id"] == "claim:proposed-edge"
        evidence = idx.claim_sources("claim:accepted-edge")
        assert evidence[0]["locator_type"] == "obsidian-block"
        assert evidence[0]["source_authority"] == "primary"


def test_merge_redirect_resolves_old_id_and_alias(vault: Path) -> None:
    merged = vault / "02_Areas/Synthetic/Old Alpha.md"
    merged.write_text("""---
id: entity:old-alpha
type: Entity
title: Old Alpha
aliases: [Legacy Alpha]
status: merged
redirect_to: entity:alpha
---
# Old Alpha
""", encoding="utf-8")
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        assert not [i for i in idx.build(vault, vault / ".agent/knowledge/schema") if i.severity == "error"]
        assert idx.resolve("entity:old-alpha")[0]["id"] == "entity:alpha"
        alias = idx.resolve("Legacy Alpha")[0]
        assert alias["id"] == "entity:alpha"
        assert alias["match"] == "redirect"


def test_temporal_contradictions_require_overlapping_validity(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    text = alpha.read_text(encoding="utf-8")
    text = text.replace("---\n# Alpha", """  - id: claim:later-state
    subject: entity:alpha
    predicate: related_to
    object: entity:gamma
    status: accepted
    derivation: asserted
    valid_from: 2026-07-01
    valid_to: 2026-12-31
---
# Alpha""")
    alpha.write_text(text, encoding="utf-8")
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        idx.build(vault, vault / ".agent/knowledge/schema")
        assert idx.contradiction_candidates() == []
        alpha.write_text(alpha.read_text(encoding="utf-8").replace("valid_from: 2026-07-01", "valid_from: 2026-06-01"), encoding="utf-8")
        idx.build(vault, vault / ".agent/knowledge/schema")
        assert any(c.get("left_claim") or c.get("right_claim") for c in idx.contradiction_candidates())


def test_state_as_of_respects_valid_and_record_time(vault: Path) -> None:
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        idx.build(vault, vault / ".agent/knowledge/schema")
        early = idx.state_as_of("entity:alpha", "2025-12-31T23:59:59+00:00")
        current = idx.state_as_of("entity:alpha", "2026-02-01T00:00:00+00:00")
        assert early["claims"] == []
        assert {x["id"] for x in current["claims"]} == {"claim:accepted-edge", "claim:proposed-edge"}


def test_batch_write_is_hash_bound(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    beta = vault / "02_Areas/Synthetic/Beta.md"
    proposals = [
        propose_frontmatter_patch(alpha, {"updated": "2026-08-20"}),
        propose_frontmatter_patch(beta, {"updated": "2026-08-20"}),
    ]
    assert not [x for x in validate_batch(proposals, vault) if x.get("severity") == "error"]
    beta.write_text(beta.read_text(encoding="utf-8") + "\nconcurrent edit\n", encoding="utf-8")
    with pytest.raises(ConflictError):
        apply_batch(proposals, vault)
    assert "updated: 2026-08-20" not in alpha.read_text(encoding="utf-8")


def test_current_schema_needs_no_migration(vault: Path) -> None:
    current = schema_version(vault)
    assert plan_migrations(vault, current, current) == []
