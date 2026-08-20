from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from agentic_vault_knowledge import cli
from agentic_vault_knowledge.core import KnowledgeError, propose_frontmatter_patch, split_frontmatter
from agentic_vault_knowledge.interop import export_okf_bundle
from agentic_vault_knowledge.runtime_index import EXPECTED_CLAIM_COLUMNS, RuntimeIndex
from agentic_vault_knowledge.validation import validate_vault_semantics


@pytest.fixture()
def vault(tmp_path: Path) -> Path:
    source_schema = Path(__file__).parents[1] / "schema"
    schema = tmp_path / ".agent/knowledge/schema"
    (schema / "extensions").mkdir(parents=True)
    for name in ("core.yaml", "relations.yaml", "VERSION"):
        (schema / name).write_text((source_schema / name).read_text(encoding="utf-8"), encoding="utf-8")
    notes = tmp_path / "02_Areas/Synthetic"
    notes.mkdir(parents=True)
    (notes / "Alpha.md").write_text(
        """---
id: entity:alpha
type: Entity
title: Sample Project
status: active
---
# Alpha
""",
        encoding="utf-8",
    )
    (notes / "Beta.md").write_text(
        """---
id: entity:beta
type: Entity
title: Beta
status: active
---
# Beta
""",
        encoding="utf-8",
    )
    return tmp_path


def test_split_frontmatter_accepts_crlf() -> None:
    fm, body = split_frontmatter("---\r\nid: concept:crlf\r\ntype: Concept\r\n---\r\n# CRLF\r\n")
    assert fm["id"] == "concept:crlf"
    assert fm["type"] == "Concept"
    assert body.startswith("# CRLF")


def test_empty_resolution_returns_no_candidates(vault: Path) -> None:
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        assert idx.build(vault, vault / ".agent/knowledge/schema") == []
        assert idx.resolve("") == []
        assert idx.resolve("---") == []


def test_relation_evidence_preserves_source_authority(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    evidence:
      - source: source:synthetic
        source_authority: primary
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        assert idx.build(vault, vault / ".agent/knowledge/schema") == []
        assert idx.sources("entity:alpha")[0]["authority"] == "primary"


def test_patch_rejects_outside_vault(vault: Path, tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-knowledge-review.md"
    outside.write_text("---\nid: entity:outside\ntype: Entity\n---\n", encoding="utf-8")
    proposal = propose_frontmatter_patch(outside, {"title": "Should Not Write"})
    from agentic_vault_knowledge.core import apply_patch
    with pytest.raises(KnowledgeError, match="escapes vault root"):
        apply_patch(proposal, vault)


def test_patch_validation_uses_extensions_and_claim_rules(vault: Path) -> None:
    schema = vault / ".agent/knowledge/schema"
    (schema / "extensions/custom.yaml").write_text(
        """relations:
  evaluates:
    domain: [KnowledgeObject]
    range: [KnowledgeObject]
""",
        encoding="utf-8",
    )
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    valid = propose_frontmatter_patch(alpha, {
        "relations": [{"predicate": "evaluates", "target": "entity:beta"}],
    })
    from agentic_vault_knowledge.core import validate_patch
    assert not [item for item in validate_patch(valid, vault) if item.severity == "error"]

    invalid = propose_frontmatter_patch(alpha, {
        "claims": [{"id": "claim:broken", "status": "accepted"}],
    })
    codes = {item.code for item in validate_patch(invalid, vault) if item.severity == "error"}
    assert "missing-predicate" in codes
    assert "missing-object" in codes


def test_duplicate_claim_ids_fail_across_notes(vault: Path) -> None:
    for name, oid in (("Alpha.md", "entity:alpha"), ("Beta.md", "entity:beta")):
        path = vault / "02_Areas/Synthetic" / name
        path.write_text(
            f"""---
id: {oid}
type: Entity
title: {oid}
claims:
  - id: claim:shared
    predicate: related_to
    object: entity:alpha
    status: accepted
---
# {oid}
""",
            encoding="utf-8",
        )
    issues = validate_vault_semantics(vault, vault / ".agent/knowledge/schema")
    assert "duplicate-claim-id" in {item.code for item in issues}
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        build_issues = idx.build(vault, vault / ".agent/knowledge/schema")
        assert "duplicate-claim-id" in {item.code for item in build_issues}
        assert idx.conn.execute("SELECT count(*) FROM claims").fetchone()[0] == 0


def test_recorded_at_offsets_compare_as_instants(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
claims:
  - id: claim:offset
    predicate: related_to
    object: entity:beta
    status: accepted
    valid_from: 2026-01-01
    recorded_at: 2026-01-02T01:00:00+02:00
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        assert idx.build(vault, vault / ".agent/knowledge/schema") == []
        state = idx.state_as_of("entity:alpha", "2026-01-02T00:00:00+00:00")
        assert [item["id"] for item in state["claims"]] == ["claim:offset"]


def test_alias_validation_uses_resolver_normalization(vault: Path) -> None:
    gamma = vault / "02_Areas/Synthetic/Gamma.md"
    gamma.write_text(
        """---
id: entity:gamma
type: Entity
title: Sample-Project
---
# Gamma
""",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, vault / ".agent/knowledge/schema")
    assert "ambiguous-alias" in {item.code for item in issues}


def test_relation_range_accepts_extension_subtype(vault: Path) -> None:
    schema = vault / ".agent/knowledge/schema"
    (schema / "extensions/people.yaml").write_text(
        """classes:
  Researcher:
    is_a: Person
""",
        encoding="utf-8",
    )
    researcher = vault / "02_Areas/Synthetic/Researcher.md"
    researcher.write_text(
        """---
id: person:researcher
type: Researcher
title: Researcher
---
# Researcher
""",
        encoding="utf-8",
    )
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: authored_by
    target: person:researcher
---
# Alpha
""",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, schema)
    assert not [item for item in issues if item.code in {"relation-domain", "relation-range"}]


def test_okf_export_is_stable_and_excluded_from_index(vault: Path) -> None:
    output = vault / ".agent/outputs/okf-export"
    first = export_okf_bundle(vault, output)
    second = export_okf_bundle(vault, output)
    assert first["concepts"] == 2
    assert second["concepts"] == 2
    assert (output / ".knowledge-ignore").exists()
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        assert idx.build(vault, vault / ".agent/knowledge/schema") == []
        assert idx.health()["objects"] == 2


def test_runtime_repairs_old_claim_schema_before_index_creation(vault: Path) -> None:
    db = vault / ".agent/knowledge/generated/knowledge.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE claims(id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()
    with RuntimeIndex(db) as idx:
        columns = {row["name"] for row in idx.conn.execute("PRAGMA table_info(claims)")}
        assert columns == EXPECTED_CLAIM_COLUMNS


def test_refresh_skips_build_when_metadata_is_unchanged(vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        assert idx.refresh(vault, vault / ".agent/knowledge/schema") == []
        monkeypatch.setattr(idx, "build", lambda *_: (_ for _ in ()).throw(AssertionError("build should not run")))
        assert idx.refresh(vault, vault / ".agent/knowledge/schema") == []


def test_cli_validation_commands_return_nonzero_on_errors(vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    proposal = propose_frontmatter_patch(alpha, {
        "relations": [{"predicate": "not_registered", "target": "entity:beta"}],
    })
    proposal_file = vault / "proposal.json"
    proposal_file.write_text(json.dumps(proposal), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["vault-knowledge", "--vault", str(vault), "validate-patch", str(proposal_file)])
    assert cli.main() == 1
