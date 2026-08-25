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
from engine.version import read_docversion

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
MIKADIV_VIB_VERSION = read_docversion(ROOT / "mikadiv-vib" / "request.bs")

from kafe import mapping as kafe_mapping  # noqa: E402  (kafe/ has no hyphen, so a plain import works)

KAFE_VERSION = read_docversion(ROOT / "kafe" / "request.bs")

MODULES: list[ModuleConfig] = [
    ModuleConfig(
        title=mikadiv_vib_mapping.LEGEND_TITLE,
        xsd_path=ROOT / "mikadiv-vib" / "ThirdPartyDisclosureRequest.xsd",
        output_dir=ROOT / "mikadiv-vib" / "generated",
        xlsx_name=f"mikadiv-vib-v{MIKADIV_VIB_VERSION}.xlsx",
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
        slug="mikadiv-vib",
        version=MIKADIV_VIB_VERSION,
        spec_url="https://openfaster.org/mikadiv-vib",
    ),
    ModuleConfig(
        title=kafe_mapping.LEGEND_TITLE,
        xsd_path=ROOT / "kafe" / "kafe.xsd",
        output_dir=ROOT / "kafe" / "generated",
        xlsx_name=f"kafe-v{KAFE_VERSION}.xlsx",
        json_name="template_metadata.json",
        doc_name="TEMPLATE_FIELDS.md",
        bs_name="fields.include.bs",
        legend_sheet_name=kafe_mapping.S_LEGEND,
        master_sheet_name=kafe_mapping.S_MASTER,
        sheet_order=kafe_mapping.SHEET_ORDER,
        build_enums=kafe_mapping.build_enums,
        build_sheets=kafe_mapping.build_sheets,
        sheet_info=kafe_mapping.SHEET_INFO,
        legend_rows=kafe_mapping.LEGEND_ROWS,
        slug="kafe",
        version=KAFE_VERSION,
        spec_url="https://openfaster.org/kafe",
        link_key="creditorId",
    ),
]


def main() -> None:
    for config in MODULES:
        Generator(config).run()


if __name__ == "__main__":
    main()
