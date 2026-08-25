# ci/tests/test_normalize_xlsx.py
from __future__ import annotations

import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from normalize_xlsx import normalize  # noqa: E402

from openpyxl import Workbook


def _write_xlsx(path: Path) -> None:
    wb = Workbook()
    wb.active["A1"] = "hello"
    wb.save(path)


def test_normalize_makes_two_runs_identical(tmp_path):
    # This must assert full raw-byte equality of the whole rewritten file,
    # not just docProps/core.xml's own XML content -- that's what
    # ci/check-generated-up-to-date.sh's `git diff` actually checks (git
    # diffs binary files byte-for-byte), and openpyxl stamps a "now"
    # date_time on EVERY zip entry it writes, not just docProps/core.xml,
    # so a docProps-only check can pass while the two files still differ.
    path_a = tmp_path / "a.xlsx"
    path_b = tmp_path / "b.xlsx"
    _write_xlsx(path_a)
    time.sleep(1.1)  # openpyxl's embedded timestamp has 1-second resolution
    _write_xlsx(path_b)

    assert path_a.read_bytes() != path_b.read_bytes()

    normalize(path_a)
    normalize(path_b)

    assert path_a.read_bytes() == path_b.read_bytes()


def test_normalize_preserves_non_timestamp_content(tmp_path):
    path = tmp_path / "a.xlsx"
    _write_xlsx(path)
    with zipfile.ZipFile(path) as z:
        before = z.read("xl/worksheets/sheet1.xml")
    normalize(path)
    with zipfile.ZipFile(path) as z:
        after = z.read("xl/worksheets/sheet1.xml")
    assert before == after
