"""Builds kafe/generated/va.include.bs from the real KaFE-VA (decision
notice) XSD.

Reuses engine.xsd_model.XsdModel (the same XSD-to-facts layer the Request-side
Excel/data-dictionary pipeline uses) so the decision-notice document's field
descriptions, types, requiredness, and enumerations are pulled from
kafe-va.xsd's own xs:documentation, never hand-typed. Unlike the Request side,
there is no Excel template to build here -- this script only renders a
Bikeshed include.

Run from the repository root::

    python -m kafe.generate_va_docs
"""

from __future__ import annotations

from pathlib import Path

from engine.xsd_model import Field, XsdModel

ROOT = Path(__file__).resolve().parent
XSD_PATH = ROOT / "kafe-va.xsd"
OUTPUT_PATH = ROOT / "generated" / "va.include.bs"

# Root type of a single Steuerbescheid (decision notice) entry within the
# KAFE-VA delivery -- confirmed by reading kafe/kafe-va.xsd directly.
VA_TYPE = "Bescheid_CType"

# Section name -> ordered list of (kind, ref) to resolve. kind is "attr",
# "elem", or "path" (a list of names to walk).
SECTIONS: list[tuple[str, list[tuple[str, object]]]] = [
    ("Decision notice envelope", [
        ("attr", "BescheidId"),
        ("elem", "BescheidArt"),
        ("elem", "SummeAbrechnung"),
        ("elem", "Faelligkeit"),
        ("elem", "Hinweise"),
    ]),
    ("Reference back to the original application", [
        ("path", ["Bezugsantrag", "TransferticketId"]),
        ("path", ["Bezugsantrag", "AntragId"]),
        ("path", ["Bezugsantrag", "RegistrierNr"]),
        ("path", ["Bezugsantrag", "KennNr"]),
    ]),
    ("Per-income refund breakdown", [
        # Confirmed by reading kafe/kafe-va.xsd directly: these three fields
        # live on BescheidErtrag_CType, the type of the Ertrag element
        # (maxOccurs unbounded) nested under Ertraege -- not directly on
        # Bescheid_CType. XsdModel.attr()/.elem() already resolve nested
        # complex types via recursive descent (see _iter_elements /
        # _iter_attributes), and these three names are unique within this
        # schema, so no "path" kind is needed to disambiguate them.
        ("attr", "ErtragId"),
        ("elem", "ErstattungKapESt"),
        ("elem", "ErstattungSolZ"),
    ]),
]

# BescheidArt_ENUM's own <xs:enumeration> values carry no per-value
# xs:documentation in the real XSD -- only the containing BescheidArt element
# has a (German) doc describing the field as a whole ("Kennzeichnung, ob es
# sich um einen erstmaligen oder korrigierten Bescheid handelt."). A genuine
# gap, confirmed by reading the schema directly (model.enum() returns empty
# meanings for both values). These two meanings are hand-authored, matching
# mikadiv-vib/generate_response_docs.py's own DESC_PROCESSING_COMPLETED
# precedent for the rare field/value the XSD itself leaves undocumented, and
# are consistent with the prose in response.bs's "Approval and clawback
# semantics" section.
ENUM_MEANING_OVERRIDES: dict[str, dict[str, str]] = {
    "BescheidArt": {
        "ERSTBESCHEID": "First (initial) decision notice for a given Erstattungsantrag.",
        "KORREKTUR": (
            "Corrected decision notice superseding an earlier one for the same "
            "Erstattungsantrag -- not chained to which specific earlier notice "
            "it corrects (only back to the original application, via "
            "Bezugsantrag)."
        ),
    },
}

# Enum key (display label) -> named XSD simple type to extract via enum().
# Unlike mikadiv-vib's ResponseToDisclosureForIncomeType (where enumerations
# are declared inline on the element), BescheidArt is typed via the
# top-level named simpleType BescheidArt_ENUM, so enum() (by type name) is
# the right lookup here, not inline_enum() (by element name).
ENUMS = [
    ("BescheidArt", "BescheidArt_ENUM"),
]


def _resolve(model: XsdModel, kind: str, ref) -> Field:
    if kind == "attr":
        return model.attr(VA_TYPE, ref)
    if kind == "elem":
        return model.elem(VA_TYPE, ref)
    if kind == "path":
        return model.path(VA_TYPE, ref)
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
    lines = ['<h2 id="va-enumerations">Enumerations</h2>', ""]
    lines.append(
        "<p>Every value that an enum-typed field in the decision notice may "
        "carry, with its meaning.</p>"
    )
    lines.append("")
    for key, type_name in ENUMS:
        anchor = f"enum-{_slug(key)}"
        values, xsd_meanings = model.enum(type_name)
        meanings = ENUM_MEANING_OVERRIDES.get(key, xsd_meanings)
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
        "<!-- Generated by kafe/generate_va_docs.py from "
        f"{XSD_PATH.name}. Do not edit by hand. -->",
        "",
        '<h2 id="va-fields">Decision notice fields</h2>',
        "",
        "<p>One KAFE-VA delivery batches one or more <code>Steuerbescheid</code> "
        "(decision notice) entries; each answers exactly one prior "
        "<code>Erstattungsantrag</code>, correlated via the "
        "<code>Bezugsantrag</code> back-reference block. Fields below are "
        "grouped by where they appear in that structure.</p>",
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
