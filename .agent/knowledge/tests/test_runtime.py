from __future__ import annotations

from pathlib import Path

import pytest

from agentic_vault_knowledge.core import (
    ConflictError,
    apply_patch,
    iter_markdown,
    parse_note,
    propose_frontmatter_patch,
    validate_note,
)
from agentic_vault_knowledge.runtime_index import RuntimeIndex


@pytest.fixture()
def vault(tmp_path: Path) -> Path:
    (tmp_path / ".agent/knowledge/schema").mkdir(parents=True)
    source_schema = Path(__file__).parents[1] / "schema"
    for name in ("relations.yaml", "core.yaml", "VERSION"):
        (tmp_path / ".agent/knowledge/schema" / name).write_text((source_schema / name).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "01_Projects/Sample Project").mkdir(parents=True)
    (tmp_path / "02_Areas/Sample").mkdir(parents=True)
    (tmp_path / "01_Projects/Sample Project/Sample Project.md").write_text(
        """---
id: project:sample-project
type: Project
title: Sample Project
aliases: [Project Sample]
status: active
relations:
  - predicate: related_to
    target: concept:sample-concept
    derivation: asserted
    status: accepted
    evidence:
      - source: source:sample-source
        locator:
          type: heading
          value: Evidence
timeline:
  - event_time: '2026-01-01'
    transaction_time: '2026-01-02'
    claim: Sample project created
    source: '[[Sample Source]]'
---
# Sample Project

See [[Sample Concept]].
""",
        encoding="utf-8",
    )
    (tmp_path / "02_Areas/Sample/Sample Concept.md").write_text(
        """---
id: concept:sample-concept
type: Concept
title: Sample Concept
status: accepted
---
# Sample Concept

A synthetic concept used only for tests.
""",
        encoding="utf-8",
    )
    return tmp_path


def test_parse_separates_navigation_and_semantics(vault: Path) -> None:
    note = parse_note(vault / "01_Projects/Sample Project/Sample Project.md", vault)
    assert note.object_id == "project:sample-project"
    assert note.wikilinks == ("Sample Source", "Sample Concept")
    assert note.relations[0].predicate == "related_to"
    assert note.relations[0].target == "concept:sample-concept"


def test_validation_accepts_fixture(vault: Path) -> None:
    note = parse_note(vault / "01_Projects/Sample Project/Sample Project.md", vault)
    registry = {"related_to": {}}
    assert validate_note(note, registry) == []


def test_index_rebuild_and_queries(vault: Path) -> None:
    db = vault / ".agent/knowledge/generated/knowledge.db"
    schema = vault / ".agent/knowledge/schema"
    with RuntimeIndex(db) as idx:
        assert idx.build(vault, schema) == []
        assert idx.get("project:sample-project")["title"] == "Sample Project"
        assert idx.resolve("Project Sample")[0]["id"] == "project:sample-project"
        assert idx.trace("project:sample-project", "concept:sample-concept") == ["project:sample-project", "concept:sample-concept"]
        assert idx.timeline("project:sample-project")[0]["claim"] == "Sample project created"
        assert idx.health()["objects"] == 2
        idx.rebuild(vault, schema)
        assert idx.health()["objects"] == 2


def test_incremental_reindex(vault: Path) -> None:
    db = vault / ".agent/knowledge/generated/knowledge.db"
    schema = vault / ".agent/knowledge/schema"
    path = vault / "02_Areas/Sample/Sample Concept.md"
    with RuntimeIndex(db) as idx:
        idx.build(vault, schema)
        before = idx.get("concept:sample-concept")["title"]
        path.write_text(path.read_text(encoding="utf-8").replace("title: Sample Concept", "title: Renamed Concept"), encoding="utf-8")
        idx.build(vault, schema)
        after = idx.get("concept:sample-concept")["title"]
    assert before == "Sample Concept"
    assert after == "Renamed Concept"


def test_hash_bound_atomic_patch_detects_conflict(vault: Path) -> None:
    path = vault / "02_Areas/Sample/Sample Concept.md"
    proposal = propose_frontmatter_patch(path, {"title": "Changed"})
    path.write_text(path.read_text(encoding="utf-8") + "\nexternal edit\n", encoding="utf-8")
    with pytest.raises(ConflictError):
        apply_patch(proposal, vault)


def test_patch_applies_when_unchanged(vault: Path) -> None:
    path = vault / "02_Areas/Sample/Sample Concept.md"
    proposal = propose_frontmatter_patch(path, {"title": "Changed"})
    apply_patch(proposal, vault)
    assert "title: Changed" in path.read_text(encoding="utf-8")


COMMAND_DEFINITION = """---
argument-hint: [optional: "interim" snapshot]
---
# Report
"""

SKILL_TEMPLATE = """---
title: {{title}}
---
# {{title}}
"""


def _scanned(vault: Path) -> set[str]:
    return {p.relative_to(vault).as_posix() for p in iter_markdown(vault)}


def test_dot_directories_are_never_scanned(vault: Path) -> None:
    """Agent workspaces and tool config are not canonical notes.

    Their Markdown is command definitions and skill templates whose frontmatter
    is not note frontmatter, so scanning them turns the fail-closed build into a
    hard stop on files that were never knowledge in the first place.
    """
    # A slash-command definition: valid YAML for a command, fatal as a note
    # (the colon inside the flow sequence is a parse error).
    (vault / ".claude/commands").mkdir(parents=True)
    (vault / ".claude/commands/report.md").write_text(COMMAND_DEFINITION, encoding="utf-8")
    # A skill template using placeholder frontmatter (unhashable dict as a key).
    (vault / ".codex/prompts").mkdir(parents=True)
    (vault / ".codex/prompts/note.md").write_text(SKILL_TEMPLATE, encoding="utf-8")
    # Obsidian's own config directory.
    (vault / ".obsidian/plugins/example").mkdir(parents=True)
    (vault / ".obsidian/plugins/example/README.md").write_text("# plugin\n", encoding="utf-8")

    scanned = _scanned(vault)
    from_dot_dirs = {
        path for path in scanned if any(part.startswith(".") for part in path.split("/")[:-1])
    }
    assert not from_dot_dirs, f"dot-directory Markdown was scanned: {sorted(from_dot_dirs)}"
    # ...while ordinary PARA notes are still picked up.
    assert "02_Areas/Sample/Sample Concept.md" in scanned


def test_non_dot_trees_still_need_an_explicit_marker(vault: Path) -> None:
    """The dot rule is not a licence to guess at ordinary folder names."""
    legacy = vault / "04_Archives/legacy"
    legacy.mkdir(parents=True)
    (legacy / "Old Note.md").write_text("# Old\n", encoding="utf-8")
    assert "04_Archives/legacy/Old Note.md" in _scanned(vault)

    (legacy / ".knowledge-ignore").write_text("skip\n", encoding="utf-8")
    assert "04_Archives/legacy/Old Note.md" not in _scanned(vault)
