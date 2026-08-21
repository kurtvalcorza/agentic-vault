from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .core import ParsedNote


class EnrichmentAdapter(Protocol):
    """Agent/model-neutral semantic enrichment adapter.

    Implementations inspect already parsed Markdown and return candidate entities,
    claims, or relations. They never receive a write handle to canonical files.
    """

    name: str

    def extract(self, note: ParsedNote) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class EnrichmentCandidate:
    kind: str
    payload: dict[str, Any]
    adapter: str
    status: str = "candidate"
    derivation: str = "inferred"


def collect_candidates(note: ParsedNote, adapters: list[EnrichmentAdapter]) -> list[EnrichmentCandidate]:
    """Run optional enrichers and normalize every result to non-canonical candidate state."""
    out: list[EnrichmentCandidate] = []
    for adapter in adapters:
        for raw in adapter.extract(note):
            if not isinstance(raw, dict):
                raise TypeError(f"enrichment adapter {adapter.name} returned non-mapping candidate")
            kind = str(raw.get("kind") or "claim")
            payload = dict(raw.get("payload") or raw)
            # Adapter attempts to self-promote are intentionally overridden.
            payload["status"] = "candidate"
            if payload.get("derivation") in (None, "asserted"):
                payload["derivation"] = "inferred"
            payload.setdefault("created_by", f"adapter:{adapter.name}")
            out.append(EnrichmentCandidate(kind=kind, payload=payload, adapter=adapter.name, derivation=str(payload["derivation"])))
    return out
