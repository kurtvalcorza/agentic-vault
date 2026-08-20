from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

from agentic_vault_knowledge.runtime_index import RuntimeIndex
from agentic_vault_knowledge.core import apply_patch, propose_frontmatter_patch, validate_patch, vault_roots

VAULT_ROOT=Path(os.environ.get("AGENTIC_VAULT_ROOT",".")).resolve()
READ_ONLY=os.environ.get("AGENTIC_VAULT_KNOWLEDGE_READ_ONLY","1").lower() not in {"0","false","no"}
_,SCHEMA_ROOT,DB_PATH=vault_roots(VAULT_ROOT)
mcp=MCPServer("agentic-vault-knowledge")

def _with_index(fn):
    with RuntimeIndex(DB_PATH) as idx:
        idx.build(VAULT_ROOT,SCHEMA_ROOT)
        return fn(idx)

@mcp.tool()
def knowledge_resolve_entity(ref:str)->list[dict[str,Any]]: return _with_index(lambda i:i.resolve(ref))
@mcp.tool()
def knowledge_search(query:str,limit:int=20)->list[dict[str,Any]]: return _with_index(lambda i:i.search(query,limit))
@mcp.tool()
def knowledge_get(object_id:str)->dict[str,Any]|None: return _with_index(lambda i:i.get(object_id))
@mcp.tool()
def knowledge_neighbors(object_id:str,predicate:str|None=None,include_derived:bool=False)->list[dict[str,Any]]: return _with_index(lambda i:i.neighbors(object_id,predicate,include_derived))
@mcp.tool()
def knowledge_trace_path(start_id:str,end_id:str,max_depth:int=6)->list[str]: return _with_index(lambda i:i.trace(start_id,end_id,max_depth))
@mcp.tool()
def knowledge_query(object_type:str|None=None,predicate:str|None=None,target:str|None=None,status:str="accepted",limit:int=100)->list[dict[str,Any]]: return _with_index(lambda i:i.query(object_type,predicate,target,status,limit))
@mcp.tool()
def knowledge_timeline(object_id:str)->list[dict[str,Any]]: return _with_index(lambda i:i.timeline(object_id))
@mcp.tool()
def knowledge_sources(object_id:str)->list[dict[str,Any]]: return _with_index(lambda i:i.sources(object_id))
@mcp.tool()
def knowledge_claims(object_id:str|None=None,status:str|None=None)->list[dict[str,Any]]: return _with_index(lambda i:i.claims(object_id,status))
@mcp.tool()
def knowledge_contradictions()->list[dict[str,Any]]: return _with_index(lambda i:i.contradiction_candidates())
@mcp.tool()
def knowledge_communities()->list[dict[str,Any]]: return _with_index(lambda i:i.communities())
@mcp.tool()
def knowledge_impact(object_id:str,max_depth:int=3)->list[dict[str,Any]]: return _with_index(lambda i:i.impact(object_id,max_depth))
@mcp.tool()
def knowledge_health()->dict[str,Any]: return _with_index(lambda i:i.health())

@mcp.tool()
def knowledge_propose_patch(relative_path:str,patch:dict[str,Any])->dict[str,Any]:
    path=(VAULT_ROOT/relative_path).resolve()
    if path==VAULT_ROOT or VAULT_ROOT not in path.parents: raise ValueError("path escapes vault root")
    proposal=propose_frontmatter_patch(path,patch); proposal["path"]=str(path); proposal["validation"]=[x.__dict__ for x in validate_patch(proposal,VAULT_ROOT)]; return proposal

@mcp.tool()
def knowledge_validate_patch(proposal_json:str)->list[dict[str,Any]]:
    return [x.__dict__ for x in validate_patch(json.loads(proposal_json),VAULT_ROOT)]

@mcp.tool()
def knowledge_apply_patch(proposal_json:str)->dict[str,Any]:
    if READ_ONLY: raise PermissionError("knowledge runtime is read-only; set AGENTIC_VAULT_KNOWLEDGE_READ_ONLY=0 to enable writes")
    proposal=json.loads(proposal_json); path=Path(proposal["path"]).resolve()
    if path==VAULT_ROOT or VAULT_ROOT not in path.parents: raise ValueError("path escapes vault root")
    apply_patch(proposal,VAULT_ROOT); return {"applied":True,"path":str(path.relative_to(VAULT_ROOT))}

def main()->None: mcp.run()
if __name__=="__main__": main()
