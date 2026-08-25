# kafe/tests/test_response_doc_build.py
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def test_va_include_documents_bescheidart_and_clawback_semantics():
    subprocess.run([sys.executable, "-m", "kafe.generate_va_docs"], cwd=ROOT, check=True)
    content = (ROOT / "kafe" / "generated" / "va.include.bs").read_text()
    assert "BescheidArt" in content
    assert "ERSTBESCHEID" in content
    assert "KORREKTUR" in content
    assert "SummeAbrechnung" in content


def test_response_bs_discloses_dip_envelope_gap():
    content = (ROOT / "kafe" / "response.bs").read_text()
    assert "not available yet" in content or "not yet available" in content
    assert "Shortname: kafe-response" in content
    assert "DOCVERSION" not in content  # no PDF/version macro on this doc, per design spec S3
