from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class RetrievalAdapter(Protocol):
    """Optional retrieval backend contract (embeddings/vector/reranker/etc.).

    Adapters return ranked IDs/snippets only. They never become canonical storage
    and may be removed without losing any vault knowledge.
    """

    name: str

    def search(self, query: str, limit: int = 20) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class RetrievalHit:
    id: str
    score: float
    source: str
    payload: dict[str, Any]


def fused_search(index, query: str, limit: int = 20, adapters: list[RetrievalAdapter] | None = None, graph_expand: bool = True) -> list[dict[str, Any]]:
    """Fuse lexical FTS, optional external retrieval, and one-hop graph context.

    Baseline operation uses SQLite FTS only. Optional adapters can contribute
    candidates, but they are rank inputs rather than authoritative knowledge.
    """
    merged: dict[str, dict[str, Any]] = {}
    lexical = index.search(query, limit)
    for rank, row in enumerate(lexical):
        oid = str(row["id"])
        merged[oid] = {**row, "score": 1.0 / (rank + 1), "retrieval_sources": ["fts"]}

    for adapter in adapters or []:
        for row in adapter.search(query, limit):
            oid = str(row.get("id") or "")
            if not oid:
                continue
            score = float(row.get("score") or 0.0)
            if oid in merged:
                merged[oid]["score"] += score
                merged[oid]["retrieval_sources"].append(adapter.name)
            else:
                merged[oid] = {**row, "id": oid, "score": score, "retrieval_sources": [adapter.name]}

    if graph_expand:
        seeds = list(merged.values())[: min(5, len(merged))]
        for seed in seeds:
            for edge in index.neighbors(seed["id"]):
                neighbor = edge["target_id"] if edge["source_id"] == seed["id"] else edge["source_id"]
                if neighbor not in merged:
                    obj = index.get(neighbor)
                    if obj:
                        merged[neighbor] = {"id": neighbor, "title": obj["title"], "score": seed["score"] * 0.25, "retrieval_sources": ["graph-expansion"]}

    return sorted(merged.values(), key=lambda x: (-float(x.get("score") or 0.0), str(x.get("id"))))[:limit]
