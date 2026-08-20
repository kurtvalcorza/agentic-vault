from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime_index import RuntimeIndex
from .core import apply_patch, propose_frontmatter_patch, validate_patch, vault_roots
from .interop import export_jsonld, export_okf_bundle, export_rdf_ntriples, import_okf_candidates, validate_okf_bundle
from .migrations import plan_migrations, schema_version
from .retrieval import fused_search
from .transactions import apply_batch, validate_batch
from .validation import validate_vault_semantics


def _root(value: str | None) -> Path: return Path(value or ".").resolve()


def main() -> int:
    p=argparse.ArgumentParser(prog="vault-knowledge"); p.add_argument("--vault",default="."); sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("validate"); b=sub.add_parser("build"); b.add_argument("--full",action="store_true"); sub.add_parser("health"); sub.add_parser("communities"); sub.add_parser("central")
    s=sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit",type=int,default=20)
    rtv=sub.add_parser("retrieve"); rtv.add_argument("query"); rtv.add_argument("--limit",type=int,default=20); rtv.add_argument("--no-graph-expand",action="store_true")
    for name in ("get","resolve","timeline","sources","claims","impact"):
        x=sub.add_parser(name); x.add_argument("id")
    cs=sub.add_parser("claim-sources"); cs.add_argument("claim_id")
    sao=sub.add_parser("state-as-of"); sao.add_argument("id"); sao.add_argument("as_of")
    n=sub.add_parser("neighbors"); n.add_argument("id"); n.add_argument("--predicate"); n.add_argument("--include-derived",action="store_true")
    t=sub.add_parser("trace"); t.add_argument("start"); t.add_argument("end"); t.add_argument("--max-depth",type=int,default=6)
    q=sub.add_parser("query"); q.add_argument("--type"); q.add_argument("--predicate"); q.add_argument("--target"); q.add_argument("--status",default="accepted"); q.add_argument("--limit",type=int,default=100)
    sub.add_parser("contradictions")
    eo=sub.add_parser("export-okf"); eo.add_argument("output")
    vo=sub.add_parser("validate-okf"); vo.add_argument("bundle")
    io=sub.add_parser("import-okf-candidates"); io.add_argument("bundle")
    ej=sub.add_parser("export-jsonld"); ej.add_argument("output")
    er=sub.add_parser("export-rdf"); er.add_argument("output")
    mp=sub.add_parser("plan-migrations"); mp.add_argument("from_version"); mp.add_argument("--to-version")
    pp=sub.add_parser("propose"); pp.add_argument("path"); pp.add_argument("patch_json")
    vp=sub.add_parser("validate-patch"); vp.add_argument("proposal")
    vb=sub.add_parser("validate-batch"); vb.add_argument("proposals")
    ap=sub.add_parser("apply-patch"); ap.add_argument("proposal")
    ab=sub.add_parser("apply-batch"); ab.add_argument("proposals")
    args=p.parse_args(); root=_root(args.vault); _,schema,db=vault_roots(root)

    if args.cmd=="validate":
        issues=validate_vault_semantics(root,schema); print(json.dumps([i.__dict__ for i in issues],indent=2)); return 1 if any(i.severity=="error" for i in issues) else 0
    if args.cmd=="propose":
        path=(root/args.path).resolve()
        if path==root or root not in path.parents: raise SystemExit("path escapes vault root")
        proposal=propose_frontmatter_patch(path,json.loads(args.patch_json)); print(json.dumps(proposal,indent=2)); return 0
    if args.cmd in {"validate-patch","apply-patch"}:
        proposal=json.loads(Path(args.proposal).read_text(encoding="utf-8"))
        if args.cmd=="validate-patch": print(json.dumps([i.__dict__ for i in validate_patch(proposal,root)],indent=2)); return 0
        apply_patch(proposal,root); return 0
    if args.cmd in {"validate-batch","apply-batch"}:
        proposals=json.loads(Path(args.proposals).read_text(encoding="utf-8"))
        if args.cmd=="validate-batch": print(json.dumps(validate_batch(proposals,root),indent=2)); return 0
        print(json.dumps({"applied":apply_batch(proposals,root)},indent=2)); return 0
    if args.cmd=="export-okf":
        print(json.dumps(export_okf_bundle(root,(root/args.output).resolve()),indent=2)); return 0
    if args.cmd=="validate-okf":
        issues=validate_okf_bundle((root/args.bundle).resolve()); print(json.dumps(issues,indent=2)); return 1 if issues else 0
    if args.cmd=="import-okf-candidates":
        print(json.dumps(import_okf_candidates((root/args.bundle).resolve()),indent=2,ensure_ascii=False)); return 0
    if args.cmd=="plan-migrations":
        target=args.to_version or schema_version(root); print(json.dumps(plan_migrations(root,args.from_version,target),indent=2)); return 0

    with RuntimeIndex(db) as idx:
        if args.cmd=="build":
            issues=idx.rebuild(root,schema) if args.full else idx.build(root,schema); print(json.dumps([i.__dict__ for i in issues],indent=2)); return 1 if any(i.severity=="error" for i in issues) else 0
        idx.build(root,schema)
        if args.cmd=="health": out=idx.health()
        elif args.cmd=="search": out=idx.search(args.query,args.limit)
        elif args.cmd=="retrieve": out=fused_search(idx,args.query,args.limit,graph_expand=not args.no_graph_expand)
        elif args.cmd=="get": out=idx.get(args.id)
        elif args.cmd=="resolve": out=idx.resolve(args.id)
        elif args.cmd=="neighbors": out=idx.neighbors(args.id,args.predicate,args.include_derived)
        elif args.cmd=="trace": out=idx.trace(args.start,args.end,args.max_depth)
        elif args.cmd=="timeline": out=idx.timeline(args.id)
        elif args.cmd=="state-as-of": out=idx.state_as_of(args.id,args.as_of)
        elif args.cmd=="sources": out=idx.sources(args.id)
        elif args.cmd=="claims": out=idx.claims(args.id)
        elif args.cmd=="claim-sources": out=idx.claim_sources(args.claim_id)
        elif args.cmd=="impact": out=idx.impact(args.id)
        elif args.cmd=="communities": out=idx.communities()
        elif args.cmd=="central": out=idx.central_objects()
        elif args.cmd=="query": out=idx.query(args.type,args.predicate,args.target,args.status,args.limit)
        elif args.cmd=="contradictions": out=idx.contradiction_candidates()
        elif args.cmd=="export-jsonld": out=export_jsonld(idx,(root/args.output).resolve())
        elif args.cmd=="export-rdf": out=export_rdf_ntriples(idx,(root/args.output).resolve())
        else: raise SystemExit(2)
        print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); return 0

if __name__=="__main__": raise SystemExit(main())
