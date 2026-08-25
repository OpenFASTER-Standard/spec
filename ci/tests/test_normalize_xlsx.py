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
    path_a = tmp_path / "a.xlsx"
    path_b = tmp_path / "b.xlsx"
    _write_xlsx(path_a)
    time.sleep(1.1)  # openpyxl's embedded timestamp has 1-second resolution
    _write_xlsx(path_b)

    with zipfile.ZipFile(path_a) as za, zipfile.ZipFile(path_b) as zb:
        assert za.read("docProps/core.xml") != zb.read("docProps/core.xml")

    normalize(path_a)
    normalize(path_b)

    with zipfile.ZipFile(path_a) as za, zipfile.ZipFile(path_b) as zb:
        assert za.read("docProps/core.xml") == zb.read("docProps/core.xml")


def test_normalize_preserves_non_timestamp_content(tmp_path):
    path = tmp_path / "a.xlsx"
    _write_xlsx(path)
    with zipfile.ZipFile(path) as z:
        before = z.read("xl/worksheets/sheet1.xml")
    normalize(path)
    with zipfile.ZipFile(path) as z:
        after = z.read("xl/worksheets/sheet1.xml")
    assert before == after
