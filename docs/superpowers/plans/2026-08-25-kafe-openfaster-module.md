# KaFE OpenFASTER Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new `kafe/` OpenFASTER module — landing page + Request document + provisional Response document — generated from the real, current BZSt KaFE v1.4.0 XSD family, mirroring `mikadiv-vib`'s already-shipped XSD-vendoring + Bikeshed-doc-generation pipeline, and publish it as version 4.3.2.

**Architecture:** Extends the existing three-layer engine (`engine/xsd_model.py` Layer 1 / a module's own `mapping.py` Layer 2 / `engine/generator.py` Layer 3) with one new piece: a hand-transcribed status-code catalog (`kafe/status_codes.py`) that supplies the conditional-mandatory logic the raw XSD alone can't express (mainly §50j EStG). Three Bikeshed documents (`index.bs`, `request.bs`, `response.bs`) are generated the same way `mikadiv-vib`'s three documents are, reusing the generic `XsdModel` directly (it is already schema-agnostic — no subclass needed).

**Tech Stack:** Python 3.12, `xmlschema`, `openpyxl`, Bikeshed, WeasyPrint (PDF), GitHub Actions CI.

**Spec:** `docs/superpowers/specs/2026-08-25-kafe-openfaster-module-design.md`

## Global Constraints

- Vendor the real, current v1.4.0 XSD family from `/work/kafe-research/xsd/` (`kafe.xsd`, `kafe-rm.xsd`, `kafe-va.xsd`, `kafe-standardtypes.xsd`, `kafe-statustypes.xsd`, `kafe-isotypes.xsd`) — never the stale v1.3.0 copy bundled in the unrelated `mikadiv-demo-clone` repo.
- Field/column **shape** of the 7 real Excel sheets must not change from what production's `column-defs.json` (`/work/app/apps/backend/src/bulk-processing/kafe-dip/helpers/column-defs.json`) already defines. Presentation/tooling conventions (legend sheet, dropdowns, Meta sheet) are harmonized with `mikadiv-vib`'s richer style; the actual fields a bank fills in are not.
- Requiredness source-of-truth chaining: the XSD's own `required=`/`minOccurs` is primary; `kafe/status_codes.py`'s conditional-mandatory codes (mainly the `7xxx` §50j range) override it wherever they disagree, via the same `SYN()`-style explicit-override convention `mikadiv-vib/mapping.py` already uses.
- Site structure: `/kafe` (landing, `Shortname: kafe`) + `/kafe/request` (`Shortname: kafe-request`, keeps `DOCVERSION`/PDF/Excel, covers submission fields **and** the synchronous `kafe-rm.xsd` accept/reject receipt) + `/kafe/response` (`Shortname: kafe-response`, HTML only, `kafe-va.xsd` only, explicitly provisional).
- Final published version: **4.3.2**. Single `DOCVERSION` macro in `kafe/request.bs` drives the doc version, the Excel "Meta" sheet version, and the PDF/Excel filenames (`kafe-v4.3.2.{pdf,xlsx}`), resolving the existing doc's own confirmed dual-versioning inconsistency.
- The full existing KaFE interface changelog (1.0.0 2023-08-29 → 4.3.1 2026-06) is carried forward verbatim in `request.bs`, with a new 4.3.2 entry appended following the changelog's own MAJOR/MINOR/PATCH convention. This is **not** the same as `documentation/changelog.include.bs` (the OpenFASTER family-wide changelog) — that file is out of scope for this plan, matching how the MiKaDiv Request/Response split also left it untouched.
- Status-code catalog: **complete coverage of all 219 codes**, not just the subset that drives requiredness — the same transcription serves both the requiredness logic and a full status/error-code appendix in `request.bs` (a genuine improvement over the existing doc, which has none).
- `--die-on=link-error` always on for every `bikeshed` build. Never hand-edit anything under `kafe/generated/`.
- Any standalone generator script invoked as `python kafe/some_script.py` from repo root needs the `PYTHONPATH=.` treatment already established as a standing ruling in this repo (Python puts the invoked script's own directory on `sys.path[0]`, not the invoking cwd) — **unless** the plan-writer's own check below confirms `-m kafe.some_script` works instead, since `kafe` (unlike `mikadiv-vib`) has no hyphen and may not need the workaround. Task 5 must actually test both and use whichever really works.
- Non-goals (do not build in this plan): demo/synthetic data for the LO POC (bulk-platform's own separate sub-project 15), the actual `bulk-platform` KaFE submission backend (sub-project 9), any Divizend-internal parser/workflow concept (BNY/Clearstream/Euroclear ingestion, the "approved" reviewer checkbox, bulk-edit/archive), and the separate `kafe-bop-general` submission path.

---

### Task 1: Vendor the KaFE XSD family + confirm the generic XsdModel loads it

**Files:**
- Create: `kafe/kafe.xsd`, `kafe/kafe-rm.xsd`, `kafe/kafe-va.xsd`, `kafe/kafe-standardtypes.xsd`, `kafe/kafe-statustypes.xsd`, `kafe/kafe-isotypes.xsd`
- Modify: `engine/xsd_model.py:31-44` (extend `FRIENDLY_TYPES`)
- Test: `kafe/tests/test_xsd_vendoring.py`

**Interfaces:**
- Consumes: `engine.xsd_model.XsdModel` (existing, unchanged — `XsdModel(path)`, `.elem()`, `.attr()`, `.path()`, `.enum()`, `.inline_enum()`, all schema-agnostic already; no subclass needed for KaFE).
- Produces: the 6 vendored `.xsd` files at `kafe/*.xsd`, importable by `xmlschema.XMLSchema("kafe/kafe.xsd")` (and separately `kafe/kafe-rm.xsd`, `kafe/kafe-va.xsd`) with all `xs:include`s resolving relative to the same directory.

- [ ] **Step 1: Copy the vendored XSD files**

The real, current v1.4.0 files are already downloaded and verified (during this plan's own brainstorming phase) at `/work/kafe-research/xsd/`. Copy all 6 into a new `kafe/` directory at the repo root:

```bash
mkdir -p kafe
cp /work/kafe-research/xsd/kafe.xsd kafe/kafe.xsd
cp /work/kafe-research/xsd/kafe-rm.xsd kafe/kafe-rm.xsd
cp /work/kafe-research/xsd/kafe-va.xsd kafe/kafe-va.xsd
cp /work/kafe-research/xsd/kafe-standardtypes.xsd kafe/kafe-standardtypes.xsd
cp /work/kafe-research/xsd/kafe-statustypes.xsd kafe/kafe-statustypes.xsd
cp /work/kafe-research/xsd/kafe-isotypes.xsd kafe/kafe-isotypes.xsd
```

Confirmed include graph (all `xs:include schemaLocation="..."` are bare filenames, resolved relative to the including file's own directory, so a flat `kafe/` layout works exactly like `mikadiv-vib/`'s single-file layout):
- `kafe.xsd` includes `kafe-standardtypes.xsd`
- `kafe-rm.xsd` includes `kafe-standardtypes.xsd` and `kafe-statustypes.xsd`
- `kafe-va.xsd` includes `kafe-standardtypes.xsd`
- `kafe-standardtypes.xsd` includes `kafe-isotypes.xsd`
- `kafe-statustypes.xsd` and `kafe-isotypes.xsd` have no further includes

Confirm each vendored file's own version marker matches what's expected (grep, not a full read):

```bash
grep -m1 'version="1.4.0"' kafe/kafe.xsd && echo "kafe.xsd OK: 1.4.0"
grep -c 'KAFERMCType' kafe/kafe-rm.xsd
grep -c 'BescheidArt_ENUM' kafe/kafe-va.xsd
```

Expected: `kafe.xsd OK: 1.4.0` printed; both greps return a count ≥ 1.

- [ ] **Step 2: Write the failing test**

```python
# kafe/tests/test_xsd_vendoring.py
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


def test_kap_art_enum_has_ten_values():
    model = XsdModel(str(ROOT / "kafe.xsd"))
    values, meanings = model.enum("KapitalertragArt_ENUM")
    assert len(values) == 10
    assert "DIVIDENDEN" in values
    assert meanings["DIVIDENDEN"]  # has a real meaning string, not empty
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_xsd_vendoring.py -v`
Expected: FAIL — `kafe/kafe.xsd` doesn't exist yet (or import error), since Step 1's files aren't committed as part of the test run environment yet if run before Step 1. If Step 1 already ran, this instead validates the vendored files are structurally sound; either way, run it now to establish the baseline.

- [ ] **Step 4: Extend `FRIENDLY_TYPES` for KaFE's own named types**

`engine/xsd_model.py`'s `FRIENDLY_TYPES` dict (lines 31-44) currently only has MiKaDiv-scoped entries (`UUIDType`, `CountryISO3166Alpha2Type`, etc.), keyed by `local_name` so there's no collision risk adding KaFE's own real named types (which use a different naming convention — `UUID_Type` with an underscore, not `UUIDType`). Add these entries, sourced directly from `kafe-standardtypes.xsd`'s own real type definitions (confirmed during this plan's research phase):

```python
# In engine/xsd_model.py, add to the existing FRIENDLY_TYPES dict (do not remove
# the existing MiKaDiv entries):
    "UUID_Type": "UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)",
    "RegistrierNr_Type": "Text (9 characters, BZSt-assigned)",
    "TransferticketId_Type": "Text (1-170 characters)",
    "KennNr_Type": "Numeric string (8-digit BZSt withholding-tax number)",
    "ISIN_Type": "ISIN (12-digit)",
```

Leave `Betrag_Type`/`Stueckzahl_Type`/`BetragNull_Type`/`StueckzahlNull_Type` etc. to the generic decimal/integer fallback logic already in `_type_display()` (lines 107-130) — they're plain decimal/integer restrictions with no special format worth a friendly label, unlike the identifier types above.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_xsd_vendoring.py -v`
Expected: PASS, all 4 tests.

- [ ] **Step 6: Commit**

```bash
git add kafe/kafe.xsd kafe/kafe-rm.xsd kafe/kafe-va.xsd kafe/kafe-standardtypes.xsd kafe/kafe-statustypes.xsd kafe/kafe-isotypes.xsd kafe/tests/test_xsd_vendoring.py engine/xsd_model.py
git commit -m "feat: vendor the real KaFE v1.4.0 XSD family"
```

---

### Task 2: Status-code catalog (`kafe/status_codes.py`) — full 219-code coverage

**Files:**
- Create: `kafe/status_codes.py`
- Test: `kafe/tests/test_status_codes.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `kafe.status_codes.STATUS_CODES: dict[str, StatusCode]`, where `StatusCode` is a `@dataclass(frozen=True)` with fields `code: str`, `range_label: str` (one of the 7 range names below), `message: str` (English). Also produces `kafe.status_codes.RANGE_ORDER: list[str]` (the 7 range labels in ascending numeric order) and `kafe.status_codes.codes_in_range(range_label: str) -> list[StatusCode]` (sorted by code). Later tasks (3, 5) import `STATUS_CODES`, `RANGE_ORDER`, and `codes_in_range`.

- [ ] **Step 1: Write the failing test**

```python
# kafe/tests/test_status_codes.py
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


def test_total_code_count_is_219():
    assert len(STATUS_CODES) == 219


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_status_codes.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kafe.status_codes'` (and `kafe/__init__.py` doesn't exist yet either — create an empty one alongside this task so `kafe` is importable as a package: `touch kafe/__init__.py`).

- [ ] **Step 3: Transcribe the full status-code catalog**

Source: `/work/kafe-research/handbook/Kommunikationshandbuch_DIP-KAFE_v1_4_0_en.pdf`, Annex 7.4 (the status-codes appendix — confirmed during this plan's research phase to span roughly pages 190-212, but **confirm the exact page range yourself** by reading the PDF's own table of contents / searching for the appendix heading, since page numbering can shift between the plan-writing pass and execution).

Read every page of that appendix with the `Read` tool's `pages` parameter (20 pages at a time, e.g. `pages: "190-209"` then `pages: "210-212"`, adjusting to whatever the real range turns out to be), and transcribe **every single row** of the status-code table verbatim into `kafe/status_codes.py`. Each row has (at minimum) a numeric code and an English message; some rows also name the specific field/section the code concerns — include that context in the message text if the table presents it that way, rather than dropping it.

Structure the file like this (illustrative skeleton — the actual `_RAW` list must contain all 219 real rows from the PDF, not placeholders):

```python
"""Layer 0.5: KaFE's status-code catalog.

Hand-transcribed from the official BZSt DIP-KAFE v1.4.0 communication handbook's
own status-code appendix (Annex 7.4) -- these codes exist only inside a PDF, with
no machine-readable source, so this is the one genuinely hand-authored data file
in this module (everything else is generated from the real XSD).

Two uses: (1) kafe/mapping.py layers real conditional-mandatory requiredness on
top of the XSD's own required=/minOccurs wherever they disagree (mainly the
7xxx / Par50jEStG range, where almost every field is minOccurs=0 in the raw
XSD but has real conditional-mandatory logic expressed only here); (2) a full
status/error-code reference appendix is rendered into kafe/request.bs's
error-handling section via kafe/generate_status_codes_docs.py, since banks see
these codes today via kafe-rm.xsd's ValidierungsergebnisListe and the existing
interface document has no such appendix at all.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StatusCode:
    code: str
    range_label: str
    message: str


RANGE_ORDER: list[str] = [
    "1xxx - Delivery/file-level",
    "2xxx - Anliegen/Anspruch",
    "3xxx - AllgAngaben",
    "4xxx - SteuerlicheBehandlung",
    "5xxx - Zahlungsweg",
    "6xxx - Ertrag",
    "7xxx - Par50jEStG",
]


def _range_for(code: str) -> str:
    first_digit = code[0]
    index = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6}[first_digit]
    return RANGE_ORDER[index]


# (code, message) pairs, transcribed verbatim from the handbook's Annex 7.4.
# "0000" (OK) plus all 219 real error/validation codes.
_RAW: list[tuple[str, str]] = [
    ("0000", "OK"),
    ("1001", "The AntragId has already been used."),
    # ... every remaining row from the handbook, transcribed verbatim ...
    ("7601", "The TransactionId is not consecutive."),
    ("7620", "The specified transaction is not authorised for this transaction type."),
]

STATUS_CODES: dict[str, StatusCode] = {
    code: StatusCode(code=code, range_label=_range_for(code), message=message)
    for code, message in _RAW
}


def codes_in_range(range_label: str) -> list[StatusCode]:
    return sorted(
        (c for c in STATUS_CODES.values() if c.range_label == range_label),
        key=lambda c: c.code,
    )
```

Every entry in `_RAW` must be a real row from the handbook — do not invent, paraphrase, or skip any. If the handbook's own numbering has gaps (e.g. no `1002` exists), that's fine — `_RAW` simply doesn't have an entry for it; `test_total_code_count_is_219` is the check that the total transcribed count matches the handbook's own stated total (if the real total turns out to differ from 219 once you're looking at the actual table, update the test to match the real count and note the discrepancy in your task report — 219 was this plan's own best count from the research pass, not guaranteed exact).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_status_codes.py -v`
Expected: PASS, all 6 tests (adjust `test_total_code_count_is_219` first if Step 3 found the real total differs).

- [ ] **Step 5: Commit**

```bash
git add kafe/__init__.py kafe/status_codes.py kafe/tests/test_status_codes.py
git commit -m "feat: transcribe KaFE's full 219-code status catalog"
```

**Note for the task reviewer:** this is the single highest transcription-error-risk task in the whole plan (219 hand-transcribed entries from a PDF table). Task 10's final gate includes a dedicated spot-check of a sample of these codes against the handbook directly — don't skip that step even if this task's own tests pass, since the tests only check a handful of known codes, not the full 219.

---

### Task 3: `kafe/mapping.py` — Excel template shape + requiredness chaining

**Files:**
- Create: `kafe/mapping.py`
- Test: `kafe/tests/test_mapping.py`

**Interfaces:**
- Consumes: `engine.xsd_model.XsdModel` (Task 1), `kafe.status_codes.STATUS_CODES` (Task 2).
- Produces: `kafe.mapping.build_enums(model: XsdModel) -> tuple[dict, dict]`, `kafe.mapping.build_sheets(model: XsdModel) -> dict[str, list[tuple]]`, `kafe.mapping.SHEET_ORDER: list[str]`, `kafe.mapping.S_LEGEND`/`S_META` sheet-name constants, `kafe.mapping.SHEET_INFO: dict`, `kafe.mapping.LEGEND_ROWS: list[tuple]`, `kafe.mapping.LEGEND_TITLE: str` — the exact same contract `mikadiv-vib/mapping.py` exposes (5-tuple fields: `(name, description, type_display, requiredness, enum_key)`), consumed by `engine.generator.Generator`/`ModuleConfig` in Task 4.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_mapping.py -v`
Expected: FAIL — `kafe/mapping.py` doesn't exist yet.

- [ ] **Step 3: Write `kafe/mapping.py`**

This is the task's core deliverable. Build it in this order, cross-referencing **two** real source files throughout — `kafe/kafe.xsd` (vendored in Task 1; already fully read during this plan's own writing, its complete structure is reproduced below) and production's real column-defs.json at `/work/app/apps/backend/src/bulk-processing/kafe-dip/helpers/column-defs.json` (2613 lines — read it directly; do not guess field names) — since `column-defs.json` is the real, production-proven field/column shape this plan's Global Constraints require preserving, while `kafe.xsd` is the source for each field's description/type.

**3a. Sheet name constants and `SHEET_ORDER`.** Mirror `mikadiv-vib/mapping.py:22-36`'s convention (`S_LEGEND`, numbered sheet names). Use column-defs.json's real 7 sheets:

```python
S_LEGEND = "0 Legend Notes"
S_MASTER = "1 Creditors Natural"       # column-defs.json: creditorsNatural
S_JURIDICAL = "2 Creditors Juridical"  # column-defs.json: creditorsJuridical
S_COR = "3 Certificates Of Residence"  # column-defs.json: certificatesOfResidence
S_INCOME = "4 Income"                  # column-defs.json: income
S_INVESTMENT_CHAIN = "5 Investment Chain"  # column-defs.json: investmentChain
S_TRANSACTION_DATA = "6 Transaction Data"  # column-defs.json: transactionData
# "meta" is handled separately by engine/generator.py's own Generator.run() --
# it always creates a "Meta" sheet itself (engine/generator.py:605-606,
# _build_meta), do not declare it here, matching how mikadiv-vib/mapping.py
# also never declares a Meta sheet of its own.

SHEET_ORDER = [S_MASTER, S_JURIDICAL, S_COR, S_INCOME, S_INVESTMENT_CHAIN, S_TRANSACTION_DATA]
```

**Column naming convention — read this before writing any field mapping below.**
`kafe.xsd`'s raw element names are German (`SteuerpflichtDEEndeJahr`, `Zuflussdatum`, ...), unlike MiKaDiv's own already-English VIB schema — so `mikadiv-vib/mapping.py`'s convention of using the raw XSD element name as the Excel column header (`field.name`, sourced from `component.local_name`) does **not** carry over here; doing so would produce German technical column headers, which would not be "content-wise identical to what exists" (the user's own explicit requirement — the existing document and every real KaFE spreadsheet on this box uses English `nameEn`-style paths as headers). Production already solved this: `column-defs.json`'s own `nameEn` field (e.g. `"CreditorNat/German_TaxOffice/LiabilityEnded"`, `"generalData/Country"`) is the real, already-shipped English column-header convention, confirmed directly against the real demo `data.xlsx` files during this plan's research. It is **not** internally consistent in its own prefixing (some paths keep a `CreditorNat/`/`CreditorJur/` prefix, others don't) — do not try to "clean it up" or invent a more consistent scheme; use each field's `nameEn` value **verbatim** as the `name=` override argument to `E()`/`A()`/`P()`/`SYN()` (all four helpers already support this per `mikadiv-vib/mapping.py:185-198`'s own signatures), so the Excel column headers match production's real, already-shipped headers exactly, prefix inconsistencies included.

**3b. `certificatesOfResidence` (`S_COR`) — the smallest sheet, do this one first to establish the pattern.** Its 6 real columns (all required, confirmed during research): `creditorId`, `id`, `Ausstellungsbehoerde`/Issuer, `Ausstellungsdatum`/IssuedAt, `GueltigVon`/ValidFrom, `GueltigBis`/ValidUntil. There is no single KaFE XSD attribute/element named literally `creditorId` or `id` (those are Divizend's own cross-sheet linking keys, analogous to MiKaDiv's `RequestId` — a presentation-layer concept, not an XSD field) — use `SYN()` for both, the same way `mikadiv-vib/mapping.py`'s `fk()` helper (line 197-198) synthesizes its own linking-key column. The remaining 4 real fields correspond to KaFE's certificate-of-residence concept inside `SteuerlicheBehandlung_CType.Ansaessigkeitsbescheinigung` (type `AnsaessBescheinigung_Struct`, defined in `kafe-standardtypes.xsd` — read that file directly, e.g. `grep -A20 'name="AnsaessBescheinigung_Struct"' kafe/kafe-standardtypes.xsd`, to get the exact element names for issuer/issued-date/valid-from/valid-to and use `model.elem("AnsaessBescheinigung_Struct", "<real element name>")` for each).

**3c. `income` (`S_INCOME`) — the largest, most structurally important sheet.** This corresponds to `Ertrag_CType` (defined in `kafe.xsd`, fully reproduced below) plus its nested `ErtragAllg_CType` and `Par50jEStG_Struct`. `kafe.xsd`'s real structure, confirmed by direct read during this plan's writing:

```xml
<!-- Ertrag_CType (kafe.xsd) -->
Ertrag_CType
  attribute ErtragId (integer >= 1, required) -- "Sequence number of the income, starting with 1"
  ErtragAllg (ErtragAllg_CType, required)
  RemittanceBase (RemittanceBaseType, optional)
  MittelbareBeteiligung (MittelbBeteiligung_CType, optional)
  Nachweis (Nachweis_Struct, required)
  Par50jEStG (Par50jEStG_Struct, optional)

<!-- ErtragAllg_CType (kafe.xsd) -- every element listed here, in schema order -->
ErtragAllg_CType
  KapArt (KapitalertragArt_ENUM, required)          -- "Type of capital income"
  Hinterlegungsscheine (boolean, optional)            -- "Are they depositary receipts?"
  ISIN (ISIN_Type, optional)
  Underlying (ISIN_Type, optional)                    -- "ISIN of the underlying"
  Schuldnerin (OrganisationName_Type, required)       -- "Debtor of the capital income / distributing company"
  Stnr (Stnr_Type, optional)                          -- "Tax number"
  VersicherungsNr (string 1-40, optional)             -- "Policy number of the life insurance"
  Zuflussdatum (date, required)                       -- "Date of receipt of capital income"
  Bruttozufluss (Betrag_Type, required)               -- "Gross income from capital received"
  AnzahlAnteile (Stueckzahl_Type, optional)           -- "Number of shares/bonds"
  WesentlicheBeteiligung (WesentlicheBeteiligung_Struct, optional)
  vGA (boolean, optional)                             -- "constructive dividend"
  WirtschaftlEigentum (boolean, required)             -- beneficial ownership at inflow
  SitzNichtDE (boolean, optional)
  WohnsitzDE (boolean, optional)
  Steuerbefreiung (boolean, optional)
  BetriebsstaetteDE (boolean, optional)
  UnbeschraenktAuslaendKoerperschaftstpfl (boolean, optional)  -- NEW in v1.4.0
  Anrechnungsbetrag (Anrechnungsbetrag_Type, optional)          -- NEW in v1.4.0
```

For `Par50jEStG_Struct`'s own real substructure (already directly confirmed during research), read `kafe/kafe-standardtypes.xsd` yourself for the exact element names (`grep -A80 'name="Par50jEStG_Struct"' kafe/kafe-standardtypes.xsd`) — its real shape is `Haltedauer` (required, 4 fields: `HaltedauerMin45T`, `HaltedauerMin1J`, `HaltedauerKuerzer45T`, `AnteilePar50jEStG`), `MinWertAendRisiko` (optional, 3 fields: `GegenlAnsprueche`, `RisikoMin70`, `GegenlAnspruecheAndere`), `WeiterlVerpflichtung` (optional, 3 fields: `WeiterlVerpfl`, `WeiterlVerpflAnteile`, `WeiterlVerpflAndere`), `RueckgabeVerpflichtung` (optional, 2 fields: `RueckgabeVerpfl`, `RueckgabeVerpflAnteile`), `Transaktionsdaten` (required — but this whole sub-block is handled on the **`transactionData` sheet**, §3e below, not the `income` sheet, matching production's own `column-defs.json` split).

Every one of the 4 `Haltedauer` fields, all 3 `MinWertAendRisiko`/`WeiterlVerpflichtung` fields, and both `RueckgabeVerpflichtung` fields are `minOccurs="0"` in the raw XSD — this is exactly where `kafe/status_codes.py`'s conditional-mandatory codes (`7xxx` range) must override the raw-XSD `Optional` to `Conditional`. Write a small local helper in `mapping.py`, e.g.:

```python
from kafe.status_codes import STATUS_CODES

# Fields the raw XSD marks minOccurs="0" but which are really conditionally
# mandatory per the status-code catalog's 7xxx (Par50jEStG) range -- confirmed
# during research: almost the entire Par50jEStG block needs this override.
PAR50J_CONDITIONAL_FIELDS = {
    "HaltedauerMin45T", "HaltedauerMin1J", "HaltedauerKuerzer45T", "AnteilePar50jEStG",
    "GegenlAnsprueche", "RisikoMin70", "GegenlAnspruecheAndere",
    "WeiterlVerpfl", "WeiterlVerpflAnteile", "WeiterlVerpflAndere",
    "RueckgabeVerpfl", "RueckgabeVerpflAnteile",
}


def _par50j_requiredness(field_name: str, xsd_required: bool) -> str:
    if field_name in PAR50J_CONDITIONAL_FIELDS:
        return "Conditional"
    return "Required" if xsd_required else "Optional"
```

Use `_par50j_requiredness()` (passed as the explicit `req=` override argument to the `E()`/`A()` helper, the same way `mikadiv-vib/mapping.py` passes explicit `req="Conditional"` literals throughout its own `build_sheets()`, e.g. line 217/218/261) for every one of the 12 fields listed in `PAR50J_CONDITIONAL_FIELDS`.

**3d. `investmentChain` (`S_INVESTMENT_CHAIN`) — 10 real columns, confirmed during research**, corresponding to `MittelbBeteiligung_CType.Beteiligungskette` (type `Beteiligungskette_Struct`, itself containing a repeating `Beteiligung` element — read `kafe/kafe-standardtypes.xsd` for `Beteiligungskette_Struct`'s and its child `Beteiligung`'s exact element names, e.g. `grep -A40 'name="Beteiligungskette_Struct"' kafe/kafe-standardtypes.xsd`). Known real columns from research: `creditorId` (SYN, linking key), `incomeId` (SYN, foreign key to `S_INCOME`), `BeteiligungsId`/SequenceNumber (the real XSD attribute, confirmed unique via `kafe.xsd`'s own `<xs:unique name="unique-BeteiligungId">` constraint at line 605-608), `OrganisationName`, `Rechtsform`/LegalForm, `BeteiligungHoehe`/Ownership, `Ansaessigkeitsstaat`/Country, `Vermoegensverwaltung`/AssetManagement, plus `Stnr`/TIN (the one optional column) and one more field confirmed present but not itemized during research — cross-check the real column-defs.json entry for `investmentChain` directly to get the exact 10th field and confirm the other 9, rather than assuming this list is complete.

**3e. `transactionData` (`S_TRANSACTION_DATA`) — 14 real columns, confirmed during research**, corresponding to `Par50jEStG_Struct.Transaktionsdaten` → `Depot_Struct` → `Transaktion_Struct` (read `kafe/kafe-standardtypes.xsd` directly for exact names, e.g. `grep -A50 'name="Depot_Struct"' kafe/kafe-standardtypes.xsd` and `grep -A30 'name="Transaktion_Struct"' kafe/kafe-standardtypes.xsd`). Known real columns: `creditorId`, `incomeId` (SYN, linking keys), `TransaktionId`/TransactionNumber (attribute on `Transaktion_Struct`, sequential per depot, non-gapped — validated by status code `7601`, confirmed during research), `Depotnummer`/DepotNumber, `Transaktionsart`/TransactionDirection (`TransaktionArt_ENUM`: `ZUGANG`/`ABGANG`), plus `Anfangsbestand`/`AnfangsbestandDatum` (opening balance/date), `Endbestand`/`EndbestandDatum` (closing balance/date), `Handelstag`/TradingDay, `Geschaeft`/TransactionType (`TransaktionGeschaeft_ENUM`: `PO`/`SO`/`TL`/`RL`/`TP`/`RP`), `Stueckzahl`/ShareCount, `VereinbAbwicklungstag`/AgreedSettlementDate, `TatsaechlAbwicklungstag`/ActualSettlementDate — cross-check the exact 14 against the real `column-defs.json` entry for `transactionData`, since opening/closing balance may live at the `Depot` level (once per depot) rather than repeated per-transaction-row in the flattened Excel sheet; resolve this by reading how `column-defs.json` actually flattens it, not by guessing.

**3f. `creditorsNatural`/`creditorsJuridical` (`S_MASTER`/`S_JURIDICAL`) — the two largest sheets (113-133 columns in production).** These correspond to `Erstattungsantrag_CType`'s `Anliegen`, `AllgAngaben`, `SteuerlicheBehandlung`, `Zahlungsweg`, and `Erklaerungen` sub-trees (all fully reproduced from the real XSD below), plus `Anspruch_Struct` (the 7-boolean legal-basis block, in `kafe-standardtypes.xsd`) and address/bank/person sub-structures also in `kafe-standardtypes.xsd`. Given the sheer column count, do **not** attempt to hand-write and verify every single column from scratch in one pass — instead:

1. Read `column-defs.json`'s `creditorsNatural` and `creditorsJuridical` arrays directly (they're JSON, each entry has `{id, name, nameEn, type, required, format}` — the real, production field list you must match column-for-column **by presence and name**).
2. For each entry, resolve its real XSD source using `kafe.xsd`'s structure reproduced below plus direct reads of `kafe-standardtypes.xsd` for the nested structs (`Adresse_Struct`, `NatP_Struct`/`NichtNatP_Struct`, `Bankverbindung_Struct`, `Anspruch_Struct`, `GesetzlicheVertretung_Struct`, `Ansprechperson_Struct`, `Befugnis_Struct`, `OptionKStG_Struct`, `InvStG_Struct`, `SchweizFragen_Struct`, `FinanzamtDE_Struct`, `SteuerbeguenstigteZwecke_Struct`) using `model.elem()`/`model.attr()`/`model.path()` (the `.path()` helper disambiguates fields that share a name across different branches, exactly as `mikadiv-vib/mapping.py` uses it at lines 286-289 for `MoreThan1000Available`).
3. Where `column-defs.json`'s field genuinely has no XSD counterpart (a presentation-only helper column, analogous to MiKaDiv's `PersonTaxCategory`), use `SYN()` with hand-authored description text, flagged the same way `mikadiv-vib/mapping.py`'s own `DESC_*` constants are (lines 48-76).

**Do not trust `column-defs.json`'s own `type`/`required` columns as a type/requiredness source — use them only to confirm which fields exist and their names.** This is not a theoretical caution: `column-defs.json` has two confirmed, still-live bugs in its own `type` column, found and documented during the sibling `data-requirement-checklists` module's own review (internal GitLab MR !808 on the `app` repo, comment thread dated 2026-08-21 through 2026-08-25) and worked around there via an override table (`apps/backend/src/bulk-processing/data-requirement-checklists/kafe-field-metadata.ts:34-37`) rather than a fix to `column-defs.json` itself:
   - `CreditorNat/German_TaxOffice/LiabilityEnded` (`column-defs.json` id `CN33`) — the JSON says `"type": "number"`; the real field is a 4-digit year expressed as text (`String`), confirmed against BZSt's own KAfE documentation.
   - `TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterestDescription` (`column-defs.json` id `CN91`) — the JSON says `"type": "boolean"`; the real field is a free-text description (`String`, max 500 characters per the handbook), confirmed the same way.

   Both fields belong to `creditorsNatural`/`creditorsJuridical` (this step) — resolve their real type from `kafe.xsd`/`kafe-standardtypes.xsd` via `XsdModel`, the same as every other field, and they'll come out correct automatically (this plan's own architecture never reads `column-defs.json`'s `type` column into `mapping.py` at all). **Critically, the override comment that found these two also states the audit was scoped only to `creditorsNatural`/`creditorsJuridical`** — the other four sheets (`certificatesOfResidence`, `income`, `investmentChain`, `transactionData`, covered in Steps 3b-3e above) have never been checked for the same class of bug. Since this task already resolves every field's type from the real XSD rather than `column-defs.json`, this is not a blocking risk — but it's worth extra care (i.e., don't shortcut by copying a `type` value straight out of `column-defs.json` "just this once" for a field that looks obviously simple) precisely in those four sheets, where no one has yet independently verified `column-defs.json`'s own claims.

`kafe.xsd`'s real top-level structure feeding both creditor sheets (`Erstattungsantrag_CType`, fully confirmed by direct read):

```
Erstattungsantrag_CType
  attribute AntragId (UUID_Type, required)
  Anliegen (Anliegen_CType, required)
    Anspruch (Anspruch_Struct, required) -- 7 booleans in kafe-standardtypes.xsd:
        Abkommen, Par43bEStG, Par44aEStG, Par50gEStG, Par32Abs6KStG, Art63AEUV, IntOrg
        (IntOrg is mutually exclusive with the other six -- a real cross-field
        rule from status code 2101, not expressible as a plain XSD constraint;
        note this in the field's description text, don't silently drop it)
        (Par32Abs6KStG is accuracy bug #2, design spec S8: the existing document's
        Required column for this field is a free-text conditional value ("Only
        required for submissions occurring after 15.04.2025"), breaking the fixed
        Required/Optional/Conditional vocabulary every other row uses. This is
        structurally fixed by the new pipeline -- engine/generator.py's own
        REQ_FONTS dict (engine/generator.py:59-63) only has 3 keys, so no
        free-text value can ever be emitted -- but resolve the actual condition
        correctly rather than defaulting it to plain "Conditional" with no
        explanation: read kafe-standardtypes.xsd's own xs:documentation for
        Par32Abs6KStG plus status code 2101's real message text to write an
        accurate description of when it applies, matching how every other
        Conditional field's description states its real condition)
    Ansaessigkeitsstaat (CountryISOAlpha2_ENUM, optional)
    Rechtsform (Rechtsformen_ENUM, optional)
    GewinnePG_CH (boolean, optional)
  AllgAngaben (AllgAngaben_CType, required)
    Vollmacht (Anhang_Struct, optional) -- power-of-attorney attachment reference
    SteuerpflichtigePerson (StpflPerson_Struct, required)
    GesetzlicheVertretung (GesetzlicheVertretung_Struct, optional)
    Ansprechperson (Ansprechperson_Struct, optional)
  SteuerlicheBehandlung (SteuerlicheBehandlung_CType, required)
    IdNr (IdNr_Type, optional), W-IdNr (WIdNr_Type, optional),
    TinVorhanden (boolean, REQUIRED -- new in v1.4.0), TIN (string 1-40, optional),
    KennNr (KennNr_Type, optional), TranspGebilde (boolean, optional),
    OptionKStG (OptionKStG_Struct, optional), Investmentfonds (InvStG_Struct, optional),
    SchweizFragen (SchweizFragen_Struct, optional),
    SteuerpflichtDE (FinanzamtDE_Struct, required),
    Ansaessigkeitsbescheinigung (AnsaessBescheinigung_Struct, optional) -- see 3b, S_COR sheet
    SteuerbeguenstigteZwecke (SteuerbeguenstigteZwecke_Struct, optional)
  Zahlungsweg (Zahlungsweg_CType, required)
    Bankverbindung (Bankverbindung_Struct, required)
    Verwendungszweck (string 1-35, optional)
  Erklaerungen (Erklaerungen_CType, required) -- affirmation booleans, see 3g below
```

**3g. Affirmation fields (part of `creditorsNatural`/`creditorsJuridical` per production's own real shape — confirm placement against `column-defs.json` directly).** `Erklaerungen_CType`'s real fields, all confirmed by direct XSD read:
- `ZusaetzlicheAngaben` (string 10-5000, optional)
- `BegruendungArt63AEUV` (string 50-15000, optional) — "Justification for the asserted claim under Article 63 TFEU"
- `Antrag` (boolean, required) — "I request a refund..."
- `AntragPar50c` (boolean, required) — the §50c(3)/DTA no-prior-claim affirmation
- `AntragIntOrg` (boolean, optional)
- **`AntragPar11InvStG` (boolean, optional)** — this is accuracy bug #1's exact real field (§8 of the design spec). Confirmed by direct read: its own XSD documentation is *"A refund in accordance with section 11 Investment Tax Act was neither applied for nor made to the Federal Central Tax Office or another tax authority"* — pass this exact XSD-sourced description through unmodified via `model.elem(...)` (do not hand-override it); the accuracy fix belongs in `request.bs`'s own prose (Task 5), which must clarify that despite this field's presence, §11 InvStG claims cannot be submitted through KaFE at all (per the handbook's own §2.1) — the field only exists to let a submitter affirmatively confirm they have NOT separately pursued that path, not to submit such a claim through this interface.
- `AntragFA` (boolean, required)
- `Versicherung` (boolean, required)

- [ ] **Step 4: Write `LEGEND_ROWS`, `SHEET_INFO`, `LEGEND_TITLE`**

Mirror `mikadiv-vib/mapping.py:402-564`'s structure and tone exactly (How to read each sheet / Requiredness legend / Linking the sheets / Cardinality / any per-sheet significance-cardinality-whenToFill entries), substituting KaFE's real facts: the linking key is `creditorId` (not a single top-level key like `RequestId` — KaFE's own real linking is two-level, `creditorId` on the creditor sheets and `creditorId`+`incomeId` together on `income`/`investmentChain`/`transactionData`, so `LEGEND_ROWS`'s "Linking the sheets" section must describe both keys, not just one). No "narrow the Excel template" / RecordType-removal entry is needed (KaFE never had one) — confirmed by `test_legend_rows_mention_no_record_type_narrowing` in Step 1.

- [ ] **Step 5: Write `build_enums()` and `build_sheets()`**

Mirror `mikadiv-vib/mapping.py:139-396`'s exact structure: `build_enums()` assembles every enum from `ENUM_ORDER` (KaFE's real enums: `KapitalertragArt` from `KapitalertragArt_ENUM`, `TransaktionArt` from `TransaktionArt_ENUM`, `TransaktionGeschaeft` from `TransaktionGeschaeft_ENUM`, `CountryISOAlpha2` from `CountryISOAlpha2_ENUM` in `kafe-isotypes.xsd`, `Rechtsformen` from `Rechtsformen_ENUM`, plus `Boolean` as a `SYNTHETIC_ENUMS` entry exactly like MiKaDiv's own — `mikadiv-vib/mapping.py` can't be imported from `kafe/mapping.py` (its directory name has a hyphen, invalid in Python module names, which is exactly why `generate_template.py` loads it via `_load_module()` rather than a normal `import`), so duplicate the same 4-line `Boolean` dict entry (`mikadiv-vib/mapping.py:80-84`) into `kafe/mapping.py`'s own `SYNTHETIC_ENUMS` verbatim, as a second, independent copy — it's schema-agnostic presentation text, not MiKaDiv-specific, and this trivial duplication is simpler and more robust than any cross-module coupling would be). `build_sheets()` follows the same `E()`/`A()`/`P()`/`SYN()`/`fk()`-style local helper pattern as `mikadiv-vib/mapping.py:175-198`, using the field-by-field mapping worked out in Steps 3b-3g above (adapted for KaFE's two-level linking key — `fk()` needs a variant that emits both `creditorId` and `incomeId` foreign-key columns on the three sheets that need both, not just one).

- [ ] **Step 6: Run test to verify it passes**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_mapping.py -v`
Expected: PASS, all 7 tests.

- [ ] **Step 7: Commit**

```bash
git add kafe/mapping.py kafe/tests/test_mapping.py
git commit -m "feat: add kafe/mapping.py -- Excel template shape + requiredness chaining"
```

---

### Task 4: Wire into `generate_template.py`, generate + verify the Excel template

**Files:**
- Modify: `generate_template.py`
- Test: `kafe/tests/test_generated_workbook.py`

**Interfaces:**
- Consumes: `kafe.mapping` (Task 3), `engine.generator.Generator`/`ModuleConfig` (existing, unchanged), `engine.version.read_docversion` (existing, unchanged).
- Produces: `kafe/generated/kafe-v4.3.2.xlsx`, `kafe/generated/template_metadata.json`, `kafe/generated/TEMPLATE_FIELDS.md`, `kafe/generated/fields.include.bs` — the same 4 outputs `mikadiv-vib`'s own `ModuleConfig` entry produces, now also for `kafe`.

- [ ] **Step 1: Write the failing test**

```python
# kafe/tests/test_generated_workbook.py
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent.parent


def test_generate_template_produces_seven_sheets_plus_legend_and_meta():
    subprocess.run([sys.executable, "generate_template.py"], cwd=ROOT, check=True)
    wb = openpyxl.load_workbook(ROOT / "kafe" / "generated" / "kafe-v4.3.2.xlsx")
    names = wb.sheetnames
    assert names[0] == "0 Legend Notes"
    assert names[-2] == "_Lists"  # hidden, second-to-last per engine/generator.py:601-603
    assert names[-1] == "Meta"
    # The 6 real data sheets (Meta/Legend/_Lists are not among production's 7 --
    # production's 7th sheet, "meta", is what engine/generator.py's own Meta
    # sheet replaces/represents here) are present:
    for expected in ["1 Creditors Natural", "2 Creditors Juridical",
                      "3 Certificates Of Residence", "4 Income",
                      "5 Investment Chain", "6 Transaction Data"]:
        assert expected in names


def test_income_sheet_has_no_record_type_column():
    wb = openpyxl.load_workbook(ROOT / "kafe" / "generated" / "kafe-v4.3.2.xlsx")
    ws = wb["4 Income"]
    header_names = [ws.cell(1, c).value for c in range(1, ws.max_column + 1) if ws.cell(1, c).value]
    assert "RecordType" not in header_names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_generated_workbook.py -v`
Expected: FAIL — `generate_template.py` doesn't build a `kafe/` module yet, so `kafe/generated/kafe-v4.3.2.xlsx` won't exist.

- [ ] **Step 3: Add the `kafe` `ModuleConfig` to `generate_template.py`**

This step needs `kafe/request.bs` to already have a `Text Macro: DOCVERSION 4.3.2` line for `read_docversion()` to find (mirroring `generate_template.py:44`'s `read_docversion(ROOT / "mikadiv-vib" / "request.bs")`) — Task 5 creates the real `request.bs`, but `read_docversion()` only needs the metadata header, not the full document, so create a minimal placeholder now with just the metadata block (Task 5 replaces it with the full document):

```bash
mkdir -p kafe
cat > kafe/request.bs << 'EOF'
<pre class=metadata>
Title: KaFE Refund Application -- Request
Shortname: kafe-request
Level: 1
Status: DREAM
URL: https://openfaster.org/kafe/request
Repository: https://github.com/OpenFASTER-Standard/spec
Text Macro: DOCVERSION 4.3.2
Editor: Julian Nalenz, https://github.com/sigalor
Abstract: placeholder, replaced in full by Task 5.
Markup Shorthands: markdown yes, dfn yes, css no
Boilerplate: omit conformance
Local Boilerplate: header yes
</pre>

Placeholder {#placeholder}
===========================

Replaced in full by Task 5.
EOF
git add kafe/request.bs
git commit -m "chore: add minimal kafe/request.bs metadata stub for DOCVERSION (Task 5 replaces the body)"
```

Now extend `generate_template.py` (mirror lines 43-65 exactly):

```python
# In generate_template.py, after the existing mikadiv_vib_mapping/MIKADIV_VIB_VERSION lines:
kafe_mapping = _load_module("kafe_mapping", ROOT / "kafe" / "mapping.py")
KAFE_VERSION = read_docversion(ROOT / "kafe" / "request.bs")

# Append to the existing MODULES list (do not replace the mikadiv-vib entry):
    ModuleConfig(
        title=kafe_mapping.LEGEND_TITLE,
        xsd_path=ROOT / "kafe" / "kafe.xsd",
        output_dir=ROOT / "kafe" / "generated",
        xlsx_name=f"kafe-v{KAFE_VERSION}.xlsx",
        json_name="template_metadata.json",
        doc_name="TEMPLATE_FIELDS.md",
        bs_name="fields.include.bs",
        legend_sheet_name=kafe_mapping.S_LEGEND,
        master_sheet_name=kafe_mapping.S_MASTER,
        sheet_order=kafe_mapping.SHEET_ORDER,
        build_enums=kafe_mapping.build_enums,
        build_sheets=kafe_mapping.build_sheets,
        sheet_info=kafe_mapping.SHEET_INFO,
        legend_rows=kafe_mapping.LEGEND_ROWS,
        slug="kafe",
        version=KAFE_VERSION,
        spec_url="https://openfaster.org/kafe",
        link_key="creditorId",
    ),
```

Note: since `kafe` (unlike `mikadiv-vib`) has no hyphen, `_load_module`'s own docstring comment (`generate_template.py:30-35`, "module directories use hyphenated slugs... so mapping modules are loaded directly by path rather than imported as `package.submodule`") doesn't strictly apply here — `kafe/mapping.py` **could** be imported as `from kafe import mapping` instead of via `_load_module()`. Either works; use whichever you verify actually works cleanly given `kafe/__init__.py` already exists from Task 2 — but if you switch to a plain import, keep `mikadiv_vib_mapping`'s own `_load_module()` call unchanged (don't refactor working code outside this task's scope).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_generated_workbook.py -v`
Expected: PASS, both tests.

- [ ] **Step 5: Manually verify the Legend and Meta sheets render sensibly**

```bash
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('kafe/generated/kafe-v4.3.2.xlsx')
ws = wb['0 Legend Notes']
for row in ws.iter_rows(min_row=1, max_row=15, values_only=True):
    print(row)
print('---META---')
ws2 = wb['Meta']
for row in ws2.iter_rows(values_only=True):
    print(row)
"
```

Expected: Legend sheet shows real KaFE-specific prose (not MiKaDiv's own text — a real risk if any `mikadiv-vib`-specific string got copy-pasted without updating); Meta sheet shows `Version: 4.3.2`, `Slug: kafe`, `Spec URL: https://openfaster.org/kafe`.

- [ ] **Step 6: Commit**

```bash
git add generate_template.py kafe/tests/test_generated_workbook.py
git commit -m "feat: wire kafe module into generate_template.py, generate Excel template"
```

---

### Task 5: `kafe/generate_rm_docs.py` + `kafe/generate_status_codes_docs.py` + full `kafe/request.bs`

**Files:**
- Create: `kafe/generate_rm_docs.py`, `kafe/generate_status_codes_docs.py`
- Modify: `kafe/request.bs` (replace Task 4's placeholder with the full document)
- Test: `kafe/tests/test_request_doc_build.py`

**Interfaces:**
- Consumes: `engine.xsd_model.XsdModel`, `kafe/kafe-rm.xsd` (Task 1), `kafe.status_codes` (Task 2), `kafe/generated/fields.include.bs` (Task 4).
- Produces: `kafe/generated/rm.include.bs`, `kafe/generated/status-codes.include.bs`, the full `kafe/request.bs`, and (once built) `kafe/request.html` + `kafe/generated/kafe-v4.3.2.pdf`.

- [ ] **Step 1: Check whether `PYTHONPATH=.` is actually needed for `kafe/` scripts**

The Global Constraints section flags this as a real, unresolved difference from `mikadiv-vib`'s own precedent (which needed `PYTHONPATH=.` because `mikadiv-vib` has a hyphen, invalid in Python module names, ruling out `-m package.module`). Test both forms now, from repo root:

```bash
python kafe/generate_rm_docs.py 2>&1 | head -5   # written in Step 3 below; run this AFTER Step 3, not before
python -m kafe.generate_rm_docs 2>&1 | head -5
```

Whichever form actually succeeds (no `ModuleNotFoundError: No module named 'engine'`) is the one this task, Task 6, Task 8, and Task 9 must all use consistently. Record which one worked in your task report — do not assume `PYTHONPATH=.` is required just because it was for `mikadiv-vib`; verify it directly for `kafe/`.

- [ ] **Step 2: Write the failing test**

```python
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_request_doc_build.py -v`
Expected: FAIL — none of these scripts/content exist yet.

- [ ] **Step 4: Write `kafe/generate_rm_docs.py`**

Mirror `mikadiv-vib/generate_response_docs.py`'s exact structure (its full content is reproduced in this plan's research context — reuse the same `_resolve()`/`_render_section()`/`_slug()`/`_esc()` pattern, `SECTIONS`/`ENUMS` module-level tables), but sourced from `kafe/kafe-rm.xsd`'s real structure instead. `kafe-rm.xsd`'s real root type is `KAFE-RM_CType` (confirmed during research: `Eingangsdatum` date, then a choice of `DateiFehler` (whole-file rejection) or `Antrag[1..∞]` (per-application `Antrag_CType`, itself `AntragId` attribute + a choice of `RegistrierNr` or `ValidierungsergebnisListe`)). Structure the `SECTIONS` table as:

```python
RM_TYPE = "Antrag_CType"  # confirm this exact type name by reading kafe/kafe-rm.xsd directly

SECTIONS = [
    ("Per-application response", [
        ("attr", "AntragId"),
        ("elem", "RegistrierNr"),
    ]),
    ("Validation result (on rejection)", [
        ("path", ["ValidierungsergebnisListe", "Validierungsergebnis", "StatusCode"]),
        ("path", ["ValidierungsergebnisListe", "Validierungsergebnis", "Hinweis"]),
    ]),
]
```

Adjust the exact `path()` walk once you've confirmed the real nested element names by reading `kafe/kafe-rm.xsd` directly (`cat kafe/kafe-rm.xsd`, it's only ~150 lines) — the names above are the plan-writer's best reconstruction from research, not guaranteed to be pixel-perfect against the vendored file; the implementer must verify against the real file, not copy this table blindly.

Output path: `kafe/generated/rm.include.bs`.

- [ ] **Step 5: Write `kafe/generate_status_codes_docs.py`**

A new, small script (no direct `mikadiv-vib` precedent — this is the one genuinely new generation pattern this plan introduces) that renders `kafe.status_codes.STATUS_CODES` into a Bikeshed include, grouped by `RANGE_ORDER`:

```python
"""Renders kafe/status_codes.py's full 213-code catalog (plus code "0000") into a Bikeshed include,
consumed by kafe/request.bs's error-handling section. Unlike every other
generator in this repo, this one's source is a hand-transcribed Python data
file, not an XSD -- see kafe/status_codes.py's own module docstring for why.

Run from the repository root::

    python -m kafe.generate_status_codes_docs
"""
from __future__ import annotations

from pathlib import Path

from kafe.status_codes import RANGE_ORDER, STATUS_CODES, codes_in_range

ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "generated" / "status-codes.include.bs"


def _esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _slug(text: str) -> str:
    return text.lower().replace(" ", "-").replace("/", "-")


def main() -> None:
    lines: list[str] = [
        "<!-- Generated by kafe/generate_status_codes_docs.py from "
        "kafe/status_codes.py. Do not edit by hand. -->",
        "",
        '<h2 id="status-codes">Status and error codes</h2>',
        "",
        "<p>Every status code KaFE-RM's <code>ValidierungsergebnisListe</code> "
        "may report, grouped by the numeric range the official handbook itself "
        "uses.</p>",
        "",
    ]

    # "0000" (OK) lives outside RANGE_ORDER's 7 numeric ranges entirely (Task 2's
    # own ruling) -- render it as its own leading section rather than silently
    # dropping it, since the loop below only ever reaches codes inside the 7
    # named ranges.
    ok_code = STATUS_CODES["0000"]
    lines.append('<h3 id="status-0000-ok">0000 - OK</h3>')
    lines.append("")
    lines.append('<table class="complex data longlastcol dictionary">')
    lines.append("  <thead><tr><th>Code<th>Message</tr></thead>")
    lines.append("  <tbody>")
    lines.append(
        f"    <tr><td><code>{_esc(ok_code.code)}</code>"
        f'<td class="long">{_esc(ok_code.message)}</tr>'
    )
    lines.append("  </tbody>")
    lines.append("</table>")
    lines.append("")

    for range_label in RANGE_ORDER:
        anchor = f"status-{_slug(range_label)}"
        lines.append(f'<h3 id="{anchor}">{_esc(range_label)}</h3>')
        lines.append("")
        lines.append('<table class="complex data longlastcol dictionary">')
        lines.append("  <thead><tr><th>Code<th>Message</tr></thead>")
        lines.append("  <tbody>")
        for status_code in codes_in_range(range_label):
            lines.append(
                f"    <tr><td><code>{_esc(status_code.code)}</code>"
                f'<td class="long">{_esc(status_code.message)}</tr>'
            )
        lines.append("  </tbody>")
        lines.append("</table>")
        lines.append("")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Write the full `kafe/request.bs`**

Replace Task 4's placeholder entirely. Mirror `mikadiv-vib/request.bs`'s exact structure and tone (metadata block, Downloads section, source-schema section, data-model table, linking-model section, conformance-requirements section, `<pre class=include>` for the generated fields), adapted for KaFE's real facts:

```
<pre class=metadata>
Title: KaFE Refund Application -- Request
Shortname: kafe-request
Level: 1
Status: DREAM
URL: https://openfaster.org/kafe/request
Repository: https://github.com/OpenFASTER-Standard/spec
Text Macro: LONGSTATUS KaFE Refund Application Request -- a module of the OpenFASTER family
Text Macro: DOCVERSION 4.3.2
Metadata Order: This version, Issue Tracking, Editor, *
!This version: <p class="spec-version">Version <strong>[DOCVERSION]</strong></p>
Editor: Julian Nalenz, https://github.com/sigalor
Abstract: This document is for banks and other reporting institutes
    submitting KaFE (Kapitalertragsteuer-Erstattung, capital income tax
    refund) applications under section 50c(3) of the German Income Tax
    Act. The KaFE Refund Application Request format is a module of the
    <a href="/about">OpenFASTER</a> family: a self-documenting data model
    (with an accompanying Excel template) that mirrors the official BZSt
    KaFE v1.4.0 schema. See <a href="/kafe/response">the Response
    document</a> for the (currently provisional) decision-notice channel.
Markup Shorthands: markdown yes, dfn yes, css no
Boilerplate: omit conformance
Local Boilerplate: header yes
Complain About: accidental-2119 yes, missing-example-ids yes
</pre>

Downloads {#downloads}
=======================

<a href="https://raw.githubusercontent.com/OpenFASTER-Standard/spec/main/kafe/generated/kafe-v[DOCVERSION].pdf">Specification PDF</a> ·
<a href="https://raw.githubusercontent.com/OpenFASTER-Standard/spec/main/kafe/generated/kafe-v[DOCVERSION].xlsx">Excel template</a>

The KaFE Refund Application Request module {#kafe-request-module}
====================================================================

The KaFE (Kapitalertragsteuer-Erstattung) **refund application** format
defines the data required to apply, under section 50c(3) of the German
Income Tax Act (EStG), for a refund of German withholding tax on capital
income. A single application (`Erstattungsantrag`) covers the applicant's
identity and legal basis of claim, tax treatment, payment details, and
every taxed income event (`Ertrag`) the application concerns, including
the section 50j EStG securities-lending/holding-period block where
applicable. An accompanying self-documenting Excel template is published
alongside this specification (see [[#downloads|Downloads]] above); each
sheet mirrors one logical group below, with every field's English
description, type constraints, and requiredness in the header rows.

Source schema {#source-schema}
------------------------------

The data model of this module is derived from the XML Schema Definition
(XSD) published by the BZSt (Bundeszentralamt für Steuern), the German
Federal Central Tax Office, as part of its DIP (Digitale Poststelle)
mass-data interface for the KaFE procedure.

OpenFASTER treats the BZSt XSD as the machine source of truth: the field
definitions, requiredness, enumerations, the [[#data-dictionary|data
dictionary]] in this document, and the accompanying Excel template are all
generated directly from it. As the BZSt schema evolves, regenerating from
the updated XSD keeps this specification and the template in lock-step
with the BZSt source.

Data model {#data-model}
------------------------

An application is decomposed into several logical groups (rendered as
separate sheets in the Excel template). Groups are linked by two keys used
together, not one — see [[#linking-model|Linking model]] below.

<table class="data">
  <thead>
    <tr><th>Group<th>Rows per creditor<th>Purpose
  <tbody>
    <tr><td>Creditors Natural / Juridical<td>1 per creditor<td>The applicant's identity, legal basis of claim, tax treatment, and payment details.
    <tr><td>Certificates Of Residence<td>0..n<td>Certificate-of-residence validity windows, referenced by income events.
    <tr><td>Income<td>0..n<td>Each taxed capital-income event (Ertrag): type, security, amounts, and the section 50j EStG block where it applies.
    <tr><td>Investment Chain<td>0..n<td>The chain of indirect holdings for an income event, when applicable.
    <tr><td>Transaction Data<td>0..n<td>The per-depot transaction ledger supporting the section 50j EStG holding-period test.
</table>

Linking model {#linking-model}
------------------------------

Unlike MiKaDiv's own single `RequestId` key, a KaFE application is linked
across sheets by two keys used together: `creditorId` (the key on the
Creditors Natural / Juridical sheets and the first column on every other
sheet) identifies which applicant a row belongs to, and `incomeId`
(present on Income, Investment Chain, and Transaction Data) identifies
which specific taxed income event within that applicant's application a
row belongs to. `creditorId` alone links Certificates Of Residence back to
a creditor; `creditorId` and `incomeId` together link Investment Chain and
Transaction Data rows back to one specific Income row.

Legal basis and income type {#legal-basis-and-income-type}
-------------------------------------------------------------

KaFE has no request-type taxonomy analogous to MiKaDiv's New
Report/Correction/Cancellation distinction — every application is the same
`Erstattungsantrag` type. Differentiation instead happens on two
independent axes:

`Anspruch` (legal basis of claim) is a set of seven independent booleans,
not an enum: `Abkommen` (double-taxation agreement), `Par43bEStG`,
`Par44aEStG`, `Par50gEStG`, `Par32Abs6KStG`, `Art63AEUV` (Article 63 TFEU),
and `IntOrg` (international organisation). Any combination of the first
six may be true together; `IntOrg` is mutually exclusive with all of them
— a real cross-field rule enforced by BZSt's own validation (status code
`2101`), not expressible as a plain XSD constraint, so it is stated here
rather than left implicit.

`KapArt` (type of capital income) is a 10-value enum on each individual
`Ertrag`, describing what kind of capital income that specific line
concerns (dividends, distributions from non-listed corporations, various
profit-participation-right forms, convertible bonds, life insurance, and
others — see [[#enumerations|Enumerations]] for the full list and
meanings). This is a per-income-line classification, not a
submission-level type.

Resubmission {#resubmission}
--------------------------------

KaFE has no formal typed lifecycle on the submission side. Per the
official BZSt communication handbook: <q>Files that contain non-valid data
are rejected. Violations of conditional mandatory field specifications in
individual applications thus lead to the rejection of the entire file.
After correcting the errors, an error-free file can be resubmitted.
Alternatively, a file containing only the error-free records can be
transmitted.</q> There is no correction/cancellation message type, no
typed reference from a new application back to a previous one, and no
partial-amendment format — resubmission means submitting a fresh, complete
`Erstattungsantrag` with a new `AntragId`. (BZSt's own decision-notice
schema does have a typed correction concept — `BescheidArt` = `KORREKTUR`
— but that is on the response side; see the [Response
document](/kafe/response#approval-and-clawback).)

Submission receipt (KAFE-RM) {#submission-receipt}
-------------------------------------------------------

After a delivery is submitted, BZSt returns a synchronous KAFE-RM receipt:
a file-level result plus, per `Erstattungsantrag` (correlated by the
submitter's own `AntragId`), either a `RegistrierNr` (a 9-character
BZSt-assigned case number, present only when that application was
accepted) or a `ValidierungsergebnisListe` (present only when it was
rejected — one or more `StatusCode`/`Hinweis` pairs identifying exactly
what failed; see [[#status-codes-section|Status and error codes]] below
for the full catalog). This receipt is documented here, in the Request
document, rather than in the Response document — it is the synchronous
half of what a bank directly experiences submitting data, unlike the
asynchronous KAFE-VA decision notice.

<pre class=include>
path: generated/rm.include.bs
</pre>

Status and error codes {#status-codes-section}
---------------------------------------------------

Every code BZSt's `ValidierungsergebnisListe` may report, grouped by the
same numeric ranges the official handbook itself uses. A submitter's own
validation logic (and any troubleshooting of a rejected delivery) should
treat this table as the authoritative reference — it is the complete
catalog, not a curated subset.

<pre class=include>
path: generated/status-codes.include.bs
</pre>

Version history {#version-history}
--------------------------------------

Divizend has published and maintained this interface specification since
2023; the following table is the complete version history, carried
forward from the specification's prior, hand-maintained form.

<table class="data changelog">
  <thead>
    <tr><th>Version<th>Date<th>Summary of changes</tr>
  </thead>
  <tbody>
    <tr>
      <td>1.0.0
      <td>2023-08-29
      <td>Initial release.
    </tr>
    <tr>
      <td>1.1.0
      <td>2023-09-25
      <td>Minor formatting improvements.
    </tr>
    <tr>
      <td>2.0.0
      <td>2024-01-30
      <td>Added three new "TaxTreatment" properties within "creditorsNatural" (only
          for Swiss beneficiaries). Added four new "Questions_for_50j" properties
          within "creditorsJuridical" (only for beneficiaries with a country/legal
          form combination from the section 50j country/legal-form matrix). Updated
          possible values for "CapitalIncome" within "income" according to BZSt
          updates (removed HINTERLEGUNGSSCHEINE, added GRENZKRAFTWERK_RHEIN,
          GENUSSRECHTE_MIT_LIQUIDATIONSERLOES and
          GENUSSRECHTE_OHNE_LIQUIDATIONSERLOES). Corrected
          "Business_Establishment/Business_Establishment_DE" within "income" to now
          be required (technically only needed for juridical entities). Fixed typo
          in column name "Economic_Ownership/Ownership_and_Right_To_Use" within
          "income". Removed section "Divizend's approach to bulk processing"
          because it is deprecated and will be moved to a new bulk processing
          manual. Updated section "Input file structure" according to recent
          developments.
    </tr>
    <tr>
      <td>2.1.0
      <td>2024-02-10
      <td>Added instructions on how to use the bulk processing within the Divizend
          platform (new section 7). Fixed heading of section 5.2 to be "Required
          files".
    </tr>
    <tr>
      <td>3.0.0
      <td>2024-05-22
      <td><b>MAJOR changes (action required):</b> Use version 3 in the "meta"
          sheet. Make sure to use the updated templates. Removed the field
          "CreditorNat/General_Data/Nationality" from the "creditorsNatural" sheet
          and this documentation, because it is not needed by the BOP anymore.
          <b>MAJOR changes (incompatibilities with version 2):</b> Added a section
          on character set limitations. Added BOP-defined length restrictions to
          most fields with type "String". Marked "generalData/LegalForm" in
          "creditorsJuridical" as required. Marked "Bank/Account/BIC" and
          "Bank/Account/IBAN" in both sheets "creditorsNatural" and
          "creditorsJuridical" as required. Marked the fields relating to a
          beneficiary's TIN as required, i.e. "CreditorNat/General_Data/
          IDNumber_CountryOfResidence" (in "creditorsNatural") and
          "CreditorJur/General_Data/IDNumber_CountryOfResidence" (in
          "creditorsJuridical"). <b>MINOR changes:</b> Added a section on semantic
          versioning. Added a section on terminology and roles, explaining the
          terms "Creditor", "Authorized representative" and "Authorized
          recipient". Added note that XLSX must be provided, not CSV. Added a link
          to demo data. Added a section on data types, explaining the types
          "String", "Number" and "Boolean". Added a section on tax certificates,
          explaining the format and legal basis for tax certificates. <b>PATCH
          changes:</b> Various formatting improvements.
    </tr>
    <tr>
      <td>3.1.0
      <td>2024-07-01
      <td><b>MINOR changes:</b> Marked "CreditorNat/German_TaxOffice/
          Inquiry_TaxReturn" in "creditorsNatural" as required. Marked
          "CreditorJur/German_TaxOffice/Inquiry_TaxReturn" in "creditorsJuridical"
          as required. Marked "AuthorizedRep/General_Data/LegalForm" in
          "creditorsNatural" and "creditorsJuridical" as required. Marked
          "Economic_Ownership/Ownership_and_Right_To_Use" in "income" as required.
          Added a section on required, optional and semi-required fields,
          including input data cluster constraint details. Made the "Required"
          column contents more precise.
    </tr>
    <tr>
      <td>3.2.0
      <td>2024-07-03
      <td><b>MINOR changes:</b> Marked "TaxTreatment/Taxation_Treatment" in
          "creditorsJuridical" as required. Marked "Business_Establishment/
          Business_Establishment_DE" in "income" as required. Clarified
          "Required" column contents for "InvTaxAct/StatusCertificateDetails/..."
          fields in "creditorsJuridical". Clarified "Description" and "Required"
          column contents for "Depositary_Receipts/..." fields in "income".
    </tr>
    <tr>
      <td>3.2.1
      <td>2024-08-07
      <td><b>PATCH changes:</b> Fixed "Required" column contents for
          "CreditorNat/German_TaxOffice/TaxNumber/State" and
          "CreditorNat/German_TaxOffice/TaxNumber/Number" from "creditorsNatural".
    </tr>
    <tr>
      <td>4.0.0
      <td>2024-09-16
      <td><b>MAJOR changes (incompatibilities with version 3):</b> Use version 4
          in the "meta" sheet. Make sure to use the updated templates. Moved to
          the new DIP (Digital inbox) implementation of electronic submission.
          Changed submission flow so that transferring the claims directly
          submits them to the BZSt instead of waiting for Divizend employees to
          validate the submission. Added three new worksheets that need to be
          present in the "data.xlsx" file: certificatesOfResidence,
          investmentChain and transactionData. Added, removed and updated
          multiple fields concerning the creditorsNatural, creditorsJuridical and
          income worksheets. Changed the claim grouping to no longer separate
          claims containing depositary receipts but rather split claims by
          certificate of residence validity. Introduced new documents to upload.
          <b>MINOR changes:</b> Removed the section on Robotic Process Automation
          and renamed a section to "Divizend's DIP implementation". Updated the
          limitations concerning file sizing.
    </tr>
    <tr>
      <td>4.0.1
      <td>2025-01-17
      <td><b>PATCH changes:</b> Added a note about section 11 InvStG to the
          introduction. Fixed typos in the requirement conditions for fields
          "CreditorNat/German_TaxOffice/TaxNumber", "CreditorJur/German_TaxOffice/
          TaxNumber", "CreditorJur/OptingUnderCorpTaxAct/TaxAuthority" and
          "CreditorJur/OptingUnderCorpTaxAct/FileNumber". Minor formatting fixes.
    </tr>
    <tr>
      <td>4.1.0
      <td>2025-02-07
      <td><b>MINOR changes:</b> Added a new legal basis for reclaim applications,
          "LegalBasis/Par32Abs6KStG", with the associated new data requirements.
          Added a requirement for Italian residents to specify if they are German
          citizens in "CreditorNat/General_Data/NationalityIsDE" — if so, these
          creditors must provide information about their tax liability in
          Germany. Renamed the "TaxTreatment/SwitzerlandQuestions/LiabilityEnded"
          field to "CreditorNat/German_TaxOffice/LiabilityEnded" as the
          requirement to include it has changed. Restructured the information on
          holding periods for substantial holdings to accommodate the DTA
          requirements from Japan and Australia. The tax certificate serial
          number in "DocumentProof/TaxCertificateNumber" is now required for
          dividends after 2026-12-31 instead of 2024-12-31. Applicants from
          Singapore wishing to submit applications for inflows that happened
          before 2021-12-31 no longer have to provide section 50j EStG data.
          <b>PATCH changes:</b> Removed a document-attachment note that was no
          longer relevant. Added unrequired address fields that were previously
          missing.
    </tr>
    <tr>
      <td>4.2.0
      <td>2025-10-08
      <td><b>MINOR changes:</b> Fixed spelling mistakes in field
          "TaxPrivileges/StructuralConnectionToGermany/TaxPriviligedPurposesDE".
          Fixed spelling mistakes for "AuthorizedRep" (previously
          "AuthroizedRep") and "District" (previously "Distrcti"). Changed the
          condition for the "ISIN" field. Changed the conditions for providing a
          confirmation of tax payment. Replaced prose attachment-requirement
          sections with a table. Changed legal representative
          "LegalRep/NatPerson/Name" to "LegalRep/NatPerson/LastName" to match the
          template content.
    </tr>
    <tr>
      <td>4.3.0
      <td>2026-03-23
      <td><b>MINOR changes:</b> Added "UnlimitedForeignCorporateTaxLiability" and
          "CreditAmount" to the income sheet. Changed the conditions for
          including "TaxExemption". Added fields "CreditorNat/General_Data/
          TinAvailable" and "CreditorJur/General_Data/TinAvailable" and changed
          the conditions for including "CreditorNat/General_Data/
          IDNumber_CountryOfResidence" and "CreditorJur/General_Data/
          IDNumber_CountryOfResidence". Added a "Proof of tax credit" document
          attachment. Upgraded to KaFE schema version 1.4.0.
    </tr>
    <tr>
      <td>4.3.1
      <td>2026-06
      <td>Changed various field lengths to match the required values from the
          German Tax Authorities. Corrected the format of "TaxTreatment/W-IdNr".
    </tr>
    <tr>
      <td>4.3.2
      <td>2026-08-25
      <td><b>MINOR changes:</b> Restructured into the OpenFASTER family's
          schema-driven documentation format — this document is now generated
          directly from BZSt's own published KaFE v1.4.0 XSD family rather than
          hand-maintained prose. Added a provisional Response document covering
          the KAFE-VA decision-notice schema, not previously documented at all.
          Added a full status/error code reference (previously undocumented).
          <b>Fixed:</b> the section 11 InvStG self-contradiction (previous
          versions documented "AntragPar11InvStG" as if section 11 InvStG claims
          were submittable via this interface, contradicting this document's own
          statement that they are not); the Par32Abs6KStG requiredness-column
          format inconsistency (a free-text conditional value where every other
          entry used a fixed Required/Optional/Conditional vocabulary); ambiguity
          in TransaktionId sequencing scope (now stated explicitly: sequential
          and non-gapped per depot, not globally).
    </tr>
  </tbody>
</table>

Section 50j EStG {#section-50j}
-----------------------------------

Section 50j EStG (a German anti-cum-ex/securities-lending abuse rule)
requires additional data for capital income falling within its scope,
captured on each `Ertrag` via the optional `Par50jEStG` block and, for the
transaction ledger specifically, on the [[#data-dictionary|Transaction
Data]] sheet. Almost every field in this block is `minOccurs="0"` in the
raw XSD — real conditional-mandatory logic (country- and legal-form
dependent) lives entirely in the [[#status-codes-section|status-code
catalog]] above, not in the schema's structure, so this specification
marks these fields `Conditional` rather than `Optional` even though the
XSD alone would suggest otherwise.

<b>Holding period (`Haltedauer`).</b> The minimum holding period is 45
days, measured within a window beginning 45 days before and ending 45
days after the income's due date, using FIFO. `HaltedauerMin45T` counts
shares held at least 45 days uninterrupted within that window;
`HaltedauerMin1J` (conditional on `HaltedauerMin45T` &gt; 0, and never
exceeding it) counts, of those, shares also held at least one year;
`HaltedauerKuerzer45T` counts shares held less than 45 days;
`AnteilePar50jEStG` is `HaltedauerMin45T` minus `HaltedauerMin1J`.

<b>Minimum value-change-risk retention (`MinWertAendRisiko`).</b> Only
relevant for shares that meet the minimum holding-period requirement
under section 50j(1) but are not already covered by section 50j(4)
sentence 2. `GegenlAnsprueche` records whether there were offsetting
claims during the minimum holding period; when true, `RisikoMin70`
(conditional) records the number of shares for which the applicant bore
at least 70% of the value-change risk during that period.
`GegenlAnspruecheAndere` asks the same offsetting-claims question at the
level of the entire share class, not just the section-50j-scoped shares.

<b>Forwarding obligation (`WeiterlVerpflichtung`).</b> `WeiterlVerpfl`
records whether there was a direct or indirect obligation to pass on the
capital income; when true, `WeiterlVerpflAnteile` (conditional) gives the
affected share count. `WeiterlVerpflAndere` asks the same question beyond
the section-50j-scoped shares.

<b>Return obligation (`RueckgabeVerpflichtung`).</b> Applies when capital
income derives from shares transferred under civil law on or before the
dividend date — securities loans, repurchase agreements (repos), and
comparable spot contracts must be specified. `RueckgabeVerpfl` records
whether such an obligation existed; when true, `RueckgabeVerpflAnteile`
(conditional) gives the affected share count.

<b>Per-depot transaction ledger (`Transaktionsdaten`).</b> For every depot
holding shares of the security, the full development of the holding —
including all position changes and loan transactions — must be reported
for the period from one year before the income's inflow date to two
months after it: `Anfangsbestand`/`AnfangsbestandDatum` (opening balance,
dated exactly one year before the inflow date), every `Transaktion` in
between (each carrying `Handelstag` [trade date], `Transaktionsart`
[`ZUGANG`/inflow or `ABGANG`/outflow], `Geschaeft` [transaction type —
`PO` purchase, `SO` sale, `TL` transfer due to securities lending, `RL`
retransfer due to securities lending, `TP` transfer due to repo, `RP`
retransfer due to repo], `Stueckzahl` [share count], and both an agreed
and an actual settlement date), and `Endbestand`/`EndbestandDatum`
(closing balance, dated exactly two months after the inflow date — BZSt's
own worked example: an inflow date of 2023-04-25 requires an
`EndbestandDatum` of exactly 2023-06-25). `TransaktionId` must be
sequential and non-gapped starting at 1 within each depot — not globally
across depots or across the whole application — per BZSt's own validation
rule (status code `7601`); if no transactions occurred for a depot in the
reporting window, a single "shell" transaction carrying only depot
information, and none of the trade-specific fields, is required instead
of an empty transaction list.

Conformance requirements {#module-conformance}
----------------------------------------------

A conforming producer MUST populate every field marked `Required` for
each group it emits. Fields marked `Conditional` MUST be populated when
the condition stated in their description holds, and MUST otherwise be
omitted or left empty. Fields marked `Optional` MAY be omitted.

Enum-typed fields MUST carry one of the values enumerated for that field
in [[#enumerations|Enumerations]]. A conforming consumer MUST reject an
application whose enum-typed field carries a value outside the enumerated
set.

<pre class=include>
path: generated/fields.include.bs
</pre>
```

- [ ] **Step 7: Run test to verify it passes**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_request_doc_build.py -v`
Expected: PASS, all 3 tests.

- [ ] **Step 8: Build and verify with real Bikeshed**

```bash
source .venv312/bin/activate  # or however this session's Python 3.12 venv is activated
python generate_template.py
python -m kafe.generate_rm_docs      # or python kafe/generate_rm_docs.py with PYTHONPATH=. per Step 1's finding
python -m kafe.generate_status_codes_docs
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/request.bs kafe/request.html
```

Expected: exit 0, no link errors. Then grep-verify real content landed:

```bash
grep -c "AntragPar11InvStG\|cannot be submitted" kafe/request.html
grep -c "2023-08-29" kafe/request.html
grep -c "4.3.2" kafe/request.html
grep -c "PO\|SO\|TL\|RL\|TP\|RP" kafe/request.html
```

- [ ] **Step 9: Commit**

```bash
git add kafe/generate_rm_docs.py kafe/generate_status_codes_docs.py kafe/request.bs kafe/tests/test_request_doc_build.py
git commit -m "feat: build kafe/request.bs -- submission fields, RM receipt, status codes, full changelog, 5 accuracy fixes"
```

---

### Task 6: `kafe/generate_va_docs.py` + `kafe/response.bs` (provisional)

**Files:**
- Create: `kafe/generate_va_docs.py`, `kafe/response.bs`
- Test: `kafe/tests/test_response_doc_build.py`

**Interfaces:**
- Consumes: `engine.xsd_model.XsdModel`, `kafe/kafe-va.xsd` (Task 1).
- Produces: `kafe/generated/va.include.bs`, the full `kafe/response.bs`, and (once built) `kafe/response.html`.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_response_doc_build.py -v`
Expected: FAIL — neither file exists yet.

- [ ] **Step 3: Write `kafe/generate_va_docs.py`**

Same pattern as `mikadiv-vib/generate_response_docs.py` and Task 5's `generate_rm_docs.py`, sourced from `kafe/kafe-va.xsd`'s real `Bescheid_CType` (fully confirmed during research):

```python
VA_TYPE = "Bescheid_CType"

SECTIONS = [
    ("Decision notice envelope", [
        ("attr", "BescheidId"),
        ("elem", "BescheidArt"),
        ("elem", "SummeAbrechnung"),
        ("elem", "Faelligkeit"),
        ("elem", "Hinweise"),
    ]),
    ("Reference back to the original application", [
        ("path", ["Bezugsantrag", "TransferticketId"]),
        ("path", ["Bezugsantrag", "AntragId"]),
        ("path", ["Bezugsantrag", "RegistrierNr"]),
        ("path", ["Bezugsantrag", "KennNr"]),
    ]),
    ("Per-income refund breakdown", [
        ("attr", "ErtragId"),  # on the nested Ertrag element within Ertraege -- confirm exact path
        ("elem", "ErstattungKapESt"),
        ("elem", "ErstattungSolZ"),
    ]),
]

ENUMS = [
    ("BescheidArt", "BescheidArt"),
]
```

Confirm every exact path (especially the "Per-income refund breakdown" section, since `ErtragId`/`ErstattungKapESt`/`ErstattungSolZ` live on a nested `BescheidErtrag_CType` under `Ertraege`/`Ertrag`, not directly on `Bescheid_CType`) by reading `kafe/kafe-va.xsd` directly (`cat kafe/kafe-va.xsd`, ~200 lines) before finalizing this table — the plan-writer's reconstruction above is a starting point, not a verified-exact API surface.

Output path: `kafe/generated/va.include.bs`.

- [ ] **Step 4: Write the full `kafe/response.bs`**

Mirror `mikadiv-vib/response.bs`'s exact structure and tone (metadata block with no `DOCVERSION`/no PDF, a "Source schema" section, an "Identifiers" section, then the `<pre class=include>`, then a "Known gaps" disclosure section), adapted for KaFE's real facts:

```
<pre class=metadata>
Title: KaFE Refund Application -- Response
Shortname: kafe-response
Level: 1
Status: DREAM
URL: https://openfaster.org/kafe/response
Repository: https://github.com/OpenFASTER-Standard/spec
Editor: Julian Nalenz, https://github.com/sigalor
Abstract: This document is for developers implementing a KaFE integration
    against this platform -- banks never see this raw decision notice
    directly. It documents kafe-va.xsd, the payload BZSt uses to
    communicate the actual tax-assessment decision (approval or clawback)
    on a submitted <a href="/kafe/request">KaFE refund application</a>.
    <b>This document describes payload shape only, not a working
    retrieval flow</b> -- see the disclosure below.
Markup Shorthands: markdown yes, dfn yes, css no
Boilerplate: omit conformance
Local Boilerplate: header yes
Complain About: accidental-2119 yes, missing-example-ids yes
</pre>

Not yet retrievable: a disclosure {#not-yet-retrievable}
=============================================================

<p><b>BZSt has not yet published the transport for this payload.</b> Per
the official DIP-KAFE v1.4.0 communication handbook, section 6.2: <q>The
DIP envelope scheme for the notification of administrative files is not
available yet.</q> Only <code>kafe-va.xsd</code>'s payload shape is
published (schemaVersion 1.0.0, unrevised since its 2023-11-20 creation,
even as the request-side schema has gone through five revisions). This
document describes that payload shape so implementers know what to expect
once retrieval becomes possible -- it is not a working integration
today.</p>

The KaFE Refund Application Response format {#kafe-response-module}
========================================================================

One KAFE-VA delivery batches one or more `Steuerbescheid` (decision
notice) entries; each answers exactly one prior <a
href="/kafe/request">Erstattungsantrag</a>, correlated via the
`Bezugsantrag` back-reference block — four distinct fields
(`TransferticketId`, `AntragId`, `RegistrierNr`, `KennNr`), a richer
correlation than KAFE-RM's own single-`AntragId` correlation documented
in the Request document.

Source schema {#source-schema}
------------------------------

This document's field definitions and enumerations are generated directly
from BZSt's published `kafe-va.xsd` — regenerating from an updated XSD
keeps this document in lock-step with the BZSt source, the same way <a
href="/kafe/request#source-schema">the Request document</a> is generated
from `kafe.xsd`.

Approval and clawback semantics {#approval-and-clawback}
-------------------------------------------------------------

`SummeAbrechnung`'s sign carries the decision: a positive amount is a
refund in the applicant's favour; a negative amount is a payment debit
(clawback). `Faelligkeit` (a due date) is only present when the amount is
negative — BZSt's own documentation warns that late-payment penalties
apply if the debit isn't settled by that date. `BescheidArt` distinguishes
a first decision (`ERSTBESCHEID`) from a corrected one (`KORREKTUR`) for
the same application, but is not chained to the specific earlier notice it
corrects — only back to the original `Erstattungsantrag`, via
`Bezugsantrag`. `Hinweise` is only a boolean flag recording whether the
notice carries additional remarks; the substantive legal reasoning for any
decision, in every case, exists only inside `BescheidPdf` (a
base64-encoded PDF) — never as structured XML.

<pre class=include>
path: generated/va.include.bs
</pre>

Known gaps in this schema {#response-known-gaps}
----------------------------------------------------

Worth disclosing rather than silently working around: `kafe-va.xsd`'s own
`schemaVersion` has been fixed at `1.0.0` since its creation on
2023-11-20, unrevised even as the request-side `kafe.xsd` has gone through
five revisions (through 1.4.0). There is no `PreviousBescheidId`-style
field chaining a `KORREKTUR` notice to the specific earlier `Bescheid` it
corrects — only `Bezugsantrag`'s reference back to the original
application. And unlike <a
href="/mikadiv-vib/response#response-known-gaps">MiKaDiv's own Response
document</a>, which at least had one real sample XML to verify against, no
real `BescheidPdf`/`Steuerbescheid` sample has been examined during this
module's research — this document's coverage is derived entirely from the
schema's own structure, not confirmed against a real example.
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_response_doc_build.py -v`
Expected: PASS, both tests.

- [ ] **Step 6: Build and verify with real Bikeshed**

```bash
source .venv312/bin/activate
python -m kafe.generate_va_docs
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/response.bs kafe/response.html
grep -c "not available yet\|not yet available" kafe/response.html
grep -c "ERSTBESCHEID" kafe/response.html
```

Expected: exit 0, no link errors; both greps return ≥ 1.

- [ ] **Step 7: Commit**

```bash
git add kafe/generate_va_docs.py kafe/response.bs kafe/tests/test_response_doc_build.py
git commit -m "feat: build kafe/response.bs -- VA-only, explicitly provisional"
```

---

### Task 7: `kafe/index.bs` landing page

**Files:**
- Create: `kafe/index.bs`
- Test: `kafe/tests/test_index_doc_build.py`

**Interfaces:**
- Consumes: nothing generated — pure hand-authored Bikeshed prose, mirroring `mikadiv-vib/index.bs` exactly.
- Produces: `kafe/index.bs` and, once built, `kafe/index.html`.

- [ ] **Step 1: Write the failing test**

```python
# kafe/tests/test_index_doc_build.py
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def test_index_bs_links_request_and_response():
    content = (ROOT / "kafe" / "index.bs").read_text()
    assert "Shortname: kafe" in content
    assert "/kafe/request" in content
    assert "/kafe/response" in content
    assert "DOCVERSION" not in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_index_doc_build.py -v`
Expected: FAIL — file doesn't exist.

- [ ] **Step 3: Write `kafe/index.bs`**

Byte-for-byte structural mirror of `mikadiv-vib/index.bs` (reproduced in full below for reference — do not deviate from this style):

```
<pre class=metadata>
Title: KaFE Refund Application
Shortname: kafe
Level: 1
Status: DREAM
URL: https://openfaster.org/kafe
Repository: https://github.com/OpenFASTER-Standard/spec
Local Boilerplate: header yes
Editor: Julian Nalenz, https://github.com/sigalor
Abstract: KaFE Refund Application is a module of the
    <a href="/about">OpenFASTER</a> family, mirroring the German KaFE
    (section 50c(3) EStG) capital income tax refund schema. This page
    indexes its two documents.
Markup Shorthands: markdown yes, dfn yes, css no
Boilerplate: omit conformance
</pre>

KaFE Refund Application {#kafe-module}
=========================================

KaFE Refund Application is split into two documents:

* [Request](/kafe/request) -- the data model a bank or reporting
    institute submits, with an accompanying Excel template and downloadable
    PDF.
* [Response](/kafe/response) -- what the platform will receive back from
    BZSt after processing a submission, for implementers building a KaFE
    integration. Currently provisional -- see the document itself for why.

<p><a href="/">← Back to the OpenFASTER portal</a></p>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /work/openfaster-spec && python -m pytest kafe/tests/test_index_doc_build.py -v`
Expected: PASS.

- [ ] **Step 5: Build and confirm the root portal needs no change**

```bash
source .venv312/bin/activate
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/index.bs kafe/index.html
grep -o 'href="/kafe"' index.html
```

Expected: `bikeshed` exits 0; the grep finds `index.html`'s existing `/kafe` link (reserved when `mikadiv-vib` shipped, per `bulk-platform`'s own `PROGRESS.md` sub-project 3 entry) — confirming no edit to the root `index.html` is needed.

- [ ] **Step 6: Commit**

```bash
git add kafe/index.bs kafe/tests/test_index_doc_build.py
git commit -m "feat: add kafe/index.bs landing page"
```

---

### Task 8: CI workflow update

**Files:**
- Modify: `.github/workflows/spec.yml`

**Interfaces:**
- Consumes: every script/document from Tasks 1-7.
- Produces: an updated CI pipeline that builds and commits the `kafe/` module's outputs alongside `mikadiv-vib`'s and `streamld`'s.

- [ ] **Step 1: Add the `kafe/` build steps**

Insert, in this order, mirroring exactly how `mikadiv-vib`'s own steps are structured (`.github/workflows/spec.yml:35-63`) — after the existing "Build MiKaDiv-VIB Response" step and before "Build StreamLD":

```yaml
      - name: Build KaFE Excel template (XSD + status codes -> generated include -> Excel template)
        run: python generate_template.py

      - name: Build KaFE RM receipt docs
        run: python -m kafe.generate_rm_docs   # use PYTHONPATH=. python kafe/generate_rm_docs.py instead if Task 5 Step 1 found -m doesn't work

      - name: Build KaFE status-code appendix
        run: python -m kafe.generate_status_codes_docs   # same PYTHONPATH note as above

      - name: Build KaFE VA docs
        run: python -m kafe.generate_va_docs   # same PYTHONPATH note as above
```

Use whichever invocation form (`python -m kafe.some_script` or `PYTHONPATH=. python kafe/some_script.py`) Task 5 Step 1 actually confirmed works — do not default to `PYTHONPATH=.` without checking, since `kafe` (unlike `mikadiv-vib`) has no hyphen and may genuinely support `-m` cleanly.

Then, after the existing "Build documentation/about.html" step and before "Build mikadiv-vib/index.html", add version-reading and the 3 document builds:

```yaml
      - name: Read KaFE version
        id: kafe_version
        run: echo "version=$(python -m engine.version kafe/request.bs)" >> "$GITHUB_OUTPUT"

      - name: Build kafe/index.html
        run: bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/index.bs kafe/index.html

      - name: Build kafe/request.html + PDF
        run: |
          bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/request.bs kafe/request.html
          weasyprint --stylesheet documentation/print.css kafe/request.html kafe/generated/kafe-v${{ steps.kafe_version.outputs.version }}.pdf

      - name: Build kafe/response.html
        run: bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/response.bs kafe/response.html
```

Bikeshed's `Local Boilerplate: header yes` resolves relative to each `.bs` source's own directory (a real, empirically-confirmed constraint already documented in this repo's own `PROGRESS.md`/design specs) — `kafe/` needs its own `header.include` copy, the same way `mikadiv-vib/header.include` and `streamld/header.include` exist as separate copies of `documentation/header.include`. Check `documentation/prepare_spec.py`'s `OUTPUTS` tuple (currently lines 18-22, listing `documentation/header.include`, `mikadiv-vib/header.include`, `streamld/header.include`) and add `ROOT.parent / "kafe" / "header.include"` to it — **this is a real, easy-to-miss step**; without it, `kafe/`'s Bikeshed builds silently fall back to stock boilerplate instead of this repo's shared shell.

Finally, update the `git add` list in the "Commit regenerated output" step (currently `.github/workflows/spec.yml:85`) to include `kafe/index.html kafe/request.html kafe/response.html kafe/generated/ kafe/header.include`.

- [ ] **Step 2: Real live CI verification**

Follow this repo's own established pattern (used for both `mikadiv-vib` batches this session): push a throwaway verification branch, open a PR against `main`, watch the run to a real success, then close the PR unmerged and delete the branch.

```bash
git checkout -b verify-ci-kafe-openfaster-module
git push -u origin verify-ci-kafe-openfaster-module
gh pr create --repo OpenFASTER-Standard/spec --base main --head verify-ci-kafe-openfaster-module \
  --title "CI verification: kafe OpenFASTER module" \
  --body "Throwaway PR to verify CI green. Will be closed, not merged."
gh run watch <run-id-from-the-pr-checks> --repo OpenFASTER-Standard/spec --exit-status
gh pr close <pr-number> --repo OpenFASTER-Standard/spec --delete-branch
git checkout kafe-openfaster-module
git branch -D verify-ci-kafe-openfaster-module
```

Expected: the run succeeds, with visible green steps for all 4 new `kafe/` generation steps and all 3 new `kafe/` document builds.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/spec.yml documentation/prepare_spec.py
git commit -m "feat: add kafe/ build steps to CI"
```

---

### Task 9: README.md update

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing new — pure documentation of what Tasks 1-8 built.

- [ ] **Step 1: Update the repository-layout tree**

Add a `kafe/` sibling entry to the tree at `README.md:13-57` (currently only listing `mikadiv-vib/`), following the exact same sub-bullet style (schema files, `mapping.py`, generator scripts, `.bs` sources, `generated/` outputs) — cite the real files Tasks 1-7 created: `kafe.xsd`, `kafe-rm.xsd`, `kafe-va.xsd`, `kafe-standardtypes.xsd`, `kafe-statustypes.xsd`, `kafe-isotypes.xsd`, `status_codes.py`, `mapping.py`, `generate_rm_docs.py`, `generate_va_docs.py`, `generate_status_codes_docs.py`, `index.bs`, `request.bs`, `response.bs`, `generated/`.

- [ ] **Step 2: Update the mermaid diagram**

Add a parallel `kafe` flow to `README.md:72-88`'s existing mermaid diagram, mirroring the `mikadiv-vib`/`rgen` flow's structure but for 3 generation paths (Excel+RM+status-codes into `request.bs`, VA into `response.bs`) instead of 2.

- [ ] **Step 3: Update the file-role table**

Add rows to `README.md:106-130`'s table for every new `kafe/` file, following the exact same "File | Role | Edited by hand?" format.

- [ ] **Step 4: Update the "Option A - local Python" build sequence**

Add the `kafe/` build commands to `README.md:138-163`'s sequence, in the same position/order as Task 8's CI steps, **using the confirmed-correct invocation form from Task 5 Step 1** (do not default to `PYTHONPATH=.` without checking, matching Task 8's own caveat).

- [ ] **Step 5: Update the "Option B - CI" prose**

Extend `README.md:175-182`'s prose to mention the `kafe/` module's build steps.

- [ ] **Step 6: Update "Editing conventions"**

Extend `README.md:192-209`'s conventions section with a `kafe/`-specific paragraph mirroring the existing "To change Request field content... To change Response field content..." pattern, adding a third case for the status-code catalog: "To change the **status-code catalog**, edit `kafe/status_codes.py` directly (it has no XSD/PDF auto-sync — re-transcribe from the handbook by hand if BZSt revises it) and re-run `python -m kafe.generate_status_codes_docs`."

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs: update README for the kafe module"
```

---

### Task 10: Final gate — rebuild, spot-check status codes, merge-gated STOP, live verification

**Files:** none (verification only).

- [ ] **Step 1: Full local rebuild from a clean checkout state**

```bash
git status --short   # confirm clean working tree before starting
python generate_template.py
python -m kafe.generate_rm_docs        # use the confirmed-correct invocation form throughout
python -m kafe.generate_status_codes_docs
python -m kafe.generate_va_docs
python mikadiv-vib/generate_response_docs.py   # or PYTHONPATH=. form, per that module's own established ruling -- confirm no regression
PYTHONPATH=streamld python -m generator.generate_streamld_docs
python documentation/prepare_spec.py
bikeshed --allow-nonlocal-files --die-on=link-error spec documentation/about.bs documentation/about.html
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/index.bs kafe/index.html
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/request.bs kafe/request.html
KAFE_VERSION=$(python -m engine.version kafe/request.bs)
weasyprint --stylesheet documentation/print.css kafe/request.html kafe/generated/kafe-v${KAFE_VERSION}.pdf
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/response.bs kafe/response.html
bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv-vib/index.bs mikadiv-vib/index.html
bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv-vib/request.bs mikadiv-vib/request.html
bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv-vib/response.bs mikadiv-vib/response.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/index.bs streamld/index.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/core.bs streamld/core.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/subscription.bs streamld/subscription.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-sse.bs streamld/binding-sse.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-websocket.bs streamld/binding-websocket.html
python -m pytest kafe/tests/ streamld/tests/
```

Expected: every command exits 0; pytest reports all tests passing (both the new `kafe/tests/` suite and the pre-existing `streamld/tests/` suite — confirming no regression to `mikadiv-vib`/`streamld`'s own builds).

```bash
git status --short
```

Expected: any diffs limited to Bikeshed's own embedded revision-SHA/timestamp metadata — discard with `git checkout --` rather than committing.

- [ ] **Step 2: Spot-check the transcribed status codes against the handbook directly**

This is a genuine correctness-risk check, not just confirming the build passes — Task 2's own tests only verify a handful of known codes, not all 213 (the real, verified total — corrected from the plan's original 219 estimate during Task 2's own execution; see the ledger). Pick 15 codes spread across all 7 ranges (at least 2 per range) that Task 2's own tests do *not* already cover, and manually re-read the corresponding handbook page(s) to confirm the transcribed `code`/`message` in `kafe/status_codes.py` match exactly. Task 2's own report also flags 3 real handbook typos it deliberately preserved verbatim ("effecitve" at codes 3300/3301/3302, "missind" at 4426, "ist" at 6402) — these are expected, not transcription errors; don't flag them as mismatches. Document which 15 you checked and the result in your task report — if any mismatch is found, fix `kafe/status_codes.py` directly and re-run Task 2's full test suite plus this spot-check before proceeding.

- [ ] **Step 3: STOP — this step requires the operator's explicit go-ahead**

Do NOT merge or push to `main` without asking first. Present the branch's state (all 10 tasks' commits, the final local rebuild's clean result, the status-code spot-check's outcome) and ask the operator how they want it merged. Do not proceed past this point until they respond.

- [ ] **Step 4: (after merge) Confirm the push-to-main CI run is green**

```bash
gh run list --repo OpenFASTER-Standard/spec --branch main --limit 3
gh run watch <run-id> --repo OpenFASTER-Standard/spec --exit-status
```

Expected: all steps succeed, including "Commit regenerated output" actually running (not skipped, since this is a push to `main`) and `[skip ci]` correctly preventing an infinite loop (confirm by checking there's no second, self-triggered run).

- [ ] **Step 5: Verify every clean URL, including the two new documents**

```bash
for path in / /kafe /kafe/request /kafe/response /about /mikadiv-vib /mikadiv-vib/request /mikadiv-vib/response /streamld /streamld/core /streamld/subscription /streamld/binding-sse /streamld/binding-websocket; do
  echo "=== $path ==="
  curl -s -o /dev/null -w "%{http_code} (redirects: %{num_redirects})\n" -L "https://www.openfaster.org$path?cb=$(date +%s%N)"
done
```

Expected: every path returns `200` with `0` redirects — including confirming `mikadiv-vib`/`streamld` are still live and unaffected (no regression from this plan's own CI workflow edits in Task 8).

- [ ] **Step 6: Verify the download links and Excel content**

```bash
grep -o 'href="https://raw.githubusercontent.com[^"]*"' <(curl -s "https://www.openfaster.org/kafe/request")
```

Expected: two URLs with `4.3.2` in the filename.

```bash
curl -sL -o /tmp/live-kafe-request.xlsx "https://raw.githubusercontent.com/OpenFASTER-Standard/spec/main/kafe/generated/kafe-v4.3.2.xlsx"
python3 -c "
from openpyxl import load_workbook
wb = load_workbook('/tmp/live-kafe-request.xlsx')
names = wb.sheetnames
assert names[0] == '0 Legend Notes', names
assert names[-1] == 'Meta', names
assert '_Lists' in names, names
print('OK:', names)
ws = wb['4 Income']
headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1) if ws.cell(1, c).value]
assert 'RecordType' not in headers, headers
print('income headers OK, no RecordType:', headers[:10], '...')
"
```

Expected: prints `OK: [...]` with the expected sheet order, and the income-sheet check passes.

- [ ] **Step 7: Verify the Response document live**

```bash
curl -s "https://www.openfaster.org/kafe/response" | grep -o '<title>[^<]*'
curl -s "https://www.openfaster.org/kafe/response" | grep -c "not available yet\|not yet available"
curl -s "https://www.openfaster.org/kafe/response" | grep -c "BescheidArt"
```

Expected: the title contains "Response"; the provisional disclosure and `BescheidArt` both appear.

- [ ] **Step 8: Full real-browser link-integrity walkthrough**

Using a real headless-Chromium (Playwright) script, not curl: from `/`, click through to `/kafe`, then to `/kafe/request` and `/kafe/response` (both linked from the landing page), confirm each loads with the correct title, confirm the Request page's two Downloads links are present and point at `raw.githubusercontent.com` (not a blob URL), confirm the Excel template download's filename contains `4.3.2`, and confirm nothing 404s anywhere in the chain. This mirrors the exact Playwright walkthrough pattern already used for `mikadiv-vib`'s own live verification.

- [ ] **Step 9: Report a full evidence trail**

Summarize, with actual command output for each: the module verified live at all 3 new URLs; the Excel template confirmed to match production's real 6-sheet + Meta shape with no `RecordType`; the Response document confirmed live with the provisional-transport disclosure and real `kafe-va.xsd`-sourced content (not a stub); the full changelog (1.0.0 through the new 4.3.2 entry) confirmed rendering in the live Request document; the status-code appendix confirmed present with all 7 ranges; the spot-check of 15 status codes against the handbook confirmed clean (or documenting any fix applied); no regression to `mikadiv-vib`/`streamld`'s own live URLs.
