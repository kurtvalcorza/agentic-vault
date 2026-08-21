#!/usr/bin/env python3
"""Launch the knowledge-runtime MCP server for this vault.

Why this exists
---------------
The MCP server reads its vault root from the ``AGENTIC_VAULT_ROOT`` environment
variable, defaulting to the process working directory. Neither is reliable from
an MCP client:

* Clients do not guarantee the working directory a stdio server is spawned in.
* Variable expansion inside a client config is client-specific. Claude Code, for
  example, expands ``${VAR}`` in ``command`` and ``args`` but sets
  ``CLAUDE_PROJECT_DIR`` in the *server's* environment rather than its own, so a
  bare ``${CLAUDE_PROJECT_DIR}`` expands to nothing and needs the
  ``${CLAUDE_PROJECT_DIR:-.}`` default. Other clients differ again.

So this launcher resolves the vault root from its own location instead — no
absolute path in any client config, and the same invocation works for every
harness. Point any MCP client at this file (see ``.mcp.json.example``).

Writes are disabled by default. ``knowledge_apply_patch`` and
``knowledge_apply_batch`` mutate canonical Markdown, so enabling them is a
deliberate act: set ``AGENTIC_VAULT_KNOWLEDGE_READ_ONLY=0`` in the client's env
block, and follow your vault's confirmation protocol before doing so.

stdout is reserved for MCP JSON-RPC — this script must never print to it.
Diagnostics go to stderr, which clients surface as server logs.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# .agent/scripts/<this file> -> vault root is two levels up.
VAULT_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    os.environ["AGENTIC_VAULT_ROOT"] = str(VAULT_ROOT)
    os.environ.setdefault("AGENTIC_VAULT_KNOWLEDGE_READ_ONLY", "1")

    try:
        from agentic_vault_knowledge.mcp_server import main as serve
    except ModuleNotFoundError:
        sys.stderr.write(
            "agentic_vault_knowledge is not importable.\n"
            f"Install it from the vault root ({VAULT_ROOT}):\n"
            "    pip install -e './.agent/knowledge[test,linkml]'\n"
            "    # or, for a uv-managed venv (which ships no pip):\n"
            "    uv pip install -e './.agent/knowledge[test,linkml]'\n"
            "Make sure the client launches this script with that environment's "
            "interpreter.\n"
        )
        return 1

    serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
