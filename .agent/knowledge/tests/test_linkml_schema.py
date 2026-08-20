from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView


def test_core_linkml_schema_loads_and_exposes_expected_classes() -> None:
    schema = Path(__file__).parents[1] / "schema/core.yaml"
    view = SchemaView(str(schema))
    classes = set(view.all_classes())
    assert {"KnowledgeObject", "Entity", "Concept", "Project", "Person", "Organization", "Source", "Claim", "Relation", "TimelineEntry"} <= classes
    assert view.get_class("Project").is_a == "Entity"
    assert view.get_slot("id").identifier is True
