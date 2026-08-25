# KaFE Withholding-Tax Refund - Excel Template - Documentation

Auto-generated from [`template_metadata.json`](template_metadata.json) (source schema: `kafe.xsd`). Do not edit by hand - re-run the generator to refresh.

## Overview

This workbook captures MiKaDiv (§45b) third-party disclosures for German capital income. Each disclosure is spread across several sheets that are all tied together by a single key, **creditorId**. One disclosure = one RequestId, reused on every sheet that carries data for that disclosure.

### How to read each sheet

Every data sheet has four header rows; data entry begins on row 5.

| Row | Meaning |
| --- | --- |
| 1 | Technical column name |
| 2 | English description |
| 3 | Expected type / format / constraints |
| 4 | Required / Optional / Conditional |

### Requiredness legend

| Value | Meaning |
| --- | --- |
| Required | Must always be filled for this record. |
| Optional | May be left blank. |
| Conditional | Required only in certain cases - see the field description. |

### Linking model

- **creditorId** is the key on `3 Certificates Of Residence` and the first column on every other sheet, used to join a request's data across all sheets. Per VIB's own schema, RequestId must stay unique even across files you submit later, not just within this one -- corrections and cancellations you submit afterward reference it by exact value.
- **Community recipients:** capture a community tax-voucher receiver (up to 10 members) by setting `ReceiverGroupType = CommunityMember` on the tax voucher sheets and giving all members of one community the same `CommunityGroupId`.

## Sheets at a glance

| Sheet | Fields | Cardinality (rows per RequestId) | When to fill |
| --- | --- | --- | --- |
| [3 Certificates Of Residence](#3-certificates-of-residence) | 6 | 0..n rows per creditorId. | Whenever an income on the Income sheet references it via CertificateOfResidenceId. |
| [4 Income](#4-income) | 46 | 1..n rows per creditorId. | Always -- every application needs at least one taxed income. |
| [5 Investment Chain](#5-investment-chain) | 10 | 0..n rows per (creditorId, incomeId) pair, ordered by SequenceNumber. | Only when the corresponding income's IndirectHolding/IndirectHolding = true. |
| [6 Transaction Data](#6-transaction-data) | 14 | 0..n rows per (creditorId, incomeId) pair, grouped by DepotNumber. | Only when the corresponding income's Par50jEStG block applies. |
| [1 Creditors Natural](#1-creditors-natural) | 114 | Exactly 1 row per creditor (this sheet defines that creditor's id). | Always, for every creditor who is a natural person. |
| [2 Creditors Juridical](#2-creditors-juridical) | 131 | Exactly 1 row per creditor (this sheet defines that creditor's id). | Always, for every creditor who is a juridical person. |

## Detailed sheet reference

### 3 Certificates Of Residence

**Significance.** One row per certificate of residence (Ansässigkeitsbescheinigung): issuing authority, issue date and validity period.

**Cardinality.** 0..n rows per creditorId.

**When to fill.** Whenever an income on the Income sheet references it via CertificateOfResidenceId.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `creditorId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match an id value on the '1 Creditors Natural' or '2 Creditors Juridical' sheet (whichever this creditor is a natural or juridical person). |
| 2 | `id` | Required | Text (identifier used to link the sheets; any unique value) | Identifier for this certificate of residence, defined by you. Referenced by the CertificateOfResidenceId column on the Income sheet. |
| 3 | `Issuer` | Required | Text (max 80) | Issuing authority |
| 4 | `IssuedAt` | Required | Date (YYYY-MM-DD) | Date of issue |
| 5 | `ValidFrom` | Required | Date (YYYY-MM-DD) | Valid from |
| 6 | `ValidUntil` | Required | Date (YYYY-MM-DD) | Valid until |

### 4 Income

**Significance.** One row per taxed capital income event: type of income, security identification, the debtor, the amount and date of inflow, the tax certificate/other-document details, the beneficial-ownership and residency questions, the indirect-holding and substantial-holding questions, the remittance-base clause, and (where section 50j German Income Tax Act applies) the Par50jEStG holding-period / risk / forwarding / return-obligation block.

**Cardinality.** 1..n rows per creditorId.

**When to fill.** Always -- every application needs at least one taxed income.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `creditorId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match an id value on the '1 Creditors Natural' or '2 Creditors Juridical' sheet (whichever this creditor is a natural or juridical person). |
| 2 | `incomeId` | Required | Integer | Sequence number of the income, starting with 1 (KaFE's own ErtragId). Also serves, together with creditorId, as the linking key referenced by the '5 Investment Chain' and '6 Transaction Data' sheets. |
| 3 | `CertificateOfResidenceId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match an id value on the '3 Certificates Of Residence' sheet -- identifies which certificate of residence supports this income. |
| 4 | `CapitalIncome` | Required | Enum [`KapitalertragArt`](#kapitalertragart): `DIVIDENDEN`, `AUSSCH_KAPG`, `GENUSSR_ML`, `GENUSSR_OL`, `WANDELANL`, `LEBENSVERS`, `EINN_STILLG`, `PART_DARL`, `GEWINNOBL`, `GRENZKW`, `SONSTIGE` | Type of capital income |
| 5 | `Stocks_ConvertibleBonds/ISIN` | Optional | ISIN (12-digit) | ISIN (12-digit) |
| 6 | `Stocks_ConvertibleBonds/NumberOfShares` | Optional | Decimal (None digits total, 4 decimals) | Number of shares/bonds |
| 7 | `SubstantialHolding/IsSubstantial` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Is it a substential holding (at least 10 %)? |
| 8 | `SubstantialHolding/Ownership` | Optional | Decimal (None digits total, 4 decimals) | Size of the ownership interest (in %) |
| 9 | `SubstantialHolding/HoldingPeriod18M` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Has the investment been held for a period of at least 18 months? |
| 10 | `SubstantialHolding/HoldingPeriod12M` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Has the investment been held for a period of at least one year? |
| 11 | `SubstantialHolding/HoldingPeriod6M` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Has the investment been held for a period of at least 6 months? |
| 12 | `IndirectHolding/IndirectHolding` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is it a joint deposit/account or another form of indirect holding? |
| 13 | `IndirectHolding/CompanyOfSpouses` | Optional | Enum [`Boolean`](#boolean): `true`, `false` |  |
| 14 | `IndirectHolding/SizeOfIndirectHolding` | Required | Decimal (None digits total, 4 decimals) | Size of the indirect holding (in %) |
| 15 | `Debtor/Name` | Required | Text (max 256) | Debtor of the capital income / distributing company |
| 16 | `Debtor/TaxNumber` | Optional | Text (max 13) | Tax number |
| 17 | `NonResidency_DE` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability a resident of the specified country of residence at the time of
						the inflow and did not have its registered office or place of management in Germany at that time? |
| 18 | `DateOfReceiptOfCapitalIncome` | Required | Date (YYYY-MM-DD) | Date of receipt of capital income |
| 19 | `GrossIncomeFromCapitalReceived` | Required | Decimal (None digits total, 2 decimals) | Gross income from capital received (in Euro) |
| 20 | `Withheld_Taxes` | Required | Decimal (None digits total, 2 decimals) | Withheld German capital income tax (in Euro) |
| 21 | `Requested_Refund` | Optional | Decimal | The refund amount being claimed for this income (informational; BZSt itself computes the actual refund from the withheld tax and the applicable treaty/statutory rate -- this is not a real KaFE XSD field). |
| 22 | `DocumentDescription` | Required | Text (max 120) | Short description of the file content (e.g. certificate of residence). |
| 23 | `DocumentProof/TaxCertificateNumber` | Optional | UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) | Serial number |
| 24 | `Hidden_ProfitDistribution/ConstructiveDividend` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Does it concern a constructive dividend? |
| 25 | `Economic_Ownership/Ownership_and_Right_To_Use` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Did the person with limited tax liability hold the beneficial ownership (right to use the income) at the
						time of the inflow? |
| 26 | `TaxExemption` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability fully (or partially) exempt from tax in the specified country of
						residence at the time of the inflow? |
| 27 | `LifeInsurancePolicyNumber` | Optional | Text (max 40) | Policy number of the life insurance |
| 28 | `Depositary_Receipts/Is_DR` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Are they depositary receipts? e.g. American Depositary Receipts (ADR). |
| 29 | `Depositary_Receipts/ISIN_DR` | Optional | ISIN (12-digit) | ISIN of the underlying (12-digit) |
| 30 | `RemittanceBase/IsSubject` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Werden die Erträge im angegebenen Ansässigkeitsstaat nur dann der Besteuerung unterworfen, wenn sie dorthin
						überwiesen oder dort bezogen worden sind (Überweisungsklausel)? |
| 31 | `RemittanceBase/Amount` | Optional | Decimal (None digits total, 2 decimals) | Betrag, der in den Ansässigkeitsstaat überwiesen oder dort bezogen wurde. |
| 32 | `Business_Establishment/Business_Establishment_DE` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Has the capital income distributed to a permanent establishment / fixed entity located in Germany of the
						person subject to limited taxation? |
| 33 | `UnlimitedForeignCorporateTaxLiability` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability subject to unlimited corporate
						income tax liability or a comparable tax liability in their country of residence without any option to choose? |
| 34 | `CreditAmount` | Optional | Decimal (None digits total, 2 decimals) | To what extent was the German capital gains tax credited in full or in
						part against taxation in the country of residence or deducted from the tax base, or is it possible
						to carry this forward to future tax periods (tax credit carryforward)? |
| 35 | `Questions_for_50j/HoldingPeriod/HoldingMore45D` | Conditional | Decimal (None digits total, 4 decimals) | Anzahl der Anteile, die innerhalb des Mindesthaltezeitraums an mindestens 45 Tagen ohne Unterbrechung
						gehalten wurden (§ 50j Absatz 4 Satz 2 EStG). |
| 36 | `Questions_for_50j/HoldingPeriod/HoldingMore1Y` | Conditional | Decimal (None digits total, 4 decimals) | Davon Anzahl der Anteile, die im Zeitpunkt des Zuflusses mindestens ein Jahr ohne Unterbrechung gehalten
						wurden (§ 50j Absatz 4 Satz 2 EStG). |
| 37 | `Questions_for_50j/HoldingPeriod/HoldingLess45D` | Conditional | Decimal (None digits total, 4 decimals) | Anzahl der Anteile, die kürzer 45 Tage gehalten wurden. |
| 38 | `Questions_for_50j/HoldingPeriod/SharesPar50jEStG` | Conditional | Decimal (None digits total, 4 decimals) | Anzahl der Anteile im Sinne des § 50j EStG. |
| 39 | `Questions_for_50j/MinValueChangeRisk/OpposingClaims` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Hatte die beschränkt steuerpflichtige Person oder eine ihr nahestehende Person während der Mindesthaltedauer
						gegenläufige Ansprüche? |
| 40 | `Questions_for_50j/MinValueChangeRisk/RiskMin70` | Conditional | Decimal (None digits total, 4 decimals) | Anzahl der Anteile, für die die beschränkt steuerpflichtige Person das Wertänderungsrisiko während der
						Mindesthaltedauer zu mindestens 70% getragen hat. (Bezogen auf die Anteile im Sinne des § 50j EStG) |
| 41 | `Questions_for_50j/MinValueChangeRisk/OtherOpposingClaims` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Waren während der Mindesthaltedauer gegenläufige Ansprüche vorhanden, die nicht vollständig den Anteilen im
						Sinne des § 50j EStG (Haltedauer mindestens 45 Tage, jedoch kürzer als 1 Jahr) zugeordnet waren? (Die Frage bezieht sich auf den
						gesamten Bestand der Anteils- oder Genussscheingattung.) |
| 42 | `Questions_for_50j/ForwardingObligation/ForwardingObligation` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Lag eine Verpflichtung zur unmittelbaren oder mittelbaren Weiterleitung der Kapitalerträge vor? |
| 43 | `Questions_for_50j/ForwardingObligation/NumberOfShares` | Conditional | Decimal (None digits total, 4 decimals) | Anzahl der Anteile, für die eine Verpflichtung zur unmittelbaren oder mittelbaren Weiterleitung der
						Kapitalerträge vorlag. (Bezogen auf die Anteile im Sinne des § 50j EStG) |
| 44 | `Questions_for_50j/ForwardingObligation/FurtherForwardingObligation` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Lag eine Verpflichtung zur unmittelbaren oder mittelbaren Weiterleitung der Kapitalerträge vor, die über die
						Anteile im Sinne des § 50j EStG (Haltedauer mindestens 45 Tage, jedoch kürzer als 1 Jahr) hinausgeht? (Bezogen auf den gesamten Bestand
						der Anteils- oder Genussscheingattung.) |
| 45 | `Questions_for_50j/ReturnObligation/ReturnObligation` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Lagen Rückgabeverpflichtungen ohne Dividendenberechtigung für mit Dividendenberechtigung erworbene Anteile
						vor? (Bezogen auf den gesamten Bestand der Anteils- oder Genussscheingattung.) |
| 46 | `Questions_for_50j/ReturnObligation/NumberOfShares` | Conditional | Decimal (None digits total, 4 decimals) | Anzahl der Anteile, für die eine Rückgabeverpflichtung ohne Dividendenberechtigung für mit
						Dividendenberechtigung erworbene Anteile vorlag. |

### 5 Investment Chain

**Significance.** The chain of companies through which an indirect holding (MittelbareBeteiligung) is held: each link's organisation, legal form, ownership percentage, country of residence, tax number/TIN, and whether it is exclusively asset-managing.

**Cardinality.** 0..n rows per (creditorId, incomeId) pair, ordered by SequenceNumber.

**When to fill.** Only when the corresponding income's IndirectHolding/IndirectHolding = true.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `creditorId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match an id value on the '1 Creditors Natural' or '2 Creditors Juridical' sheet (whichever this creditor is a natural or juridical person). |
| 2 | `incomeId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match an incomeId value on the '4 Income' sheet for this creditorId. |
| 3 | `SequenceNumber` | Required | Integer | Sequence number of the holding. From the person subject of limited taxation to the debtor oft he capital income
					/ distributing company, starting at 1. |
| 4 | `OrganizationName` | Required | Text (max 256) | Company name |
| 5 | `LegalForm` | Required | Text (max 80) | Legal form |
| 6 | `Ownership` | Required | Decimal (None digits total, 4 decimals) | Size of the ownership in interest (in %) |
| 7 | `Country` | Optional | Enum [`CountryISOAlpha2`](#countryisoalpha2): `AD`, `AE`, `AF`, `AG`, `AI`, `AL`, `AM`, `AO`, `AQ`, `AR`, `AS`, `AT`, `AU`, `AW`, `AX`, `AZ`, `BA`, `BB`, `BD`, `BE`, `BF`, `BG`, `BH`, `BI`, `BJ`, `BL`, `BM`, `BN`, `BO`, `BQ`, `BR`, `BS`, `BT`, `BV`, `BW`, `BY`, `BZ`, `CA`, `CC`, `CD`, `CF`, `CG`, `CH`, `CI`, `CK`, `CL`, `CM`, `CN`, `CO`, `CP`, `CR`, `CU`, `CV`, `CW`, `CX`, `CY`, `CZ`, `DE`, `DJ`, `DK`, `DM`, `DO`, `DZ`, `EC`, `EE`, `EG`, `EH`, `ER`, `ES`, `ET`, `FI`, `FJ`, `FK`, `FM`, `FO`, `FR`, `GA`, `GB`, `GD`, `GE`, `GF`, `GG`, `GH`, `GI`, `GL`, `GM`, `GN`, `GP`, `GQ`, `GR`, `GS`, `GT`, `GU`, `GW`, `GY`, `HK`, `HM`, `HN`, `HR`, `HT`, `HU`, `ID`, `IE`, `IL`, `IM`, `IN`, `IO`, `IQ`, `IR`, `IS`, `IT`, `JE`, `JM`, `JO`, `JP`, `KE`, `KG`, `KH`, `KI`, `KM`, `KN`, `KP`, `KR`, `KW`, `KY`, `KZ`, `LA`, `LB`, `LC`, `LI`, `LK`, `LR`, `LS`, `LT`, `LU`, `LV`, `LY`, `MA`, `MC`, `MD`, `ME`, `MF`, `MG`, `MH`, `MK`, `ML`, `MM`, `MN`, `MO`, `MP`, `MQ`, `MR`, `MS`, `MT`, `MU`, `MV`, `MW`, `MX`, `MY`, `MZ`, `NA`, `NC`, `NE`, `NF`, `NG`, `NI`, `NL`, `NO`, `NP`, `NR`, `NU`, `NZ`, `OM`, `PA`, `PE`, `PF`, `PG`, `PH`, `PK`, `PL`, `PM`, `PN`, `PR`, `PS`, `PT`, `PW`, `PY`, `QA`, `RE`, `RO`, `RS`, `RU`, `RW`, `SA`, `SB`, `SC`, `SD`, `SE`, `SG`, `SH`, `SI`, `SJ`, `SK`, `SL`, `SM`, `SN`, `SO`, `SR`, `SS`, `ST`, `SV`, `SX`, `SY`, `SZ`, `TC`, `TD`, `TF`, `TG`, `TH`, `TJ`, `TK`, `TL`, `TM`, `TN`, `TO`, `TR`, `TT`, `TV`, `TW`, `TZ`, `UA`, `UG`, `UM`, `US`, `UY`, `UZ`, `VA`, `VC`, `VE`, `VG`, `VI`, `VN`, `VU`, `WF`, `WS`, `XK`, `YE`, `YT`, `ZA`, `ZM`, `ZW` | Country of residence |
| 8 | `GermanTaxNumber` | Optional | Text (max 13) | Tax number |
| 9 | `TIN` | Optional | Text (max 40) | Foreign tax identification number |
| 10 | `AssetManagement` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the company exclusively engaged in asset management? |

### 6 Transaction Data

**Significance.** The per-depot transaction ledger required by section 50j German Income Tax Act: opening/closing balance (repeated per transaction row), each transaction's direction, business type, share count, trading day and settlement dates.

**Cardinality.** 0..n rows per (creditorId, incomeId) pair, grouped by DepotNumber.

**When to fill.** Only when the corresponding income's Par50jEStG block applies.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `creditorId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match an id value on the '1 Creditors Natural' or '2 Creditors Juridical' sheet (whichever this creditor is a natural or juridical person). |
| 2 | `incomeId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match an incomeId value on the '4 Income' sheet for this creditorId. |
| 3 | `TransactionNumber` | Required | Integer | Sequence number of the transaction, starting with 1 |
| 4 | `DepotNumber` | Required | Text (max 40) | Account / deposit number |
| 5 | `Depot/OpeningBalance` | Required | Decimal (None digits total, 4 decimals) | Opening balance (number of shares) |
| 6 | `Depot/DateOfOpeningBalance` | Required | Date (YYYY-MM-DD) | Date of the specified opening balance |
| 7 | `Depot/ClosingBalance` | Required | Decimal (None digits total, 4 decimals) | Closing balance two months after the inflow date (number of shares) |
| 8 | `Depot/DateOfClosingBalance` | Required | Date (YYYY-MM-DD) | Date of the specified closing balance |
| 9 | `TransactionDirection` | Required | Enum [`TransaktionArt`](#transaktionart): `ZUGANG`, `ABGANG` | Inflow / Outflow |
| 10 | `TradingDay` | Required | Date (YYYY-MM-DD) | Trading day |
| 11 | `TransactionType` | Required | Enum [`TransaktionGeschaeft`](#transaktiongeschaeft): `PO`, `SO`, `TL`, `RL`, `TP`, `RP` | Transaction |
| 12 | `NumberOfShares` | Required | Decimal (None digits total, 4 decimals) | Number of shares |
| 13 | `AgreedSettlementDate` | Required | Date (YYYY-MM-DD) | Agreed settlement date |
| 14 | `ActualSettlementDate` | Required | Date (YYYY-MM-DD) | Actual settlement date |

### 1 Creditors Natural

**Significance.** One row per creditor who is a natural person: identity, address, German tax office details, the authorised representative and legal representative (if any), the legal basis for the refund claim, bank details, the Switzerland questions, the affirmations, and (if claiming under section 32(6) German Corporate Tax Act) the tax-privileged-purposes block.

**Cardinality.** Exactly 1 row per creditor (this sheet defines that creditor's id).

**When to fill.** Always, for every creditor who is a natural person.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `id` | Required | Text (identifier used to link the sheets; any unique value) | Identifier for this creditor, defined by you. Referenced by the creditorId column on every other sheet. |
| 2 | `generalData/Country` | Optional | Enum [`CountryISOAlpha2`](#countryisoalpha2): `AD`, `AE`, `AF`, `AG`, `AI`, `AL`, `AM`, `AO`, `AQ`, `AR`, `AS`, `AT`, `AU`, `AW`, `AX`, `AZ`, `BA`, `BB`, `BD`, `BE`, `BF`, `BG`, `BH`, `BI`, `BJ`, `BL`, `BM`, `BN`, `BO`, `BQ`, `BR`, `BS`, `BT`, `BV`, `BW`, `BY`, `BZ`, `CA`, `CC`, `CD`, `CF`, `CG`, `CH`, `CI`, `CK`, `CL`, `CM`, `CN`, `CO`, `CP`, `CR`, `CU`, `CV`, `CW`, `CX`, `CY`, `CZ`, `DE`, `DJ`, `DK`, `DM`, `DO`, `DZ`, `EC`, `EE`, `EG`, `EH`, `ER`, `ES`, `ET`, `FI`, `FJ`, `FK`, `FM`, `FO`, `FR`, `GA`, `GB`, `GD`, `GE`, `GF`, `GG`, `GH`, `GI`, `GL`, `GM`, `GN`, `GP`, `GQ`, `GR`, `GS`, `GT`, `GU`, `GW`, `GY`, `HK`, `HM`, `HN`, `HR`, `HT`, `HU`, `ID`, `IE`, `IL`, `IM`, `IN`, `IO`, `IQ`, `IR`, `IS`, `IT`, `JE`, `JM`, `JO`, `JP`, `KE`, `KG`, `KH`, `KI`, `KM`, `KN`, `KP`, `KR`, `KW`, `KY`, `KZ`, `LA`, `LB`, `LC`, `LI`, `LK`, `LR`, `LS`, `LT`, `LU`, `LV`, `LY`, `MA`, `MC`, `MD`, `ME`, `MF`, `MG`, `MH`, `MK`, `ML`, `MM`, `MN`, `MO`, `MP`, `MQ`, `MR`, `MS`, `MT`, `MU`, `MV`, `MW`, `MX`, `MY`, `MZ`, `NA`, `NC`, `NE`, `NF`, `NG`, `NI`, `NL`, `NO`, `NP`, `NR`, `NU`, `NZ`, `OM`, `PA`, `PE`, `PF`, `PG`, `PH`, `PK`, `PL`, `PM`, `PN`, `PR`, `PS`, `PT`, `PW`, `PY`, `QA`, `RE`, `RO`, `RS`, `RU`, `RW`, `SA`, `SB`, `SC`, `SD`, `SE`, `SG`, `SH`, `SI`, `SJ`, `SK`, `SL`, `SM`, `SN`, `SO`, `SR`, `SS`, `ST`, `SV`, `SX`, `SY`, `SZ`, `TC`, `TD`, `TF`, `TG`, `TH`, `TJ`, `TK`, `TL`, `TM`, `TN`, `TO`, `TR`, `TT`, `TV`, `TW`, `TZ`, `UA`, `UG`, `UM`, `US`, `UY`, `UZ`, `VA`, `VC`, `VE`, `VG`, `VI`, `VN`, `VU`, `WF`, `WS`, `XK`, `YE`, `YT`, `ZA`, `ZM`, `ZW` | Country of residence |
| 3 | `CreditorNat/General_Data/WithholdingTaxNumber` | Optional | Numeric string (8-digit BZSt withholding-tax number) | Withholding tax number for refund |
| 4 | `CreditorNat/General_Data/FormOfAddress` | Required | Enum [`Anrede`](#anrede): `FRAU`, `HERR`, `KEINE_ANREDE` | Form of address |
| 5 | `CreditorNat/General_Data/FormOfTitle` | Optional | Text (max 40) | Title |
| 6 | `CreditorNat/General_Data/Name` | Required | Text (max 120) | Last name |
| 7 | `CreditorNat/General_Data/GivenName` | Required | Text (max 80) | First and middle name |
| 8 | `CreditorNat/General_Data/Birthday` | Required | Date (YYYY-MM-DD) | Date of birth |
| 9 | `CreditorNat/General_Data/NationalityIsDE` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability have German citizenship? |
| 10 | `CreditorNat/General_Data/NationalityIsKW` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability have Kuwaiti citizenship? |
| 11 | `CreditorNat/General_Data/NationalityIsCH` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability have Swiss citizenship? |
| 12 | `CreditorNat/General_Data/TinAvailable` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability have a foreign tax identification number? |
| 13 | `CreditorNat/General_Data/IDNumber_CountryOfResidence` | Optional | Text (max 40) | Foreign tax identification number |
| 14 | `CreditorNat/Address/Street` | Required | Text (max 120) | Street |
| 15 | `CreditorNat/Address/Floor` | Optional | Text (max 40) | Floor |
| 16 | `CreditorNat/Address/Apartment` | Optional | Text (max 40) | Apartment number |
| 17 | `CreditorNat/Address/StreetNumber` | Optional | Text (max 20) | Street number |
| 18 | `CreditorNat/Address/AdditionalAddressDetails` | Optional | Text (max 80) | Additional address details |
| 19 | `CreditorNat/Address/District` | Optional | Text (max 80) | District |
| 20 | `CreditorNat/Address/Postcode` | Optional | Text (max 20) | Postcode |
| 21 | `CreditorNat/Address/City` | Required | Text (max 120) | City |
| 22 | `CreditorNat/Address/Region_FederalState` | Optional | Text (max 120) | State or province |
| 23 | `CreditorNat/Address/Country` | Required | Text | Country |
| 24 | `CreditorNat/ContactPerson/FirstName` | Required | Text (max 80) | First and middle name |
| 25 | `CreditorNat/ContactPerson/Name` | Required | Text (max 120) | Last name |
| 26 | `CreditorNat/ContactPerson/Organization` | Optional | Text (max 256) | Organisation |
| 27 | `CreditorNat/ContactPerson/Email` | Optional | Text (max 254) | E-mail address |
| 28 | `CreditorNat/ContactPerson/PhoneNumber` | Optional | Text (max 21) | Telephone number (area code/phone number) |
| 29 | `CreditorNat/German_TaxOffice/German_TaxOffice` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability registered with a German tax office? |
| 30 | `CreditorNat/German_TaxOffice/TaxNumber` | Optional | Text (max 13) | Tax number (13 digits) |
| 31 | `CreditorNat/German_TaxOffice/TaxLiabilityGermany` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability subject to unlimited income tax liability and did this tax
						liability end in the year the tax was due or during the ten calendar years preceding the most recent inflow indicated in the
						application? |
| 32 | `CreditorNat/German_TaxOffice/TaxLiabilityGermany5Years` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability subject to unlimited tax liability in Germany for at least five
						years during the ten years preceding the end of the unlimited tax liability? |
| 33 | `CreditorNat/German_TaxOffice/LiabilityEnded` | Optional | Text | In which calendar year did the unlimited tax liability end? |
| 34 | `AuthorizedRep/General_Data/LegalForm` | Optional | Enum [`PersonChoice`](#personchoice): `NatuerlichePerson`, `NichtNatuerlichePerson` | Which block below is filled in for this representative: a natural person or a non-natural person (organisation). |
| 35 | `AuthorizedRep/Authority/TaxProfessions` | Required | Enum [`Boolean`](#boolean): `true`, `false` | I confirm that I am a member of the tax advisory professions within the meaning of sections 3 or 4 number 11
						German Tax Advisory Act. |
| 36 | `AuthorizedRep/Authority/OtherReasons` | Required | Enum [`Boolean`](#boolean): `true`, `false` | I confirm that I am authorised to provide assistance in tax matters for other reasons. |
| 37 | `AuthorizedRep/NaturalPerson/General_Data/FormOfAddress` | Required | Enum [`Anrede`](#anrede): `FRAU`, `HERR`, `KEINE_ANREDE` | Form of address |
| 38 | `AuthorizedRep/NaturalPerson/General_Data/Title` | Optional | Text (max 40) | Title |
| 39 | `AuthorizedRep/NaturalPerson/General_Data/FirstName` | Required | Text (max 80) | First and middle name |
| 40 | `AuthorizedRep/NaturalPerson/General_Data/LastName` | Required | Text (max 120) | Last name |
| 41 | `AuthorizedRep/NonNaturalPerson/General_Data/Name` | Required | Text (max 256) | Legal name |
| 42 | `AuthorizedRep/NonNaturalPerson/General_Data/Department` | Optional | Text (max 80) | Department |
| 43 | `AuthorizedRep/Address/Street` | Required | Text (max 120) | Street |
| 44 | `AuthorizedRep/Address/StreetNumber` | Optional | Text (max 20) | Street number |
| 45 | `AuthorizedRep/Address/AdditionalAddressDetails` | Optional | Text (max 80) | Additional address details |
| 46 | `AuthorizedRep/Address/District` | Optional | Text (max 80) | District |
| 47 | `AuthorizedRep/Address/Postcode` | Optional | Text (max 20) | Postcode |
| 48 | `AuthorizedRep/Address/City` | Required | Text (max 120) | City |
| 49 | `AuthorizedRep/Address/Region_FederalState` | Optional | Text (max 120) | State or province |
| 50 | `AuthorizedRep/Address/Country` | Required | Text | Country |
| 51 | `AuthorizedRep/Address/Apartment` | Optional | Text (max 40) | Apartment number |
| 52 | `AuthorizedRep/Address/Floor` | Optional | Text (max 40) | Floor |
| 53 | `LegalRep/LegalForm` | Optional | Enum [`PersonChoice`](#personchoice): `NatuerlichePerson`, `NichtNatuerlichePerson` | Which block below is filled in for this representative: a natural person or a non-natural person (organisation). |
| 54 | `LegalRep/NatPerson/FormOfAddress` | Required | Enum [`Anrede`](#anrede): `FRAU`, `HERR`, `KEINE_ANREDE` | Form of address |
| 55 | `LegalRep/NatPerson/Title` | Optional | Text (max 40) | Title |
| 56 | `LegalRep/NatPerson/FirstName` | Required | Text (max 80) | First and middle name |
| 57 | `LegalRep/NatPerson/LastName` | Required | Text (max 120) | Last name |
| 58 | `LegalRep/JurPerson/OrganisationName` | Required | Text (max 256) | Legal name |
| 59 | `LegalRep/JurPerson/OrganisationDepartment` | Optional | Text (max 80) | Department |
| 60 | `LegalRep/Address/Street` | Required | Text (max 120) | Street |
| 61 | `LegalRep/Address/City` | Required | Text (max 120) | City |
| 62 | `LegalRep/Address/Country` | Required | Text | Country |
| 63 | `LegalRep/Address/HouseNumber` | Optional | Text (max 20) | Street number |
| 64 | `LegalRep/Address/ApartmentNumber` | Optional | Text (max 40) | Apartment number |
| 65 | `LegalRep/Address/Floor` | Optional | Text (max 40) | Floor |
| 66 | `LegalRep/Address/District` | Optional | Text (max 80) | District |
| 67 | `LegalRep/Address/Region_FederalState` | Optional | Text (max 120) | State or province |
| 68 | `LegalRep/Address/PostCode` | Optional | Text (max 20) | Postcode |
| 69 | `LegalRep/Address/AdditionalAddressDetails` | Optional | Text (max 80) | Additional address details |
| 70 | `LegalBasis/DTA` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Double taxation agreements (DTAs) or other bilateral agreements KaFE also defines a seventh legal basis, IntOrg (agreements/conventions for international organisations and intergovernmental organisations), which status code 2101 treats as mutually exclusive with all six legal bases above; IntOrg has no column of its own in production's own field list, so this template cannot express it. (status code 2101: "It is not permitted to combine the legal bases.") |
| 71 | `LegalBasis/Par43bEStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Section 43b German Income Tax Act (Directive 2011/96/EU) |
| 72 | `LegalBasis/Par44aEStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Section 44a (9) German Income Tax Act |
| 73 | `LegalBasis/Par50gEStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Section 50g German Income Tax Act |
| 74 | `LegalBasis/Par32Abs6KStG` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Section 32 (6) German Corporate Tax Act This legal basis only applies to claims concerning inflows on or after 15 April 2025; like the other legal-basis flags, it cannot be combined with the IntOrg legal basis (status code 2101: "It is not permitted to combine the legal bases."). |
| 75 | `LegalBasis/Art63AEUV` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Asserted claim under Article 63 of the Treaty on the Functioning of the European Union (TFEU) |
| 76 | `Bank/Name` | Required | Text (max 70) | Name of the bank |
| 77 | `Bank/City` | Required | Text (max 70) | City |
| 78 | `Bank/AccountHolder` | Required | Text (max 70) | Name of the the account holder |
| 79 | `Bank/Account/BIC` | Required | Text (max 11) | BIC/SWIFT code |
| 80 | `Bank/Account/IBAN` | Conditional | Text (max 34) | IBAN |
| 81 | `Bank/Account/AccountNumber` | Conditional | Text (max 40) | Indication of the account number, if no IBAN available |
| 82 | `Residence/NonResidency_DE` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability a resident of the specified country of residence at the time of
						the inflow and did not have its registered office or place of management in Germany at that time? |
| 83 | `TaxTreatment/IdNr` | Optional | Text (max 11) | German tax identification number (IdNo) (11-digit) |
| 84 | `TaxTreatment/SwitzerlandQuestions/TaxLiabilityCH` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Has the person with limited tax liability been subject to the generally levied taxes in Switzerland
						(federal, cantonal, municipal) with all generally taxable income from Germany? |
| 85 | `TaxTreatment/SwitzerlandQuestions/In_Germany_Min_5_Years_Taxable` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability subject to unlimited tax liability in Germany for at least five
						years? |
| 86 | `TaxTreatment/SwitzerlandQuestions/In_Germany_Tax_Liability_Ended` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Did the unlimited tax liability in Germany end in the due year or in the five calendar years preceding the
						oldest inflow included in the application? |
| 87 | `TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EmploymentReasons` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Has the person with limited tax liability become resident in Switzerland, in order to pursue genuine
						employment there? |
| 88 | `TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/Employer` | Optional | Text (max 500) | Name and address of the employer |
| 89 | `TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterest` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability have an interest in the employer or another significant economic
						interest (e.g. a participating loan)? |
| 90 | `TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterestDescription` | Optional | Text (max 500) | Please describe |
| 91 | `TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/MoveDate` | Optional | Date (YYYY-MM-DD) | When did the move to Switzerland take place? |
| 92 | `TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/OtherReasons` | Optional | Text (max 500) | What were the reasons for moving to Switzerland? |
| 93 | `Affirmations/AdditionalInformation` | Optional | Text (max 5000) | Additional information on the application |
| 94 | `Affirmations/JustificationArt63TFEU` | Optional | Text (max 15000) | Justification for the asserted claim under Article 63 TFEU. |
| 95 | `Affirmations/ApplicationPar50c` | Required | Enum [`Boolean`](#boolean): `true`, `false` | A refund according to section 50c (3) German Income Tax Act in connection with an agreement for the
						avoidance of double taxation (DTA) or other bilateral agreements has neither been applied for nor made to date. |
| 96 | `TaxPrivileges/ZER/Registration` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability recorded in the German register of non-profit organisations
						authorised to issue donation receipts (Zuwendungsempfängerregister)? |
| 97 | `TaxPrivileges/ZER/ReferenceNumber` | Optional | Text (max 36) | Reference number |
| 98 | `TaxPrivileges/Purposes/NonProfit` | Required | Enum [`Boolean`](#boolean): `true`, `false` | The person with limited tax liability pursues public benefit purposes (section 52 of the Fiscal Code). |
| 99 | `TaxPrivileges/Purposes/PublicBenefitPurposes` | Optional | Text | Free-text list of which of the 26 numbered public-benefit purposes (section 52(2) German Fiscal Code) apply, e.g. '1, 8, 21'. The real schema models these as 26 separate yes/no flags (ZweckNr1..ZweckNr26, GemeinnuetzigeZwecke_Struct); this column collapses them into one field. |
| 100 | `TaxPrivileges/Purposes/Charity` | Required | Enum [`Boolean`](#boolean): `true`, `false` | The person with limited tax liability pursues charitable purposes (section 53 of the Fiscal Code). |
| 101 | `TaxPrivileges/Purposes/Church` | Required | Enum [`Boolean`](#boolean): `true`, `false` | The person with limited tax liability pursues ecclesiastical purposes (section 54 of the Fiscal Code). |
| 102 | `TaxPrivileges/Purposes/Exclusivity` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability serve directly and exclusively tax-privileged purposes (see
						sections 56 and 57 of the Fiscal Code)? |
| 103 | `TaxPrivileges/Purposes/StartDate` | Required | Date (YYYY-MM-DD) | Start of the public-benefit, charitable or ecclesiastical activity |
| 104 | `TaxPrivileges/Statuses/LastChangeDate` | Required | Date (YYYY-MM-DD) | Date on which the statutes were last changed |
| 105 | `TaxPrivileges/StructuralConnectionToGermany/TaxPrivilegedPurposesDE` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability pursuing the tax-privileged purposes at least partly in Germany? |
| 106 | `TaxPrivileges/StructuralConnectionToGermany/GermanResidentsEligibility` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Are natural persons who have their place of residence or habitual abode in Germany being advanced? |
| 107 | `TaxPrivileges/StructuralConnectionToGermany/GermanReputation` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Does the activity carried out by the taxpayer contribute to the reputation of the Federal Republic of
						Germany abroad? |
| 108 | `TaxPrivileges/StructuralConnectionToGermany/Explanation` | Required | Text (max 5000) | Specification how the connection to Germany is manifested |
| 109 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporation` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases, the
						assets accrue - at least in part - to a tax-privileged corporation resident in Germany for tax-privileged purposes. |
| 110 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporationKStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases, the
						assets accrue - at least in part - to one of the corporations listed in section 5 (2) of the Corporation Tax Act for tax-privileged
						purposes. |
| 111 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/LegalEntity` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases,the
						assets accrue - at least in part - to a legal person under public law for tax-privileged purposes. |
| 112 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/Other` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases,the
						assets accrue - at least in part - to another person. |
| 113 | `TaxPrivileges/Management` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the actual management directed exclusively and directly towards achieving the tax-privileged purposes and
						does it conform to the provisions on the requirements for tax privileges contained in the statutes? |
| 114 | `TaxPrivileges/ConstitutionLoyalty` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability advance efforts directed against the liberal democratic basic
						order (freiheitliche demokratische Grundordnung) or against the existence or security of the Federal Republic of Germany or its Länder? |

### 2 Creditors Juridical

**Significance.** One row per creditor who is a juridical (non-natural) person: legal form, incorporation details, LEI/register/stock-exchange details, the option under section 1a German Corporate Tax Act, investment-fund questions, the authorised representative and legal representative (if any), the legal basis for the refund claim, bank details, and the affirmations.

**Cardinality.** Exactly 1 row per creditor (this sheet defines that creditor's id).

**When to fill.** Always, for every creditor who is a juridical person.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `id` | Required | Text (identifier used to link the sheets; any unique value) | Identifier for this creditor, defined by you. Referenced by the creditorId column on every other sheet. |
| 2 | `generalData/Country` | Optional | Enum [`CountryISOAlpha2`](#countryisoalpha2): `AD`, `AE`, `AF`, `AG`, `AI`, `AL`, `AM`, `AO`, `AQ`, `AR`, `AS`, `AT`, `AU`, `AW`, `AX`, `AZ`, `BA`, `BB`, `BD`, `BE`, `BF`, `BG`, `BH`, `BI`, `BJ`, `BL`, `BM`, `BN`, `BO`, `BQ`, `BR`, `BS`, `BT`, `BV`, `BW`, `BY`, `BZ`, `CA`, `CC`, `CD`, `CF`, `CG`, `CH`, `CI`, `CK`, `CL`, `CM`, `CN`, `CO`, `CP`, `CR`, `CU`, `CV`, `CW`, `CX`, `CY`, `CZ`, `DE`, `DJ`, `DK`, `DM`, `DO`, `DZ`, `EC`, `EE`, `EG`, `EH`, `ER`, `ES`, `ET`, `FI`, `FJ`, `FK`, `FM`, `FO`, `FR`, `GA`, `GB`, `GD`, `GE`, `GF`, `GG`, `GH`, `GI`, `GL`, `GM`, `GN`, `GP`, `GQ`, `GR`, `GS`, `GT`, `GU`, `GW`, `GY`, `HK`, `HM`, `HN`, `HR`, `HT`, `HU`, `ID`, `IE`, `IL`, `IM`, `IN`, `IO`, `IQ`, `IR`, `IS`, `IT`, `JE`, `JM`, `JO`, `JP`, `KE`, `KG`, `KH`, `KI`, `KM`, `KN`, `KP`, `KR`, `KW`, `KY`, `KZ`, `LA`, `LB`, `LC`, `LI`, `LK`, `LR`, `LS`, `LT`, `LU`, `LV`, `LY`, `MA`, `MC`, `MD`, `ME`, `MF`, `MG`, `MH`, `MK`, `ML`, `MM`, `MN`, `MO`, `MP`, `MQ`, `MR`, `MS`, `MT`, `MU`, `MV`, `MW`, `MX`, `MY`, `MZ`, `NA`, `NC`, `NE`, `NF`, `NG`, `NI`, `NL`, `NO`, `NP`, `NR`, `NU`, `NZ`, `OM`, `PA`, `PE`, `PF`, `PG`, `PH`, `PK`, `PL`, `PM`, `PN`, `PR`, `PS`, `PT`, `PW`, `PY`, `QA`, `RE`, `RO`, `RS`, `RU`, `RW`, `SA`, `SB`, `SC`, `SD`, `SE`, `SG`, `SH`, `SI`, `SJ`, `SK`, `SL`, `SM`, `SN`, `SO`, `SR`, `SS`, `ST`, `SV`, `SX`, `SY`, `SZ`, `TC`, `TD`, `TF`, `TG`, `TH`, `TJ`, `TK`, `TL`, `TM`, `TN`, `TO`, `TR`, `TT`, `TV`, `TW`, `TZ`, `UA`, `UG`, `UM`, `US`, `UY`, `UZ`, `VA`, `VC`, `VE`, `VG`, `VI`, `VN`, `VU`, `WF`, `WS`, `XK`, `YE`, `YT`, `ZA`, `ZM`, `ZW` | Country of residence |
| 3 | `generalData/LegalForm` | Optional | Enum [`Rechtsformen`](#rechtsformen): `NATP`, `KAPG`, `SOJP`, `INVF`, `PENF`, `GSTF`, `HHTR`, `PGES` | Legal form |
| 4 | `generalData/SpecificLegalForm` | Required | Text (max 80) | specific legal form |
| 5 | `generalData/ProfitsPG_CH` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | At least three quarters of the profits of the partnership attributable to persons who are resident in
						Switzerland as natural persons or legal entities within the meaning of art. 4 DTA-CH? |
| 6 | `CreditorJur/ContactPerson/FirstName` | Required | Text (max 80) | First and middle name |
| 7 | `CreditorJur/ContactPerson/Name` | Required | Text (max 120) | Last name |
| 8 | `CreditorJur/ContactPerson/Organization` | Optional | Text (max 256) | Organisation |
| 9 | `CreditorJur/ContactPerson/Email` | Optional | Text (max 254) | E-mail address |
| 10 | `CreditorJur/ContactPerson/PhoneNumber` | Optional | Text (max 21) | Telephone number (area code/phone number) |
| 11 | `CreditorJur/General_Data/DateOfEstablishment` | Required | Date (YYYY-MM-DD) | Date of incorporation |
| 12 | `CreditorJur/General_Data/IncorporationCountry` | Optional | Enum [`CountryISOAlpha2`](#countryisoalpha2): `AD`, `AE`, `AF`, `AG`, `AI`, `AL`, `AM`, `AO`, `AQ`, `AR`, `AS`, `AT`, `AU`, `AW`, `AX`, `AZ`, `BA`, `BB`, `BD`, `BE`, `BF`, `BG`, `BH`, `BI`, `BJ`, `BL`, `BM`, `BN`, `BO`, `BQ`, `BR`, `BS`, `BT`, `BV`, `BW`, `BY`, `BZ`, `CA`, `CC`, `CD`, `CF`, `CG`, `CH`, `CI`, `CK`, `CL`, `CM`, `CN`, `CO`, `CP`, `CR`, `CU`, `CV`, `CW`, `CX`, `CY`, `CZ`, `DE`, `DJ`, `DK`, `DM`, `DO`, `DZ`, `EC`, `EE`, `EG`, `EH`, `ER`, `ES`, `ET`, `FI`, `FJ`, `FK`, `FM`, `FO`, `FR`, `GA`, `GB`, `GD`, `GE`, `GF`, `GG`, `GH`, `GI`, `GL`, `GM`, `GN`, `GP`, `GQ`, `GR`, `GS`, `GT`, `GU`, `GW`, `GY`, `HK`, `HM`, `HN`, `HR`, `HT`, `HU`, `ID`, `IE`, `IL`, `IM`, `IN`, `IO`, `IQ`, `IR`, `IS`, `IT`, `JE`, `JM`, `JO`, `JP`, `KE`, `KG`, `KH`, `KI`, `KM`, `KN`, `KP`, `KR`, `KW`, `KY`, `KZ`, `LA`, `LB`, `LC`, `LI`, `LK`, `LR`, `LS`, `LT`, `LU`, `LV`, `LY`, `MA`, `MC`, `MD`, `ME`, `MF`, `MG`, `MH`, `MK`, `ML`, `MM`, `MN`, `MO`, `MP`, `MQ`, `MR`, `MS`, `MT`, `MU`, `MV`, `MW`, `MX`, `MY`, `MZ`, `NA`, `NC`, `NE`, `NF`, `NG`, `NI`, `NL`, `NO`, `NP`, `NR`, `NU`, `NZ`, `OM`, `PA`, `PE`, `PF`, `PG`, `PH`, `PK`, `PL`, `PM`, `PN`, `PR`, `PS`, `PT`, `PW`, `PY`, `QA`, `RE`, `RO`, `RS`, `RU`, `RW`, `SA`, `SB`, `SC`, `SD`, `SE`, `SG`, `SH`, `SI`, `SJ`, `SK`, `SL`, `SM`, `SN`, `SO`, `SR`, `SS`, `ST`, `SV`, `SX`, `SY`, `SZ`, `TC`, `TD`, `TF`, `TG`, `TH`, `TJ`, `TK`, `TL`, `TM`, `TN`, `TO`, `TR`, `TT`, `TV`, `TW`, `TZ`, `UA`, `UG`, `UM`, `US`, `UY`, `UZ`, `VA`, `VC`, `VE`, `VG`, `VI`, `VN`, `VU`, `WF`, `WS`, `XK`, `YE`, `YT`, `ZA`, `ZM`, `ZW` | Country under whose law the organisation/company is incorporated |
| 13 | `CreditorJur/General_Data/TinAvailable` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability have a foreign tax identification number? |
| 14 | `CreditorJur/General_Data/IDNumber_CountryOfResidence` | Optional | Text (max 40) | Foreign tax identification number |
| 15 | `CreditorJur/General_Data/TransparentEntity` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability treated as a transparent entity by the tax authority of the country
						of residence? |
| 16 | `CreditorJur/General_Data/WithholdingTaxNumber` | Optional | Numeric string (8-digit BZSt withholding-tax number) | Withholding tax number for refund |
| 17 | `CreditorJur/General_Data/Name` | Required | Text (max 256) | Legal name |
| 18 | `CreditorJur/General_Data/Department` | Optional | Text (max 80) | Department |
| 19 | `CreditorJur/Address/Street` | Required | Text (max 120) | Street |
| 20 | `CreditorJur/Address/StreetNumber` | Optional | Text (max 20) | Street number |
| 21 | `CreditorJur/Address/AdditionalAddressDetails` | Optional | Text (max 80) | Additional address details |
| 22 | `CreditorJur/Address/District` | Optional | Text (max 80) | District |
| 23 | `CreditorJur/Address/Postcode` | Optional | Text (max 20) | Postcode |
| 24 | `CreditorJur/Address/City` | Required | Text (max 120) | City |
| 25 | `CreditorJur/Address/Region_FederalState` | Optional | Text (max 120) | State or province |
| 26 | `CreditorJur/Address/Country` | Required | Text | Country |
| 27 | `CreditorJur/Address/Apartment` | Optional | Text (max 40) | Apartment number |
| 28 | `CreditorJur/Address/Floor` | Optional | Text (max 40) | Floor |
| 29 | `CreditorJur/LEI` | Optional | Text (max 20) | Legal Entity Identifier (LEI) |
| 30 | `CreditorJur/Register/Register` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability entered in a register (e.g. company register, commercial register,
						foundation register)? |
| 31 | `CreditorJur/Register/RegistryAuthority` | Conditional | Text (max 80) | Registry authority |
| 32 | `CreditorJur/Register/RegistrationNumber` | Conditional | Text (max 40) | Registration number |
| 33 | `CreditorJur/Boerse/StockExchange` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Are the principal class of shares belonging to the person subject to limited tax liability subject to
						substantial and regular trading on a recognised stock exchange? |
| 34 | `CreditorJur/Boerse/ISIN` | Optional | ISIN (12-digit) | ISIN (12-digit) |
| 35 | `CreditorJur/Boerse/Boersenplatz` | Optional | Text (max 120) | Stock exchange on which the stocks are traded. |
| 36 | `CreditorJur/German_TaxOffice/German_TaxOffice` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability registered with a German tax office? |
| 37 | `CreditorJur/German_TaxOffice/TaxNumber` | Optional | Text (max 13) | Tax number (13 digits) |
| 38 | `CreditorJur/OptingUnderCorpTaxAct/OptionKStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Has the option to be treated like a corporation for tax purposes pursuant to section 1a German Corporate
						Income Tax Act been exercised? |
| 39 | `CreditorJur/OptingUnderCorpTaxAct/TaxAuthority` | Optional | Enum [`Steuerbehoerden`](#steuerbehoerden): `FA`, `BZST` | Tax authority |
| 40 | `CreditorJur/OptingUnderCorpTaxAct/FileNumber` | Optional | Text (max 30) | File number / tax number |
| 41 | `InvTaxAct/Requested_StatusCertificate` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Has a status certificate pursuant to section 7 (3) Investment Tax Act been issued or applied for? |
| 42 | `InvTaxAct/StatusCertificateDetails/Issuer` | Optional | Enum [`Steuerbehoerden`](#steuerbehoerden): `FA`, `BZST` | Issuing authority or authority to which the status certificate was applied for |
| 43 | `InvTaxAct/StatusCertificateDetails/FileNumber` | Optional | Text (max 13) | Ordinal number / tax number (if issued) |
| 44 | `InvTaxAct/StatusCertificateDetails/Period/from` | Optional | Date (YYYY-MM-DD) | Valid from |
| 45 | `InvTaxAct/StatusCertificateDetails/Period/to` | Optional | Date (YYYY-MM-DD) | Valid until |
| 46 | `InvTaxAct/SpecialInvestmentFunds/Special` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is this a special investment fund within the meaning of section 26 Investment Tax Act? |
| 47 | `InvTaxAct/SpecialInvestmentFunds/TransparencyOption` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Has the transparency option been exercised? |
| 48 | `AuthorizedRep/General_Data/LegalForm` | Optional | Enum [`PersonChoice`](#personchoice): `NatuerlichePerson`, `NichtNatuerlichePerson` | Which block below is filled in for this representative: a natural person or a non-natural person (organisation). |
| 49 | `AuthorizedRep/Authority/TaxProfessions` | Required | Enum [`Boolean`](#boolean): `true`, `false` | I confirm that I am a member of the tax advisory professions within the meaning of sections 3 or 4 number 11
						German Tax Advisory Act. |
| 50 | `AuthorizedRep/Authority/OtherReasons` | Required | Enum [`Boolean`](#boolean): `true`, `false` | I confirm that I am authorised to provide assistance in tax matters for other reasons. |
| 51 | `AuthorizedRep/NaturalPerson/General_Data/FormOfAddress` | Required | Enum [`Anrede`](#anrede): `FRAU`, `HERR`, `KEINE_ANREDE` | Form of address |
| 52 | `AuthorizedRep/NaturalPerson/General_Data/Title` | Optional | Text (max 40) | Title |
| 53 | `AuthorizedRep/NaturalPerson/General_Data/FirstName` | Required | Text (max 80) | First and middle name |
| 54 | `AuthorizedRep/NaturalPerson/General_Data/LastName` | Required | Text (max 120) | Last name |
| 55 | `AuthorizedRep/NonNaturalPerson/General_Data/Name` | Required | Text (max 256) | Legal name |
| 56 | `AuthorizedRep/NonNaturalPerson/General_Data/Department` | Optional | Text (max 80) | Department |
| 57 | `AuthorizedRep/Address/Street` | Required | Text (max 120) | Street |
| 58 | `AuthorizedRep/Address/StreetNumber` | Optional | Text (max 20) | Street number |
| 59 | `AuthorizedRep/Address/AdditionalAddressDetails` | Optional | Text (max 80) | Additional address details |
| 60 | `AuthorizedRep/Address/District` | Optional | Text (max 80) | District |
| 61 | `AuthorizedRep/Address/Postcode` | Optional | Text (max 20) | Postcode |
| 62 | `AuthorizedRep/Address/City` | Required | Text (max 120) | City |
| 63 | `AuthorizedRep/Address/Region_FederalState` | Optional | Text (max 120) | State or province |
| 64 | `AuthorizedRep/Address/Country` | Required | Text | Country |
| 65 | `AuthorizedRep/Address/Apartment` | Optional | Text (max 40) | Apartment number |
| 66 | `AuthorizedRep/Address/Floor` | Optional | Text (max 40) | Floor |
| 67 | `LegalRep/LegalForm` | Optional | Enum [`PersonChoice`](#personchoice): `NatuerlichePerson`, `NichtNatuerlichePerson` | Which block below is filled in for this representative: a natural person or a non-natural person (organisation). |
| 68 | `LegalRep/NatPerson/FormOfAddress` | Required | Enum [`Anrede`](#anrede): `FRAU`, `HERR`, `KEINE_ANREDE` | Form of address |
| 69 | `LegalRep/NatPerson/Title` | Optional | Text (max 40) | Title |
| 70 | `LegalRep/NatPerson/FirstName` | Required | Text (max 80) | First and middle name |
| 71 | `LegalRep/NatPerson/LastName` | Required | Text (max 120) | Last name |
| 72 | `LegalRep/JurPerson/OrganisationName` | Required | Text (max 256) | Legal name |
| 73 | `LegalRep/JurPerson/OrganisationDepartment` | Optional | Text (max 80) | Department |
| 74 | `LegalRep/Address/Street` | Required | Text (max 120) | Street |
| 75 | `LegalRep/Address/City` | Required | Text (max 120) | City |
| 76 | `LegalRep/Address/Country` | Required | Text | Country |
| 77 | `LegalRep/Address/HouseNumber` | Optional | Text (max 20) | Street number |
| 78 | `LegalRep/Address/ApartmentNumber` | Optional | Text (max 40) | Apartment number |
| 79 | `LegalRep/Address/Floor` | Optional | Text (max 40) | Floor |
| 80 | `LegalRep/Address/District` | Optional | Text (max 80) | District |
| 81 | `LegalRep/Address/Region_FederalState` | Optional | Text (max 120) | State or province |
| 82 | `LegalRep/Address/PostCode` | Optional | Text (max 20) | Postcode |
| 83 | `LegalRep/Address/AdditionalAddressDetails` | Optional | Text (max 80) | Additional address details |
| 84 | `Residence/NonResidency_DE` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Was the person with limited tax liability a resident of the specified country of residence at the time of
						the inflow and did not have its registered office or place of management in Germany at that time? |
| 85 | `Management/DifferentAddress` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Weicht der Ort der tatsächlichen Geschäftsleitung von der angegebenen Adresse ab? |
| 86 | `Management/Address/Street` | Required | Text (max 120) | Street |
| 87 | `Management/Address/City` | Required | Text (max 120) | City |
| 88 | `Management/Address/Country` | Required | Text | Country |
| 89 | `Management/Address/HouseNumber` | Optional | Text (max 20) | Street number |
| 90 | `Management/Address/ApartmentNumber` | Optional | Text (max 40) | Apartment number |
| 91 | `Management/Address/Floor` | Optional | Text (max 40) | Floor |
| 92 | `Management/Address/District` | Optional | Text (max 80) | District |
| 93 | `Management/Address/Region_FederalState` | Optional | Text (max 120) | State or province |
| 94 | `Management/Address/PostCode` | Optional | Text (max 20) | Postcode |
| 95 | `Management/Address/AdditionalAddressDetails` | Optional | Text (max 80) | Additional address details |
| 96 | `TaxTreatment/W-IdNr` | Optional | Text (max 16) | Business identification number |
| 97 | `LegalBasis/DTA` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Double taxation agreements (DTAs) or other bilateral agreements KaFE also defines a seventh legal basis, IntOrg (agreements/conventions for international organisations and intergovernmental organisations), which status code 2101 treats as mutually exclusive with all six legal bases above; IntOrg has no column of its own in production's own field list, so this template cannot express it. (status code 2101: "It is not permitted to combine the legal bases.") |
| 98 | `LegalBasis/Par43bEStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Section 43b German Income Tax Act (Directive 2011/96/EU) |
| 99 | `LegalBasis/Par44aEStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Section 44a (9) German Income Tax Act |
| 100 | `LegalBasis/Par50gEStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Section 50g German Income Tax Act |
| 101 | `LegalBasis/Par32Abs6KStG` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Section 32 (6) German Corporate Tax Act This legal basis only applies to claims concerning inflows on or after 15 April 2025; like the other legal-basis flags, it cannot be combined with the IntOrg legal basis (status code 2101: "It is not permitted to combine the legal bases."). |
| 102 | `LegalBasis/Art63AEUV` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Asserted claim under Article 63 of the Treaty on the Functioning of the European Union (TFEU) |
| 103 | `Bank/Name` | Required | Text (max 70) | Name of the bank |
| 104 | `Bank/City` | Required | Text (max 70) | City |
| 105 | `Bank/AccountHolder` | Required | Text (max 70) | Name of the the account holder |
| 106 | `Bank/Account/BIC` | Required | Text (max 11) | BIC/SWIFT code |
| 107 | `Bank/Account/IBAN` | Conditional | Text (max 34) | IBAN |
| 108 | `Bank/Account/AccountNumber` | Conditional | Text (max 40) | Indication of the account number, if no IBAN available |
| 109 | `Affirmations/AdditionalInformation` | Optional | Text (max 5000) | Additional information on the application |
| 110 | `Affirmations/JustificationArt63TFEU` | Optional | Text (max 15000) | Justification for the asserted claim under Article 63 TFEU. |
| 111 | `Affirmations/ApplicationPar50c` | Required | Enum [`Boolean`](#boolean): `true`, `false` | A refund according to section 50c (3) German Income Tax Act in connection with an agreement for the
						avoidance of double taxation (DTA) or other bilateral agreements has neither been applied for nor made to date. |
| 112 | `Affirmations/ApplicationPar11InvStG` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | A refund in accordance with section 11 Investment Tax Act was neither applied for nor made to the Federal
						Central Tax Office or another tax authority. |
| 113 | `TaxPrivileges/ZER/Registration` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability recorded in the German register of non-profit organisations
						authorised to issue donation receipts (Zuwendungsempfängerregister)? |
| 114 | `TaxPrivileges/ZER/ReferenceNumber` | Optional | Text (max 36) | Reference number |
| 115 | `TaxPrivileges/Purposes/NonProfit` | Required | Enum [`Boolean`](#boolean): `true`, `false` | The person with limited tax liability pursues public benefit purposes (section 52 of the Fiscal Code). |
| 116 | `TaxPrivileges/Purposes/PublicBenefitPurposes` | Optional | Text | Free-text list of which of the 26 numbered public-benefit purposes (section 52(2) German Fiscal Code) apply, e.g. '1, 8, 21'. The real schema models these as 26 separate yes/no flags (ZweckNr1..ZweckNr26, GemeinnuetzigeZwecke_Struct); this column collapses them into one field. |
| 117 | `TaxPrivileges/Purposes/Charity` | Required | Enum [`Boolean`](#boolean): `true`, `false` | The person with limited tax liability pursues charitable purposes (section 53 of the Fiscal Code). |
| 118 | `TaxPrivileges/Purposes/Church` | Required | Enum [`Boolean`](#boolean): `true`, `false` | The person with limited tax liability pursues ecclesiastical purposes (section 54 of the Fiscal Code). |
| 119 | `TaxPrivileges/Purposes/Exclusivity` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability serve directly and exclusively tax-privileged purposes (see
						sections 56 and 57 of the Fiscal Code)? |
| 120 | `TaxPrivileges/Purposes/StartDate` | Required | Date (YYYY-MM-DD) | Start of the public-benefit, charitable or ecclesiastical activity |
| 121 | `TaxPrivileges/Statuses/LastChangeDate` | Required | Date (YYYY-MM-DD) | Date on which the statutes were last changed |
| 122 | `TaxPrivileges/StructuralConnectionToGermany/TaxPrivilegedPurposesDE` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the person with limited tax liability pursuing the tax-privileged purposes at least partly in Germany? |
| 123 | `TaxPrivileges/StructuralConnectionToGermany/GermanResidentsEligibility` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Are natural persons who have their place of residence or habitual abode in Germany being advanced? |
| 124 | `TaxPrivileges/StructuralConnectionToGermany/GermanReputation` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | Does the activity carried out by the taxpayer contribute to the reputation of the Federal Republic of
						Germany abroad? |
| 125 | `TaxPrivileges/StructuralConnectionToGermany/Explanation` | Required | Text (max 5000) | Specification how the connection to Germany is manifested |
| 126 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporation` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases, the
						assets accrue - at least in part - to a tax-privileged corporation resident in Germany for tax-privileged purposes. |
| 127 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporationKStG` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases, the
						assets accrue - at least in part - to one of the corporations listed in section 5 (2) of the Corporation Tax Act for tax-privileged
						purposes. |
| 128 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/LegalEntity` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases,the
						assets accrue - at least in part - to a legal person under public law for tax-privileged purposes. |
| 129 | `TaxPrivileges/StructuralConnectionToGermany/AssetLock/Other` | Required | Enum [`Boolean`](#boolean): `true`, `false` | If the person with limited tax liabiliy is dissolved or liquidated or if its former purpose ceases,the
						assets accrue - at least in part - to another person. |
| 130 | `TaxPrivileges/Management` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Is the actual management directed exclusively and directly towards achieving the tax-privileged purposes and
						does it conform to the provisions on the requirements for tax privileges contained in the statutes? |
| 131 | `TaxPrivileges/ConstitutionLoyalty` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Does the person with limited tax liability advance efforts directed against the liberal democratic basic
						order (freiheitliche demokratische Grundordnung) or against the existence or security of the Federal Republic of Germany or its Länder? |

## Enumerations reference

Every value that can be chosen from a dropdown, with its meaning and the fields that use it.

### Boolean

*Used in:* `4 Income.SubstantialHolding/IsSubstantial`, `4 Income.SubstantialHolding/HoldingPeriod18M`, `4 Income.SubstantialHolding/HoldingPeriod12M`, `4 Income.SubstantialHolding/HoldingPeriod6M`, `4 Income.IndirectHolding/IndirectHolding`, `4 Income.IndirectHolding/CompanyOfSpouses`, `4 Income.NonResidency_DE`, `4 Income.Hidden_ProfitDistribution/ConstructiveDividend`, `4 Income.Economic_Ownership/Ownership_and_Right_To_Use`, `4 Income.TaxExemption`, `4 Income.Depositary_Receipts/Is_DR`, `4 Income.RemittanceBase/IsSubject`, `4 Income.Business_Establishment/Business_Establishment_DE`, `4 Income.UnlimitedForeignCorporateTaxLiability`, `4 Income.Questions_for_50j/MinValueChangeRisk/OpposingClaims`, `4 Income.Questions_for_50j/MinValueChangeRisk/OtherOpposingClaims`, `4 Income.Questions_for_50j/ForwardingObligation/ForwardingObligation`, `4 Income.Questions_for_50j/ForwardingObligation/FurtherForwardingObligation`, `4 Income.Questions_for_50j/ReturnObligation/ReturnObligation`, `5 Investment Chain.AssetManagement`, `1 Creditors Natural.CreditorNat/General_Data/NationalityIsDE`, `1 Creditors Natural.CreditorNat/General_Data/NationalityIsKW`, `1 Creditors Natural.CreditorNat/General_Data/NationalityIsCH`, `1 Creditors Natural.CreditorNat/General_Data/TinAvailable`, `1 Creditors Natural.CreditorNat/German_TaxOffice/German_TaxOffice`, `1 Creditors Natural.CreditorNat/German_TaxOffice/TaxLiabilityGermany`, `1 Creditors Natural.CreditorNat/German_TaxOffice/TaxLiabilityGermany5Years`, `1 Creditors Natural.AuthorizedRep/Authority/TaxProfessions`, `1 Creditors Natural.AuthorizedRep/Authority/OtherReasons`, `1 Creditors Natural.LegalBasis/DTA`, `1 Creditors Natural.LegalBasis/Par43bEStG`, `1 Creditors Natural.LegalBasis/Par44aEStG`, `1 Creditors Natural.LegalBasis/Par50gEStG`, `1 Creditors Natural.LegalBasis/Par32Abs6KStG`, `1 Creditors Natural.LegalBasis/Art63AEUV`, `1 Creditors Natural.Residence/NonResidency_DE`, `1 Creditors Natural.TaxTreatment/SwitzerlandQuestions/TaxLiabilityCH`, `1 Creditors Natural.TaxTreatment/SwitzerlandQuestions/In_Germany_Min_5_Years_Taxable`, `1 Creditors Natural.TaxTreatment/SwitzerlandQuestions/In_Germany_Tax_Liability_Ended`, `1 Creditors Natural.TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EmploymentReasons`, `1 Creditors Natural.TaxTreatment/SwitzerlandQuestions/DependantPersonalServices/EconomicInterest`, `1 Creditors Natural.Affirmations/ApplicationPar50c`, `1 Creditors Natural.TaxPrivileges/ZER/Registration`, `1 Creditors Natural.TaxPrivileges/Purposes/NonProfit`, `1 Creditors Natural.TaxPrivileges/Purposes/Charity`, `1 Creditors Natural.TaxPrivileges/Purposes/Church`, `1 Creditors Natural.TaxPrivileges/Purposes/Exclusivity`, `1 Creditors Natural.TaxPrivileges/StructuralConnectionToGermany/TaxPrivilegedPurposesDE`, `1 Creditors Natural.TaxPrivileges/StructuralConnectionToGermany/GermanResidentsEligibility`, `1 Creditors Natural.TaxPrivileges/StructuralConnectionToGermany/GermanReputation`, `1 Creditors Natural.TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporation`, `1 Creditors Natural.TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporationKStG`, `1 Creditors Natural.TaxPrivileges/StructuralConnectionToGermany/AssetLock/LegalEntity`, `1 Creditors Natural.TaxPrivileges/StructuralConnectionToGermany/AssetLock/Other`, `1 Creditors Natural.TaxPrivileges/Management`, `1 Creditors Natural.TaxPrivileges/ConstitutionLoyalty`, `2 Creditors Juridical.generalData/ProfitsPG_CH`, `2 Creditors Juridical.CreditorJur/General_Data/TinAvailable`, `2 Creditors Juridical.CreditorJur/General_Data/TransparentEntity`, `2 Creditors Juridical.CreditorJur/Register/Register`, `2 Creditors Juridical.CreditorJur/Boerse/StockExchange`, `2 Creditors Juridical.CreditorJur/German_TaxOffice/German_TaxOffice`, `2 Creditors Juridical.CreditorJur/OptingUnderCorpTaxAct/OptionKStG`, `2 Creditors Juridical.InvTaxAct/Requested_StatusCertificate`, `2 Creditors Juridical.InvTaxAct/SpecialInvestmentFunds/Special`, `2 Creditors Juridical.InvTaxAct/SpecialInvestmentFunds/TransparencyOption`, `2 Creditors Juridical.AuthorizedRep/Authority/TaxProfessions`, `2 Creditors Juridical.AuthorizedRep/Authority/OtherReasons`, `2 Creditors Juridical.Residence/NonResidency_DE`, `2 Creditors Juridical.Management/DifferentAddress`, `2 Creditors Juridical.LegalBasis/DTA`, `2 Creditors Juridical.LegalBasis/Par43bEStG`, `2 Creditors Juridical.LegalBasis/Par44aEStG`, `2 Creditors Juridical.LegalBasis/Par50gEStG`, `2 Creditors Juridical.LegalBasis/Par32Abs6KStG`, `2 Creditors Juridical.LegalBasis/Art63AEUV`, `2 Creditors Juridical.Affirmations/ApplicationPar50c`, `2 Creditors Juridical.Affirmations/ApplicationPar11InvStG`, `2 Creditors Juridical.TaxPrivileges/ZER/Registration`, `2 Creditors Juridical.TaxPrivileges/Purposes/NonProfit`, `2 Creditors Juridical.TaxPrivileges/Purposes/Charity`, `2 Creditors Juridical.TaxPrivileges/Purposes/Church`, `2 Creditors Juridical.TaxPrivileges/Purposes/Exclusivity`, `2 Creditors Juridical.TaxPrivileges/StructuralConnectionToGermany/TaxPrivilegedPurposesDE`, `2 Creditors Juridical.TaxPrivileges/StructuralConnectionToGermany/GermanResidentsEligibility`, `2 Creditors Juridical.TaxPrivileges/StructuralConnectionToGermany/GermanReputation`, `2 Creditors Juridical.TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporation`, `2 Creditors Juridical.TaxPrivileges/StructuralConnectionToGermany/AssetLock/GermanCorporationKStG`, `2 Creditors Juridical.TaxPrivileges/StructuralConnectionToGermany/AssetLock/LegalEntity`, `2 Creditors Juridical.TaxPrivileges/StructuralConnectionToGermany/AssetLock/Other`, `2 Creditors Juridical.TaxPrivileges/Management`, `2 Creditors Juridical.TaxPrivileges/ConstitutionLoyalty`

| Value | Meaning |
| --- | --- |
| `true` | Yes - the condition applies. |
| `false` | No - the condition does not apply. |

### KapitalertragArt

*Used in:* `4 Income.CapitalIncome`

| Value | Meaning |
| --- | --- |
| `DIVIDENDEN` | Dividends from listed shares |
| `AUSSCH_KAPG` | Distributions from non-listed company (e.g. GmbH) |
| `GENUSSR_ML` | Income from profit participation rights with participation in liquidation proceeds |
| `GENUSSR_OL` | Income from profit participation rights without participation in liquidation proceeds |
| `WANDELANL` | Income from convertible bonds |
| `LEBENSVERS` | Income from life insurance (section 20 [1] no 6 Income Tax Act) |
| `EINN_STILLG` | Income from a shareholding in a business as a silent partner |
| `PART_DARL` | Income from loans with an interest rate linked to the borrower's profit (partiarisches Darlehen) |
| `GEWINNOBL` | Income from participation bonds |
| `GRENZKW` | Income from a border power station on the Rhine |
| `SONSTIGE` | Other income |

### TransaktionArt

*Used in:* `6 Transaction Data.TransactionDirection`

| Value | Meaning |
| --- | --- |
| `ZUGANG` | Inflow |
| `ABGANG` | Outflow |

### TransaktionGeschaeft

*Used in:* `6 Transaction Data.TransactionType`

| Value | Meaning |
| --- | --- |
| `PO` | Purchase |
| `SO` | Sale |
| `TL` | Transfer due to securities lending |
| `RL` | Retransfer due to securities lending |
| `TP` | Transfer due to repurchase agreement |
| `RP` | Retransfer due to repurchase agreement |

### CountryISOAlpha2

*Used in:* `5 Investment Chain.Country`, `1 Creditors Natural.generalData/Country`, `2 Creditors Juridical.generalData/Country`, `2 Creditors Juridical.CreditorJur/General_Data/IncorporationCountry`

| Value | Meaning |
| --- | --- |
| `AD` | Andorra |
| `AE` | United Arab Emirates (the) |
| `AF` | Afghanistan |
| `AG` | Antigua and Barbuda |
| `AI` | Anguilla |
| `AL` | Albania |
| `AM` | Armenia |
| `AO` | Angola |
| `AQ` | Antarctica |
| `AR` | Argentina |
| `AS` | American Samoa |
| `AT` | Austria |
| `AU` | Australia |
| `AW` | Aruba |
| `AX` | Åland Islands |
| `AZ` | Azerbaijan |
| `BA` | Bosnia and Herzegovina |
| `BB` | Barbados |
| `BD` | Bangladesh |
| `BE` | Belgium |
| `BF` | Burkina Faso |
| `BG` | Bulgaria |
| `BH` | Bahrain |
| `BI` | Burundi |
| `BJ` | Benin |
| `BL` | Saint Barthélemy |
| `BM` | Bermuda |
| `BN` | Brunei Darussalam |
| `BO` | Bolivia (Plurinational State of) |
| `BQ` | Bonaire, Sint Eustatius and Saba |
| `BR` | Brazil |
| `BS` | Bahamas (the) |
| `BT` | Bhutan |
| `BV` | Bouvet Island |
| `BW` | Botswana |
| `BY` | Belarus |
| `BZ` | Belize |
| `CA` | Canada |
| `CC` | Cocos (Keeling) Islands (the) |
| `CD` | Congo (the Democratic Republic of the) |
| `CF` | Central African Republic (the) |
| `CG` | Congo (the) |
| `CH` | Switzerland |
| `CI` | Côte d'Ivoire |
| `CK` | Cook Islands (the) |
| `CL` | Chile |
| `CM` | Cameroon |
| `CN` | China |
| `CO` | Colombia |
| `CP` | Clipperton |
| `CR` | Costa Rica |
| `CU` | Cuba |
| `CV` | Cabo Verde |
| `CW` | Curaçao |
| `CX` | Christmas Island |
| `CY` | Cyprus |
| `CZ` | Czechia |
| `DE` | Germany |
| `DJ` | Djibouti |
| `DK` | Denmark |
| `DM` | Dominica |
| `DO` | Dominican Republic (the) |
| `DZ` | Algeria |
| `EC` | Ecuador |
| `EE` | Estonia |
| `EG` | Egypt |
| `EH` | Western Sahara |
| `ER` | Eritrea |
| `ES` | Spain |
| `ET` | Ethiopia |
| `FI` | Finland |
| `FJ` | Fiji |
| `FK` | Falkland Islands (the) [Malvinas] |
| `FM` | Micronesia (Federated States of) |
| `FO` | Faroe Islands (the) |
| `FR` | France |
| `GA` | Gabon |
| `GB` | United Kingdom of Great Britain and Northern Ireland (the) |
| `GD` | Grenada |
| `GE` | Georgia |
| `GF` | French Guiana |
| `GG` | Guernsey |
| `GH` | Ghana |
| `GI` | Gibraltar |
| `GL` | Greenland |
| `GM` | Gambia (the) |
| `GN` | Guinea |
| `GP` | Guadeloupe |
| `GQ` | Equatorial Guinea |
| `GR` | Greece |
| `GS` | South Georgia and the South Sandwich Islands |
| `GT` | Guatemala |
| `GU` | Guam |
| `GW` | Guinea-Bissau |
| `GY` | Guyana |
| `HK` | Hong Kong |
| `HM` | Heard Island and McDonald Islands |
| `HN` | Honduras |
| `HR` | Croatia |
| `HT` | Haiti |
| `HU` | Hungary |
| `ID` | Indonesia |
| `IE` | Ireland |
| `IL` | Israel |
| `IM` | Isle of Man |
| `IN` | India |
| `IO` | British Indian Ocean Territory (the) |
| `IQ` | Iraq |
| `IR` | Iran (Islamic Republic of) |
| `IS` | Iceland |
| `IT` | Italy |
| `JE` | Jersey |
| `JM` | Jamaica |
| `JO` | Jordan |
| `JP` | Japan |
| `KE` | Kenya |
| `KG` | Kyrgyzstan |
| `KH` | Cambodia |
| `KI` | Kiribati |
| `KM` | Comoros (the) |
| `KN` | Saint Kitts and Nevis |
| `KP` | Korea (the Democratic People's Republic of) |
| `KR` | Korea (the Republic of) |
| `KW` | Kuwait |
| `KY` | Cayman Islands (the) |
| `KZ` | Kazakhstan |
| `LA` | Lao People's Democratic Republic (the) |
| `LB` | Lebanon |
| `LC` | Saint Lucia |
| `LI` | Liechtenstein |
| `LK` | Sri Lanka |
| `LR` | Liberia |
| `LS` | Lesotho |
| `LT` | Lithuania |
| `LU` | Luxembourg |
| `LV` | Latvia |
| `LY` | Libya |
| `MA` | Morocco |
| `MC` | Monaco |
| `MD` | Moldova (the Republic of) |
| `ME` | Montenegro |
| `MF` | Saint Martin (French part) |
| `MG` | Madagascar |
| `MH` | Marshall Islands (the) |
| `MK` | North Macedonia |
| `ML` | Mali |
| `MM` | Myanmar |
| `MN` | Mongolia |
| `MO` | Macao |
| `MP` | Northern Mariana Islands (the) |
| `MQ` | Martinique |
| `MR` | Mauritania |
| `MS` | Montserrat |
| `MT` | Malta |
| `MU` | Mauritius |
| `MV` | Maldives |
| `MW` | Malawi |
| `MX` | Mexico |
| `MY` | Malaysia |
| `MZ` | Mozambique |
| `NA` | Namibia |
| `NC` | New Caledonia |
| `NE` | Niger (the) |
| `NF` | Norfolk Island |
| `NG` | Nigeria |
| `NI` | Nicaragua |
| `NL` | Netherlands (Kingdom of the) |
| `NO` | Norway |
| `NP` | Nepal |
| `NR` | Nauru |
| `NU` | Niue |
| `NZ` | New Zealand |
| `OM` | Oman |
| `PA` | Panama |
| `PE` | Peru |
| `PF` | French Polynesia |
| `PG` | Papua New Guinea |
| `PH` | Philippines (the) |
| `PK` | Pakistan |
| `PL` | Poland |
| `PM` | Saint Pierre and Miquelon |
| `PN` | Pitcairn |
| `PR` | Puerto Rico |
| `PS` | Palestine, State of |
| `PT` | Portugal |
| `PW` | Palau |
| `PY` | Paraguay |
| `QA` | Qatar |
| `RE` | Réunion |
| `RO` | Romania |
| `RS` | Serbia |
| `RU` | Russian Federation (the) |
| `RW` | Rwanda |
| `SA` | Saudi Arabia |
| `SB` | Solomon Islands |
| `SC` | Seychelles |
| `SD` | Sudan (the) |
| `SE` | Sweden |
| `SG` | Singapore |
| `SH` | Saint Helena, Ascension and Tristan da Cunha |
| `SI` | Slovenia |
| `SJ` | Svalbard and Jan Mayen |
| `SK` | Slovakia |
| `SL` | Sierra Leone |
| `SM` | San Marino |
| `SN` | Senegal |
| `SO` | Somalia |
| `SR` | Suriname |
| `SS` | South Sudan |
| `ST` | Sao Tome and Principe |
| `SV` | El Salvador |
| `SX` | Sint Maarten (Dutch part) |
| `SY` | Syrian Arab Republic (the) |
| `SZ` | Eswatini |
| `TC` | Turks and Caicos Islands (the) |
| `TD` | Chad |
| `TF` | French Southern Territories (the) |
| `TG` | Togo |
| `TH` | Thailand |
| `TJ` | Tajikistan |
| `TK` | Tokelau |
| `TL` | Timor-Leste |
| `TM` | Turkmenistan |
| `TN` | Tunisia |
| `TO` | Tonga |
| `TR` | Türkiye |
| `TT` | Trinidad and Tobago |
| `TV` | Tuvalu |
| `TW` | Taiwan (Province of China) |
| `TZ` | Tanzania, the United Republic of |
| `UA` | Ukraine |
| `UG` | Uganda |
| `UM` | United States Minor Outlying Islands (the) |
| `US` | United States of America (the) |
| `UY` | Uruguay |
| `UZ` | Uzbekistan |
| `VA` | Holy See (the) |
| `VC` | Saint Vincent and the Grenadines |
| `VE` | Venezuela (Bolivarian Republic of) |
| `VG` | Virgin Islands (British) |
| `VI` | Virgin Islands (U.S.) |
| `VN` | Viet Nam |
| `VU` | Vanuatu |
| `WF` | Wallis and Futuna |
| `WS` | Samoa |
| `XK` | Kosovo |
| `YE` | Yemen |
| `YT` | Mayotte |
| `ZA` | South Africa |
| `ZM` | Zambia |
| `ZW` | Zimbabwe |

### Rechtsformen

*Used in:* `2 Creditors Juridical.generalData/LegalForm`

| Value | Meaning |
| --- | --- |
| `NATP` | Natural person |
| `KAPG` | Corporation |
| `SOJP` | Other legal entity |
| `INVF` | Investment fund |
| `PENF` | Pension fund/retirement provision institution |
| `GSTF` | Non-profit institution/tax-exempt organisation |
| `HHTR` | Sovereign entity or comparable institution |
| `PGES` | Partnership |

### Anrede

*Used in:* `1 Creditors Natural.CreditorNat/General_Data/FormOfAddress`, `1 Creditors Natural.AuthorizedRep/NaturalPerson/General_Data/FormOfAddress`, `1 Creditors Natural.LegalRep/NatPerson/FormOfAddress`, `2 Creditors Juridical.AuthorizedRep/NaturalPerson/General_Data/FormOfAddress`, `2 Creditors Juridical.LegalRep/NatPerson/FormOfAddress`

| Value | Meaning |
| --- | --- |
| `FRAU` | Ms |
| `HERR` | Mr |
| `KEINE_ANREDE` | No form of address/no indication |

### Steuerbehoerden

*Used in:* `2 Creditors Juridical.CreditorJur/OptingUnderCorpTaxAct/TaxAuthority`, `2 Creditors Juridical.InvTaxAct/StatusCertificateDetails/Issuer`

| Value | Meaning |
| --- | --- |
| `FA` | Tax office |
| `BZST` | Federal Central Tax Office |

### PersonChoice

*Used in:* `1 Creditors Natural.AuthorizedRep/General_Data/LegalForm`, `1 Creditors Natural.LegalRep/LegalForm`, `2 Creditors Juridical.AuthorizedRep/General_Data/LegalForm`, `2 Creditors Juridical.LegalRep/LegalForm`

| Value | Meaning |
| --- | --- |
| `NatuerlichePerson` | Natural person - fill in the Natural Person fields below. |
| `NichtNatuerlichePerson` | Non-natural person / organisation - fill in the Non-Natural Person fields below. |
