"""Build entry point: SHACL -> Bikeshed data-dictionary include + derived JSON
Schema. Mirrors generate_template.py's role for mikadiv-vib/, but for SHACL
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


def _html_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_bikeshed_include(model_path: str) -> str:
    """Render the per-shape field tables as a Bikeshed include.

    Emits real HTML (``<h3>``/``<table>``/``<thead>``/``<tbody>``) rather than
    Markdown pipe-table syntax: Bikeshed's Markdown-to-HTML pass only runs on
    the main .bs source document's own body text, not on content spliced in
    via ``<pre class=include>``, so Markdown syntax placed here would pass
    through unprocessed into the final HTML. Mirrors the HTML-table approach
    engine/generator.py's ``_write_bikeshed_include`` uses for kafe/mikadiv-vib.
    """
    graph = load_shapes(model_path)
    esc = _html_escape
    lines = ["<!-- Generated from streamld/model/envelope.ttl. Do not edit by hand. -->", ""]

    for shape_name, shape_iri in SHAPES.items():
        anchor = f"{shape_name.lower()}-fields"
        lines.append(f'<h3 id="{anchor}">{esc(shape_name)}</h3>')
        lines.append("")
        lines.append('<table class="complex data longlastcol dictionary">')
        lines.append("  <thead><tr><th>Field<th>Type<th>Required</tr></thead>")
        lines.append("  <tbody>")
        for field in fields_for_shape(graph, shape_iri):
            required = "Yes" if field.min_count >= 1 else "No"
            type_col = esc(field.datatype) if field.datatype else "(node)"
            lines.append(
                f"    <tr><td><code>{esc(field.name)}</code>"
                f"<td>{type_col}"
                f"<td>{required}</tr>"
            )
        lines.append("  </tbody>")
        lines.append("</table>")
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
