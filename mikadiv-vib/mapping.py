"""Layer 2: template mapping for the MiKaDiv Third-Party Disclosure module.

This is the only place where the *presentation* of the template lives: which
sheets exist, in what order their columns appear, how the XSD's nested choices
collapse into flat columns, and the handful of presentation-only helper columns
that have no XSD counterpart (they model choices the schema expresses
structurally). Every field's description, type/format string and enumeration is
pulled from the XSD via :class:`xsd_model.XsdModel` - this file only says
*where* each column comes from, never *what it means*.

Fields are 5-tuples, matching the renderer contract:
``(name, description, type_display, requiredness, enum_key)``.
"""

from __future__ import annotations

from engine.xsd_model import XsdModel

# --------------------------------------------------------------------------- #
# Sheet names (no underscores, no TV/TP abbreviations)
# --------------------------------------------------------------------------- #
S_LEGEND = "0 Legend Notes"
S_MASTER = "1 Requests Master"
S_SECURITY = "2 Security Related Information"
S_TV_IND = "3 Tax Voucher Individuals"
S_TV_LEGAL = "4 Tax Voucher Legal Persons"
S_TP_IND = "5 Third Party Individuals"
S_TP_LEGAL = "6 Third Party Legal Persons"
S_CUSTODY = "7 Custody Chain"
S_FIFO = "8 FIFO Trades"
S_RAW = "9 Raw Transactions All"

SHEET_ORDER = [
    S_MASTER, S_SECURITY, S_TV_IND, S_TV_LEGAL, S_TP_IND,
    S_TP_LEGAL, S_CUSTODY, S_FIFO, S_RAW,
]

# Display string for the RequestId link key. The XSD types RequestId as a UUID,
# but the template deliberately treats it as a free identifier used only to join
# the sheets, so this is an intentional, documented deviation from the schema.
LINK_ID = "Text (identifier used to link the sheets; any unique value)"

# --------------------------------------------------------------------------- #
# Presentation-only ("synthetic") column descriptions
# These model XSD choices as flat helper columns; they have no XSD field to
# source wording from, so the text is authored here and flagged as such.
# --------------------------------------------------------------------------- #
DESC_MASTER_REQUESTID = (
    "Identifier for the request, defined by you. Used only as the key that links "
    "every sheet together, so any unique value (e.g. a running number) is fine."
)
DESC_FK_REQUESTID = f"Foreign key. Must match a RequestId in the '{S_MASTER}' sheet."
DESC_RECORDTYPE = (
    "'Request' for a MiKaDiv reporting for income; 'Cancel' to cancel a previously "
    "submitted request (leave the child sheets empty for cancellation rows)."
)
DESC_RAD_MODE = (
    f"Whether receipts/deliveries are declared with FiFo calculation (use the "
    f"'{S_FIFO}' sheet) or without (use the '{S_RAW}' sheet)."
)
DESC_RECEIVER_GROUP = (
    "'Single' for a normal recipient; 'CommunityMember' when this row is one member "
    "of a community of up to 10 persons."
)
DESC_COMMUNITY_ID = (
    "Identifier grouping up to 10 community members into one receiver. Required when "
    "ReceiverGroupType=CommunityMember."
)
DESC_PERSON_TAX_CATEGORY = (
    "'German' or 'NonGerman'. Determines which tax-ID fields apply."
)
DESC_FIFO_DIRECTION = (
    "'Receipt' (purchase / delivery-in / loan / repo) or 'Delivery' (sale / "
    "delivery-out / loan / repo). Up to 1000 rows each per request."
)
DESC_CORP_ACTION_ID = (
    "Depositary receipt only: Corporate Action Identifier of the custodian for the "
    "underlying security."
)

# Meanings for the synthetic enums (no XSD source). XSD-backed enums get their
# meanings from the schema in build_enums().
SYNTHETIC_ENUMS: dict[str, tuple[list[str], dict[str, str]]] = {
    "Boolean": (
        ["true", "false"],
        {"true": "Yes - the condition applies.",
         "false": "No - the condition does not apply."},
    ),
    "RecordType": (
        ["Request", "Cancel"],
        {"Request": "A MiKaDiv reporting-for-income disclosure (a new or corrective submission).",
         "Cancel": "Cancellation of a previously submitted disclosure request; only the master cancellation fields are filled and the child sheets stay empty."},
    ),
    "ReceiptsAndDeliveriesMode": (
        ["FiFo", "All"],
        {"FiFo": "Receipts and deliveries are declared WITH FiFo calculation already applied by the submitter - fill the FIFO Trades sheet.",
         "All": "Receipts and deliveries are declared WITHOUT FiFo (the German paying agent applies FiFo) - fill the Raw Transactions All sheet."},
    ),
    "ReceiverGroupType": (
        ["Single", "CommunityMember"],
        {"Single": "A single tax-certificate receiver (one individual or one legal person).",
         "CommunityMember": "One member of a community of up to 10 persons; all members share the same CommunityGroupId and together form one receiver."},
    ),
    "PersonTaxCategory": (
        ["German", "NonGerman"],
        {"German": "German-identified person: provide German identifiers (IdNr / Wirtschafts-IdNr / Steuernummer).",
         "NonGerman": "Non-German person: provide foreign identifiers (ForeignTaxId, LEI, EUID, or legal form + date of foundation, as applicable)."},
    ),
    "FifoDirection": (
        ["Receipt", "Delivery"],
        {"Receipt": "Receipt trade: purchases, book-entry transfers in (delivery in), securities lending, and repo transactions.",
         "Delivery": "Delivery trade: sales, book-entry transfers out (delivery out), securities lending, and repo transactions."},
    ),
}

# Order of enums in the generated metadata/documentation.
ENUM_ORDER = [
    "Boolean", "RecordType", "RequestedService", "RequestedAttestationType",
    "AccountType", "AccountRelationship", "TypeOfSecurity", "PayoutType",
    "ReceiptsAndDeliveriesMode", "TVRelationship", "TPRelationship",
    "ReceiverGroupType", "PersonTaxCategory", "FifoDirection",
    "FifoTransactionType", "RawTransactionType",
]

# XSD-backed enums: enum_key -> named simple type in the schema.
XSD_NAMED_ENUMS = {
    "RequestedService": "DisclosureRequestedServiceType",
    "RequestedAttestationType": "DisclosureRequestedAttestationType",
    "AccountType": "AccountTypeType",
    "AccountRelationship": "AccountRelationshipType",
    "TypeOfSecurity": "TypeOfSecurityType",
    "PayoutType": "IncomePayoutTypeType",
    "RawTransactionType": "RawTransactionTypeType",
}

# XSD-backed enums defined inline on an element: enum_key -> (type, element).
XSD_INLINE_ENUMS = {
    "TVRelationship": ("TaxCertificateReceiverPersonType", "Relationship"),
    "TPRelationship": ("ThirdPartyPersonType", "Relationship"),
}

# FifoTransactionType is the union of the two directional transaction enums,
# in the order the template presents them.
FIFO_TX_ORDER = ["PO", "SO", "DT", "TL", "TP", "RL", "RP"]
FIFO_TX_SOURCES = ["ReceiptsTransactionType", "DeliveriesTransactionType"]


def build_enums(model: XsdModel) -> tuple[dict[str, list[str]], dict[str, dict[str, str]]]:
    """Assemble ENUMS + ENUM_MEANINGS from the XSD (and synthetic definitions)."""
    values: dict[str, list[str]] = {}
    meanings: dict[str, dict[str, str]] = {}

    for key in ENUM_ORDER:
        if key in SYNTHETIC_ENUMS:
            vals, mean = SYNTHETIC_ENUMS[key]
        elif key in XSD_NAMED_ENUMS:
            vals, mean = model.enum(XSD_NAMED_ENUMS[key])
        elif key in XSD_INLINE_ENUMS:
            type_name, field_name = XSD_INLINE_ENUMS[key]
            vals, mean = model.inline_enum(type_name, field_name)
        elif key == "FifoTransactionType":
            vals, mean = _fifo_transaction_enum(model)
        else:  # pragma: no cover - guarded by ENUM_ORDER
            raise KeyError(f"no source defined for enum {key!r}")
        values[key] = list(vals)
        meanings[key] = dict(mean)

    return values, meanings


def _fifo_transaction_enum(model: XsdModel) -> tuple[list[str], dict[str, str]]:
    merged: dict[str, str] = {}
    for source in FIFO_TX_SOURCES:
        _, source_meanings = model.enum(source)
        for value, meaning in source_meanings.items():
            merged.setdefault(value, meaning)
    meanings = {value: merged.get(value, "") for value in FIFO_TX_ORDER}
    return list(FIFO_TX_ORDER), meanings


def build_sheets(model: XsdModel) -> dict[str, list[tuple]]:
    """Assemble every sheet's ordered field list, pulling wording from the XSD."""

    def resolve(field, req, enum, name):
        requiredness = req if req is not None else ("Required" if field.required else "Optional")
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

    def fk():
        return SYN("RequestId", DESC_FK_REQUESTID, LINK_ID, "Required")

    def address_block():
        order = ["StreetOrPostalCode", "HouseNumber", "HouseNumberAddition",
                 "AddressAddition", "Postcode", "City", "Country"]
        return [E("AddressType", n) for n in order]

    def individual_person_block():
        order = ["Title", "NamePrefix", "FirstName", "LastName", "NameAffix", "DateOfBirth"]
        return [E("IndividualPersonType", n) for n in order]

    def person_tax_category():
        return SYN("PersonTaxCategory", DESC_PERSON_TAX_CATEGORY, "Enum", "Required", "PersonTaxCategory")

    def individual_tax_id_block():
        t = "IndividualPersonTaxIdentificationType"
        return [
            E(t, "CountryOfTaxResidence", "Required"),
            person_tax_category(),
            E(t, "InvestmentMarketTaxId", "Conditional"),
            E(t, "ForeignTaxId", "Conditional"),
        ]

    sheets: dict[str, list[tuple]] = {}

    req = "RequestMiKaDivReportingForIncomeType"
    sheets[S_MASTER] = [
        SYN("RequestId", DESC_MASTER_REQUESTID, LINK_ID, "Required"),
        SYN("RecordType", DESC_RECORDTYPE, "Enum", "Required", "RecordType"),
        A(req, "AccountNumber", "Required"),
        A(req, "ClientReference"),
        A(req, "ClientContactpersonName"),
        A(req, "ClientContactpersonPhone"),
        A(req, "ClientContactpersonEmail"),
        A(req, "RequestedService", "Conditional", "RequestedService"),
        A(req, "RequestedServiceReason"),
        A(req, "RequestedAttestationType", "Optional", "RequestedAttestationType"),
        A(req, "IsCorrectionRequest", "Optional", "Boolean"),
        A(req, "PreviousRequestIdForCorrection"),
        A(req, "ReportSerialNumber"),
        A(req, "TaxCertificatePrintedContactpersonName"),
        A(req, "TaxCertificatePrintedContactpersonPhone"),
        A(req, "TaxCertificatePrintedContactpersonEmail"),
        A(req, "TaxCertificateAlternativeRecipientName"),
        A(req, "TaxCertificateAlternativeRecipientAddress"),
        A(req, "TaxCertificateAlternativeRecipientEmail"),
        A(req, "EventType"),
        A(req, "FundId"),
        A("CancelMiKaDivReportingForIncomeType", "PreviousRequestIdForCancellation", "Conditional"),
        E("AccountOwnersAndRepresentativeType", "SecuritiesAccountNumber", "Conditional"),
        E("AccountOwnersAndRepresentativeType", "AccountType", "Conditional", "AccountType"),
        E("AccountOwnersAndRepresentativeType", "AccountRelationship", "Optional", "AccountRelationship"),
    ]

    ci = "CapitalIncomeType"
    sheets[S_SECURITY] = [
        fk(),
        A(ci, "IncomeIdentifier"),
        A(ci, "CustodianIncomeIdentifier"),
        E(ci, "ISIN", "Required"),
        E(ci, "NameOfSecurity", "Required"),
        E(ci, "TypeOfSecurity", "Optional", "TypeOfSecurity"),
        E(ci, "COAF", "Required"),
        E(ci, "IsDepositaryReceipt", "Required", "Boolean"),
        A(ci, "CorporateActionIdOfUnderlyingSecurity", "Optional", desc=DESC_CORP_ACTION_ID),
        E(ci, "ISINOfUnderlyingSecurity", "Conditional"),
        E(ci, "NameOfUnderlyingSecurity", "Conditional"),
        E(ci, "Recorddate", "Conditional"),
        E(ci, "TotalNumberOfCertificatesIssued", "Optional"),
        E(ci, "TotalNumberOfUnderlyingShares", "Optional"),
        E(ci, "Ratio", "Optional"),
        E(ci, "NumberOfCertificatesHeld", "Conditional"),
        E(ci, "Paydate", "Required"),
        E(ci, "PayoutType", "Required", "PayoutType"),
        E(ci, "CashAccountNumber", "Required"),
        E(ci, "AccountNumberPayingAgentLevel", "Optional"),
        E(ci, "GrossAmount", "Required"),
        E(ci, "NetIncomePayment", "Required"),
        E(ci, "WithholdingTaxAmount", "Required"),
        E(ci, "SurchargesAmount", "Required"),
        E(ci, "WithholdingTaxRate", "Required"),
        E(ci, "SurchargesRate", "Required"),
        E(ci, "Nominal", "Required"),
        E(ci, "NominalMoreThan5DaysPriorExdate", "Required"),
        E(ci, "NominalWithin5DaysPriorExdate", "Required"),
        E(ci, "NominalLinkedToFinancialArrangement", "Required"),
        E(ci, "NominalNotLinkedToFinancialArrangement", "Required"),
        E(ci, "NominalLinkedToSecLending", "Required"),
        E(ci, "NominalLinkedToRepo", "Required"),
        SYN("ReceiptsAndDeliveriesMode", DESC_RAD_MODE, "Enum", "Required", "ReceiptsAndDeliveriesMode"),
        P("ReceiptsAndDeliveriesFiFoType", ["Receipts", "MoreThan1000Available"],
          "Conditional", "Boolean", name="FifoReceiptsMoreThan1000Available"),
        P("ReceiptsAndDeliveriesFiFoType", ["Deliveries", "MoreThan1000Available"],
          "Conditional", "Boolean", name="FifoDeliveriesMoreThan1000Available"),
        E("ReceiptsAndDeliveriesAllType", "OpeningBalance", "Conditional"),
        E("ReceiptsAndDeliveriesAllType", "OpeningBalanceDate", "Conditional"),
    ]

    sheets[S_TV_IND] = [
        fk(),
        E("TaxCertificateReceiverPersonType", "Relationship", "Required", "TVRelationship"),
        SYN("ReceiverGroupType", DESC_RECEIVER_GROUP, "Enum", "Required", "ReceiverGroupType"),
        SYN("CommunityGroupId", DESC_COMMUNITY_ID, "Text (max 45)", "Conditional"),
        A("IndividualPersonType", "PersonIdentifier", "Optional"),
        *individual_person_block(),
        *address_block(),
        *individual_tax_id_block(),
    ]

    tv_legal_tax_id = "TaxCertificateLegalPersonTaxIdentificationType"
    sheets[S_TV_LEGAL] = [
        fk(),
        E("TaxCertificateReceiverPersonType", "Relationship", "Required", "TVRelationship"),
        SYN("ReceiverGroupType", DESC_RECEIVER_GROUP, "Enum", "Required", "ReceiverGroupType"),
        SYN("CommunityGroupId", DESC_COMMUNITY_ID, "Text (max 45)", "Conditional"),
        A("LegalPersonType", "PersonIdentifier", "Optional"),
        E("LegalPersonType", "Name", "Required"),
        *address_block(),
        E(tv_legal_tax_id, "CountryOfTaxResidence", "Required"),
        person_tax_category(),
        E(tv_legal_tax_id, "InvestmentMarketBusinessId", "Conditional"),
        E(tv_legal_tax_id, "InvestmentMarketTaxNumber", "Conditional"),
        E(tv_legal_tax_id, "LEI", "Conditional"),
        E(tv_legal_tax_id, "EUID", "Conditional"),
        E(tv_legal_tax_id, "ForeignTaxId", "Conditional"),
        E(tv_legal_tax_id, "LegalForm", "Conditional"),
        E(tv_legal_tax_id, "DateOfFoundation", "Conditional"),
    ]

    sheets[S_TP_IND] = [
        fk(),
        E("ThirdPartyPersonType", "Relationship", "Required", "TPRelationship"),
        A("IndividualPersonType", "PersonIdentifier", "Optional"),
        *individual_person_block(),
        *address_block(),
        *individual_tax_id_block(),
    ]

    tp_legal_tax_id = "ThirdPartyLegalPersonTaxIdentificationType"
    sheets[S_TP_LEGAL] = [
        fk(),
        E("ThirdPartyPersonType", "Relationship", "Required", "TPRelationship"),
        A("LegalPersonType", "PersonIdentifier", "Optional"),
        E("LegalPersonType", "Name", "Required"),
        *address_block(),
        E(tp_legal_tax_id, "CountryOfTaxResidence", "Required"),
        person_tax_category(),
        E(tp_legal_tax_id, "InvestmentMarketBusinessId", "Conditional"),
        E(tp_legal_tax_id, "InvestmentMarketTaxNumber", "Conditional"),
        E(tp_legal_tax_id, "InvestmentMarketSpecialFundsTaxNumber", "Conditional"),
        E(tp_legal_tax_id, "LEI", "Conditional"),
        E(tp_legal_tax_id, "EUID", "Conditional"),
        E(tp_legal_tax_id, "ForeignTaxId", "Conditional"),
    ]

    cc = "CustodyChainType"
    sheets[S_CUSTODY] = [
        fk(),
        E(cc, "NumberInChain", "Required"),
        E(cc, "NameOfIntermediary", "Required"),
        *address_block(),
        E(cc, "AccountNumber", "Required"),
        E(cc, "AccountType", "Required", "AccountType"),
        E(cc, "NominalInAccount", "Required"),
        E(cc, "BIC", "Optional"),
        E(cc, "CountryOfTaxResidence", "Required"),
        person_tax_category(),
        E(cc, "InvestmentMarketBusinessId", "Conditional"),
        E(cc, "InvestmentMarketTaxNumber", "Conditional"),
        E(cc, "LEI", "Conditional"),
        E(cc, "EUID", "Conditional"),
        E(cc, "ForeignTaxId", "Conditional"),
    ]

    sheets[S_FIFO] = [
        fk(),
        SYN("Direction", DESC_FIFO_DIRECTION, "Enum", "Required", "FifoDirection"),
        E("ReceiptType", "Nominal", "Required"),
        E("ReceiptType", "TradeDate", "Required"),
        E("ReceiptType", "TransactionType", "Required", "FifoTransactionType"),
        E("ReceiptType", "ContractualSettlementDate", "Required"),
        E("ReceiptType", "ActualSettlementDate", "Required"),
        A("ReceiptType", "TransactionReference", "Optional"),
        A("ReceiptType", "TransactionReferencePayingAgent", "Optional"),
    ]

    rt = "RawTransactionType"
    sheets[S_RAW] = [
        fk(),
        E(rt, "Nominal", "Required"),
        E(rt, "TradeDate", "Required"),
        E(rt, "IntraDaySequence", "Required"),
        E(rt, "TransactionType", "Required", "RawTransactionType"),
        E(rt, "ContractualSettlementDate", "Required"),
        E(rt, "ActualSettlementDate", "Required"),
        E(rt, "COAF", "Conditional"),
        A(rt, "TransactionReference", "Optional"),
        A(rt, "TransactionReferencePayingAgent", "Optional"),
    ]

    return sheets


# --------------------------------------------------------------------------- #
# Legend / notes content (presentation prose; not field-level XSD content)
# --------------------------------------------------------------------------- #
LEGEND_TITLE = "MiKaDiv Third-Party Disclosure - Excel Template"

LEGEND_ROWS = [
    ("How to read each sheet", ""),
    ("Row 1", "Technical column name (as defined in ThirdPartyDisclosureRequest.xsd)."),
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
    ("RequestId", f"The key on '{S_MASTER}' and the first column on every other sheet. It is only used to link the sheets, so any unique value works (it does not need to be a UUID). Use the same RequestId to join a request's data across all sheets."),
    ("Request vs Cancel", f"Set RecordType on '{S_MASTER}'. For 'Cancel' rows, fill PreviousRequestIdForCancellation (and optionally ReportSerialNumber) and leave all other sheets empty for that RequestId."),
    ("", ""),
    ("Cardinality (rows per RequestId)", ""),
    (S_SECURITY, "0..1 (required for Request records). Includes the depositary-receipt fields, which are required when IsDepositaryReceipt = true."),
    (f"{S_TV_IND} / {S_TV_LEGAL}", "Tax voucher receivers: up to 2 receivers in total per request (across both sheets)."),
    (f"{S_TP_IND} / {S_TP_LEGAL}", "Third-party owners: up to 5 in total per request (across both sheets)."),
    (S_CUSTODY, "Up to 20 links per request; sort by NumberInChain (1 = closest to the beneficiary)."),
    (S_FIFO, "Up to 1000 Receipt rows and 1000 Delivery rows per request (use when ReceiptsAndDeliveriesMode = FiFo)."),
    (S_RAW, "Unbounded rows per request (use when ReceiptsAndDeliveriesMode = All)."),
    ("", ""),
    ("Community recipients", "A community tax certificate receiver (up to 10 members) is captured by setting ReceiverGroupType = CommunityMember on the tax voucher sheets and giving all members of one community the same CommunityGroupId."),
    ("Enum dropdowns", "Cells backed by a fixed value list provide an in-cell dropdown. Manual values outside the list are rejected."),
]

# --------------------------------------------------------------------------- #
# Per-sheet documentation (significance, cardinality, when to fill)
# --------------------------------------------------------------------------- #
SHEET_INFO: dict[str, dict[str, str]] = {
    S_MASTER: {
        "significance": (
            "The parent record. One row per disclosure, holding administrative and "
            "routing metadata, the record type (new request vs cancellation), the "
            "directly-contracted securities account, the account type and the account "
            "relationship. Every other sheet links back to this one through RequestId."
        ),
        "cardinality": "Exactly 1 row per RequestId (this sheet defines the RequestId).",
        "whenToFill": "Always - every disclosure or cancellation starts here.",
    },
    S_SECURITY: {
        "significance": (
            "The single capital-income event being disclosed: the security (ISIN, name, "
            "type), the corporate-action reference, payment details, the complete tax "
            "breakdown (gross/net, withholding tax, solidarity surcharge and the nominal "
            "quantities per holding category) and which receipts/deliveries mode is used. "
            "It also contains the depositary-receipt block (underlying German security, "
            "record date, issuance ratios, certificates held), which describes the "
            "depositary receipt (e.g. ADR/GDR) through which the income was received."
        ),
        "cardinality": "0..1 row per RequestId.",
        "whenToFill": (
            "Required when RecordType = Request. Leave empty for RecordType = Cancel. "
            "Within this sheet, the depositary-receipt fields are required only when "
            "IsDepositaryReceipt = true."
        ),
    },
    S_TV_IND: {
        "significance": (
            "Natural persons who receive the tax certificate (voucher) - either as "
            "beneficial owner (Creditor) or as account holder - with their name, "
            "registration address and tax identification. Community members are recorded "
            "here as well."
        ),
        "cardinality": (
            "Tax-voucher receivers total up to 2 per RequestId, counted across this sheet "
            f"and '{S_TV_LEGAL}'. A community counts as ONE receiver and may span up to 10 "
            "member rows that share one CommunityGroupId."
        ),
        "whenToFill": (
            "For Request records at least one tax-voucher receiver is required (here or on "
            "the legal-persons sheet). Add one row per natural-person receiver or community "
            "member."
        ),
    },
    S_TV_LEGAL: {
        "significance": (
            "Non-natural tax-certificate receivers (companies, funds, partnerships) with "
            "name, registration address and the detailed legal-person tax identification."
        ),
        "cardinality": (
            "Counts towards the up-to-2 tax-voucher receivers per RequestId (shared with "
            f"'{S_TV_IND}')."
        ),
        "whenToFill": (
            "For Request records, use when a tax-voucher receiver (or community member) is "
            "a legal person."
        ),
    },
    S_TP_IND: {
        "significance": (
            "Natural persons who are the account holder but not the beneficial owner "
            "(third parties), stating in what capacity they hold for the beneficial owner "
            "(trustee, pledgor or grantor of usufruct)."
        ),
        "cardinality": (
            "Third-party persons total up to 5 per RequestId, counted across this sheet and "
            f"'{S_TP_LEGAL}'."
        ),
        "whenToFill": (
            "Only when the account holder is not the beneficial owner AND the beneficial "
            "owner is disclosed. Otherwise leave empty."
        ),
    },
    S_TP_LEGAL: {
        "significance": (
            "Non-natural third parties (account holders that are not the beneficial owner) "
            "with name, address and legal-person tax identification, including the special "
            "investment-funds tax number where relevant."
        ),
        "cardinality": (
            "Counts towards the up-to-5 third-party persons per RequestId (shared with "
            f"'{S_TP_IND}')."
        ),
        "whenToFill": (
            f"Same condition as '{S_TP_IND}', when the third party is a legal person."
        ),
    },
    S_CUSTODY: {
        "significance": (
            "The ordered chain of custodians / intermediaries between the beneficiary and "
            "the German paying agent. Each link carries its name, address, tax "
            "identification, BIC, account number, account type and the nominal held."
        ),
        "cardinality": (
            "0..20 rows per RequestId, ordered by NumberInChain (1 = the custodian closest "
            "to the beneficiary)."
        ),
        "whenToFill": (
            "Required for Request records; add one row per intermediary link in the custody "
            "chain."
        ),
    },
    S_FIFO: {
        "significance": (
            "Receipts and deliveries within the relevant window, already reduced with FiFo "
            "(first-in-first-out) calculation by the submitter. Receipts and deliveries "
            "share this sheet and are distinguished by the Direction column."
        ),
        "cardinality": (
            "Up to 1000 Receipt rows and up to 1000 Delivery rows per RequestId."
        ),
        "whenToFill": (
            "Only when ReceiptsAndDeliveriesMode = FiFo. Leave empty when the mode = All."
        ),
    },
    S_RAW: {
        "significance": (
            "The full, unreduced ledger of receipts and deliveries (no FiFo applied); the "
            "German paying agent performs the FiFo calculation. The opening balance is "
            "captured on the Security Related Information sheet; every movement is one row "
            "here."
        ),
        "cardinality": "Unbounded rows per RequestId.",
        "whenToFill": (
            "Only when ReceiptsAndDeliveriesMode = All. Leave empty when the mode = FiFo."
        ),
    },
}
