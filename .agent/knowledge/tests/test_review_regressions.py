from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from agentic_vault_knowledge import cli, core
from agentic_vault_knowledge.core import (
    ConflictError,
    KnowledgeError,
    apply_patch,
    propose_frontmatter_patch,
    sha256_text,
    split_frontmatter,
    validate_patch,
)
from agentic_vault_knowledge.interop import export_okf_bundle
from agentic_vault_knowledge.proposals import propose_entity
from agentic_vault_knowledge.runtime_index import EXPECTED_CLAIM_COLUMNS, RuntimeIndex
from agentic_vault_knowledge.transactions import validate_batch
from agentic_vault_knowledge.validation import validate_vault_semantics


def _schema(vault: Path) -> Path:
    return vault / ".agent/knowledge/schema"


def _db(vault: Path) -> Path:
    return vault / ".agent/knowledge/generated/knowledge.db"


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


# --- Second review pass (current head) regression coverage ---


def test_split_frontmatter_accepts_closing_delimiter_at_eof() -> None:
    fm, body = split_frontmatter("---\nid: concept:eof\ntype: Concept\n---")
    assert fm["id"] == "concept:eof"
    assert fm["type"] == "Concept"
    assert body == ""


def test_apply_patch_rejects_semantic_demotion(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    proposal = {
        "path": str(alpha),
        "base_hash": sha256_text(alpha.read_text(encoding="utf-8")),
        "content": "# demoted\n",
    }
    codes = {item.code for item in validate_patch(proposal, vault) if item.severity == "error"}
    assert "semantic-demotion" in codes
    with pytest.raises(KnowledgeError):
        apply_patch(proposal, vault)
    assert "id: entity:alpha" in alpha.read_text(encoding="utf-8")


def test_patch_rejects_stable_id_change(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    proposal = propose_frontmatter_patch(alpha, {"id": "entity:renamed"})
    codes = {item.code for item in validate_patch(proposal, vault) if item.severity == "error"}
    assert "identity-change" in codes


def test_apply_patch_rechecks_hash_after_validation(vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    proposal = propose_frontmatter_patch(alpha, {"title": "New Title"})

    def racing_validate(prop: dict, root: Path) -> list:
        alpha.write_text(alpha.read_text(encoding="utf-8") + "\nconcurrent edit\n", encoding="utf-8")
        return []

    monkeypatch.setattr(core, "validate_patch", racing_validate)
    with pytest.raises(ConflictError):
        core.apply_patch(proposal, vault)


def test_create_proposal_can_be_applied(vault: Path) -> None:
    proposal = propose_entity(vault, "02_Areas/Synthetic/New.md", {
        "id": "entity:new", "type": "Entity", "title": "New Entity",
    })
    apply_patch(proposal, vault)
    created = vault / "02_Areas/Synthetic/New.md"
    assert created.exists()
    assert "id: entity:new" in created.read_text(encoding="utf-8")
    with pytest.raises(ConflictError):
        apply_patch(proposal, vault)


def test_batch_validates_combined_final_state(vault: Path) -> None:
    person = vault / "02_Areas/Synthetic/Person.md"
    person.write_text(
        """---
id: person:p
type: Person
title: P
---
# P
""",
        encoding="utf-8",
    )
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    prop_relation = propose_frontmatter_patch(alpha, {
        "relations": [{"predicate": "authored_by", "target": "person:p"}],
    })
    prop_retype = propose_frontmatter_patch(person, {"type": "Artifact"})
    # Each proposal is individually valid against the current vault.
    assert not [i for i in validate_patch(prop_relation, vault) if i.severity == "error"]
    assert not [i for i in validate_patch(prop_retype, vault) if i.severity == "error"]
    # Combined, authored_by's range ([Person, Organization]) is violated.
    codes = {i["code"] for i in validate_batch([prop_relation, prop_retype], vault) if i.get("severity") == "error"}
    assert "relation-range" in codes


def test_claim_domain_uses_declared_subject(vault: Path) -> None:
    (vault / "02_Areas/Synthetic/Artifact.md").write_text(
        """---
id: art:thing
type: Artifact
title: Thing
---
# Thing
""",
        encoding="utf-8",
    )
    person = vault / "02_Areas/Synthetic/Person.md"
    person.write_text(
        """---
id: person:p
type: Person
title: P
claims:
  - id: claim:c
    subject: art:thing
    predicate: authored
    object: entity:beta
    status: accepted
---
# P
""",
        encoding="utf-8",
    )
    # The note type (Person) is a valid domain for `authored`, but the claim's
    # declared subject (Artifact) is not; validation must use the subject type.
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "relation-domain" in {item.code for item in issues}


def test_relation_validity_fields_are_projected(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    valid_from: 2026-01-01
    valid_to: 2026-06-01
    recorded_at: 2026-01-02T03:00:00+00:00
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        row = idx.conn.execute(
            "SELECT valid_from,valid_to,recorded_at FROM relations "
            "WHERE source_id='entity:alpha' AND predicate='related_to'"
        ).fetchone()
        assert row["valid_from"] == "2026-01-01"
        assert row["valid_to"] == "2026-06-01"
        recorded_at = str(row["recorded_at"])
        assert recorded_at.startswith("2026-01-02") and "03:00:00" in recorded_at


def test_imported_relation_derivation_is_valid(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    derivation: imported
---
# Alpha
""",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "invalid-derivation" not in {item.code for item in issues}


def test_invalid_object_status_is_rejected(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(alpha.read_text(encoding="utf-8").replace("status: active", "status: accpeted"), encoding="utf-8")
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "invalid-object-status" in {item.code for item in issues}


def test_claim_requires_stable_id(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
claims:
  - predicate: related_to
    object: entity:beta
    status: accepted
---
# Alpha
""",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "missing-claim-id" in {item.code for item in issues}


def test_trace_excludes_inferred_edges_by_default(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    derivation: inferred
    status: accepted
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        assert idx.trace("entity:alpha", "entity:beta") == []
        assert idx.trace("entity:alpha", "entity:beta", include_derived=True) == ["entity:alpha", "entity:beta"]


def test_contradiction_candidates_not_duplicated(vault: Path) -> None:
    (vault / "02_Areas/Synthetic/Gamma.md").write_text(
        """---
id: entity:gamma
type: Entity
title: Gamma
---
# Gamma
""",
        encoding="utf-8",
    )
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
claims:
  - id: claim:a
    predicate: related_to
    object: entity:beta
    status: accepted
    valid_from: 2026-01-01
  - id: claim:b
    predicate: related_to
    object: entity:gamma
    status: accepted
    valid_from: 2026-01-01
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        # Accepted claims are also projected into relations; the contradiction
        # must be reported once, not once per projection surface.
        assert len(idx.contradiction_candidates()) == 1


def test_index_connection_is_usable_across_threads(vault: Path) -> None:
    import threading

    with RuntimeIndex(_db(vault)) as idx:
        idx.build(vault, _schema(vault))
        result: dict[str, int] = {}

        def worker() -> None:
            result["objects"] = idx.health()["objects"]

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        assert result["objects"] == 2


def test_export_refuses_protected_and_unowned_destinations(vault: Path) -> None:
    with pytest.raises(ValueError, match="protected"):
        export_okf_bundle(vault, vault / ".agent")
    victim = vault / "02_Areas/Synthetic"
    (victim / ".knowledge-ignore").write_text("scan-ignore", encoding="utf-8")
    with pytest.raises(ValueError, match="ownership manifest"):
        export_okf_bundle(vault, victim)
    assert (victim / "Alpha.md").exists()
