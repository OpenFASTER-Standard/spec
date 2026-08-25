"""Layer 2: template mapping for the KaFE withholding-tax refund module.

Mirrors ``mikadiv-vib/mapping.py``'s own architecture and contract exactly
(5-tuple fields: ``(name, description, type_display, requiredness, enum_key)``,
``build_enums()``/``build_sheets()``/``SHEET_ORDER``/``S_LEGEND``/``S_META``/
``SHEET_INFO``/``LEGEND_ROWS``/``LEGEND_TITLE``) -- see that file's own module
docstring for the general philosophy: every field's description, type/format
string and enumeration is pulled from the XSD via :class:`engine.xsd_model.XsdModel`,
this file only says *where* each column comes from.

Two things are different from MiKaDiv here, both load-bearing:

1. **Column naming.** ``kafe.xsd``'s raw element names are German
   (``SteuerpflichtDEEndeJahr``, ``Zuflussdatum``, ...), unlike VIB's own
   already-English schema, so MiKaDiv's convention of using the raw XSD local
   name as the Excel header does not carry over. Production's real,
   already-shipped field list -- ``column-defs.json`` (the KaFE bulk-processing
   pipeline's own field catalog) -- uses an English ``nameEn`` value per field
   (e.g. ``"CreditorNat/German_TaxOffice/LiabilityEnded"``) as its column
   header, and that convention is **not** internally consistent in its own
   prefixing (some paths keep a ``CreditorNat/``/``CreditorJur/`` prefix,
   others don't). This file uses each field's real ``nameEn`` value verbatim
   as the ``name=`` override on ``E()``/``A()``/``P()``/``SYN()`` for every
   field, including the Certificates Of Residence sheet's four real fields
   (``Issuer``/``IssuedAt``/``ValidFrom``/``ValidUntil``) and the Income
   sheet's twelve Par50jEStG fields (``Questions_for_50j/...``). An earlier
   version of this file's own test suite (task 3 brief's own Step 1) briefly
   asserted the *raw XSD* element names for those two spots instead -- an
   authoring mistake in the brief itself, now fixed there and here, per the
   task 3 report's fix-round-1 addendum.

2. **Requiredness.** ``column-defs.json``'s own ``type``/``required`` columns
   are never trusted as a source of truth -- only used (during this file's
   own research) to confirm which fields exist and their names. Every
   field's type and requiredness is resolved from the real XSD via
   :class:`XsdModel`. This is not a theoretical caution: ``column-defs.json``
   has two confirmed, still-live bugs in its own ``type`` column (internal
   GitLab MR !808 on the ``app`` repo) --
   ``CreditorNat/German_TaxOffice/LiabilityEnded`` says ``number`` but is
   really a 4-digit year expressed as text, and
   ``TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterestDescription``
   says ``boolean`` but is really free text -- both resolve correctly here
   simply because this file never reads that column at all. The one
   deliberate exception is KaFE's ``7xxx`` (Par50jEStG) status-code range:
   almost every field there is ``minOccurs="0"`` in the raw XSD, but the
   status-code catalog (``kafe/status_codes.py``) makes clear the real
   business rule is conditional-mandatory, not optional -- see
   ``PAR50J_CONDITIONAL_FIELDS`` below. A second, narrower exception is
   ``Par32Abs6KStG`` (see its own comment in ``build_sheets()``).
"""

from __future__ import annotations

from engine.xsd_model import XsdModel
from kafe.status_codes import STATUS_CODES

# --------------------------------------------------------------------------- #
# Sheet names
# --------------------------------------------------------------------------- #
S_LEGEND = "0 Legend Notes"
S_MASTER = "1 Creditors Natural"          # column-defs.json: creditorsNatural
S_JURIDICAL = "2 Creditors Juridical"     # column-defs.json: creditorsJuridical
S_COR = "3 Certificates Of Residence"     # column-defs.json: certificatesOfResidence
S_INCOME = "4 Income"                     # column-defs.json: income
S_INVESTMENT_CHAIN = "5 Investment Chain"  # column-defs.json: investmentChain
S_TRANSACTION_DATA = "6 Transaction Data"  # column-defs.json: transactionData
# "Meta" is handled separately by engine/generator.py's own Generator.run()
# (_build_meta) -- not declared here, matching mikadiv-vib/mapping.py.

SHEET_ORDER = [
    S_MASTER, S_JURIDICAL, S_COR, S_INCOME, S_INVESTMENT_CHAIN, S_TRANSACTION_DATA,
]

# Display string for the synthetic linking-key columns (creditorId / incomeId /
# the COR sheet's own id). KaFE's linking is two-level: creditorId alone links
# the four "child" sheets back to a row on the two creditor sheets; incomeId
# (together with creditorId) additionally links investmentChain/transactionData
# rows back to a specific row on the Income sheet.
LINK_ID = "Text (identifier used to link the sheets; any unique value)"

# --------------------------------------------------------------------------- #
# Presentation-only ("synthetic") column descriptions
# --------------------------------------------------------------------------- #
DESC_CREDITOR_PK = (
    "Identifier for this creditor, defined by you. Referenced by the "
    "creditorId column on every other sheet."
)
DESC_CREDITOR_FK = (
    f"Foreign key. Must match an id value on the '{S_MASTER}' or "
    f"'{S_JURIDICAL}' sheet (whichever this creditor is a natural or "
    "juridical person)."
)
DESC_COR_PK = (
    "Identifier for this certificate of residence, defined by you. "
    "Referenced by the CertificateOfResidenceId column on the Income sheet."
)
DESC_INCOME_PK = (
    "Sequence number of the income, starting with 1 (KaFE's own ErtragId). "
    "Also serves, together with creditorId, as the linking key referenced "
    f"by the '{S_INVESTMENT_CHAIN}' and '{S_TRANSACTION_DATA}' sheets."
)
DESC_INCOME_FK = (
    f"Foreign key. Must match an incomeId value on the '{S_INCOME}' sheet "
    "for this creditorId."
)
DESC_COR_FK = (
    f"Foreign key. Must match an id value on the '{S_COR}' sheet -- "
    "identifies which certificate of residence supports this income."
)
DESC_PERSON_CHOICE = (
    "Which block below is filled in for this representative: a natural "
    "person or a non-natural person (organisation)."
)
DESC_REQUESTED_REFUND = (
    "The refund amount being claimed for this income (informational; BZSt "
    "itself computes the actual refund from the withheld tax and the "
    "applicable treaty/statutory rate -- this is not a real KaFE XSD field)."
)
DESC_PUBLIC_BENEFIT_PURPOSES = (
    "Free-text list of which of the 26 numbered public-benefit purposes "
    "(section 52(2) German Fiscal Code) apply, e.g. '1, 8, 21'. The real "
    "schema models these as 26 separate yes/no flags (ZweckNr1..ZweckNr26, "
    "GemeinnuetzigeZwecke_Struct); this column collapses them into one field."
)
ANSPRUCH_INTORG_NOTE = (
    " KaFE also defines a seventh legal basis, IntOrg (agreements/conventions "
    "for international organisations and intergovernmental organisations), "
    "which status code 2101 treats as mutually exclusive with all six legal "
    "bases above; IntOrg has no column of its own in production's own field "
    "list, so this template cannot express it."
)

# --------------------------------------------------------------------------- #
# Synthetic enums (no XSD source) + the order/source of every enum rendered.
# --------------------------------------------------------------------------- #
SYNTHETIC_ENUMS: dict[str, tuple[list[str], dict[str, str]]] = {
    "Boolean": (
        ["true", "false"],
        {"true": "Yes - the condition applies.",
         "false": "No - the condition does not apply."},
    ),
    "PersonChoice": (
        ["NatuerlichePerson", "NichtNatuerlichePerson"],
        {"NatuerlichePerson": "Natural person - fill in the Natural Person fields below.",
         "NichtNatuerlichePerson": "Non-natural person / organisation - fill in the Non-Natural Person fields below."},
    ),
}

ENUM_ORDER = [
    "Boolean", "KapitalertragArt", "TransaktionArt", "TransaktionGeschaeft",
    "CountryISOAlpha2", "Rechtsformen", "Anrede", "Steuerbehoerden", "PersonChoice",
]

XSD_NAMED_ENUMS = {
    "KapitalertragArt": "KapitalertragArt_ENUM",
    "TransaktionArt": "TransaktionArt_ENUM",
    "TransaktionGeschaeft": "TransaktionGeschaeft_ENUM",
    "CountryISOAlpha2": "CountryISOAlpha2_ENUM",
    "Rechtsformen": "Rechtsformen_ENUM",
    "Anrede": "Anrede_ENUM",
    "Steuerbehoerden": "Steuerbehoerden_ENUM",
}


def build_enums(model: XsdModel) -> tuple[dict[str, list[str]], dict[str, dict[str, str]]]:
    """Assemble ENUMS + ENUM_MEANINGS from the XSD (and synthetic definitions)."""
    values: dict[str, list[str]] = {}
    meanings: dict[str, dict[str, str]] = {}

    for key in ENUM_ORDER:
        if key in SYNTHETIC_ENUMS:
            vals, mean = SYNTHETIC_ENUMS[key]
        elif key in XSD_NAMED_ENUMS:
            vals, mean = model.enum(XSD_NAMED_ENUMS[key])
        else:  # pragma: no cover - guarded by ENUM_ORDER
            raise KeyError(f"no source defined for enum {key!r}")
        values[key] = list(vals)
        meanings[key] = dict(mean)

    return values, meanings


# --------------------------------------------------------------------------- #
# Par50jEStG conditional-mandatory override.
#
# Every one of these 12 fields is minOccurs="0" in the raw XSD (Haltedauer_Struct,
# MinWertAendRisiko_Struct, WeiterlVerpflichtung_Struct, RueckgabeVerpflichtung_Struct),
# but kafe/status_codes.py's own 7xxx range (7200/7210/7300/7310/7400/7410, plus the
# always-required-in-practice Haltedauer quartet) makes clear the real business rule
# is conditional-mandatory: fill in the block if Par50jEStG applies to this income at
# all. This is the one place in this module where the raw XSD's own requiredness is
# deliberately overridden rather than trusted as-is.
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Address field -> XSD element name (Adresse_Struct is reused, verbatim, by
# every address block in the schema: StpflAdresse, BevAdresse, GVAdresse,
# GeschaeftsleitungOrt).
# --------------------------------------------------------------------------- #
_ADDR_XSD = {
    "Street": "Strasse",
    "StreetNumber": "Hausnummer",
    "HouseNumber": "Hausnummer",
    "Apartment": "Wohnung",
    "ApartmentNumber": "Wohnung",
    "Floor": "Etage",
    "District": "Verwaltungsbezirk",
    "Postcode": "Postleitzahl",
    "PostCode": "Postleitzahl",
    "City": "Ort",
    "Region_FederalState": "Bundesstaat",
    "Country": "Staat",
    "AdditionalAddressDetails": "Adressergaenzung",
}


def build_sheets(model: XsdModel) -> dict[str, list[tuple]]:
    """Assemble every sheet's ordered field list, pulling wording from the XSD."""

    def resolve(field, req, enum, name):
        requiredness = req if req is not None else ("Required" if field.required else "Optional")
        # Every plain xs:boolean field gets a real Excel dropdown (matching the
        # "Enum dropdowns" legend entry) even when the caller didn't ask for
        # one explicitly -- KaFE has dozens of yes/no fields and MiKaDiv's own
        # sparse opt-in would mean most of them silently got no validation.
        if enum is None and field.type_display.startswith("Boolean"):
            enum = "Boolean"
        if enum == "Boolean":
            type_display = "Boolean (true / false)"
        elif enum:
            type_display = "Enum"
        else:
            type_display = field.type_display
        return (name or field.name, field.description, type_display, requiredness, enum)

    def E(type_name, field_name, req=None, enum=None, desc=None, name=None):
        return resolve(model.elem(type_name, field_name, description=desc), req, enum, name)

    def A(type_name, field_name, req=None, enum=None, desc=None, name=None):
        return resolve(model.attr(type_name, field_name, description=desc), req, enum, name)

    def P(type_name, names, req=None, enum=None, desc=None, name=None):
        return resolve(model.path(type_name, names, description=desc), req, enum, name)

    def SYN(name, desc, type_display, req, enum=None):
        return (name, desc, type_display, req, enum)

    def xsd_desc(type_name, field_name):
        return model.elem(type_name, field_name).description

    def creditor_pk():
        return SYN("id", DESC_CREDITOR_PK, LINK_ID, "Required")

    def creditor_fk():
        return SYN("creditorId", DESC_CREDITOR_FK, LINK_ID, "Required")

    def income_fk():
        return SYN("incomeId", DESC_INCOME_FK, LINK_ID, "Required")

    def address_block(prefix, order):
        return [E("Adresse_Struct", _ADDR_XSD[suffix], name=f"{prefix}/{suffix}")
                for suffix in order]

    def anspruch_fields():
        """LegalBasis/* -- shared verbatim between both creditor sheets."""
        note = ANSPRUCH_INTORG_NOTE + (
            f' (status code 2101: "{STATUS_CODES["2101"].message}")'
        )
        par32_desc = xsd_desc("Anspruch_Struct", "Par32Abs6KStG") + (
            " This legal basis only applies to claims concerning inflows on or "
            "after 15 April 2025; like the other legal-basis flags, it cannot "
            f'be combined with the IntOrg legal basis (status code 2101: '
            f'"{STATUS_CODES["2101"].message}").'
        )
        return [
            E("Anspruch_Struct", "Abkommen", name="LegalBasis/DTA",
              desc=xsd_desc("Anspruch_Struct", "Abkommen") + note),
            E("Anspruch_Struct", "Par43bEStG", name="LegalBasis/Par43bEStG"),
            E("Anspruch_Struct", "Par44aEStG", name="LegalBasis/Par44aEStG"),
            E("Anspruch_Struct", "Par50gEStG", name="LegalBasis/Par50gEStG"),
            E("Anspruch_Struct", "Par32Abs6KStG", req="Conditional",
              name="LegalBasis/Par32Abs6KStG", desc=par32_desc),
            E("Anspruch_Struct", "Art63AEUV", name="LegalBasis/Art63AEUV"),
        ]

    def bank_fields():
        """Bank/* -- shared verbatim between both creditor sheets."""
        return [
            E("Bankverbindung_Struct", "GeldinstitutName", name="Bank/Name"),
            E("Bankverbindung_Struct", "GeldinstitutOrt", name="Bank/City"),
            E("Bankverbindung_Struct", "Kontoinhaber", name="Bank/AccountHolder"),
            E("Bankverbindung_Struct", "BIC", name="Bank/Account/BIC"),
            E("Bankverbindung_Struct", "IBAN", req="Conditional", name="Bank/Account/IBAN"),
            E("Bankverbindung_Struct", "Kontonummer", req="Conditional",
              name="Bank/Account/AccountNumber"),
        ]

    def bevollmaechtigter_fields():
        """AuthorizedRep/* -- shared verbatim between both creditor sheets."""
        return [
            SYN("AuthorizedRep/General_Data/LegalForm", DESC_PERSON_CHOICE,
                "Enum", "Optional", "PersonChoice"),
            E("Befugnis_Struct", "StBerBerufe", name="AuthorizedRep/Authority/TaxProfessions"),
            E("Befugnis_Struct", "AndereGruende", name="AuthorizedRep/Authority/OtherReasons"),
            E("NatP_Struct", "Anrede", enum="Anrede",
              name="AuthorizedRep/NaturalPerson/General_Data/FormOfAddress"),
            E("NatP_Struct", "Titel", name="AuthorizedRep/NaturalPerson/General_Data/Title"),
            E("NatP_Struct", "Vorname", name="AuthorizedRep/NaturalPerson/General_Data/FirstName"),
            E("NatP_Struct", "Nachname", name="AuthorizedRep/NaturalPerson/General_Data/LastName"),
            E("NichtNatP_Struct", "OrganisationName",
              name="AuthorizedRep/NonNaturalPerson/General_Data/Name"),
            E("NichtNatP_Struct", "Organisationseinheit",
              name="AuthorizedRep/NonNaturalPerson/General_Data/Department"),
            *address_block("AuthorizedRep/Address",
                            ["Street", "StreetNumber", "AdditionalAddressDetails", "District",
                             "Postcode", "City", "Region_FederalState", "Country",
                             "Apartment", "Floor"]),
        ]

    def gesetzliche_vertretung_fields():
        """LegalRep/* -- shared verbatim between both creditor sheets."""
        return [
            SYN("LegalRep/LegalForm", DESC_PERSON_CHOICE, "Enum", "Optional", "PersonChoice"),
            E("NatP_Struct", "Anrede", enum="Anrede", name="LegalRep/NatPerson/FormOfAddress"),
            E("NatP_Struct", "Titel", name="LegalRep/NatPerson/Title"),
            E("NatP_Struct", "Vorname", name="LegalRep/NatPerson/FirstName"),
            E("NatP_Struct", "Nachname", name="LegalRep/NatPerson/LastName"),
            E("NichtNatP_Struct", "OrganisationName", name="LegalRep/JurPerson/OrganisationName"),
            E("NichtNatP_Struct", "Organisationseinheit",
              name="LegalRep/JurPerson/OrganisationDepartment"),
            *address_block("LegalRep/Address",
                            ["Street", "City", "Country", "HouseNumber", "ApartmentNumber",
                             "Floor", "District", "Region_FederalState", "PostCode",
                             "AdditionalAddressDetails"]),
        ]

    def steuerbeguenstigte_zwecke_fields():
        """TaxPrivileges/* -- shared verbatim between both creditor sheets."""
        return [
            E("ZER_Struct", "Eintrag", name="TaxPrivileges/ZER/Registration"),
            E("ZER_Struct", "Referenznummer", name="TaxPrivileges/ZER/ReferenceNumber"),
            E("Zwecke_Struct", "Gemeinnuetzig", name="TaxPrivileges/Purposes/NonProfit"),
            SYN("TaxPrivileges/Purposes/PublicBenefitPurposes", DESC_PUBLIC_BENEFIT_PURPOSES,
                "Text", "Optional"),
            E("Zwecke_Struct", "Mildtaetig", name="TaxPrivileges/Purposes/Charity"),
            E("Zwecke_Struct", "Kirchlich", name="TaxPrivileges/Purposes/Church"),
            E("Zwecke_Struct", "Ausschliesslich", name="TaxPrivileges/Purposes/Exclusivity"),
            E("Zwecke_Struct", "Beginn", name="TaxPrivileges/Purposes/StartDate"),
            E("Satzung_Struct", "LetzteAenderung", name="TaxPrivileges/Statuses/LastChangeDate"),
            E("Inlandsbezug_Struct", "VerwirklichungDE",
              name="TaxPrivileges/StructuralConnectionToGermany/TaxPrivilegedPurposesDE"),
            E("Inlandsbezug_Struct", "FoerderungDE",
              name="TaxPrivileges/StructuralConnectionToGermany/GermanResidentsEligibility"),
            E("Inlandsbezug_Struct", "AnsehenDE",
              name="TaxPrivileges/StructuralConnectionToGermany/GermanReputation"),
            E("Inlandsbezug_Struct", "Erlaeuterung",
              name="TaxPrivileges/StructuralConnectionToGermany/Explanation"),
            E("Vermoegensbindung_Struct", "KoerperschaftDE",
              name="TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporation"),
            E("Vermoegensbindung_Struct", "KoerperschaftKStG",
              name="TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporationKStG"),
            E("Vermoegensbindung_Struct", "KoerperschaftOeRecht",
              name="TaxPrivileges/StructuralConnectionToGermany/AssetLock/LegalEntity"),
            E("Vermoegensbindung_Struct", "Andere",
              name="TaxPrivileges/StructuralConnectionToGermany/AssetLock/Other"),
            E("SteuerbeguenstigteZwecke_Struct", "Geschaeftsfuehrung", name="TaxPrivileges/Management"),
            E("SteuerbeguenstigteZwecke_Struct", "Verfassungstreue",
              name="TaxPrivileges/ConstitutionLoyalty"),
        ]

    sheets: dict[str, list[tuple]] = {}

    # ----------------------------------------------------------------- #
    # 3 Certificates Of Residence -- the smallest sheet, establishes the
    # SYN()-for-linking-keys / E()-for-real-fields pattern. The 4 real fields
    # use column-defs.json's real nameEn values verbatim as column headers
    # (Issuer/IssuedAt/ValidFrom/ValidUntil), per this module's own "Column
    # naming convention" -- not the raw German XSD element names.
    # ----------------------------------------------------------------- #
    sheets[S_COR] = [
        creditor_fk(),
        SYN("id", DESC_COR_PK, LINK_ID, "Required"),
        E("AnsaessBescheinigung_Struct", "Ausstellungsbehoerde", name="Issuer"),
        E("AnsaessBescheinigung_Struct", "Ausstellungsdatum", name="IssuedAt"),
        E("AnsaessBescheinigung_Struct", "GueltigVon", name="ValidFrom"),
        E("AnsaessBescheinigung_Struct", "GueltigBis", name="ValidUntil"),
    ]

    # ----------------------------------------------------------------- #
    # 4 Income -- Ertrag_CType / ErtragAllg_CType / Nachweis_Struct /
    # WesentlicheBeteiligung_Struct / MittelbBeteiligung_CType / RemittanceBaseType /
    # Par50jEStG_Struct's Haltedauer/MinWertAendRisiko/WeiterlVerpflichtung/
    # RueckgabeVerpflichtung blocks (Transaktionsdaten lives on its own sheet, 3e).
    # ----------------------------------------------------------------- #
    def par50j(field_name, name_en, path):
        # Column header is column-defs.json's real nameEn value, verbatim,
        # matching every other sheet's convention (see this module's own
        # docstring, point 1).
        req = _par50j_requiredness(field_name, model.path("Par50jEStG_Struct", path).required)
        return P("Par50jEStG_Struct", path, req=req, name=name_en)

    sheets[S_INCOME] = [
        creditor_fk(),
        A("Ertrag_CType", "ErtragId", name="incomeId", desc=DESC_INCOME_PK),
        SYN("CertificateOfResidenceId", DESC_COR_FK, LINK_ID, "Required"),
        E("ErtragAllg_CType", "KapArt", enum="KapitalertragArt", name="CapitalIncome"),
        E("ErtragAllg_CType", "ISIN", name="Stocks_ConvertibleBonds/ISIN"),
        E("ErtragAllg_CType", "AnzahlAnteile", name="Stocks_ConvertibleBonds/NumberOfShares"),
        E("WesentlicheBeteiligung_Struct", "WesentlBeteiligung",
          name="SubstantialHolding/IsSubstantial"),
        E("WesentlicheBeteiligung_Struct", "WesentlBeteiligungHoehe",
          name="SubstantialHolding/Ownership"),
        E("WesentlicheBeteiligung_Struct", "Beteiligungsdauer18M",
          name="SubstantialHolding/HoldingPeriod18M"),
        E("WesentlicheBeteiligung_Struct", "Beteiligungsdauer12M",
          name="SubstantialHolding/HoldingPeriod12M"),
        E("WesentlicheBeteiligung_Struct", "Beteiligungsdauer6M",
          name="SubstantialHolding/HoldingPeriod6M"),
        E("MittelbBeteiligung_CType", "MittelbBeteiligung",
          name="IndirectHolding/IndirectHolding"),
        E("MittelbBeteiligung_CType", "EhegattenGbR", name="IndirectHolding/CompanyOfSpouses"),
        P("MittelbBeteiligung_CType", ["Beteiligungskette", "MittelbBeteiligungProzent"],
          name="IndirectHolding/SizeOfIndirectHolding"),
        E("ErtragAllg_CType", "Schuldnerin", name="Debtor/Name"),
        E("ErtragAllg_CType", "Stnr", name="Debtor/TaxNumber"),
        E("ErtragAllg_CType", "SitzNichtDE", name="NonResidency_DE"),
        E("ErtragAllg_CType", "Zuflussdatum", name="DateOfReceiptOfCapitalIncome"),
        E("ErtragAllg_CType", "Bruttozufluss", name="GrossIncomeFromCapitalReceived"),
        E("Nachweis_Struct", "Abzugssteuer", name="Withheld_Taxes"),
        SYN("Requested_Refund", DESC_REQUESTED_REFUND, "Decimal", "Optional"),
        P("Nachweis_Struct", ["Steuerbescheinigung", "DateiBeschreibung"],
          name="DocumentDescription"),
        E("Nachweis_Struct", "Ordnungsnummer", name="DocumentProof/TaxCertificateNumber"),
        E("ErtragAllg_CType", "vGA", name="Hidden_ProfitDistribution/ConstructiveDividend"),
        E("ErtragAllg_CType", "WirtschaftlEigentum",
          name="Economic_Ownership/Ownership_and_Right_To_Use"),
        E("ErtragAllg_CType", "Steuerbefreiung", name="TaxExemption"),
        E("ErtragAllg_CType", "VersicherungsNr", name="LifeInsurancePolicyNumber"),
        E("ErtragAllg_CType", "Hinterlegungsscheine", name="Depositary_Receipts/Is_DR"),
        E("ErtragAllg_CType", "Underlying", name="Depositary_Receipts/ISIN_DR"),
        E("RemittanceBaseType", "RemBaseBesteuerung", name="RemittanceBase/IsSubject"),
        E("RemittanceBaseType", "RemBaseUeberweisung", name="RemittanceBase/Amount"),
        E("ErtragAllg_CType", "BetriebsstaetteDE",
          name="Business_Establishment/Business_Establishment_DE"),
        E("ErtragAllg_CType", "UnbeschraenktAuslaendKoerperschaftstpfl",
          name="UnlimitedForeignCorporateTaxLiability"),
        E("ErtragAllg_CType", "Anrechnungsbetrag", name="CreditAmount"),
        par50j("HaltedauerMin45T", "Questions_for_50j/HoldingPeriod/HoldingMore45D",
               ["Haltedauer", "HaltedauerMin45T"]),
        par50j("HaltedauerMin1J", "Questions_for_50j/HoldingPeriod/HoldingMore1Y",
               ["Haltedauer", "HaltedauerMin1J"]),
        par50j("HaltedauerKuerzer45T", "Questions_for_50j/HoldingPeriod/HoldingLess45D",
               ["Haltedauer", "HaltedauerKuerzer45T"]),
        par50j("AnteilePar50jEStG", "Questions_for_50j/HoldingPeriod/SharesPar50jEStG",
               ["Haltedauer", "AnteilePar50jEStG"]),
        par50j("GegenlAnsprueche", "Questions_for_50j/MinValueChangeRisk/OpposingClaims",
               ["MinWertAendRisiko", "GegenlAnsprueche"]),
        par50j("RisikoMin70", "Questions_for_50j/MinValueChangeRisk/RiskMin70",
               ["MinWertAendRisiko", "RisikoMin70"]),
        par50j("GegenlAnspruecheAndere", "Questions_for_50j/MinValueChangeRisk/OtherOpposingClaims",
               ["MinWertAendRisiko", "GegenlAnspruecheAndere"]),
        par50j("WeiterlVerpfl", "Questions_for_50j/ForwardingObligation/ForwardingObligation",
               ["WeiterlVerpflichtung", "WeiterlVerpfl"]),
        par50j("WeiterlVerpflAnteile", "Questions_for_50j/ForwardingObligation/NumberOfShares",
               ["WeiterlVerpflichtung", "WeiterlVerpflAnteile"]),
        par50j("WeiterlVerpflAndere", "Questions_for_50j/ForwardingObligation/FurtherForwardingObligation",
               ["WeiterlVerpflichtung", "WeiterlVerpflAndere"]),
        par50j("RueckgabeVerpfl", "Questions_for_50j/ReturnObligation/ReturnObligation",
               ["RueckgabeVerpflichtung", "RueckgabeVerpfl"]),
        par50j("RueckgabeVerpflAnteile", "Questions_for_50j/ReturnObligation/NumberOfShares",
               ["RueckgabeVerpflichtung", "RueckgabeVerpflAnteile"]),
    ]

    # ----------------------------------------------------------------- #
    # 5 Investment Chain -- MittelbBeteiligung_CType.Beteiligungskette
    # (Beteiligungskette_Struct.Beteiligung, repeating). Note: the real XSD's
    # Beteiligung_Struct.AnsaessigkeitDE ("is the company resident in Germany?",
    # required) and .Beteiligungsnachweis (attachment) have no column here --
    # confirmed directly against column-defs.json's real 10-field investmentChain
    # array, not assumed; see the task 3 report.
    # ----------------------------------------------------------------- #
    sheets[S_INVESTMENT_CHAIN] = [
        creditor_fk(),
        income_fk(),
        A("Beteiligung_Struct", "BeteiligungsId", name="SequenceNumber"),
        E("Beteiligung_Struct", "OrganisationName", name="OrganizationName"),
        E("Beteiligung_Struct", "Rechtsform", name="LegalForm"),
        E("Beteiligung_Struct", "BeteiligungHoehe", name="Ownership"),
        E("Beteiligung_Struct", "Ansaessigkeitsstaat", enum="CountryISOAlpha2", name="Country"),
        E("Beteiligung_Struct", "Stnr", name="GermanTaxNumber"),
        E("Beteiligung_Struct", "TIN", name="TIN"),
        E("Beteiligung_Struct", "Vermoegensverwaltung", name="AssetManagement"),
    ]

    # ----------------------------------------------------------------- #
    # 6 Transaction Data -- Par50jEStG_Struct.Transaktionsdaten -> Depot_Struct
    # -> Transaktion_Struct. Confirmed directly against column-defs.json: the
    # Depot-level opening/closing balance fields (Anfangsbestand/Endbestand and
    # their dates) are repeated on every transaction row in the flattened
    # Excel sheet, not captured once per depot.
    # ----------------------------------------------------------------- #
    sheets[S_TRANSACTION_DATA] = [
        creditor_fk(),
        income_fk(),
        A("Transaktion_Struct", "TransaktionId", name="TransactionNumber"),
        E("Depot_Struct", "Depotnummer", name="DepotNumber"),
        E("Depot_Struct", "Anfangsbestand", name="Depot/OpeningBalance"),
        E("Depot_Struct", "AnfangsbestandDatum", name="Depot/DateOfOpeningBalance"),
        E("Depot_Struct", "Endbestand", name="Depot/ClosingBalance"),
        E("Depot_Struct", "EndbestandDatum", name="Depot/DateOfClosingBalance"),
        E("Transaktion_Struct", "Transaktionsart", enum="TransaktionArt",
          name="TransactionDirection"),
        E("Transaktion_Struct", "Handelstag", name="TradingDay"),
        E("Transaktion_Struct", "Geschaeft", enum="TransaktionGeschaeft", name="TransactionType"),
        E("Transaktion_Struct", "Stueckzahl", name="NumberOfShares"),
        E("Transaktion_Struct", "VereinbAbwicklungstag", name="AgreedSettlementDate"),
        E("Transaktion_Struct", "TatsaechlAbwicklungstag", name="ActualSettlementDate"),
    ]

    # ----------------------------------------------------------------- #
    # 1 Creditors Natural -- Erstattungsantrag_CType's Anliegen/AllgAngaben/
    # SteuerlicheBehandlung/Zahlungsweg/Erklaerungen sub-trees, StpflPerson_Struct's
    # NatuerlichePerson (StpflNatP_Struct) branch.
    #
    # column-defs.json's own creditorsNatural array only carries 3 of
    # Erklaerungen_CType's 8 real affirmation fields (ZusaetzlicheAngaben,
    # BegruendungArt63AEUV, AntragPar50c) -- Antrag/AntragIntOrg/AntragFA/
    # Versicherung/AntragPar11InvStG have no column on either creditor sheet in
    # production's real shape (AntragPar11InvStG appears only on Juridical, see
    # below). Confirmed directly against column-defs.json, not assumed; flagged
    # in the task 3 report as a real surprise relative to the brief's own
    # reconstruction (which listed all 8 as belonging "per production's own
    # real shape").
    # ----------------------------------------------------------------- #
    sheets[S_MASTER] = [
        creditor_pk(),
        E("Anliegen_CType", "Ansaessigkeitsstaat", enum="CountryISOAlpha2",
          name="generalData/Country"),
        E("SteuerlicheBehandlung_CType", "KennNr", name="CreditorNat/General_Data/WithholdingTaxNumber"),
        E("NatP_Struct", "Anrede", enum="Anrede", name="CreditorNat/General_Data/FormOfAddress"),
        E("NatP_Struct", "Titel", name="CreditorNat/General_Data/FormOfTitle"),
        E("NatP_Struct", "Nachname", name="CreditorNat/General_Data/Name"),
        E("NatP_Struct", "Vorname", name="CreditorNat/General_Data/GivenName"),
        E("StpflNatP_Struct", "Geburtsdatum", name="CreditorNat/General_Data/Birthday"),
        E("StpflNatP_Struct", "StaatsangehoerigkeitDE", name="CreditorNat/General_Data/NationalityIsDE"),
        E("StpflNatP_Struct", "StaatsangehoerigkeitKW", name="CreditorNat/General_Data/NationalityIsKW"),
        E("StpflNatP_Struct", "StaatsangehoerigkeitCH", name="CreditorNat/General_Data/NationalityIsCH"),
        E("SteuerlicheBehandlung_CType", "TinVorhanden", name="CreditorNat/General_Data/TinAvailable"),
        E("SteuerlicheBehandlung_CType", "TIN", name="CreditorNat/General_Data/IDNumber_CountryOfResidence"),
        *address_block("CreditorNat/Address",
                        ["Street", "Floor", "Apartment", "StreetNumber", "AdditionalAddressDetails",
                         "District", "Postcode", "City", "Region_FederalState", "Country"]),
        E("Ansprechperson_Struct", "Vorname", name="CreditorNat/ContactPerson/FirstName"),
        E("Ansprechperson_Struct", "Nachname", name="CreditorNat/ContactPerson/Name"),
        E("Ansprechperson_Struct", "Organisation", name="CreditorNat/ContactPerson/Organization"),
        E("Ansprechperson_Struct", "E-Mail", name="CreditorNat/ContactPerson/Email"),
        E("Ansprechperson_Struct", "Telefon", name="CreditorNat/ContactPerson/PhoneNumber"),
        E("FinanzamtDE_Struct", "FinanzamtDE", name="CreditorNat/German_TaxOffice/German_TaxOffice"),
        E("FinanzamtDE_Struct", "Stnr", name="CreditorNat/German_TaxOffice/TaxNumber"),
        E("FinanzamtDE_Struct", "SteuerpflichtDE", name="CreditorNat/German_TaxOffice/TaxLiabilityGermany"),
        E("FinanzamtDE_Struct", "SteuerpflichtDE5J",
          name="CreditorNat/German_TaxOffice/TaxLiabilityGermany5Years"),
        # Regression-tested (task-3-brief Step 1): xs:gYear resolves to a
        # "Text" type_display, not "number" as column-defs.json's own (buggy)
        # type column claims.
        E("FinanzamtDE_Struct", "SteuerpflichtDEEndeJahr",
          name="CreditorNat/German_TaxOffice/LiabilityEnded"),
        *bevollmaechtigter_fields(),
        *gesetzliche_vertretung_fields(),
        *anspruch_fields(),
        *bank_fields(),
        E("ErtragAllg_CType", "SitzNichtDE", name="Residence/NonResidency_DE"),
        E("SteuerlicheBehandlung_CType", "IdNr", name="TaxTreatment/IdNr"),
        E("SchweizFragen_Struct", "SteuerpflichtCH", name="TaxTreatment/SwitzerlandQuestions/TaxLiabilityCH"),
        E("SchweizFragen_Struct", "SteuerpflichtDE",
          name="TaxTreatment/SwitzerlandQuestions/In_Germany_Min_5_Years_Taxable"),
        E("SchweizFragen_Struct", "StpflDE5Jahre",
          name="TaxTreatment/SwitzerlandQuestions/In_Germany_Tax_Liability_Ended"),
        E("UnselbstArbeit_Struct", "UnselbstArbeit",
          name="TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EmploymentReasons"),
        E("UnselbstArbeit_Struct", "Arbeitgeber",
          name="TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/Employer"),
        E("UnselbstArbeit_Struct", "InteresseArbeitgeber",
          name="TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterest"),
        # Regression-tested (task-3-brief Step 1): resolves to a "Text"
        # type_display (free text, max 500), not "boolean" as
        # column-defs.json's own (buggy) type column claims.
        E("UnselbstArbeit_Struct", "InteresseBeschreibung",
          name="TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterestDescription"),
        E("UnselbstArbeit_Struct", "Zuzugsdatum",
          name="TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/MoveDate"),
        E("UnselbstArbeit_Struct", "Zuzugsgruende",
          name="TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/OtherReasons"),
        E("Erklaerungen_CType", "ZusaetzlicheAngaben", name="Affirmations/AdditionalInformation"),
        E("Erklaerungen_CType", "BegruendungArt63AEUV", name="Affirmations/JustificationArt63TFEU"),
        E("Erklaerungen_CType", "AntragPar50c", name="Affirmations/ApplicationPar50c"),
        *steuerbeguenstigte_zwecke_fields(),
    ]

    # ----------------------------------------------------------------- #
    # 2 Creditors Juridical -- same Erstattungsantrag_CType, StpflPerson_Struct's
    # NichtNatuerlichePerson (StpflNichtNatP_Struct) branch. Juridical-only
    # blocks (LEI/Register/Boerse/OptionKStG/Investmentfonds/W-IdNr/
    # AntragPar11InvStG) have no counterpart on the Natural sheet.
    # ----------------------------------------------------------------- #
    sheets[S_JURIDICAL] = [
        creditor_pk(),
        E("Anliegen_CType", "Ansaessigkeitsstaat", enum="CountryISOAlpha2",
          name="generalData/Country"),
        E("Anliegen_CType", "Rechtsform", enum="Rechtsformen", name="generalData/LegalForm"),
        E("StpflNichtNatP_Struct", "RechtsformAuspraegung", name="generalData/SpecificLegalForm"),
        E("Anliegen_CType", "GewinnePG_CH", name="generalData/ProfitsPG_CH"),
        E("Ansprechperson_Struct", "Vorname", name="CreditorJur/ContactPerson/FirstName"),
        E("Ansprechperson_Struct", "Nachname", name="CreditorJur/ContactPerson/Name"),
        E("Ansprechperson_Struct", "Organisation", name="CreditorJur/ContactPerson/Organization"),
        E("Ansprechperson_Struct", "E-Mail", name="CreditorJur/ContactPerson/Email"),
        E("Ansprechperson_Struct", "Telefon", name="CreditorJur/ContactPerson/PhoneNumber"),
        E("StpflNichtNatP_Struct", "Gruendungsdatum", name="CreditorJur/General_Data/DateOfEstablishment"),
        E("StpflNichtNatP_Struct", "Gruendungsstaat", enum="CountryISOAlpha2",
          name="CreditorJur/General_Data/IncorporationCountry"),
        E("SteuerlicheBehandlung_CType", "TinVorhanden", name="CreditorJur/General_Data/TinAvailable"),
        E("SteuerlicheBehandlung_CType", "TIN",
          name="CreditorJur/General_Data/IDNumber_CountryOfResidence"),
        E("SteuerlicheBehandlung_CType", "TranspGebilde", name="CreditorJur/General_Data/TransparentEntity"),
        E("SteuerlicheBehandlung_CType", "KennNr", name="CreditorJur/General_Data/WithholdingTaxNumber"),
        E("NichtNatP_Struct", "OrganisationName", name="CreditorJur/General_Data/Name"),
        E("NichtNatP_Struct", "Organisationseinheit", name="CreditorJur/General_Data/Department"),
        *address_block("CreditorJur/Address",
                        ["Street", "StreetNumber", "AdditionalAddressDetails", "District",
                         "Postcode", "City", "Region_FederalState", "Country",
                         "Apartment", "Floor"]),
        E("StpflNichtNatP_Struct", "LEI", name="CreditorJur/LEI"),
        E("Registereintragung_Struct", "Register", name="CreditorJur/Register/Register"),
        E("Registereintragung_Struct", "Registerbehoerde", req="Conditional",
          name="CreditorJur/Register/RegistryAuthority"),
        E("Registereintragung_Struct", "Registernummer", req="Conditional",
          name="CreditorJur/Register/RegistrationNumber"),
        E("Boersenhandel_Struct", "Boersenhandel", name="CreditorJur/Boerse/StockExchange"),
        E("Boersenhandel_Struct", "ISIN", name="CreditorJur/Boerse/ISIN"),
        E("Boersenhandel_Struct", "Boersenplatz", name="CreditorJur/Boerse/Boersenplatz"),
        E("FinanzamtDE_Struct", "FinanzamtDE", name="CreditorJur/German_TaxOffice/German_TaxOffice"),
        E("FinanzamtDE_Struct", "Stnr", name="CreditorJur/German_TaxOffice/TaxNumber"),
        E("OptionKStG_Struct", "OptionKStG", name="CreditorJur/OptingUnderCorpTaxAct/OptionKStG"),
        E("OptionKStG_Struct", "Steuerbehoerde", enum="Steuerbehoerden",
          name="CreditorJur/OptingUnderCorpTaxAct/TaxAuthority"),
        E("OptionKStG_Struct", "Aktenzeichen", name="CreditorJur/OptingUnderCorpTaxAct/FileNumber"),
        E("Statusbescheinigung_Struct", "StatusbescheinigungBeantragt",
          name="InvTaxAct/Requested_StatusCertificate"),
        E("Statusbescheinigung_Struct", "Steuerbehoerde", enum="Steuerbehoerden",
          name="InvTaxAct/StatusCertificateDetails/Issuer"),
        E("Statusbescheinigung_Struct", "Aktenzeichen", name="InvTaxAct/StatusCertificateDetails/FileNumber"),
        E("Statusbescheinigung_Struct", "GueltigVon", name="InvTaxAct/StatusCertificateDetails/Period/from"),
        E("Statusbescheinigung_Struct", "GueltigBis", name="InvTaxAct/StatusCertificateDetails/Period/to"),
        E("SpezialInvestmentfonds_Struct", "SpezialInvestmentfonds",
          name="InvTaxAct/SpecialInvestmentFunds/Special"),
        E("SpezialInvestmentfonds_Struct", "Transparenzoption",
          name="InvTaxAct/SpecialInvestmentFunds/TransparencyOption"),
        *bevollmaechtigter_fields(),
        *gesetzliche_vertretung_fields(),
        E("ErtragAllg_CType", "SitzNichtDE", name="Residence/NonResidency_DE"),
        E("Geschaeftsleitung_Struct", "GeschaeftsleitungAbw", name="Management/DifferentAddress"),
        *address_block("Management/Address",
                        ["Street", "City", "Country", "HouseNumber", "ApartmentNumber",
                         "Floor", "District", "Region_FederalState", "PostCode",
                         "AdditionalAddressDetails"]),
        E("SteuerlicheBehandlung_CType", "W-IdNr", name="TaxTreatment/W-IdNr"),
        *anspruch_fields(),
        *bank_fields(),
        E("Erklaerungen_CType", "ZusaetzlicheAngaben", name="Affirmations/AdditionalInformation"),
        E("Erklaerungen_CType", "BegruendungArt63AEUV", name="Affirmations/JustificationArt63TFEU"),
        E("Erklaerungen_CType", "AntragPar50c", name="Affirmations/ApplicationPar50c"),
        # Accuracy bug #1 (design spec S8): pass the XSD's own documentation
        # through unmodified. KaFE cannot actually accept section 11 InvStG
        # claims (handbook section 2.1) -- this field only lets a submitter
        # affirm they have NOT separately pursued that path elsewhere. The
        # accuracy note itself belongs in request.bs's own prose (Task 5), not
        # here.
        E("Erklaerungen_CType", "AntragPar11InvStG", name="Affirmations/ApplicationPar11InvStG"),
        *steuerbeguenstigte_zwecke_fields(),
    ]

    return sheets


# --------------------------------------------------------------------------- #
# Legend / notes content (presentation prose; not field-level XSD content)
# --------------------------------------------------------------------------- #
LEGEND_TITLE = "KaFE Withholding-Tax Refund - Excel Template"

LEGEND_ROWS = [
    ("How to read each sheet", ""),
    ("Row 1", "Column name (KaFE's real English field path, as used by the production KaFE pipeline)."),
    ("Row 2", "Plain-English description of what to enter."),
    ("Row 3", "Expected type / format / constraints for the value."),
    ("Row 4", "Whether the field is Required, Optional, or Conditional."),
    ("Row 5+", "Your data. One row per record."),
    ("", ""),
    ("Requiredness legend", ""),
    ("Required", "Must always be filled for this record."),
    ("Optional", "May be left blank."),
    ("Conditional", "Required only in certain cases (see the description in row 2)."),
    ("", ""),
    ("Linking the sheets", ""),
    ("id / creditorId",
     f"'{S_MASTER}' and '{S_JURIDICAL}' each define their own rows with an id column; every "
     "other sheet links back to one of those two rows through its own creditorId column "
     "(matching either sheet's id, depending on whether the creditor is a natural or "
     "juridical person)."),
    ("incomeId",
     f"'{S_INCOME}' defines one row per income (KaFE's own ErtragId, starting at 1 within "
     f"each creditor); '{S_INVESTMENT_CHAIN}' and '{S_TRANSACTION_DATA}' each link back to a "
     "specific income row through both creditorId AND incomeId together, not creditorId alone."),
    ("", ""),
    ("Cardinality (rows per creditorId)", ""),
    (f"{S_MASTER} / {S_JURIDICAL}", "Exactly 1 row per creditor (whichever sheet matches its legal form)."),
    (S_COR, "0..n rows per creditorId; each Income row references at most one via CertificateOfResidenceId."),
    (S_INCOME, "1..n rows per creditorId -- at least one taxed income is required per application."),
    (S_INVESTMENT_CHAIN, "0..n rows per (creditorId, incomeId) pair; sort by SequenceNumber (1 = closest to the debtor)."),
    (S_TRANSACTION_DATA, "0..n rows per (creditorId, incomeId) pair, grouped by DepotNumber; required whenever the income's Par50jEStG block applies."),
    ("", ""),
    ("Enum dropdowns", "Cells backed by a fixed value list provide an in-cell dropdown. Manual values outside the list are rejected."),
]

# --------------------------------------------------------------------------- #
# Per-sheet documentation (significance, cardinality, when to fill)
# --------------------------------------------------------------------------- #
SHEET_INFO: dict[str, dict[str, str]] = {
    S_MASTER: {
        "significance": (
            "One row per creditor who is a natural person: identity, address, German tax "
            "office details, the authorised representative and legal representative (if "
            "any), the legal basis for the refund claim, bank details, the Switzerland "
            "questions, the affirmations, and (if claiming under section 32(6) German "
            "Corporate Tax Act) the tax-privileged-purposes block."
        ),
        "cardinality": "Exactly 1 row per creditor (this sheet defines that creditor's id).",
        "whenToFill": "Always, for every creditor who is a natural person.",
    },
    S_JURIDICAL: {
        "significance": (
            "One row per creditor who is a juridical (non-natural) person: legal form, "
            "incorporation details, LEI/register/stock-exchange details, the option under "
            "section 1a German Corporate Tax Act, investment-fund questions, the "
            "authorised representative and legal representative (if any), the legal basis "
            "for the refund claim, bank details, and the affirmations."
        ),
        "cardinality": "Exactly 1 row per creditor (this sheet defines that creditor's id).",
        "whenToFill": "Always, for every creditor who is a juridical person.",
    },
    S_COR: {
        "significance": (
            "One row per certificate of residence (Ansässigkeitsbescheinigung): issuing "
            "authority, issue date and validity period."
        ),
        "cardinality": "0..n rows per creditorId.",
        "whenToFill": (
            "Whenever an income on the Income sheet references it via "
            "CertificateOfResidenceId."
        ),
    },
    S_INCOME: {
        "significance": (
            "One row per taxed capital income event: type of income, security "
            "identification, the debtor, the amount and date of inflow, the tax "
            "certificate/other-document details, the beneficial-ownership and "
            "residency questions, the indirect-holding and substantial-holding "
            "questions, the remittance-base clause, and (where section 50j German "
            "Income Tax Act applies) the Par50jEStG holding-period / risk / forwarding "
            "/ return-obligation block."
        ),
        "cardinality": "1..n rows per creditorId.",
        "whenToFill": "Always -- every application needs at least one taxed income.",
    },
    S_INVESTMENT_CHAIN: {
        "significance": (
            "The chain of companies through which an indirect holding (MittelbareBeteiligung) "
            "is held: each link's organisation, legal form, ownership percentage, country of "
            "residence, tax number/TIN, and whether it is exclusively asset-managing."
        ),
        "cardinality": "0..n rows per (creditorId, incomeId) pair, ordered by SequenceNumber.",
        "whenToFill": "Only when the corresponding income's IndirectHolding/IndirectHolding = true.",
    },
    S_TRANSACTION_DATA: {
        "significance": (
            "The per-depot transaction ledger required by section 50j German Income Tax "
            "Act: opening/closing balance (repeated per transaction row), each "
            "transaction's direction, business type, share count, trading day and "
            "settlement dates."
        ),
        "cardinality": "0..n rows per (creditorId, incomeId) pair, grouped by DepotNumber.",
        "whenToFill": "Only when the corresponding income's Par50jEStG block applies.",
    },
}
