from pathlib import Path

from agentic_vault_knowledge.interop import export_okf_bundle, import_okf_candidates, validate_okf_bundle


def test_okf_bundle_round_trip_candidates(tmp_path: Path) -> None:
    (tmp_path / "02_Areas").mkdir()
    (tmp_path / "02_Areas/Concept.md").write_text("""---
id: concept:synthetic
type: Concept
title: Synthetic Concept
---
# Synthetic Concept

Synthetic body.
""", encoding="utf-8")
    bundle = tmp_path / "export"
    result = export_okf_bundle(tmp_path, bundle)
    assert result["okf_version"] == "0.2"
    assert result["concepts"] == 1
    assert validate_okf_bundle(bundle) == []
    candidates = import_okf_candidates(bundle)
    assert len(candidates) == 1
    assert candidates[0]["frontmatter"]["type"] == "Concept"
    assert candidates[0]["status"] == "candidate"
