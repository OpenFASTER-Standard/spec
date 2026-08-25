# kafe/tests/test_request_doc_build.py
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def test_rm_include_documents_registriernr_and_validation_list():
    subprocess.run([sys.executable, "-m", "kafe.generate_rm_docs"], cwd=ROOT, check=True)
    content = (ROOT / "kafe" / "generated" / "rm.include.bs").read_text()
    assert "RegistrierNr" in content
    assert "ValidierungsergebnisListe" in content


def test_status_codes_include_has_all_seven_ranges():
    subprocess.run([sys.executable, "-m", "kafe.generate_status_codes_docs"], cwd=ROOT, check=True)
    content = (ROOT / "kafe" / "generated" / "status-codes.include.bs").read_text()
    for range_label in ["1xxx", "2xxx", "3xxx", "4xxx", "5xxx", "6xxx", "7xxx"]:
        assert range_label in content
    # Real total (Task 2, verified via two independent extraction passes) is 213
    # codes across the 7 ranges, plus code "0000" (OK) which lives outside
    # RANGE_ORDER entirely -- 214 real codes total. Data-row <tr> count should be
    # 214 (213 + the "0000" row); allow for a handful of header/structural <tr>s
    # on top, so assert generously rather than exactly.
    assert content.count("<tr>") >= 214
    assert "0000" in content  # confirm the "OK" code isn't silently dropped just
    # because it lives outside RANGE_ORDER's 7 buckets -- see this task's own
    # Step 5 instruction on rendering it as its own section.


def test_request_bs_has_full_changelog_and_docversion_4_3_2():
    content = (ROOT / "kafe" / "request.bs").read_text()
    assert "Text Macro: DOCVERSION 4.3.2" in content
    assert "2023-08-29" in content  # earliest changelog entry, 1.0.0
    assert "4.3.2" in content  # the new entry this task adds
    assert "AntragPar11InvStG" not in content or "cannot be submitted" in content  # bug #1 fix present
