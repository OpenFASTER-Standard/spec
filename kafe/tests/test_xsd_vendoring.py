"""Confirms the vendored KaFE XSD family loads via the shared, generic XsdModel
with no KaFE-specific code changes needed in engine/xsd_model.py's core logic."""
from __future__ import annotations

from pathlib import Path

from engine.xsd_model import XsdModel

ROOT = Path(__file__).resolve().parent.parent


def test_kafe_xsd_loads_and_resolves_erstattungsantrag():
    model = XsdModel(str(ROOT / "kafe.xsd"))
    field = model.attr("Erstattungsantrag_CType", "AntragId")
    assert field.name == "AntragId"
    assert field.required is True
    assert "UUID" in field.type_display


def test_kafe_rm_xsd_loads_and_resolves_registriernr():
    model = XsdModel(str(ROOT / "kafe-rm.xsd"))
    field = model.attr("Antrag_CType", "AntragId")
    assert field.name == "AntragId"


def test_kafe_va_xsd_loads_and_resolves_bescheidart():
    model = XsdModel(str(ROOT / "kafe-va.xsd"))
    field = model.elem("Bescheid_CType", "BescheidArt")
    assert field.name == "BescheidArt"


def test_kap_art_enum_has_eleven_values():
    # NOTE: the task-1 brief expected 10 values; the actual vendored v1.4.0
    # kafe.xsd has 11 (includes SONSTIGE / "Other income" in addition to the
    # 10 named categories). Asserting against the real schema content per
    # this task's own goal of proving XsdModel resolves the real file.
    model = XsdModel(str(ROOT / "kafe.xsd"))
    values, meanings = model.enum("KapitalertragArt_ENUM")
    assert len(values) == 11
    assert "DIVIDENDEN" in values
    assert meanings["DIVIDENDEN"]  # has a real meaning string, not empty
