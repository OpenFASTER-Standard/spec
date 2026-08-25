#!/usr/bin/env python3
"""Strip openpyxl's per-run timestamps from an xlsx so two builds of
otherwise-identical content produce byte-identical files. Two separate
non-determinism sources, both handled: (1) docProps/core.xml's own
dcterms:created/modified XML content, and (2) the ZIP container's
per-entry date_time field, which openpyxl also stamps with "now" for
every entry it writes, not just docProps/core.xml -- both must be
normalized or the rewritten files still differ byte-for-byte even after
the XML-level fix. Mutates each given file in place.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

TIMESTAMP_RE = re.compile(
    rb"<dcterms:(created|modified)([^>]*)>[^<]*</dcterms:\1>"
)
PLACEHOLDER = rb"<dcterms:\1\2>1970-01-01T00:00:00Z</dcterms:\1>"
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)  # ZIP format's own minimum representable date


def normalize(path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".normalizing")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                data = TIMESTAMP_RE.sub(PLACEHOLDER, data)
            item.date_time = FIXED_DATE_TIME
            zout.writestr(item, data)
    tmp.replace(path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: normalize_xlsx.py <path.xlsx> [<path.xlsx> ...]", file=sys.stderr)
        raise SystemExit(2)
    for arg in sys.argv[1:]:
        normalize(Path(arg))
