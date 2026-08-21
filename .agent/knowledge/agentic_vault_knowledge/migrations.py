from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class Migration:
    path: Path
    from_version: str
    to_version: str
    plan: Callable[[Path], list[dict[str, Any]]]
    apply: Callable[[Path, list[dict[str, Any]]], Any]


def schema_version(vault_root: Path) -> str:
    return (vault_root / ".agent/knowledge/schema/VERSION").read_text(encoding="utf-8").strip()


def discover(vault_root: Path) -> list[Migration]:
    root = vault_root / ".agent/knowledge/migrations"
    found: list[Migration] = []
    for path in sorted(root.glob("[0-9][0-9][0-9]-*.py")):
        spec = importlib.util.spec_from_file_location(f"agentic_vault_migration_{path.stem}", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load migration: {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        required = ("FROM_VERSION", "TO_VERSION", "plan", "apply")
        if any(not hasattr(mod, x) for x in required):
            raise RuntimeError(f"migration missing required contract: {path}")
        found.append(Migration(path, str(mod.FROM_VERSION), str(mod.TO_VERSION), mod.plan, mod.apply))
    return found


def migration_path(vault_root: Path, from_version: str, to_version: str) -> list[Migration]:
    current = from_version
    chain: list[Migration] = []
    available = discover(vault_root)
    seen: set[str] = set()
    while current != to_version:
        if current in seen:
            raise RuntimeError("migration cycle detected")
        seen.add(current)
        candidates = [m for m in available if m.from_version == current]
        if len(candidates) != 1:
            raise RuntimeError(f"expected exactly one migration from {current}; found {len(candidates)}")
        step = candidates[0]
        chain.append(step)
        current = step.to_version
    return chain


def plan_migrations(vault_root: Path, from_version: str, to_version: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for migration in migration_path(vault_root, from_version, to_version):
        out.append({
            "migration": migration.path.name,
            "from": migration.from_version,
            "to": migration.to_version,
            "proposals": migration.plan(vault_root),
        })
    return out
