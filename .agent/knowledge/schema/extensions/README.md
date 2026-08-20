# Schema extensions

Downstream/private vaults may add domain-specific classes and relation definitions here without modifying the public core.

Extension files are loaded in lexical order. A relation extension uses:

```yaml
relations:
  custom_relation:
    inverse: custom_inverse
    description: Domain-specific meaning.
```

Rules:

- extensions must not shadow core relation names;
- public `agentic-vault` fixtures remain synthetic/domain-neutral;
- extensions may be kept outside a public clone and copied/mounted locally;
- schema/type extensions should preserve the core identity/provenance/write invariants.
