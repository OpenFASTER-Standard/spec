"""Build entry point: SHACL -> Bikeshed data-dictionary include + derived JSON
Schema. Mirrors generate_template.py's role for mikadiv/, but for SHACL
instead of XSD.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from rdflib import Namespace

from generator.shacl_model import fields_for_shape, load_shapes

STREAMLD = Namespace("https://openfaster.org/streamld#")

SHAPES = {
    "EventEnvelope": STREAMLD.EventEnvelopeShape,
    "ReplicationFrame": STREAMLD.ReplicationFrameShape,
    "SubscriptionRequest": STREAMLD.SubscriptionRequestShape,
    "GapSignal": STREAMLD.GapSignalShape,
}


def render_bikeshed_include(model_path: str) -> str:
    graph = load_shapes(model_path)
    lines = ["<!-- Generated from streamld/model/envelope.ttl. Do not edit by hand. -->", ""]

    for shape_name, shape_iri in SHAPES.items():
        lines.append(f"### {shape_name} ### {{#{shape_name.lower()}-fields}}")
        lines.append("")
        lines.append("| Field | Type | Required |")
        lines.append("| --- | --- | --- |")
        for field in fields_for_shape(graph, shape_iri):
            required = "Yes" if field.min_count >= 1 else "No"
            lines.append(f"| `{field.name}` | {field.datatype or '(node)'} | {required} |")
        lines.append("")

    return "\n".join(lines)


def generate_json_schema(model_path: str, output_path: str) -> None:
    subprocess.run(
        ["shacl2code", "generate", "-i", model_path, "jsonschema", "-o", output_path],
        check=True,
    )


def main() -> None:
    model_path = "streamld/model/envelope.ttl"
    generated_dir = Path("streamld/generated")
    generated_dir.mkdir(parents=True, exist_ok=True)

    (generated_dir / "fields.include.bs").write_text(render_bikeshed_include(model_path))
    generate_json_schema(model_path, str(generated_dir / "envelope.schema.json"))


if __name__ == "__main__":
    main()
