"""Build entry point for the OpenFASTER templates and documentation.

Wires the shared generation engine (:mod:`engine`) to each module's schema and
template mapping, and generates that module's Excel workbook, metadata store,
field reference and Bikeshed include into the module's ``generated/`` folder.

Field-level content is machine-sourced from each module's XSD; the template
shape lives in the module's ``mapping.py``. Add a new module by appending a
``ModuleConfig`` to ``MODULES`` below.

Run from the repository root::

    python generate_template.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from engine.generator import Generator, ModuleConfig

ROOT = Path(__file__).resolve().parent


def _load_module(name: str, path: Path) -> ModuleType:
    """Load a module by file path.

    Module directories use hyphenated slugs (e.g. ``mikadiv-vib/``) to match
    their live URL path, which isn't a valid Python package name -- so
    mapping modules are loaded directly by path rather than imported as
    ``package.submodule``.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mikadiv_vib_mapping = _load_module("mikadiv_vib_mapping", ROOT / "mikadiv-vib" / "mapping.py")

MODULES: list[ModuleConfig] = [
    ModuleConfig(
        title=mikadiv_vib_mapping.LEGEND_TITLE,
        xsd_path=ROOT / "mikadiv-vib" / "ThirdPartyDisclosureRequest.xsd",
        output_dir=ROOT / "mikadiv-vib" / "generated",
        xlsx_name="MiKaDiv_ThirdPartyDisclosure_Template.xlsx",
        json_name="template_metadata.json",
        doc_name="TEMPLATE_FIELDS.md",
        bs_name="fields.include.bs",
        legend_sheet_name=mikadiv_vib_mapping.S_LEGEND,
        master_sheet_name=mikadiv_vib_mapping.S_MASTER,
        sheet_order=mikadiv_vib_mapping.SHEET_ORDER,
        build_enums=mikadiv_vib_mapping.build_enums,
        build_sheets=mikadiv_vib_mapping.build_sheets,
        sheet_info=mikadiv_vib_mapping.SHEET_INFO,
        legend_rows=mikadiv_vib_mapping.LEGEND_ROWS,
    ),
]


def main() -> None:
    for config in MODULES:
        Generator(config).run()


if __name__ == "__main__":
    main()
