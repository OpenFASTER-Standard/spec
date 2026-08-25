from __future__ import annotations

from kafe.status_codes import RANGE_ORDER, STATUS_CODES, codes_in_range


def test_has_all_seven_ranges_in_ascending_order():
    assert RANGE_ORDER == [
        "1xxx - Delivery/file-level",
        "2xxx - Anliegen/Anspruch",
        "3xxx - AllgAngaben",
        "4xxx - SteuerlicheBehandlung",
        "5xxx - Zahlungsweg",
        "6xxx - Ertrag",
        "7xxx - Par50jEStG",
    ]


def test_total_code_count_is_213():
    # The handbook's own Annex 7.4 ("7.4. Status codes" / "Table 70: Status
    # codes", pages 190-212) has 213 rows total: "0000" plus 212 further
    # error/validation codes. This plan's own research pass had estimated 219
    # before the appendix was actually read in full; 213 is the real,
    # verified count (cross-checked via two independent extraction passes
    # over the source PDF -- see task-2-report.md for detail).
    assert len(STATUS_CODES) == 213


def test_known_code_0000_is_ok():
    assert STATUS_CODES["0000"].message.strip() != ""


def test_known_code_1001_antragid_reused():
    code = STATUS_CODES["1001"]
    assert "AntragId" in code.message
    assert code.range_label == "1xxx - Delivery/file-level"


def test_known_code_7601_transaction_sequence():
    code = STATUS_CODES["7601"]
    assert "TransactionId" in code.message or "TransaktionId" in code.message
    assert code.range_label == "7xxx - Par50jEStG"


def test_codes_in_range_returns_sorted_subset():
    par50j = codes_in_range("7xxx - Par50jEStG")
    assert all(c.code.startswith("7") for c in par50j)
    assert par50j == sorted(par50j, key=lambda c: c.code)
