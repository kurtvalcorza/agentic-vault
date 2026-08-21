from __future__ import annotations

from pathlib import Path

from agentic_vault_knowledge.core import parse_note
from agentic_vault_knowledge.enrichment import collect_candidates
from agentic_vault_knowledge.interop import export_rdf_ntriples
from agentic_vault_knowledge.retrieval import fused_search
from agentic_vault_knowledge.runtime_index import RuntimeIndex


class FakeEnricher:
    name = "fake"

    def extract(self, note):
        return [{"kind": "claim", "payload": {"predicate": "related_to", "object": "concept:other", "status": "accepted", "derivation": "asserted"}}]


class FakeRetriever:
    name = "fake-vector"

    def search(self, query: str, limit: int = 20):
        return [{"id": "concept:other", "score": 0.8, "snippet": "vector candidate"}]


def _vault(tmp_path: Path) -> Path:
    schema_src = Path(__file__).parents[1] / "schema"
    schema = tmp_path / ".agent/knowledge/schema"
    schema.mkdir(parents=True)
    for name in ("core.yaml", "relations.yaml", "VERSION"):
        (schema / name).write_text((schema_src / name).read_text(encoding="utf-8"), encoding="utf-8")
    notes = tmp_path / "02_Areas"
    notes.mkdir()
    (notes / "Main.md").write_text("""---
id: concept:main
type: Concept
title: Main Concept
relations:
  - predicate: related_to
    target: concept:other
    status: accepted
    derivation: asserted
---
# Main Concept

Retrieval anchor phrase.
""", encoding="utf-8")
    (notes / "Other.md").write_text("""---
id: concept:other
type: Concept
title: Other Concept
---
# Other Concept
""", encoding="utf-8")
    return tmp_path


def test_enrichment_cannot_self_promote(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    note = parse_note(vault / "02_Areas/Main.md", vault)
    candidate = collect_candidates(note, [FakeEnricher()])[0]
    assert candidate.status == "candidate"
    assert candidate.payload["status"] == "candidate"
    assert candidate.payload["derivation"] == "inferred"
    assert candidate.payload["created_by"] == "adapter:fake"


def test_fused_retrieval_accepts_optional_adapter_without_canonicalizing_it(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        idx.build(vault, vault / ".agent/knowledge/schema")
        hits = fused_search(idx, "Retrieval", adapters=[FakeRetriever()])
        ids = {h["id"] for h in hits}
        assert {"concept:main", "concept:other"} <= ids
        assert idx.get("concept:other")["frontmatter_json"]  # runtime object remains sourced from Markdown


def test_rdf_export_is_disposable_projection(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    output = tmp_path / "export.nt"
    with RuntimeIndex(vault / ".agent/knowledge/generated/knowledge.db") as idx:
        idx.build(vault, vault / ".agent/knowledge/schema")
        result = export_rdf_ntriples(idx, output)
    text = output.read_text(encoding="utf-8")
    assert result["format"] == "application/n-triples"
    assert "urn:agentic-vault:object:concept%3Amain" in text
    assert "urn:agentic-vault:relation:related_to" in text
