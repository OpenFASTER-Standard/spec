"""Generate Bikeshed boilerplate consumed by documentation/index.bs.

Bikeshed's `Local Boilerplate: header yes` resolves relative to each `.bs`
source file's own directory, so this shared shell needs a byte-identical copy
in each of the four directories that reference it (documentation/, mikadiv-vib/,
streamld/, kafe/) or Bikeshed silently falls back to stock boilerplate. All
four copies are regenerated here from the same merged content.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "header.template.include"
OUTPUTS = (
    ROOT / "header.include",
    ROOT.parent / "mikadiv-vib" / "header.include",
    ROOT.parent / "streamld" / "header.include",
    ROOT.parent / "kafe" / "header.include",
)


def main() -> None:
    merged = TEMPLATE.read_text(encoding="utf-8")
    for output in OUTPUTS:
        output.write_text(merged, encoding="utf-8")


if __name__ == "__main__":
    main()
