from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def test_index_bs_links_request_and_response():
    content = (ROOT / "kafe" / "index.bs").read_text()
    assert "Shortname: kafe" in content
    assert "/kafe/request" in content
    assert "/kafe/response" in content
    assert "DOCVERSION" not in content
