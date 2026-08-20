# Knowledge Runtime Design

## Boundary

`agentic-vault` is the product. The knowledge runtime is an optional subsystem. It must not require a particular AI agent, LLM, graph database, embedding model, or domain ontology.

## Canonical and derived state

```text
Markdown/YAML/WikiLinks (canonical)
  -> deterministic parsing
  -> schema/entity/claim normalization
  -> validation
  -> accepted semantic state
  -> disposable SQLite + FTS projection
  -> semantic query API
  -> MCP adapter / skills
```

Deleting `generated/knowledge.db` must never delete knowledge. A full build must reconstruct equivalent deterministic state from the vault.

## Graphs

The runtime maintains distinct logical graphs:

1. **Navigation graph** — WikiLinks and addressable Markdown navigation.
2. **Assertion graph** — accepted typed relations/claims backed by authored or extracted evidence.
3. **Derived graph** — computed/inferred relationships. Derived edges never silently promote to assertions.

## Identity

- `id` is immutable machine identity.
- `title` is mutable display text.
- `aliases` are normalized lookup names.
- `path` is mutable storage location.
- Renaming/moving a note must not change its ID.
- Exact stable ID wins over aliases; aliases win over normalized title/path matching.
- Ambiguous resolution returns candidates. It does not auto-merge.

Recommended IDs use a namespace prefix (`project:sample-project`, `person:sample-person`). UUID-backed IDs are valid for claims/events where slug identity is inappropriate.

## Knowledge lifecycle

Machine-produced semantic knowledge follows:

`candidate -> proposed -> accepted -> superseded|retracted`

Only accepted claims/relations enter the assertion graph by default. Inferred candidates may be stored in generated state or proposed as Markdown patches, but not silently canonicalized.

## Provenance

Evidence supports file-, heading-, block-, line-, URL-, page-, timestamp-, or commit-level locators. Source authority, derivation method, extraction confidence, claim confidence, and review status are separate fields.

## Time

Temporal records support:

- `event_time` / validity: when a fact is/was true in the modeled world.
- `transaction_time`: when the vault recorded it.

Historical records are append/supersede/retract oriented. They are not rewritten in place by default.

## Writes

Mutation is proposal-first:

1. read source + content hash;
2. construct patch;
3. validate candidate full state;
4. verify source hash unchanged (optimistic concurrency);
5. atomically replace file;
6. re-index affected file(s);
7. validate post-write state.

If the hash changed, the write fails with a conflict rather than overwriting another agent/user edit.

## Query semantics

The public API is semantic, not SQL-centric. Required operations include entity resolution, lexical search, object lookup, typed neighbors, path tracing, timeline lookup, claim/evidence lookup, contradiction candidates, validation, and health.

Backends may change without changing these contracts.

## Extension model

The public core defines conservative generic classes/relations. A downstream vault may add LinkML schema files and relation registry entries under `schema/extensions/` or a configured external path. Core operation must not require domain-specific extensions.

## Optional semantic enrichment

LLM enrichment is an adapter boundary. Deterministically recoverable structure (YAML, WikiLinks, tags, headings, block IDs, paths) must never depend on an LLM. Semantic adapters return candidates with derivation metadata; they do not directly mutate canonical Markdown.

## Interoperability

OKF/JSON-LD/RDF exports are projections. Importers must convert external representations into validated candidate Markdown/state. No interchange format becomes canonical.
