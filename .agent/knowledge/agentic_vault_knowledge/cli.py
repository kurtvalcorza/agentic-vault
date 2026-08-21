from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    KnowledgeError,
    _reject_unwritable_target,
    _resolve_vault_path,
    apply_patch,
    propose_frontmatter_patch,
    validate_patch,
    vault_roots,
)
from .interop import export_jsonld, export_okf_bundle, export_rdf_ntriples, import_okf_candidates, validate_okf_bundle
from .migrations import plan_migrations, schema_version
from .retrieval import fused_search
from .runtime_index import RuntimeIndex
from .transactions import apply_batch, validate_batch
from .validation import validate_vault_semantics


def _root(value: str | None) -> Path:
    return Path(value or ".").resolve()


def _has_errors(issues) -> bool:
    return any((getattr(item, "severity", None) or item.get("severity", "error")) == "error" for item in issues)


def main() -> int:
    parser = argparse.ArgumentParser(prog="vault-knowledge")
    parser.add_argument("--vault", default=".")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    build = sub.add_parser("build")
    build.add_argument("--full", action="store_true")
    sub.add_parser("health")
    sub.add_parser("communities")
    sub.add_parser("central")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    retrieve = sub.add_parser("retrieve")
    retrieve.add_argument("query")
    retrieve.add_argument("--limit", type=int, default=20)
    retrieve.add_argument("--no-graph-expand", action="store_true")
    for name in ("get", "resolve", "timeline", "sources", "claims", "impact"):
        item = sub.add_parser(name)
        item.add_argument("id")
    claim_sources = sub.add_parser("claim-sources")
    claim_sources.add_argument("claim_id")
    state = sub.add_parser("state-as-of")
    state.add_argument("id")
    state.add_argument("as_of")
    neighbors = sub.add_parser("neighbors")
    neighbors.add_argument("id")
    neighbors.add_argument("--predicate")
    neighbors.add_argument("--include-derived", action="store_true")
    trace = sub.add_parser("trace")
    trace.add_argument("start")
    trace.add_argument("end")
    trace.add_argument("--max-depth", type=int, default=6)
    trace.add_argument("--include-derived", action="store_true")
    query = sub.add_parser("query")
    query.add_argument("--type")
    query.add_argument("--predicate")
    query.add_argument("--target")
    query.add_argument("--status", default="accepted")
    query.add_argument("--limit", type=int, default=100)
    sub.add_parser("contradictions")
    export_okf = sub.add_parser("export-okf")
    export_okf.add_argument("output")
    validate_okf = sub.add_parser("validate-okf")
    validate_okf.add_argument("bundle")
    import_okf = sub.add_parser("import-okf-candidates")
    import_okf.add_argument("bundle")
    export_json = sub.add_parser("export-jsonld")
    export_json.add_argument("output")
    export_rdf = sub.add_parser("export-rdf")
    export_rdf.add_argument("output")
    migrations = sub.add_parser("plan-migrations")
    migrations.add_argument("from_version")
    migrations.add_argument("--to-version")
    propose = sub.add_parser("propose")
    propose.add_argument("path")
    propose.add_argument("patch_json")
    validate_one = sub.add_parser("validate-patch")
    validate_one.add_argument("proposal")
    validate_many = sub.add_parser("validate-batch")
    validate_many.add_argument("proposals")
    apply_one = sub.add_parser("apply-patch")
    apply_one.add_argument("proposal")
    apply_many = sub.add_parser("apply-batch")
    apply_many.add_argument("proposals")

    args = parser.parse_args()
    root = _root(args.vault)
    _, schema, db = vault_roots(root)

    if args.cmd == "validate":
        issues = validate_vault_semantics(root, schema)
        print(json.dumps([item.__dict__ for item in issues], indent=2))
        return 1 if _has_errors(issues) else 0
    if args.cmd == "propose":
        # Guard the target BEFORE reading it: propose_frontmatter_patch reads the
        # whole file into the proposal, so a secret-bearing or protected target
        # (.env, mcp.json, .git/...) must be rejected before any read.
        try:
            path = _resolve_vault_path(args.path, root)
            _reject_unwritable_target(path, root)
        except KnowledgeError as exc:
            raise SystemExit(str(exc))
        proposal = propose_frontmatter_patch(path, json.loads(args.patch_json))
        print(json.dumps(proposal, indent=2))
        return 0
    if args.cmd in {"validate-patch", "apply-patch"}:
        proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
        if args.cmd == "validate-patch":
            issues = validate_patch(proposal, root)
            print(json.dumps([item.__dict__ for item in issues], indent=2))
            return 1 if _has_errors(issues) else 0
        apply_patch(proposal, root)
        return 0
    if args.cmd in {"validate-batch", "apply-batch"}:
        proposals = json.loads(Path(args.proposals).read_text(encoding="utf-8"))
        if args.cmd == "validate-batch":
            issues = validate_batch(proposals, root)
            print(json.dumps(issues, indent=2))
            return 1 if _has_errors(issues) else 0
        print(json.dumps({"applied": apply_batch(proposals, root)}, indent=2))
        return 0
    if args.cmd == "export-okf":
        print(json.dumps(export_okf_bundle(root, (root / args.output).resolve()), indent=2))
        return 0
    if args.cmd == "validate-okf":
        issues = validate_okf_bundle((root / args.bundle).resolve())
        print(json.dumps(issues, indent=2))
        return 1 if issues else 0
    if args.cmd == "import-okf-candidates":
        print(json.dumps(import_okf_candidates((root / args.bundle).resolve()), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "plan-migrations":
        target = args.to_version or schema_version(root)
        print(json.dumps(plan_migrations(root, args.from_version, target), indent=2))
        return 0

    with RuntimeIndex(db) as idx:
        if args.cmd == "build":
            issues = idx.rebuild(root, schema) if args.full else idx.build(root, schema)
            print(json.dumps([item.__dict__ for item in issues], indent=2))
            return 1 if _has_errors(issues) else 0

        issues = idx.refresh(root, schema)
        if _has_errors(issues):
            print(json.dumps({"error": "knowledge index validation failed", "issues": [item.__dict__ for item in issues]}, indent=2))
            return 1

        if args.cmd == "health":
            out = idx.health()
        elif args.cmd == "search":
            out = idx.search(args.query, args.limit)
        elif args.cmd == "retrieve":
            out = fused_search(idx, args.query, args.limit, graph_expand=not args.no_graph_expand)
        elif args.cmd == "get":
            out = idx.get(args.id)
        elif args.cmd == "resolve":
            out = idx.resolve(args.id)
        elif args.cmd == "neighbors":
            out = idx.neighbors(args.id, args.predicate, args.include_derived)
        elif args.cmd == "trace":
            out = idx.trace(args.start, args.end, args.max_depth, args.include_derived)
        elif args.cmd == "timeline":
            out = idx.timeline(args.id)
        elif args.cmd == "state-as-of":
            out = idx.state_as_of(args.id, args.as_of)
        elif args.cmd == "sources":
            out = idx.sources(args.id)
        elif args.cmd == "claims":
            out = idx.claims(args.id)
        elif args.cmd == "claim-sources":
            out = idx.claim_sources(args.claim_id)
        elif args.cmd == "impact":
            out = idx.impact(args.id)
        elif args.cmd == "communities":
            out = idx.communities()
        elif args.cmd == "central":
            out = idx.central_objects()
        elif args.cmd == "query":
            out = idx.query(args.type, args.predicate, args.target, args.status, args.limit)
        elif args.cmd == "contradictions":
            out = idx.contradiction_candidates()
        elif args.cmd == "export-jsonld":
            out = export_jsonld(idx, (root / args.output).resolve())
        elif args.cmd == "export-rdf":
            out = export_rdf_ntriples(idx, (root / args.output).resolve())
        else:
            raise SystemExit(2)
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
