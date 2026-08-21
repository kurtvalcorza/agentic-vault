from __future__ import annotations

import json
import os
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
from agentic_vault_knowledge import interop
from agentic_vault_knowledge.interop import (
    export_jsonld,
    export_okf_bundle,
    export_rdf_ntriples,
    import_okf_candidates,
    validate_okf_bundle,
)
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


# --- Third review pass (head f2c8a5e) regression coverage ---


def test_batch_rechecks_hash_after_validation(vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from agentic_vault_knowledge import transactions

    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    beta = vault / "02_Areas/Synthetic/Beta.md"
    prop_a = propose_frontmatter_patch(alpha, {"updated": "2026-08-21"})
    prop_b = propose_frontmatter_patch(beta, {"updated": "2026-08-21"})
    original_alpha = alpha.read_text(encoding="utf-8")

    def racing_validate(proposals: list, root: Path) -> list:
        # Simulate a concurrent edit landing on a target during validation.
        beta.write_text(beta.read_text(encoding="utf-8") + "\nconcurrent edit\n", encoding="utf-8")
        return []

    monkeypatch.setattr(transactions, "validate_batch", racing_validate)
    with pytest.raises(ConflictError):
        transactions.apply_batch([prop_a, prop_b], vault)
    # No proposal was applied: the untouched target is unchanged.
    assert alpha.read_text(encoding="utf-8") == original_alpha


def test_migrate_operation_still_rejects_demotion(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    demote = {
        "operation": "migrate",
        "path": str(alpha),
        "base_hash": sha256_text(alpha.read_text(encoding="utf-8")),
        "content": "# stripped\n",
    }
    codes = {item.code for item in validate_patch(demote, vault) if item.severity == "error"}
    assert "semantic-demotion" in codes
    # A migrate that keeps the note semantic may change the id without tripping.
    renamed = propose_frontmatter_patch(alpha, {"id": "entity:renamed"})
    renamed["operation"] = "migrate"
    codes2 = {item.code for item in validate_patch(renamed, vault) if item.severity == "error"}
    assert "identity-change" not in codes2 and "semantic-demotion" not in codes2


def test_patch_rejects_protected_workspace_target(vault: Path) -> None:
    (vault / ".claude").mkdir(exist_ok=True)
    protected = vault / ".claude/settings.md"
    protected.write_text("---\nid: x:y\ntype: Entity\ntitle: X\n---\n", encoding="utf-8")
    proposal = propose_frontmatter_patch(protected, {"title": "Z"})
    with pytest.raises(KnowledgeError, match="protected workspace"):
        apply_patch(proposal, vault)
    non_markdown = vault / "02_Areas/Synthetic/data.txt"
    non_markdown.write_text("hi", encoding="utf-8")
    proposal2 = {"path": str(non_markdown), "base_hash": sha256_text("hi"), "content": "bye"}
    with pytest.raises(KnowledgeError, match="Markdown"):
        apply_patch(proposal2, vault)


def test_relation_contradictions_require_overlapping_validity(vault: Path) -> None:
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
    non_overlapping = """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    valid_from: 2026-01-01
    valid_to: 2026-06-01
  - predicate: related_to
    target: entity:gamma
    valid_from: 2026-07-01
    valid_to: 2026-12-01
---
# Alpha
"""
    alpha.write_text(non_overlapping, encoding="utf-8")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        assert idx.contradiction_candidates() == []
        # Make the two intervals overlap; now they contradict.
        alpha.write_text(non_overlapping.replace("2026-07-01", "2026-03-01"), encoding="utf-8")
        assert idx.build(vault, _schema(vault)) == []
        assert len(idx.contradiction_candidates()) == 1


def test_timeline_must_be_a_list(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
timeline:
  event_time: 2026-01-01
  transaction_time: 2026-01-01
  claim: single
  source: source:x
---
# Alpha
""",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "invalid-timeline" in {item.code for item in issues}


def test_refresh_detects_content_change_with_stable_mtime(vault: Path) -> None:
    import os

    path = vault / "02_Areas/Synthetic/Alpha.md"
    stat = path.stat()
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.refresh(vault, _schema(vault)) == []
        before = idx.get("entity:alpha")["title"]
        text = path.read_text(encoding="utf-8")
        assert "Sample Project" in text
        # Same-length edit, then restore the original mtime — a metadata-only
        # fingerprint would miss this and serve stale data.
        path.write_text(text.replace("Sample Project", "Sample Projekt"), encoding="utf-8")
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        idx.refresh(vault, _schema(vault))
        after = idx.get("entity:alpha")["title"]
    assert before == "Sample Project"
    assert after == "Sample Projekt"


def test_batch_rechecks_create_target_absence_after_validation(vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from agentic_vault_knowledge import transactions

    new_path = vault / "02_Areas/Synthetic/New.md"
    proposal = propose_entity(vault, "02_Areas/Synthetic/New.md", {
        "id": "entity:new", "type": "Entity", "title": "New Entity",
    })

    def racing_validate(proposals: list, root: Path) -> list:
        # Simulate a concurrent create landing on the target during validation.
        new_path.write_text("---\nid: entity:other\ntype: Entity\ntitle: Other\n---\n", encoding="utf-8")
        return []

    monkeypatch.setattr(transactions, "validate_batch", racing_validate)
    with pytest.raises(ConflictError):
        transactions.apply_batch([proposal], vault)
    # The concurrently-created file was not overwritten by the stale create.
    assert "entity:other" in new_path.read_text(encoding="utf-8")


# --- Fourth review pass (head 1b14981) regression coverage ---


def test_merged_relation_status_is_valid(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    status: merged
---
# Alpha
""",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "invalid-status" not in {item.code for item in issues}


def test_trace_respects_max_depth(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        assert idx.trace("entity:alpha", "entity:beta", max_depth=0) == []
        assert idx.trace("entity:alpha", "entity:beta", max_depth=1) == ["entity:alpha", "entity:beta"]


def test_generic_generated_folder_is_indexed(vault: Path) -> None:
    note = vault / "01_Projects/report/generated/Note.md"
    note.parent.mkdir(parents=True)
    note.write_text(
        """---
id: entity:gen
type: Entity
title: Generated Report Note
---
# Note
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        assert idx.get("entity:gen") is not None


def test_claim_derived_edge_preserves_validity(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
claims:
  - id: claim:edge
    predicate: related_to
    object: entity:beta
    status: accepted
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
            "SELECT valid_from,valid_to,recorded_at FROM relations WHERE path LIKE '__claim__:%'"
        ).fetchone()
        assert row is not None
        assert row["valid_from"] == "2026-01-01"
        assert row["valid_to"] == "2026-06-01"
        assert str(row["recorded_at"]).startswith("2026-01-02")


def test_graph_export_refuses_markdown_output(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    original = alpha.read_text(encoding="utf-8")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        with pytest.raises(ValueError, match="Markdown"):
            export_jsonld(idx, alpha)
        with pytest.raises(ValueError, match="Markdown"):
            export_rdf_ntriples(idx, alpha)
    assert alpha.read_text(encoding="utf-8") == original


def test_okf_export_uniquifies_reserved_name_collision(vault: Path, tmp_path: Path) -> None:
    synthetic = vault / "02_Areas/Synthetic"
    (synthetic / "index.md").write_text(
        "---\nid: concept:idx\ntype: Concept\ntitle: Idx\n---\n# Idx\n", encoding="utf-8"
    )
    (synthetic / "index-concept.md").write_text(
        "---\nid: concept:idxc\ntype: Concept\ntitle: IdxC\n---\n# IdxC\n", encoding="utf-8"
    )
    out = tmp_path / "bundle"
    export_okf_bundle(vault, out)
    names = {p.name for p in out.rglob("*.md")}
    # The reserved-name rename collides; both objects survive under distinct names.
    assert "index-concept.md" in names
    assert "index-concept-1.md" in names


def test_unsupported_schema_version_is_rejected(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
knowledge_schema: "99.0"
---
# Alpha
""",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "unsupported-schema-version" in {item.code for item in issues}


def test_merged_redirect_cycle_is_rejected(vault: Path) -> None:
    (vault / "02_Areas/Synthetic/A1.md").write_text(
        "---\nid: entity:a1\ntype: Entity\ntitle: A1\nstatus: merged\nredirect_to: entity:a2\n---\n# A1\n",
        encoding="utf-8",
    )
    (vault / "02_Areas/Synthetic/A2.md").write_text(
        "---\nid: entity:a2\ntype: Entity\ntitle: A2\nstatus: merged\nredirect_to: entity:a1\n---\n# A2\n",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "redirect-cycle" in {item.code for item in issues}


def test_source_object_authority_is_validated(vault: Path) -> None:
    (vault / "02_Areas/Synthetic/Src.md").write_text(
        "---\nid: source:x\ntype: Source\ntitle: Src\nsource_authority: primry\n---\n# Src\n",
        encoding="utf-8",
    )
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "invalid-source-authority" in {item.code for item in issues}


def test_rdf_export_excludes_inferred_relations(vault: Path, tmp_path: Path) -> None:
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
    out = tmp_path / "graph.nt"
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        export_rdf_ntriples(idx, out)
    content = out.read_text(encoding="utf-8")
    # The inferred edge must not appear as a plain asserted triple.
    assert "relation:related_to" not in content


# --- Fifth review pass (head 612b4c9) regression coverage ---


def test_graph_export_refuses_protected_config_output(vault: Path) -> None:
    (vault / ".claude").mkdir(exist_ok=True)
    (vault / ".git").mkdir(exist_ok=True)
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        with pytest.raises(ValueError, match="protected workspace"):
            export_jsonld(idx, vault / ".claude/settings.json")
        with pytest.raises(ValueError, match="protected workspace"):
            export_rdf_ntriples(idx, vault / ".git/config")


def test_semantic_note_requires_authored_title(vault: Path) -> None:
    note = vault / "02_Areas/Synthetic/NoTitle.md"
    note.write_text("---\nid: entity:notitle\ntype: Entity\n---\n# Heading Only\n", encoding="utf-8")
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "missing-title" in {item.code for item in issues}


def test_patch_rejects_agent_workspace_target(vault: Path) -> None:
    target = vault / ".agent/skills/demo/SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\nid: x:y\ntype: Entity\ntitle: X\n---\n", encoding="utf-8")
    proposal = propose_frontmatter_patch(target, {"title": "Z"})
    with pytest.raises(KnowledgeError, match="protected workspace"):
        apply_patch(proposal, vault)


def test_okf_import_demotes_nested_status_and_derivation(vault: Path, tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / ".knowledge-ignore").write_text("x", encoding="utf-8")
    (bundle / "index.md").write_text("---\nokf_version: '0.2'\ntype: Index\ntitle: I\n---\n", encoding="utf-8")
    (bundle / "C.md").write_text(
        """---
id: concept:c
type: Concept
title: C
status: accepted
relations:
  - predicate: related_to
    target: concept:d
    status: accepted
    derivation: asserted
---
# C
""",
        encoding="utf-8",
    )
    candidates = import_okf_candidates(bundle)
    fm = next(c["frontmatter"] for c in candidates if c["concept_id"].endswith("C"))
    assert fm["status"] == "candidate"
    assert fm["relations"][0]["status"] == "candidate"
    assert fm["relations"][0]["derivation"] == "imported"


def test_relation_review_metadata_is_projected(vault: Path) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    extraction_confidence: 0.5
    claim_confidence: 0.9
    review_status: pending
    created_by: agent:test
    reviewed_by:
      - user:reviewer
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        row = idx.conn.execute(
            "SELECT extraction_confidence,claim_confidence,review_status,created_by,reviewed_by_json "
            "FROM relations WHERE source_id='entity:alpha' AND predicate='related_to'"
        ).fetchone()
        assert row["review_status"] == "pending"
        assert row["created_by"] == "agent:test"
        assert row["claim_confidence"] == 0.9
        assert json.loads(row["reviewed_by_json"]) == ["user:reviewer"]


# --- Sixth review pass (head b848a92) regression coverage ---


def test_graph_export_allowed_in_agent_outputs(vault: Path) -> None:
    out = vault / ".agent/outputs/knowledge.jsonld"
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        export_jsonld(idx, out)
    assert out.exists()


def test_okf_export_rejects_nested_protected_destination(vault: Path) -> None:
    with pytest.raises(ValueError, match="protected workspace"):
        export_okf_bundle(vault, vault / ".claude/generated/okf")


def test_cli_propose_rejects_secret_target(vault: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    (vault / ".env").write_text("SECRET=supersecret\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["vault-knowledge", "--vault", str(vault), "propose", ".env", '{"title": "x"}'])
    with pytest.raises(SystemExit):
        cli.main()
    captured = capsys.readouterr()
    assert "supersecret" not in captured.out


def test_neighbors_include_derived_keeps_accepted_filter(vault: Path) -> None:
    (vault / "02_Areas/Synthetic/Gamma.md").write_text(
        "---\nid: entity:gamma\ntype: Entity\ntitle: Gamma\n---\n# Gamma\n", encoding="utf-8"
    )
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:beta
    status: retracted
  - predicate: related_to
    target: entity:gamma
    status: accepted
    derivation: inferred
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        neighbors = idx.neighbors("entity:alpha", include_derived=True)
        targets = {r["target_id"] for r in neighbors}
        assert "entity:gamma" in targets   # accepted inferred edge is included
        assert "entity:beta" not in targets  # retracted edge stays filtered out


@pytest.mark.skipif(
    os.name == "nt",
    reason="POSIX permission bits are not representable on NTFS: os.chmod only "
    "toggles the read-only attribute, so 0o644 reads back as 0o666.",
)
def test_apply_patch_preserves_file_mode(vault: Path) -> None:
    import stat as stat_mod

    path = vault / "02_Areas/Synthetic/Alpha.md"
    os.chmod(path, 0o644)
    proposal = propose_frontmatter_patch(path, {"title": "New Title"})
    apply_patch(proposal, vault)
    assert stat_mod.S_IMODE(path.stat().st_mode) == 0o644


def test_duplicate_frontmatter_keys_rejected() -> None:
    with pytest.raises(KnowledgeError, match="duplicate frontmatter key"):
        split_frontmatter("---\nid: x:y\nid: x:z\ntype: Entity\ntitle: Dup\n---\n# Dup\n")


# --- Seventh review pass (head 2bec376) regression coverage ---


def test_graph_export_refuses_root_secret_files(vault: Path) -> None:
    (vault / ".env").write_text("SECRET=supersecret\n", encoding="utf-8")
    (vault / "mcp.json").write_text("{}\n", encoding="utf-8")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        with pytest.raises(ValueError):
            export_jsonld(idx, vault / ".env")
        with pytest.raises(ValueError):
            export_rdf_ntriples(idx, vault / "mcp.json")
    assert "supersecret" in (vault / ".env").read_text(encoding="utf-8")


def test_propose_relation_defaults_to_proposed(vault: Path) -> None:
    from agentic_vault_knowledge.proposals import propose_relation

    proposal = propose_relation(vault, "02_Areas/Synthetic/Alpha.md", {
        "predicate": "related_to", "target": "entity:beta",
    })
    assert proposal["frontmatter"]["relations"][-1]["status"] == "proposed"


def test_patch_rejects_target_under_knowledge_ignore(vault: Path) -> None:
    ignored = vault / "02_Areas/Ignored"
    ignored.mkdir(parents=True)
    (ignored / ".knowledge-ignore").write_text("x", encoding="utf-8")
    target = ignored / "Note.md"
    target.write_text("---\nid: entity:ign\ntype: Entity\ntitle: I\n---\n# I\n", encoding="utf-8")
    proposal = propose_frontmatter_patch(target, {"title": "Z"})
    with pytest.raises(KnowledgeError, match="knowledge-ignore"):
        apply_patch(proposal, vault)


def test_patch_allowed_in_generic_generated_folder(vault: Path) -> None:
    note = vault / "01_Projects/report/generated/Summary.md"
    note.parent.mkdir(parents=True)
    note.write_text("---\nid: entity:sum\ntype: Entity\ntitle: Summary\n---\n# S\n", encoding="utf-8")
    proposal = propose_frontmatter_patch(note, {"title": "Summary Two"})
    apply_patch(proposal, vault)  # must not raise: a real PARA 'generated' folder is canonical
    assert "Summary Two" in note.read_text(encoding="utf-8")


def test_symlinked_note_escaping_vault_is_skipped(vault: Path, tmp_path: Path) -> None:
    import os

    external = tmp_path.parent / "external_note_escape.md"
    external.write_text("---\nid: entity:external\ntype: Entity\ntitle: External\n---\n# X\n", encoding="utf-8")
    link = vault / "02_Areas/Synthetic/Link.md"
    try:
        os.symlink(external, link)
    except (OSError, NotImplementedError):
        import pytest as _pytest
        _pytest.skip("symlinks not supported here")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        assert idx.get("entity:external") is None


def test_cli_propose_serializes_date_values(vault: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    alpha = vault / "02_Areas/Synthetic/Alpha.md"
    alpha.write_text(
        "---\nid: entity:alpha\ntype: Entity\ntitle: Alpha\ncreated: 2026-08-21\n---\n# Alpha\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys, "argv",
        ["vault-knowledge", "--vault", str(vault), "propose", "02_Areas/Synthetic/Alpha.md", '{"title": "New"}'],
    )
    assert cli.main() == 0
    assert "2026-08-21" in capsys.readouterr().out


def test_search_orders_by_relevance(vault: Path) -> None:
    (vault / "02_Areas/Synthetic/Buried.md").write_text(
        "---\nid: entity:buried\ntype: Entity\ntitle: Buried\n---\n# Buried\n" + ("filler " * 200) + "zeta\n",
        encoding="utf-8",
    )
    (vault / "02_Areas/Synthetic/Titled.md").write_text(
        "---\nid: entity:titled\ntype: Entity\ntitle: Zeta\n---\n# Zeta\n", encoding="utf-8"
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        top = idx.search("zeta", limit=1)
        assert top and top[0]["id"] == "entity:titled"


def test_fused_search_discards_stale_adapter_hits(vault: Path) -> None:
    from agentic_vault_knowledge.retrieval import fused_search

    class StaleAdapter:
        name = "stale"

        def search(self, query: str, limit: int = 20):
            return [{"id": "entity:ghost", "score": 99.0, "title": "Ghost"}]

    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        results = fused_search(idx, "sample", adapters=[StaleAdapter()], graph_expand=False)
        assert "entity:ghost" not in {r["id"] for r in results}


# --- Eighth review pass (head 2681a65) regression coverage ---


def test_okf_export_rechecks_ownership_before_rmtree(vault: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = vault / ".agent/outputs/okf"
    export_okf_bundle(vault, out)  # first export creates an owned bundle
    real_parse = interop.parse_note

    def racing_parse(path, root=None):
        # Simulate a concurrent process replacing the owned bundle mid-export.
        (out / ".okf-bundle").write_text("not-ours\n", encoding="utf-8")
        return real_parse(path, root)

    monkeypatch.setattr(interop, "parse_note", racing_parse)
    with pytest.raises(ValueError, match="ownership manifest changed"):
        export_okf_bundle(vault, out)


def test_graph_export_refuses_symlink_output(vault: Path) -> None:
    import os

    (vault / ".env").write_text("SECRET=supersecret\n", encoding="utf-8")
    link = vault / ".agent/outputs/knowledge.jsonld"
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(vault / ".env", link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported here")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        with pytest.raises(ValueError, match="symlink"):
            export_jsonld(idx, link)
    assert "supersecret" in (vault / ".env").read_text(encoding="utf-8")


def test_contradictions_across_multiple_subject_groups(vault: Path) -> None:
    for oid in ("entity:gamma", "entity:delta"):
        (vault / f"02_Areas/Synthetic/{oid.split(':')[1]}.md").write_text(
            f"---\nid: {oid}\ntype: Entity\ntitle: {oid}\n---\n# {oid}\n", encoding="utf-8"
        )
    (vault / "02_Areas/Synthetic/Alpha.md").write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
claims:
  - id: claim:a1
    predicate: related_to
    object: entity:beta
    status: accepted
    valid_from: 2026-01-01
  - id: claim:a2
    predicate: related_to
    object: entity:gamma
    status: accepted
    valid_from: 2026-01-01
---
# Alpha
""",
        encoding="utf-8",
    )
    (vault / "02_Areas/Synthetic/Beta.md").write_text(
        """---
id: entity:beta
type: Entity
title: Beta
claims:
  - id: claim:b1
    predicate: related_to
    object: entity:gamma
    status: accepted
    valid_from: 2026-01-01
  - id: claim:b2
    predicate: related_to
    object: entity:delta
    status: accepted
    valid_from: 2026-01-01
---
# Beta
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        subjects = {c["subject_id"] for c in idx.contradiction_candidates() if c.get("subject_id")}
        assert {"entity:alpha", "entity:beta"} <= subjects  # both groups detected past the break


def test_knowledge_schema_without_id_is_flagged(vault: Path) -> None:
    note = vault / "02_Areas/Synthetic/Partial.md"
    note.write_text("---\nknowledge_schema: '0.1.0'\ntype: Entity\ntitle: Partial\n---\n# P\n", encoding="utf-8")
    issues = validate_vault_semantics(vault, _schema(vault))
    assert "incomplete-semantic" in {item.code for item in issues}


def test_symlink_into_ignored_tree_is_skipped(vault: Path) -> None:
    import os

    ignored = vault / "02_Areas/Ignored"
    ignored.mkdir(parents=True)
    (ignored / ".knowledge-ignore").write_text("x", encoding="utf-8")
    real = ignored / "Hidden.md"
    real.write_text("---\nid: entity:hidden\ntype: Entity\ntitle: Hidden\n---\n# H\n", encoding="utf-8")
    link = vault / "02_Areas/Synthetic/Visible.md"
    try:
        os.symlink(real, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported here")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        assert idx.get("entity:hidden") is None


def test_merged_redirect_repoints_graph_edges(vault: Path) -> None:
    (vault / "02_Areas/Synthetic/New.md").write_text(
        "---\nid: entity:new\ntype: Entity\ntitle: New\n---\n# New\n", encoding="utf-8"
    )
    (vault / "02_Areas/Synthetic/Old.md").write_text(
        "---\nid: entity:old\ntype: Entity\ntitle: Old\nstatus: merged\nredirect_to: entity:new\n---\n# Old\n",
        encoding="utf-8",
    )
    (vault / "02_Areas/Synthetic/Alpha.md").write_text(
        """---
id: entity:alpha
type: Entity
title: Alpha
relations:
  - predicate: related_to
    target: entity:old
---
# Alpha
""",
        encoding="utf-8",
    )
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        endpoints = set()
        for edge in idx.neighbors("entity:new"):
            endpoints.add(edge["source_id"])
            endpoints.add(edge["target_id"])
        assert "entity:alpha" in endpoints  # edge repointed from merged old id to new


def test_validate_okf_rejects_missing_bundle(tmp_path: Path) -> None:
    issues = validate_okf_bundle(tmp_path / "does-not-exist")
    assert issues and issues[0]["code"] == "missing-bundle"


# --- Ninth review pass (head 3905b4c) regression coverage ---


def test_graph_export_refuses_unowned_existing_file(vault: Path) -> None:
    system = vault / "System"
    system.mkdir(exist_ok=True)
    target = system / "settings.json"
    target.write_text('{"unrelated": true}\n', encoding="utf-8")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        # A matching .json extension is not ownership evidence: refuse + preserve.
        with pytest.raises(ValueError, match="not an agentic-vault export"):
            export_jsonld(idx, target)
        assert '"unrelated": true' in target.read_text(encoding="utf-8")
        # Explicit overwrite opt-in is honored...
        export_jsonld(idx, target, overwrite=True)
        assert "@generator" in target.read_text(encoding="utf-8")
        # ...and a prior owned export can be re-exported without the opt-in.
        export_jsonld(idx, target)


def test_rdf_export_refuses_unowned_existing_file(vault: Path) -> None:
    target = vault / "System" / "graph.nt"
    target.parent.mkdir(exist_ok=True)
    target.write_text("<urn:foreign> <urn:p> <urn:o> .\n", encoding="utf-8")
    with RuntimeIndex(_db(vault)) as idx:
        assert idx.build(vault, _schema(vault)) == []
        with pytest.raises(ValueError, match="not an agentic-vault export"):
            export_rdf_ntriples(idx, target)
        assert "urn:foreign" in target.read_text(encoding="utf-8")
        export_rdf_ntriples(idx, target, overwrite=True)
        export_rdf_ntriples(idx, target)  # now owned -> allowed
