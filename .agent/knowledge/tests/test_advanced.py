from __future__ import annotations

from pathlib import Path

import pytest

from agentic_vault_knowledge.advanced import load_relation_registry_with_extensions
from agentic_vault_knowledge.runtime_index import RuntimeIndex


@pytest.fixture()
def vault(tmp_path: Path) -> Path:
    schema_src = Path(__file__).parents[1] / "schema"
    schema = tmp_path / ".agent/knowledge/schema"
    (schema / "extensions").mkdir(parents=True)
    for name in ("core.yaml", "relations.yaml", "VERSION"):
        (schema / name).write_text((schema_src / name).read_text(encoding="utf-8"), encoding="utf-8")
    (schema / "extensions/custom.yaml").write_text("relations:\n  custom_link:\n    description: synthetic extension\n", encoding="utf-8")

    notes = tmp_path / "02_Areas/Synthetic"
    notes.mkdir(parents=True)
    (notes / "Alpha.md").write_text("""---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: custom_link
    target: entity:beta
    derivation: asserted
    status: accepted
claims:
  - id: claim:alpha-state
    predicate: related_to
    object: entity:beta
    status: proposed
    derivation: inferred
    evidence:
      - source: source:synthetic
        locator:
          type: heading
          value: Evidence
---
# Alpha
""", encoding="utf-8")
    (notes / "Beta.md").write_text("""---
id: entity:beta
type: Entity
title: Beta
relations:
  - predicate: depends_on
    target: entity:gamma
    derivation: asserted
    status: accepted
---
# Beta
""", encoding="utf-8")
    (notes / "Gamma.md").write_text("""---
id: entity:gamma
type: Entity
title: Gamma
---
# Gamma
""", encoding="utf-8")
    return tmp_path


def test_extension_relation_loaded(vault: Path) -> None:
    registry = load_relation_registry_with_extensions(vault / ".agent/knowledge/schema")
    assert "custom_link" in registry


def test_claim_projection_and_analytics(vault: Path) -> None:
    db = vault / ".agent/knowledge/generated/knowledge.db"
    with RuntimeIndex(db) as idx:
        issues = idx.build(vault, vault / ".agent/knowledge/schema")
        assert not [i for i in issues if i.code == "unknown-relation"]
        claims = idx.claims("entity:alpha")
        assert claims[0]["id"] == "claim:alpha-state"
        assert claims[0]["status"] == "proposed"
        assert idx.health()["candidate_claims"] == 1
        assert idx.query(predicate="custom_link")[0]["target_id"] == "entity:beta"
        assert idx.trace("entity:alpha", "entity:gamma") == ["entity:alpha", "entity:beta", "entity:gamma"]
        assert any(x["id"] == "entity:gamma" for x in idx.impact("entity:beta"))
        assert idx.communities()[0]["size"] == 3


def test_full_rebuild_recreates_claim_schema(vault: Path) -> None:
    db = vault / ".agent/knowledge/generated/knowledge.db"
    with RuntimeIndex(db) as idx:
        idx.build(vault, vault / ".agent/knowledge/schema")
        before = idx.health()
        idx.rebuild(vault, vault / ".agent/knowledge/schema")
        after = idx.health()
    assert before["objects"] == after["objects"] == 3
    assert before["claims"] == after["claims"] == 1
