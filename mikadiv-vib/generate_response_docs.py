"""Builds mikadiv-vib/generated/response.include.bs from the real VIB Response XSD.

Reuses engine.xsd_model.XsdModel (the same XSD-to-facts layer the Request-side
Excel/data-dictionary pipeline uses) so the Response document's field
descriptions, types, and enumerations are pulled from
ThirdPartyDisclosureResponse.xsd's own xs:documentation, never hand-typed.
Unlike the Request side, there is no Excel template to build here -- this
script only renders a Bikeshed include.

Run from the repository root::

    python mikadiv-vib/generate_response_docs.py
"""

from __future__ import annotations

from pathlib import Path

from engine.xsd_model import Field, XsdModel

ROOT = Path(__file__).resolve().parent
XSD_PATH = ROOT / "ThirdPartyDisclosureResponse.xsd"
OUTPUT_PATH = ROOT / "generated" / "response.include.bs"

RESPONSE_TYPE = "ResponseToDisclosureForIncomeType"

# ProcessingCompleted has no xs:documentation of its own in the real XSD (a
# genuine gap, confirmed by reading the schema directly) -- this is the one
# hand-authored override in this script, matching mapping.py's own SYN(...)
# convention for the rare field the XSD itself leaves undocumented.
DESC_PROCESSING_COMPLETED = (
    "Whether processing of this item is fully finished (true) or further "
    "responses covering later stages are still to follow (false). Independent "
    "of ProcessingResult: a stage can succeed with ProcessingCompleted=false, "
    "meaning more responses are still to come."
)

# Section name -> ordered list of (kind, ref) to resolve. kind is "attr",
# "elem", or "path" (a list of names to walk, needed only to disambiguate
# Reference, which appears both under Message and under Document).
SECTIONS: list[tuple[str, list[tuple[str, object]]]] = [
    ("Response envelope", [
        ("attr", "ResponseId"),
        ("attr", "RequestId"),
        ("attr", "ResponseDate"),
        ("elem", "ProcessingStatus"),
        ("elem", "ProcessingResult"),
        ("elem", "ProcessingCompleted"),
    ]),
    ("Messages", [
        ("elem", "Code"),
        ("elem", "Text"),
        ("elem", "Level"),
        ("path", ["Messages", "Message", "Reference"]),
    ]),
    ("Records", [
        ("elem", "Content"),
        ("elem", "RecordType"),
        ("elem", "RecordTypeInfo"),
    ]),
    ("Documents", [
        ("elem", "FilePath"),
        ("elem", "ContentMimeType"),
        ("elem", "DocumentType"),
        ("path", ["Documents", "Document", "Reference"]),
    ]),
]

# Enum key (display label) -> element name to extract via inline_enum(). Each
# element name is unique within the type, so no path disambiguation is needed
# here even though the enums live at different nesting depths.
ENUMS = [
    ("ProcessingStatus", "ProcessingStatus"),
    ("ProcessingResult", "ProcessingResult"),
    ("Message.Level", "Level"),
    ("Record.RecordType", "RecordType"),
    ("Document.DocumentType", "DocumentType"),
]


def _resolve(model: XsdModel, kind: str, ref) -> Field:
    if kind == "attr":
        return model.attr(RESPONSE_TYPE, ref)
    if kind == "elem":
        if ref == "ProcessingCompleted":
            return model.elem(RESPONSE_TYPE, ref, description=DESC_PROCESSING_COMPLETED)
        return model.elem(RESPONSE_TYPE, ref)
    if kind == "path":
        return model.path(RESPONSE_TYPE, ref)
    raise ValueError(f"unknown field kind {kind!r}")


def _slug(name: str) -> str:
    return name.lower().replace(".", "-").replace(" ", "-")


def _esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_section(name: str, fields: list[tuple[str, object]], model: XsdModel) -> list[str]:
    anchor = _slug(name)
    lines = [f'<h3 id="{anchor}">{_esc(name)}</h3>', ""]
    lines.append('<table class="complex data longlastcol dictionary">')
    lines.append("  <colgroup>")
    lines.append('    <col style="width:18%">')
    lines.append('    <col style="width:12%">')
    lines.append('    <col style="width:20%">')
    lines.append('    <col style="width:50%">')
    lines.append("  </colgroup>")
    lines.append(
        '  <thead><tr><th>Field<th class="col-req">Requiredness'
        "<th>Type / Allowed values<th>Description</tr></thead>"
    )
    lines.append("  <tbody>")
    for kind, ref in fields:
        field = _resolve(model, kind, ref)
        requiredness = "Required" if field.required else "Optional"
        lines.append(
            f"    <tr><td><code>{_esc(field.name)}</code>"
            f'<td class="col-req">{requiredness}'
            f"<td>{_esc(field.type_display)}"
            f'<td class="long">{_esc(field.description)}</tr>'
        )
    lines.append("  </tbody>")
    lines.append("</table>")
    lines.append("")
    return lines


def _render_enumerations(model: XsdModel) -> list[str]:
    lines = ['<h2 id="response-enumerations">Enumerations</h2>', ""]
    lines.append(
        "<p>Every value that an enum-typed field in the response may carry, "
        "with its meaning.</p>"
    )
    lines.append("")
    for key, element_name in ENUMS:
        anchor = f"enum-{_slug(key)}"
        values, meanings = model.inline_enum(RESPONSE_TYPE, element_name)
        lines.append(f'<h3 id="{anchor}">{_esc(key)}</h3>')
        lines.append("")
        lines.append('<table class="complex data longlastcol enum-table">')
        lines.append("  <colgroup>")
        lines.append('    <col style="width:18%">')
        lines.append('    <col style="width:82%">')
        lines.append("  </colgroup>")
        lines.append("  <thead><tr><th>Value<th>Meaning</tr></thead>")
        lines.append("  <tbody>")
        for value in values:
            meaning = _esc(meanings.get(value, ""))
            lines.append(f'    <tr><td><code>{_esc(value)}</code><td class="long">{meaning}</tr>')
        lines.append("  </tbody>")
        lines.append("</table>")
        lines.append("")
    return lines


def main() -> None:
    model = XsdModel(str(XSD_PATH))

    lines: list[str] = [
        "<!-- Generated by mikadiv-vib/generate_response_docs.py from "
        f"{XSD_PATH.name}. Do not edit by hand. -->",
        "",
        '<h2 id="response-fields">Response fields</h2>',
        "",
        "<p>Every response batches one or more "
        "<code>ResponseToDisclosureForIncomeType</code> entries, each "
        "answering one prior request. Fields below are grouped by where they "
        "appear in that structure.</p>",
        "",
    ]
    for name, fields in SECTIONS:
        lines.extend(_render_section(name, fields, model))
    lines.extend(_render_enumerations(model))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
