#!/usr/bin/env python3
"""Strip openpyxl's per-run created/modified timestamps from an xlsx's
docProps/core.xml so two builds of otherwise-identical content compare
equal. Mutates each given file in place.
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


def normalize(path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".normalizing")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                data = TIMESTAMP_RE.sub(PLACEHOLDER, data)
            zout.writestr(item, data)
    tmp.replace(path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: normalize_xlsx.py <path.xlsx> [<path.xlsx> ...]", file=sys.stderr)
        raise SystemExit(2)
    for arg in sys.argv[1:]:
        normalize(Path(arg))
