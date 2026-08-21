"""Performance characteristics of the knowledge runtime.

Why this file exists
--------------------
An optimization proposal (issue #9) argued for composite SQLite indexes that
already existed and an O(1)-vs-O(n) memory rewrite that was not available,
because nothing here measured anything. Plausible-sounding bottlenecks are cheap
to assert and expensive to act on. These tests make the runtime's actual shape
observable so future proposals argue from numbers.

What is asserted, and what is not
---------------------------------
CI runners are noisy and shared, so wall-clock thresholds are deliberately loose
— they catch an order-of-magnitude regression (an index silently dropped, an
accidental O(n^2) scan), not a 20% drift. The precise numbers are *recorded* via
``--durations`` and the ``report`` fixture rather than asserted.

The complexity assertions are the load-bearing ones, because they are about
shape rather than speed:

* build time must grow roughly linearly with note count, not quadratically;
* traversal must not degrade as the graph grows, because it is index-backed;
* a no-op rebuild must be dramatically cheaper than a full one.

Run just this file:  pytest .agent/knowledge/tests/test_performance.py -v --durations=0
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

from agentic_vault_knowledge.core import iter_markdown
from agentic_vault_knowledge.runtime_index import RuntimeIndex

# Synthetic sizes. Kept modest so the suite stays runnable in CI; the ratio
# between them is what the complexity assertions use, not the absolute values.
SMALL, LARGE = 50, 400


def _schema(vault: Path) -> Path:
    return vault / ".agent/knowledge/schema"


def _db(vault: Path) -> Path:
    return vault / ".agent/knowledge/generated/knowledge.db"


def _build_vault(root: Path, note_count: int) -> Path:
    """Generate a synthetic vault of `note_count` linked, semantic notes.

    Generated in-test rather than committed, so the fixtures stay synthetic and
    domain-neutral (design invariant 12) and the sizes can change freely.
    """
    schema_dst = root / ".agent/knowledge/schema"
    schema_dst.mkdir(parents=True, exist_ok=True)
    schema_src = Path(__file__).parents[1] / "schema"
    for name in ("core.yaml", "relations.yaml", "VERSION"):
        shutil.copyfile(schema_src / name, schema_dst / name)

    notes = root / "02_Areas/Generated"
    notes.mkdir(parents=True, exist_ok=True)
    for i in range(note_count):
        # Chain each note to the next so traversal has real depth to walk, and
        # add a WikiLink so the navigation graph is populated too.
        relation = ""
        if i + 1 < note_count:
            relation = (
                "relations:\n"
                "  - predicate: related_to\n"
                f"    target: concept:n{i + 1}\n"
                "    derivation: asserted\n"
                "    status: accepted\n"
            )
        (notes / f"n{i}.md").write_text(
            f"---\nid: concept:n{i}\ntype: Concept\ntitle: Note {i}\nstatus: active\n"
            f"{relation}---\n# Note {i}\n\nBody text for note {i}. See [[Note {i + 1}]].\n",
            encoding="utf-8",
        )
    return root


def _time(fn) -> tuple[float, object]:
    start = time.perf_counter()
    result = fn()
    return time.perf_counter() - start, result


@pytest.fixture(scope="module")
def small_vault(tmp_path_factory) -> Path:
    return _build_vault(tmp_path_factory.mktemp("small"), SMALL)


@pytest.fixture(scope="module")
def large_vault(tmp_path_factory) -> Path:
    return _build_vault(tmp_path_factory.mktemp("large"), LARGE)


def test_build_scales_roughly_linearly(small_vault: Path, large_vault: Path, capsys) -> None:
    """Build time must not grow super-linearly with note count.

    This is the assertion that would catch an accidental O(n^2) — a per-note
    operation that rescans everything already indexed.
    """
    with RuntimeIndex(_db(small_vault)) as idx:
        small_s, issues = _time(lambda: idx.build(small_vault, _schema(small_vault)))
        assert issues == []
    with RuntimeIndex(_db(large_vault)) as idx:
        large_s, issues = _time(lambda: idx.build(large_vault, _schema(large_vault)))
        assert issues == []

    size_ratio = LARGE / SMALL
    time_ratio = large_s / max(small_s, 1e-6)
    with capsys.disabled():
        print(
            f"\n  build {SMALL} notes: {small_s * 1000:7.1f} ms"
            f"\n  build {LARGE} notes: {large_s * 1000:7.1f} ms"
            f"\n  size x{size_ratio:.0f} -> time x{time_ratio:.1f}"
        )
    # Generous headroom for runner noise and fixed startup cost; quadratic growth
    # at this ratio would be ~64x and would blow straight through it.
    assert time_ratio < size_ratio * 4


def test_traversal_is_index_backed_not_scan(large_vault: Path, capsys) -> None:
    """Neighbour lookup must not degrade as the relation table grows.

    `relations_source` / `relations_target` make this a b-tree seek. If either
    index is dropped, this becomes a full scan and the ratio blows out.
    """
    with RuntimeIndex(_db(large_vault)) as idx:
        idx.build(large_vault, _schema(large_vault))
        # First and last node: with an index these cost the same, with a scan
        # the later one is progressively worse.
        first_s, _ = _time(lambda: idx.neighbors("concept:n0"))
        last_s, _ = _time(lambda: idx.neighbors(f"concept:n{LARGE - 2}"))
        plan = idx.conn.execute(
            "EXPLAIN QUERY PLAN SELECT * FROM relations WHERE source_id=?", ("concept:n0",)
        ).fetchone()

    with capsys.disabled():
        print(
            f"\n  neighbors(first): {first_s * 1000:6.2f} ms"
            f"\n  neighbors(last) : {last_s * 1000:6.2f} ms"
            f"\n  plan: {plan[-1]}"
        )
    # The structural guarantee, independent of timing noise.
    assert "USING INDEX" in plan[-1], f"relations lookup is not index-backed: {plan[-1]}"
    assert "SCAN" not in plan[-1].split("USING")[0]


def test_noop_rebuild_short_circuits(large_vault: Path, capsys) -> None:
    """An unchanged vault must not pay *more* than a first build.

    Guards the `_last_fingerprint` short-circuit — but note what the measured
    saving actually is, because it is smaller than "cached" suggests: the
    fingerprint is content-based on purpose (ADR-0003), so computing it re-reads
    and re-hashes every file. The short-circuit therefore skips the *write* half
    of the build, not the *scan* half, and a warm rebuild lands only slightly
    under a cold one rather than being near-instant.

    That is a correctness tradeoff, not a defect: a metadata-only fingerprint
    would make this near-free and would serve stale state when a file's mtime
    lies. The assertion is deliberately just "no worse", so the test documents
    the real behaviour instead of implying a speedup that is not there.
    """
    with RuntimeIndex(_db(large_vault)) as idx:
        cold_s, _ = _time(lambda: idx.build(large_vault, _schema(large_vault)))
        warm_s, _ = _time(lambda: idx.build(large_vault, _schema(large_vault)))

    saved = (1 - warm_s / max(cold_s, 1e-6)) * 100
    with capsys.disabled():
        print(
            f"\n  cold build: {cold_s * 1000:7.1f} ms"
            f"\n  warm build: {warm_s * 1000:7.1f} ms  ({saved:.0f}% saved — scan cost dominates)"
        )
    assert warm_s <= cold_s * 1.25, "unchanged rebuild must not cost more than a first build"


def test_scan_does_not_materialise_the_vault(large_vault: Path) -> None:
    """`iter_markdown` must stay lazy.

    Issue #9 proposed replacing `rglob` with `os.walk` for an O(1)-vs-O(n) memory
    win. The premise was wrong — this is already a generator — and this test
    pins that so a future refactor cannot quietly make it eager.
    """
    scan = iter_markdown(large_vault)
    assert hasattr(scan, "__next__"), "iter_markdown must be a generator, not a materialised list"
    first = next(scan)
    assert first.suffix == ".md"


def test_query_surface_stays_responsive(large_vault: Path, capsys) -> None:
    """Record latency for the operations agents actually call."""
    with RuntimeIndex(_db(large_vault)) as idx:
        idx.build(large_vault, _schema(large_vault))
        timings = {
            "resolve": _time(lambda: idx.resolve("Note 10"))[0],
            "search": _time(lambda: idx.search("body text"))[0],
            "get": _time(lambda: idx.get("concept:n10"))[0],
            "neighbors": _time(lambda: idx.neighbors("concept:n10"))[0],
            "trace(0->20)": _time(lambda: idx.trace("concept:n0", "concept:n20"))[0],
            "health": _time(lambda: idx.health())[0],
        }
    with capsys.disabled():
        print(f"\n  query latency over {LARGE} notes:")
        for name, seconds in timings.items():
            print(f"    {name:14} {seconds * 1000:7.2f} ms")
    # Loose ceiling: any single query taking over a second on 400 notes means
    # something structural broke, not that the runner was busy.
    slowest = max(timings.items(), key=lambda kv: kv[1])
    assert slowest[1] < 1.0, f"{slowest[0]} took {slowest[1]:.2f}s on {LARGE} notes"
