from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import KnowledgeIndex, apply_patch, export_okf_like, propose_frontmatter_patch, validate_patch, validate_vault, vault_roots


def _root(value: str | None) -> Path:
    return Path(value or ".").resolve()


def main() -> int:
    p=argparse.ArgumentParser(prog="vault-knowledge")
    p.add_argument("--vault", default=".")
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("validate")
    b=sub.add_parser("build"); b.add_argument("--full",action="store_true")
    sub.add_parser("health")
    s=sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit",type=int,default=20)
    g=sub.add_parser("get"); g.add_argument("id")
    r=sub.add_parser("resolve"); r.add_argument("ref")
    n=sub.add_parser("neighbors"); n.add_argument("id"); n.add_argument("--predicate"); n.add_argument("--include-derived",action="store_true")
    t=sub.add_parser("trace"); t.add_argument("start"); t.add_argument("end"); t.add_argument("--max-depth",type=int,default=6)
    tl=sub.add_parser("timeline"); tl.add_argument("id")
    src=sub.add_parser("sources"); src.add_argument("id")
    sub.add_parser("contradictions")
    e=sub.add_parser("export-okf"); e.add_argument("output")
    pp=sub.add_parser("propose"); pp.add_argument("path"); pp.add_argument("patch_json")
    vp=sub.add_parser("validate-patch"); vp.add_argument("proposal")
    ap=sub.add_parser("apply-patch"); ap.add_argument("proposal")
    args=p.parse_args(); root=_root(args.vault); _,schema,db=vault_roots(root)

    if args.cmd=="validate":
        issues=validate_vault(root); print(json.dumps([i.__dict__ for i in issues],indent=2)); return 1 if issues else 0
    if args.cmd=="propose":
        proposal=propose_frontmatter_patch((root/args.path).resolve(),json.loads(args.patch_json)); print(json.dumps(proposal,indent=2)); return 0
    if args.cmd in {"validate-patch","apply-patch"}:
        proposal=json.loads(Path(args.proposal).read_text(encoding="utf-8"))
        if args.cmd=="validate-patch": print(json.dumps([i.__dict__ for i in validate_patch(proposal,root)],indent=2)); return 0
        apply_patch(proposal,root); return 0

    with KnowledgeIndex(db) as idx:
        if args.cmd=="build":
            issues=idx.rebuild(root,schema) if args.full else idx.build(root,schema); print(json.dumps([i.__dict__ for i in issues],indent=2)); return 1 if issues else 0
        # Queries assume an index exists; build incrementally first to keep results fresh.
        idx.build(root,schema)
        if args.cmd=="health": out=idx.health()
        elif args.cmd=="search": out=idx.search(args.query,args.limit)
        elif args.cmd=="get": out=idx.get(args.id)
        elif args.cmd=="resolve": out=idx.resolve(args.ref)
        elif args.cmd=="neighbors": out=idx.neighbors(args.id,args.predicate,args.include_derived)
        elif args.cmd=="trace": out=idx.trace(args.start,args.end,args.max_depth)
        elif args.cmd=="timeline": out=idx.timeline(args.id)
        elif args.cmd=="sources": out=idx.sources(args.id)
        elif args.cmd=="contradictions": out=idx.contradiction_candidates()
        elif args.cmd=="export-okf": export_okf_like(idx,(root/args.output).resolve()); out={"written":args.output}
        else: raise SystemExit(2)
        print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); return 0


if __name__=="__main__": raise SystemExit(main())
