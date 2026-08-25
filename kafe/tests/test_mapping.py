# kafe/tests/test_mapping.py
from __future__ import annotations

from pathlib import Path

from engine.xsd_model import XsdModel
from kafe import mapping

ROOT = Path(__file__).resolve().parent.parent


def _model() -> XsdModel:
    return XsdModel(str(ROOT / "kafe.xsd"))


def test_sheet_order_has_seven_real_sheets():
    assert mapping.SHEET_ORDER == [
        mapping.S_MASTER,
        mapping.S_JURIDICAL,
        mapping.S_COR,
        mapping.S_INCOME,
        mapping.S_INVESTMENT_CHAIN,
        mapping.S_TRANSACTION_DATA,
    ]


def test_certificates_of_residence_sheet_has_six_columns():
    model = _model()
    sheets = mapping.build_sheets(model)
    cor = sheets[mapping.S_COR]
    assert len(cor) == 6
    names = [f[0] for f in cor]
    assert names == [
        "creditorId", "id", "Ausstellungsbehoerde", "Ausstellungsdatum",
        "GueltigVon", "GueltigBis",
    ]


def test_par50j_field_is_conditional_not_optional():
    """HaltedauerMin45T is minOccurs=0 in the raw XSD (Optional by default),
    but status_codes.py's conditional-mandatory logic must override it to
    Conditional -- the whole point of the status-code chaining layer."""
    model = _model()
    sheets = mapping.build_sheets(model)
    income = sheets[mapping.S_INCOME]
    field = next(f for f in income if f[0] == "HaltedauerMin45T")
    assert field[3] == "Conditional"  # requiredness, not "Optional"


def test_transaction_geschaeft_enum_has_six_values():
    model = _model()
    enums, meanings = mapping.build_enums(model)
    assert set(enums["TransaktionGeschaeft"]) == {"PO", "SO", "TL", "RL", "TP", "RP"}


def test_liability_ended_type_is_text_not_number():
    """Regression test for a confirmed, still-live column-defs.json bug (app repo
    MR !808): that JSON says type="number" for this field, but it's really a
    4-digit year expressed as text. This test only passes if mapping.py resolved
    the type from the real XSD (as this task requires) rather than copying
    column-defs.json's own (wrong) type column. Field name is column-defs.json's
    own real nameEn value, verbatim, per this task's column-naming convention."""
    model = _model()
    sheets = mapping.build_sheets(model)
    master = sheets[mapping.S_MASTER]
    field = next(f for f in master if f[0] == "CreditorNat/German_TaxOffice/LiabilityEnded")
    assert "Text" in field[2] or "String" in field[2]  # type_display, not "Integer"/"Number"


def test_economic_interest_description_type_is_text_not_boolean():
    """Same class of regression as above, for the other confirmed column-defs.json
    bug: that JSON says type="boolean", but it's really a free-text description."""
    model = _model()
    sheets = mapping.build_sheets(model)
    master = sheets[mapping.S_MASTER]
    field = next(
        f for f in master
        if f[0] == "TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterestDescription"
    )
    assert "Text" in field[2] or "String" in field[2]  # type_display, not "Boolean"


def test_legend_rows_mention_no_record_type_narrowing():
    """KaFE has no request-type taxonomy at all (confirmed during research) so
    there must be no MiKaDiv-style Excel-narrowing/RecordType legend entry."""
    joined = " ".join(f"{label} {value}" for label, value in mapping.LEGEND_ROWS)
    assert "RecordType" not in joined
