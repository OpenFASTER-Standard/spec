"""Parses a module's canonical version out of its Bikeshed source.

The ``Text Macro: DOCVERSION`` line in a module's own ``.bs`` file is the
single source of truth for that module's version. Everywhere else that needs
it (Excel/PDF filenames, the Excel Meta sheet, CI) reads it from here rather
than keeping an independent copy that could drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_DOCVERSION_RE = re.compile(r"^Text Macro: DOCVERSION (\S+)$", re.MULTILINE)


def read_docversion(bs_path: Path) -> str:
    """Return the DOCVERSION text macro's value from a Bikeshed ``.bs`` file.

    Raises ``ValueError`` if the file has no ``Text Macro: DOCVERSION`` line.
    """
    text = bs_path.read_text(encoding="utf-8")
    match = _DOCVERSION_RE.search(text)
    if match is None:
        raise ValueError(f"No 'Text Macro: DOCVERSION' line found in {bs_path}")
    return match.group(1)


if __name__ == "__main__":
    print(read_docversion(Path(sys.argv[1])))
