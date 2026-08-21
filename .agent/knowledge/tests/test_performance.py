"""Performance and complexity characteristics of the knowledge runtime.

Why this file exists
--------------------
An optimization proposal (issue #9) argued for composite SQLite indexes that
already existed and an O(1)-vs-O(n) memory rewrite that was not available,
because nothing here measured anything. Plausible-sounding bottlenecks are cheap
to assert and expensive to act on.

What is asserted, and what is not
---------------------------------
CI runners are noisy and shared, so wall-clock thresholds are deliberately loose
— they catch an order-of-magnitude regression, not a 20% drift. Precise numbers
are *recorded* rather than asserted.

The structural assertions are the load-bearing ones, and they are written to
exercise the code path the runtime actually takes:

* build time grows with note count, not its square;
* the query plan is checked for the predicate `neighbors()` really issues
  (``source_id=? OR target_id=?``), so dropping *either* index fails the test;
* the fingerprint short-circuit is exercised through ``refresh()``, which is the
  method that implements it — ``build()`` does not;
* ``iter_markdown`` is proven lazy by counting how much of the underlying walk
  is consumed before the first yield, not merely by its type;
* traced paths are asserted reachable, so a latency number can never come from a
  search that silently bottomed out on ``max_depth``.

Run just this file:  pytest .agent/knowledge/tests/test_performance.py -v
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

from agentic_vault_knowledge import core as core_mod
from agentic_vault_knowledge.core import iter_markdown
from agentic_vault_knowledge.runtime_index import RuntimeIndex

# Synthetic sizes. Modest so the suite stays runnable in CI; the *ratio* is what
# the complexity assertion uses, not the absolute values.
SMALL, LARGE = 50, 400

# core.trace() defaults to max_depth=6, so a benchmark target must sit within
# that many edges of the start or the call returns [] and times a failed search.
TRACE_HOPS = 4


def _schema(vault: Path) -> Path:
    return vault / ".agent/knowledge/schema"


def _fresh_db(vault: Path, tag: str) -> Path:
    """A DB path nothing else has touched.

    Timing a 'cold' build against a database a previous test already populated
    measures an incremental update, not a cold build.
    """
    path = vault / ".agent/knowledge/generated" / f"{tag}.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return path


def _build_vault(root: Path, note_count: int) -> Path:
    """Generate a synthetic vault of `note_count` linked, semantic notes.

    Generated in-test rather than committed, so fixtures stay synthetic and
    domain-neutral (design invariant 12) and sizes can change freely.
    """
    schema_dst = root / ".agent/knowledge/schema"
    schema_dst.mkdir(parents=True, exist_ok=True)
    schema_src = Path(__file__).parents[1] / "schema"
    for name in ("core.yaml", "relations.yaml", "VERSION"):
        shutil.copyfile(schema_src / name, schema_dst / name)

    notes = root / "02_Areas/Generated"
    notes.mkdir(parents=True, exist_ok=True)
    for i in range(note_count):
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

    Catches an accidental O(n^2) — a per-note operation that rescans everything
    already indexed. Both builds run against a freshly-unlinked database so
    neither is secretly incremental.
    """
    with RuntimeIndex(_fresh_db(small_vault, "scale")) as idx:
        small_s, issues = _time(lambda: idx.build(small_vault, _schema(small_vault)))
        assert issues == []
    with RuntimeIndex(_fresh_db(large_vault, "scale")) as idx:
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
    # Quadratic growth at this ratio would be ~64x and would blow through this.
    assert time_ratio < size_ratio * 4


def test_neighbors_query_uses_both_relation_indexes(large_vault: Path, capsys) -> None:
    """The plan check must cover the predicate `neighbors()` actually issues.

    `neighbors()` matches `source_id=? OR target_id=?`. Checking only `source_id`
    would keep passing if `relations_target` were dropped, which is exactly the
    regression this test exists to catch.
    """
    with RuntimeIndex(_fresh_db(large_vault, "plan")) as idx:
        idx.build(large_vault, _schema(large_vault))
        sql = (
            "SELECT * FROM relations WHERE status='accepted' "
            "AND (source_id=? OR target_id=?) AND derivation!='inferred'"
        )
        plan = "\n".join(
            row[-1] for row in idx.conn.execute("EXPLAIN QUERY PLAN " + sql, ("concept:n10",) * 2)
        )
        # Behavioural counterpart: an edge is reachable from *either* end.
        forward = idx.neighbors("concept:n0")
        backward = idx.neighbors("concept:n1")

    with capsys.disabled():
        print(f"\n  neighbors() plan:\n    " + plan.replace("\n", "\n    "))
    for index_name in ("relations_source", "relations_target"):
        assert index_name in plan, f"{index_name} unused by neighbors(); plan was:\n{plan}"
    assert forward, "n0 should see its outgoing edge"
    assert backward, "n1 should see the same edge from the target side"


def test_refresh_short_circuits_on_unchanged_vault(large_vault: Path, capsys) -> None:
    """The fingerprint short-circuit lives in `refresh()`, not `build()`.

    `build()` always does the full work; calling it twice measures two builds and
    tells you nothing about caching. `refresh()` computes the fingerprint and
    returns early when it matches.

    The saving is real but bounded: the fingerprint carries a content digest
    (ADR-0003), so the warm path still reads and hashes every file. It skips the
    parse-validate-write half, not the read half.

    Timing alone cannot prove the short-circuit exists. If the `_last_fingerprint`
    early return were deleted, the warm call would fall through to an incremental
    `build()` whose unchanged hashes skip every upsert — still faster than cold
    population, so `warm < cold` would keep passing. The load-bearing assertion is
    therefore that the warm path does not call `build()` at all.
    """
    with RuntimeIndex(_fresh_db(large_vault, "refresh")) as idx:
        builds: list[str] = []
        real_build = idx.build

        def counting_build(*args, **kwargs):
            builds.append("call")
            return real_build(*args, **kwargs)

        idx.build = counting_build  # type: ignore[method-assign]

        cold_s, cold_issues = _time(lambda: idx.refresh(large_vault, _schema(large_vault)))
        builds_after_cold = len(builds)
        warm_s, warm_issues = _time(lambda: idx.refresh(large_vault, _schema(large_vault)))
        builds_after_warm = len(builds)
        assert cold_issues == [] and warm_issues == []

    saved = (1 - warm_s / max(cold_s, 1e-6)) * 100
    with capsys.disabled():
        print(
            f"\n  refresh (cold): {cold_s * 1000:7.1f} ms  (build calls: {builds_after_cold})"
            f"\n  refresh (warm): {warm_s * 1000:7.1f} ms  (build calls: +"
            f"{builds_after_warm - builds_after_cold})  ({saved:.0f}% saved)"
        )
    assert builds_after_cold == 1, "a cold refresh must populate the index"
    assert builds_after_warm == 1, (
        "the warm refresh called build() — the fingerprint short-circuit is not engaging"
    )
    assert warm_s < cold_s, "the short-circuit should also be measurably cheaper"


def test_iter_markdown_does_not_materialise_the_walk(large_vault: Path, monkeypatch, capsys) -> None:
    """Prove laziness by observation, not by type.

    `hasattr(scan, "__next__")` is satisfied by a generator that builds the whole
    `rglob()` list internally before its first yield — which is precisely the
    O(n) behaviour issue #9 claimed existed. Counting how much of the underlying
    walk is consumed before the first item comes out tests the actual property.
    """
    consumed = 0
    real_rglob = Path.rglob

    def counting_rglob(self, pattern):
        nonlocal consumed
        for item in real_rglob(self, pattern):
            consumed += 1
            yield item

    monkeypatch.setattr(Path, "rglob", counting_rglob)

    scan = iter_markdown(large_vault)
    first = next(scan)
    consumed_at_first_yield = consumed
    total = sum(1 for _ in scan) + 1

    with capsys.disabled():
        print(
            f"\n  walk entries consumed before first yield: {consumed_at_first_yield}"
            f"\n  total notes yielded: {total}"
        )
    assert first.suffix == ".md"
    assert total >= LARGE, "the scan should still find every note"
    assert consumed_at_first_yield < total, (
        "iter_markdown materialised the whole walk before yielding; it must stay lazy"
    )


def test_query_surface_stays_responsive(large_vault: Path, capsys) -> None:
    """Record latency for the operations agents actually call.

    Every result is asserted non-empty. A trace that bottoms out on `max_depth`
    returns [] quickly, and timing that would report a failed search as fast
    traversal.
    """
    with RuntimeIndex(_fresh_db(large_vault, "queries")) as idx:
        idx.build(large_vault, _schema(large_vault))

        target = f"concept:n{TRACE_HOPS}"
        results: dict[str, object] = {}
        timings: dict[str, float] = {}
        for name, fn in (
            ("resolve", lambda: idx.resolve("Note 10")),
            ("search", lambda: idx.search("body text")),
            ("get", lambda: idx.get("concept:n10")),
            ("neighbors", lambda: idx.neighbors("concept:n10")),
            (f"trace(0->{TRACE_HOPS})", lambda: idx.trace("concept:n0", target)),
            ("health", lambda: idx.health()),
        ):
            timings[name], results[name] = _time(fn)

        deep_target = f"concept:n{LARGE - 1}"
        timings[f"trace(0->{LARGE - 1}, deep)"], results["deep"] = _time(
            lambda: idx.trace("concept:n0", deep_target, max_depth=LARGE)
        )

    with capsys.disabled():
        print(f"\n  query latency over {LARGE} notes:")
        for name, seconds in timings.items():
            print(f"    {name:26} {seconds * 1000:8.2f} ms")

    trace_path = results[f"trace(0->{TRACE_HOPS})"]
    assert trace_path, f"trace to {TRACE_HOPS} hops returned nothing — inside default max_depth?"
    assert len(trace_path) == TRACE_HOPS + 1, f"expected {TRACE_HOPS} edges, got {trace_path}"
    assert results["deep"], "explicit deep trace across the full chain should succeed"
    for name in ("resolve", "search", "get", "neighbors"):
        assert results[name], f"{name} returned nothing; the timing would be meaningless"

    slowest = max(timings.items(), key=lambda kv: kv[1])
    assert slowest[1] < 5.0, f"{slowest[0]} took {slowest[1]:.2f}s on {LARGE} notes"
