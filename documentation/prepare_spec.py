"""Generate Bikeshed boilerplate consumed by documentation/index.bs.

Embeds the changelog table into header.include so it appears above the table of
contents in both the HTML site and the PDF.

Bikeshed's `Local Boilerplate: header yes` resolves relative to each `.bs`
source file's own directory, so this shared shell needs a byte-identical copy
in each of the three directories that reference it (documentation/, mikadiv-vib/,
streamld/) or Bikeshed silently falls back to stock boilerplate. All three
copies are regenerated here from the same merged content.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "header.template.include"
CHANGELOG = ROOT / "changelog.include.bs"
OUTPUTS = (
    ROOT / "header.include",
    ROOT.parent / "mikadiv-vib" / "header.include",
    ROOT.parent / "streamld" / "header.include",
)


def _strip_bs_comments(text: str) -> str:
    lines: list[str] = []
    in_comment = False
    for line in text.splitlines():
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    changelog = _strip_bs_comments(CHANGELOG.read_text(encoding="utf-8"))
    merged = template.replace("{{CHANGELOG}}", changelog)
    for output in OUTPUTS:
        output.write_text(merged, encoding="utf-8")


if __name__ == "__main__":
    main()
