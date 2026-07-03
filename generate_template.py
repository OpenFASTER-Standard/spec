"""Build entry point for the OpenFASTER templates and documentation.

Wires the shared generation engine (:mod:`engine`) to each module's schema and
template mapping, and generates that module's Excel workbook, metadata store,
field reference and Bikeshed include into the module's ``generated/`` folder.

Field-level content is machine-sourced from each module's XSD; the template
shape lives in the module's ``mapping`` package. Add a new module by appending a
``ModuleConfig`` to ``MODULES`` below.

Run from the repository root::

    python generate_template.py
"""

from __future__ import annotations

from pathlib import Path

from engine.generator import Generator, ModuleConfig
from mikadiv import mapping as mikadiv_mapping

ROOT = Path(__file__).resolve().parent

MODULES: list[ModuleConfig] = [
    ModuleConfig(
        title=mikadiv_mapping.LEGEND_TITLE,
        xsd_path=ROOT / "mikadiv" / "ThirdPartyDisclosureRequest.xsd",
        output_dir=ROOT / "mikadiv" / "generated",
        xlsx_name="MiKaDiv_ThirdPartyDisclosure_Template.xlsx",
        json_name="template_metadata.json",
        doc_name="TEMPLATE_FIELDS.md",
        bs_name="fields.include.bs",
        legend_sheet_name=mikadiv_mapping.S_LEGEND,
        master_sheet_name=mikadiv_mapping.S_MASTER,
        sheet_order=mikadiv_mapping.SHEET_ORDER,
        build_enums=mikadiv_mapping.build_enums,
        build_sheets=mikadiv_mapping.build_sheets,
        sheet_info=mikadiv_mapping.SHEET_INFO,
        legend_rows=mikadiv_mapping.LEGEND_ROWS,
    ),
]


def main() -> None:
    for config in MODULES:
        Generator(config).run()


if __name__ == "__main__":
    main()
