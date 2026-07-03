# MiKaDiv Third-Party Disclosure - Excel Template - Documentation

Auto-generated from [`template_metadata.json`](template_metadata.json) (source schema: `ThirdPartyDisclosureRequest.xsd`). Do not edit by hand - re-run the generator to refresh.

## Overview

This workbook captures MiKaDiv (§45b) third-party disclosures for German capital income. Each disclosure is spread across several sheets that are all tied together by a single key, **RequestId**. One disclosure = one RequestId, reused on every sheet that carries data for that disclosure.

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

- **RequestId** is the key on `1 Requests Master` and the first column of every other sheet. It is only used to link the sheets, so any unique value works (it does not need to be a UUID).
- **Cancellations:** set `RecordType = Cancel` on the master sheet, fill `PreviousRequestIdForCancellation` (and optionally `ReportSerialNumber`), and leave every other sheet empty for that RequestId.
- **Community recipients:** capture a community tax-voucher receiver (up to 10 members) by setting `ReceiverGroupType = CommunityMember` on the tax voucher sheets and giving all members of one community the same `CommunityGroupId`.

## Sheets at a glance

| Sheet | Fields | Cardinality (rows per RequestId) | When to fill |
| --- | --- | --- | --- |
| [1 Requests Master](#1-requests-master) | 25 | Exactly 1 row per RequestId (this sheet defines the RequestId). | Always - every disclosure or cancellation starts here. |
| [2 Security Related Information](#2-security-related-information) | 38 | 0..1 row per RequestId. | Required when RecordType = Request. Leave empty for RecordType = Cancel. Within this sheet, the depositary-receipt fields are required only when IsDepositaryReceipt = true. |
| [3 Tax Voucher Individuals](#3-tax-voucher-individuals) | 22 | Tax-voucher receivers total up to 2 per RequestId, counted across this sheet and '4 Tax Voucher Legal Persons'. A community counts as ONE receiver and may span up to 10 member rows that share one CommunityGroupId. | For Request records at least one tax-voucher receiver is required (here or on the legal-persons sheet). Add one row per natural-person receiver or community member. |
| [4 Tax Voucher Legal Persons](#4-tax-voucher-legal-persons) | 22 | Counts towards the up-to-2 tax-voucher receivers per RequestId (shared with '3 Tax Voucher Individuals'). | For Request records, use when a tax-voucher receiver (or community member) is a legal person. |
| [5 Third Party Individuals](#5-third-party-individuals) | 20 | Third-party persons total up to 5 per RequestId, counted across this sheet and '6 Third Party Legal Persons'. | Only when the account holder is not the beneficial owner AND the beneficial owner is disclosed. Otherwise leave empty. |
| [6 Third Party Legal Persons](#6-third-party-legal-persons) | 19 | Counts towards the up-to-5 third-party persons per RequestId (shared with '5 Third Party Individuals'). | Same condition as '5 Third Party Individuals', when the third party is a legal person. |
| [7 Custody Chain](#7-custody-chain) | 21 | 0..20 rows per RequestId, ordered by NumberInChain (1 = the custodian closest to the beneficiary). | Required for Request records; add one row per intermediary link in the custody chain. |
| [8 FIFO Trades](#8-fifo-trades) | 9 | Up to 1000 Receipt rows and up to 1000 Delivery rows per RequestId. | Only when ReceiptsAndDeliveriesMode = FiFo. Leave empty when the mode = All. |
| [9 Raw Transactions All](#9-raw-transactions-all) | 10 | Unbounded rows per RequestId. | Only when ReceiptsAndDeliveriesMode = All. Leave empty when the mode = FiFo. |

## Detailed sheet reference

### 1 Requests Master

**Significance.** The parent record. One row per disclosure, holding administrative and routing metadata, the record type (new request vs cancellation), the directly-contracted securities account, the account type and the account relationship. Every other sheet links back to this one through RequestId.

**Cardinality.** Exactly 1 row per RequestId (this sheet defines the RequestId).

**When to fill.** Always - every disclosure or cancellation starts here.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Identifier for the request, defined by you. Used only as the key that links every sheet together, so any unique value (e.g. a running number) is fine. |
| 2 | `RecordType` | Required | Enum [`RecordType`](#recordtype): `Request`, `Cancel` | 'Request' for a MiKaDiv reporting for income; 'Cancel' to cancel a previously submitted request (leave the child sheets empty for cancellation rows). |
| 3 | `AccountNumber` | Required | Text (max 200) | Account number of the requesting custodian. |
| 4 | `ClientReference` | Optional | Text (max 200) | Custom reference data of the client. |
| 5 | `ClientContactpersonName` | Optional | Text (max 200) | Name of the responsible foreign bank contact person. |
| 6 | `ClientContactpersonPhone` | Optional | Text (max 35) | Telephone number of the responsible foreign bank contact person. |
| 7 | `ClientContactpersonEmail` | Optional | Text (max 200) | E-mail address of the responsible foreign bank contact person. |
| 8 | `RequestedService` | Conditional | Enum [`RequestedService`](#requestedservice): `TaxReportAndCertificate`, `Reclaim`, `Relief` | Type of requested service. |
| 9 | `RequestedServiceReason` | Optional | Text (max 256) | Reason for the requested service, especially for correction or cancellation. |
| 10 | `RequestedAttestationType` | Optional | Enum [`RequestedAttestationType`](#requestedattestationtype): `BV`, `PV`, `SB` | Type of requested tax voucher. |
| 11 | `IsCorrectionRequest` | Optional | Enum [`Boolean`](#boolean): `true`, `false` | A correction is to be performed for a report. The data record contains a reference to the preceding request. |
| 12 | `PreviousRequestIdForCorrection` | Optional | UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) | If the request is for correction of a previous request, then the RequestId of the previous request must be provided. |
| 13 | `ReportSerialNumber` | Optional | UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) | Serial number (UUID) of an already submitted report, if provided previously by the German Paying agent. Used as a (additional) reference for correction. |
| 14 | `TaxCertificatePrintedContactpersonName` | Optional | Text (max 200) | Name of the contact person for the customer, printed on the tax certificate or cover letter. |
| 15 | `TaxCertificatePrintedContactpersonPhone` | Optional | Text (max 35) | Telephone number of the contact person for the customer, printed on the tax certificate or cover letter. |
| 16 | `TaxCertificatePrintedContactpersonEmail` | Optional | Text (max 200) | E-mail address of the contact person for the customer, printed on the tax certificate or cover letter. |
| 17 | `TaxCertificateAlternativeRecipientName` | Optional | Text (max 200) | Name of the alternative mailing address recipient. |
| 18 | `TaxCertificateAlternativeRecipientAddress` | Optional | Text (max 256) | Address of the alternative mailing address recipient. |
| 19 | `TaxCertificateAlternativeRecipientEmail` | Optional | Text (max 256) | E-mail address of the alternative mailing address recipient. |
| 20 | `EventType` | Optional | Text (max 20) | Event designations of the German paying agent according to ISO 20022. |
| 21 | `FundId` | Optional | Text (max 20) | Fund identifier (status certificate number). |
| 22 | `PreviousRequestIdForCancellation` | Conditional | UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) | If the request is for cancellation of a previous request, then the RequestId of the previous request must be provided. |
| 23 | `SecuritiesAccountNumber` | Conditional | Text (max 200) | Account number of the tax voucher person at the custodian to whom the tax voucher person is directly contracted. |
| 24 | `AccountType` | Conditional | Enum [`AccountType`](#accounttype): `A`, `B`, `Ct`, `D`, `E`, `F`, `G` | Account type. |
| 25 | `AccountRelationship` | Optional | Enum [`AccountRelationship`](#accountrelationship): `Trust`, `Usufruct`, `Pledge` | If the tax voucher person is not the beneficial owner (creditor), then the account relationship has to be specified. |

### 2 Security Related Information

**Significance.** The single capital-income event being disclosed: the security (ISIN, name, type), the corporate-action reference, payment details, the complete tax breakdown (gross/net, withholding tax, solidarity surcharge and the nominal quantities per holding category) and which receipts/deliveries mode is used. It also contains the depositary-receipt block (underlying German security, record date, issuance ratios, certificates held), which describes the depositary receipt (e.g. ADR/GDR) through which the income was received.

**Cardinality.** 0..1 row per RequestId.

**When to fill.** Required when RecordType = Request. Leave empty for RecordType = Cancel. Within this sheet, the depositary-receipt fields are required only when IsDepositaryReceipt = true.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `IncomeIdentifier` | Optional | Text (max 45) | Unique identifier for an income. Must be unique over subsequent files. For a subsequent request to the same income, the same identifier must be provided. To be defined by the customer institute. |
| 3 | `CustodianIncomeIdentifier` | Optional | Text (max 45) | Bookingnumber of the payment received from the custodian. Used to reference a specific booking, if there are multiple custody chains. |
| 4 | `ISIN` | Required | ISIN (ISO 6166, 12 chars: 2 letters + 10 alphanumeric) | International Securities Identification Number (ISIN) according to ISO 6166: 2 uppercase letters followed by 10 alphanumeric characters. |
| 5 | `NameOfSecurity` | Required | Text (max 256) | Designation of the category of security. |
| 6 | `TypeOfSecurity` | Optional | Enum [`TypeOfSecurity`](#typeofsecurity): `Equity`, `Bond`, `DepositaryReceipt` | Type of the security generating the capital income. Determines the category of the financial instrument held in the custodian account. |
| 7 | `COAF` | Required | Text (Corporate Action Event Reference, max 16) | Corporate Action Event Reference (COAF). |
| 8 | `IsDepositaryReceipt` | Required | Enum [`Boolean`](#boolean): `true`, `false` | Did the beneficial owner receive the capital income via a depositary receipt on German equities (for example via an American Depositary Receipt (ADR))? Then the structure DepositaryReceipts has to be provided. |
| 9 | `CorporateActionIdOfUnderlyingSecurity` | Optional | Text (max 45) | Depositary receipt only: Corporate Action Identifier of the custodian for the underlying security. |
| 10 | `ISINOfUnderlyingSecurity` | Conditional | ISIN (ISO 6166, 12 chars: 2 letters + 10 alphanumeric) | International Securities Identification Number (ISIN) according to ISO 6166: 2 uppercase letters followed by 10 alphanumeric characters. |
| 11 | `NameOfUnderlyingSecurity` | Conditional | Text (max 256) | Name of the underlying German security. |
| 12 | `Recorddate` | Conditional | Date (YYYY-MM-DD) | Record date of the underlying German share. |
| 13 | `TotalNumberOfCertificatesIssued` | Optional | Decimal (19 digits total, 4 decimals) | Total number of depositary certificates (DRs) issued on the date of the profit distribution resolution (date of annual general meeting of the German stock corporation) by the respective DR issuer. |
| 14 | `TotalNumberOfUnderlyingShares` | Optional | Decimal (19 digits total, 4 decimals) | Total number of underlying German ordinary shares deposited by the respective DR issuer at the German depositary bank on the date of the profit resolution distribution of the German stock corporation. |
| 15 | `Ratio` | Optional | Decimal (13 digits total, 2 decimals) | Ratio of the depositary certificate to the deposited securities. The ratio of depositary certificates stipulated in the issue conditions of the depositary certificate to the domestic securities stored by the German depository. |
| 16 | `NumberOfCertificatesHeld` | Conditional | Decimal (19 digits total, 4 decimals) | Number of depositary certificates held by the creditor of the capital income (of the tax certificate) at the date of the profit distribution resolution. |
| 17 | `Paydate` | Required | Date (YYYY-MM-DD) | Date of Payment. |
| 18 | `PayoutType` | Required | Enum [`PayoutType`](#payouttype): `Cash`, `Shares` | Type of Payment. |
| 19 | `CashAccountNumber` | Required | Text (max 200) | Cash account number to which the income got credited at the custodian to whom the tax voucher person is directly contracted. |
| 20 | `AccountNumberPayingAgentLevel` | Optional | Text (max 200) | If known: Account number of the account at the level of the German paying agent in which the shares are held. |
| 21 | `GrossAmount` | Required | Decimal (16 digits total, 2 decimals) | Gross amount of the capital income generated (in Euro). |
| 22 | `NetIncomePayment` | Required | Decimal (16 digits total, 2 decimals) | Net income payment (in EURO). |
| 23 | `WithholdingTaxAmount` | Required | Decimal (16 digits total, 2 decimals) | German withholding tax amount in Euro. |
| 24 | `SurchargesAmount` | Required | Decimal (16 digits total, 2 decimals) | German solidarity surcharge amount in Euro. |
| 25 | `WithholdingTaxRate` | Required | Decimal (4 digits total, 2 decimals) | Tax rate applied to capital income (German withholding tax rate). |
| 26 | `SurchargesRate` | Required | Decimal (4 digits total, 2 decimals) | Tax rate of the solidarity surcharge applied (Solidarity surcharge rate) The current solidarity surcharge rate of 5.5% must be populated as 5.50. |
| 27 | `Nominal` | Required | Decimal (19 digits total, 4 decimals) | Quantity of securities on which the capital income is based (Number of shares / nominal value on which the income has been paid including Market Claims). |
| 28 | `NominalMoreThan5DaysPriorExdate` | Required | Decimal (19 digits total, 4 decimals) | Number of shares which have been received more than 5 days prior to the ex-date. |
| 29 | `NominalWithin5DaysPriorExdate` | Required | Decimal (19 digits total, 4 decimals) | Number of shares which have been received within 5 days prior to the ex-date. |
| 30 | `NominalLinkedToFinancialArrangement` | Required | Decimal (19 digits total, 4 decimals) | Number of German shares value which were linked to Financial Arrangements (particularly hedging instruments like options, futures etc. but also borrowed securities or securities purchased under a Repo).
                                    Financial arrangements in the meaning of Section 45b (3) of the German Income Tax Act and as defined in margin number 80 of the guidance notes of the German Ministry of Finance from April 22, 2025. According to marginal 5 of the guidance notes from the German Ministry of Finance, German shares were linked to Financial Arrangements if the Financial Arrangements were not yet settled, expired or otherwise completed on the day after the annual general meeting of the German stock corporation which distributed the dividend. |
| 31 | `NominalNotLinkedToFinancialArrangement` | Required | Decimal (19 digits total, 4 decimals) | Number of German shares which were not linked to a Financial Arrangement. |
| 32 | `NominalLinkedToSecLending` | Required | Decimal (19 digits total, 4 decimals) | Number of German shares which are linked to a securities lending transaction that had not yet been completed on the day after the annual general meeting (AGM date). |
| 33 | `NominalLinkedToRepo` | Required | Decimal (19 digits total, 4 decimals) | Number of German shares which are linked to a repo transaction that had not yet been completed on the day after the annual general meeting (AGM date). |
| 34 | `ReceiptsAndDeliveriesMode` | Required | Enum [`ReceiptsAndDeliveriesMode`](#receiptsanddeliveriesmode): `FiFo`, `All` | Whether receipts/deliveries are declared with FiFo calculation (use the '8 FIFO Trades' sheet) or without (use the '9 Raw Transactions All' sheet). |
| 35 | `FifoReceiptsMoreThan1000Available` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Are more than 1.000 (one thousand) remaining reportable receipt transactions available? |
| 36 | `FifoDeliveriesMoreThan1000Available` | Conditional | Enum [`Boolean`](#boolean): `true`, `false` | Are more than 1.000 (one thousand) reportable deliver transactions available? |
| 37 | `OpeningBalance` | Conditional | Decimal (19 digits total, 4 decimals) | Balance before 12 month. |
| 38 | `OpeningBalanceDate` | Conditional | DateTime (YYYY-MM-DDThh:mm:ss) | Date of the initial holdings evaluation. |

### 3 Tax Voucher Individuals

**Significance.** Natural persons who receive the tax certificate (voucher) - either as beneficial owner (Creditor) or as account holder - with their name, registration address and tax identification. Community members are recorded here as well.

**Cardinality.** Tax-voucher receivers total up to 2 per RequestId, counted across this sheet and '4 Tax Voucher Legal Persons'. A community counts as ONE receiver and may span up to 10 member rows that share one CommunityGroupId.

**When to fill.** For Request records at least one tax-voucher receiver is required (here or on the legal-persons sheet). Add one row per natural-person receiver or community member.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `Relationship` | Required | Enum [`TVRelationship`](#tvrelationship): `Creditor`, `AccountHolder` | Indicate the role of the tax certificate receiver person. |
| 3 | `ReceiverGroupType` | Required | Enum [`ReceiverGroupType`](#receivergrouptype): `Single`, `CommunityMember` | 'Single' for a normal recipient; 'CommunityMember' when this row is one member of a community of up to 10 persons. |
| 4 | `CommunityGroupId` | Conditional | Text (max 45) | Identifier grouping up to 10 community members into one receiver. Required when ReceiverGroupType=CommunityMember. |
| 5 | `PersonIdentifier` | Optional | Text (max 45) | Unique identifier for a person. Must be unique over subsequent files. For a subsequent request to the same person, the same identifier must be provided. To be defined by the customer institute. |
| 6 | `Title` | Optional | Text (max 20) | The person’s title if applicable. |
| 7 | `NamePrefix` | Optional | Text (max 20) | The person’s name prefix if applicable. |
| 8 | `FirstName` | Required | Text (max 45) | The person’s first name. |
| 9 | `LastName` | Required | Text (max 45) | The person’s last name. |
| 10 | `NameAffix` | Optional | Text (max 20) | The person’s name prefix if applicable. |
| 11 | `DateOfBirth` | Required | Date (YYYY-MM-DD; partial 0000 allowed) | Date of birth. Partially unknown dates are permitted: yyyy-mm-00 (unknown day), yyyy-00-00 (unknown month and day), 0000-00-00 (entirely unknown). |
| 12 | `StreetOrPostalCode` | Optional | Text (max 80) | The street name of the address. |
| 13 | `HouseNumber` | Optional | Integer (0 - 99999) | Possible range 0 – 99999. Specifying the house number “0” as a default, if no house number has been assigned, is not permissible. Specifying it as such is only permissible if the municipality has assigned the number “0”. |
| 14 | `HouseNumberAddition` | Optional | Text (max 20) | Possible additions to the house number in the address: With a house number “5a”, the “a” would be mentioned here, the “5” must be indicated in the house number field. With a house number “105-109”, the “-109” would be mentioned here. |
| 15 | `AddressAddition` | Optional | Text (max 50) | Possible addition to foreign addresses. |
| 16 | `Postcode` | Optional | Text (max 5) | The postcode of the address. For German addresses only five digits are allowed. |
| 17 | `City` | Required | Text (max 80) | The place name of the address. |
| 18 | `Country` | Optional | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | The contry of the address in ISO 3166-1 alpha-2. |
| 19 | `CountryOfTaxResidence` | Required | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | Country of tax residency in ISO 3166-1 alpha-2. |
| 20 | `PersonTaxCategory` | Required | Enum [`PersonTaxCategory`](#persontaxcategory): `German`, `NonGerman` | 'German' or 'NonGerman'. Determines which tax-ID fields apply. |
| 21 | `InvestmentMarketTaxId` | Conditional | Numeric string (German IdNr, exactly 11 digits) | The German tax identification number (IdNr) of the tax voucher person. Only digits are permitted. |
| 22 | `ForeignTaxId` | Conditional | Text (max 35) | If no German tax id number has been assigned yet: Tax identification attribute awarded by the country of residence. |

### 4 Tax Voucher Legal Persons

**Significance.** Non-natural tax-certificate receivers (companies, funds, partnerships) with name, registration address and the detailed legal-person tax identification.

**Cardinality.** Counts towards the up-to-2 tax-voucher receivers per RequestId (shared with '3 Tax Voucher Individuals').

**When to fill.** For Request records, use when a tax-voucher receiver (or community member) is a legal person.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `Relationship` | Required | Enum [`TVRelationship`](#tvrelationship): `Creditor`, `AccountHolder` | Indicate the role of the tax certificate receiver person. |
| 3 | `ReceiverGroupType` | Required | Enum [`ReceiverGroupType`](#receivergrouptype): `Single`, `CommunityMember` | 'Single' for a normal recipient; 'CommunityMember' when this row is one member of a community of up to 10 persons. |
| 4 | `CommunityGroupId` | Conditional | Text (max 45) | Identifier grouping up to 10 community members into one receiver. Required when ReceiverGroupType=CommunityMember. |
| 5 | `PersonIdentifier` | Optional | Text (max 45) | Unique identifier for a person. Must be unique over subsequent files. For a subsequent request to the same person, the same identifier must be provided. To be defined by the customer institute. |
| 6 | `Name` | Required | Text (max 256) | The name of the non-natural person. |
| 7 | `StreetOrPostalCode` | Optional | Text (max 80) | The street name of the address. |
| 8 | `HouseNumber` | Optional | Integer (0 - 99999) | Possible range 0 – 99999. Specifying the house number “0” as a default, if no house number has been assigned, is not permissible. Specifying it as such is only permissible if the municipality has assigned the number “0”. |
| 9 | `HouseNumberAddition` | Optional | Text (max 20) | Possible additions to the house number in the address: With a house number “5a”, the “a” would be mentioned here, the “5” must be indicated in the house number field. With a house number “105-109”, the “-109” would be mentioned here. |
| 10 | `AddressAddition` | Optional | Text (max 50) | Possible addition to foreign addresses. |
| 11 | `Postcode` | Optional | Text (max 5) | The postcode of the address. For German addresses only five digits are allowed. |
| 12 | `City` | Required | Text (max 80) | The place name of the address. |
| 13 | `Country` | Optional | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | The contry of the address in ISO 3166-1 alpha-2. |
| 14 | `CountryOfTaxResidence` | Required | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | Country of tax residency in ISO 3166-1 alpha-2. |
| 15 | `PersonTaxCategory` | Required | Enum [`PersonTaxCategory`](#persontaxcategory): `German`, `NonGerman` | 'German' or 'NonGerman'. Determines which tax-ID fields apply. |
| 16 | `InvestmentMarketBusinessId` | Conditional | Numeric string (German Wirtschafts-IdNr, 13 digits) | German business identification number. The business identification number of the non-natural person without a hyphen before the differentiating element. |
| 17 | `InvestmentMarketTaxNumber` | Conditional | Numeric string (German Steuernummer, 13 digits) | If a German business identification number hasn´t been assigned yet: The German tax number of the non-natural person. |
| 18 | `LEI` | Conditional | LEI (ISO 17442, 20 alphanumeric) | If neither a German business tax id number in the meaning of section 139c German General Tax Code nor a German tax id number (usually the Corporate Income Tax id number) is available, the Legal Entity Identifier (LEI). |
| 19 | `EUID` | Conditional | Text (max 200) | If neither a German business tax id number in the meaning of section 139c German General Tax Code nor a German tax id number (usually the Corporate Income Tax id number) is available nor a Legal Entity Identifier (LEI) is available, the European unique identifier (EUID; as referred to in Article 16 of Directive (EU) 2017/1132 of the European Parliament and of the Council). |
| 20 | `ForeignTaxId` | Conditional | Text (max 35) | Tax identification number assigned to the tax voucher person by its country of tax residency. |
| 21 | `LegalForm` | Conditional | Text (max 60) | The foreign legal entity type must be specified as free text. Long and short form. |
| 22 | `DateOfFoundation` | Conditional | Date (YYYY-MM-DD) | Date when the entity was established / founded / incorporated / launched. |

### 5 Third Party Individuals

**Significance.** Natural persons who are the account holder but not the beneficial owner (third parties), stating in what capacity they hold for the beneficial owner (trustee, pledgor or grantor of usufruct).

**Cardinality.** Third-party persons total up to 5 per RequestId, counted across this sheet and '6 Third Party Legal Persons'.

**When to fill.** Only when the account holder is not the beneficial owner AND the beneficial owner is disclosed. Otherwise leave empty.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `Relationship` | Required | Enum [`TPRelationship`](#tprelationship): `Trustee`, `Pledgor`, `Grantor of usufruct` | If the account holder is not the beneficial owner, this category specifies, how the account holder represents the beneficial owner. |
| 3 | `PersonIdentifier` | Optional | Text (max 45) | Unique identifier for a person. Must be unique over subsequent files. For a subsequent request to the same person, the same identifier must be provided. To be defined by the customer institute. |
| 4 | `Title` | Optional | Text (max 20) | The person’s title if applicable. |
| 5 | `NamePrefix` | Optional | Text (max 20) | The person’s name prefix if applicable. |
| 6 | `FirstName` | Required | Text (max 45) | The person’s first name. |
| 7 | `LastName` | Required | Text (max 45) | The person’s last name. |
| 8 | `NameAffix` | Optional | Text (max 20) | The person’s name prefix if applicable. |
| 9 | `DateOfBirth` | Required | Date (YYYY-MM-DD; partial 0000 allowed) | Date of birth. Partially unknown dates are permitted: yyyy-mm-00 (unknown day), yyyy-00-00 (unknown month and day), 0000-00-00 (entirely unknown). |
| 10 | `StreetOrPostalCode` | Optional | Text (max 80) | The street name of the address. |
| 11 | `HouseNumber` | Optional | Integer (0 - 99999) | Possible range 0 – 99999. Specifying the house number “0” as a default, if no house number has been assigned, is not permissible. Specifying it as such is only permissible if the municipality has assigned the number “0”. |
| 12 | `HouseNumberAddition` | Optional | Text (max 20) | Possible additions to the house number in the address: With a house number “5a”, the “a” would be mentioned here, the “5” must be indicated in the house number field. With a house number “105-109”, the “-109” would be mentioned here. |
| 13 | `AddressAddition` | Optional | Text (max 50) | Possible addition to foreign addresses. |
| 14 | `Postcode` | Optional | Text (max 5) | The postcode of the address. For German addresses only five digits are allowed. |
| 15 | `City` | Required | Text (max 80) | The place name of the address. |
| 16 | `Country` | Optional | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | The contry of the address in ISO 3166-1 alpha-2. |
| 17 | `CountryOfTaxResidence` | Required | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | Country of tax residency in ISO 3166-1 alpha-2. |
| 18 | `PersonTaxCategory` | Required | Enum [`PersonTaxCategory`](#persontaxcategory): `German`, `NonGerman` | 'German' or 'NonGerman'. Determines which tax-ID fields apply. |
| 19 | `InvestmentMarketTaxId` | Conditional | Numeric string (German IdNr, exactly 11 digits) | The German tax identification number (IdNr) of the tax voucher person. Only digits are permitted. |
| 20 | `ForeignTaxId` | Conditional | Text (max 35) | If no German tax id number has been assigned yet: Tax identification attribute awarded by the country of residence. |

### 6 Third Party Legal Persons

**Significance.** Non-natural third parties (account holders that are not the beneficial owner) with name, address and legal-person tax identification, including the special investment-funds tax number where relevant.

**Cardinality.** Counts towards the up-to-5 third-party persons per RequestId (shared with '5 Third Party Individuals').

**When to fill.** Same condition as '5 Third Party Individuals', when the third party is a legal person.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `Relationship` | Required | Enum [`TPRelationship`](#tprelationship): `Trustee`, `Pledgor`, `Grantor of usufruct` | If the account holder is not the beneficial owner, this category specifies, how the account holder represents the beneficial owner. |
| 3 | `PersonIdentifier` | Optional | Text (max 45) | Unique identifier for a person. Must be unique over subsequent files. For a subsequent request to the same person, the same identifier must be provided. To be defined by the customer institute. |
| 4 | `Name` | Required | Text (max 256) | The name of the non-natural person. |
| 5 | `StreetOrPostalCode` | Optional | Text (max 80) | The street name of the address. |
| 6 | `HouseNumber` | Optional | Integer (0 - 99999) | Possible range 0 – 99999. Specifying the house number “0” as a default, if no house number has been assigned, is not permissible. Specifying it as such is only permissible if the municipality has assigned the number “0”. |
| 7 | `HouseNumberAddition` | Optional | Text (max 20) | Possible additions to the house number in the address: With a house number “5a”, the “a” would be mentioned here, the “5” must be indicated in the house number field. With a house number “105-109”, the “-109” would be mentioned here. |
| 8 | `AddressAddition` | Optional | Text (max 50) | Possible addition to foreign addresses. |
| 9 | `Postcode` | Optional | Text (max 5) | The postcode of the address. For German addresses only five digits are allowed. |
| 10 | `City` | Required | Text (max 80) | The place name of the address. |
| 11 | `Country` | Optional | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | The contry of the address in ISO 3166-1 alpha-2. |
| 12 | `CountryOfTaxResidence` | Required | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | Country of tax residency in ISO 3166-1 alpha-2. |
| 13 | `PersonTaxCategory` | Required | Enum [`PersonTaxCategory`](#persontaxcategory): `German`, `NonGerman` | 'German' or 'NonGerman'. Determines which tax-ID fields apply. |
| 14 | `InvestmentMarketBusinessId` | Conditional | Numeric string (German Wirtschafts-IdNr, 13 digits) | German business identification number. The business identification number of the non-natural person without a hyphen before the differentiating element. |
| 15 | `InvestmentMarketTaxNumber` | Conditional | Numeric string (German Steuernummer, 13 digits) | If a German business identification number hasn´t been assigned yet: The German tax number of the non-natural person. |
| 16 | `InvestmentMarketSpecialFundsTaxNumber` | Conditional | Numeric string (German Steuernummer, 13 digits) | This specific German tax number gets assigned by the German Federal Central Tax Authority (Bundeszentralamt für Steuern) to non-German Special-Investment Funds in the meaning of Section 26 of the German Investment Tax Act (GITA) which opted to be treated as a tax transparent fund under Section 30 GITA. This is a conditional mandatory field. Please leave the field blank if you don´t meet the above condition. |
| 17 | `LEI` | Conditional | LEI (ISO 17442, 20 alphanumeric) | If neither a German business tax id number in the meaning of section 139c German General Tax Code nor a German tax id number (usually the Corporate Income Tax id number) is available, the Legal Entity Identifier (LEI). |
| 18 | `EUID` | Conditional | Text (max 200) | If neither a German business tax id number in the meaning of section 139c German General Tax Code nor a German tax id number (usually the Corporate Income Tax id number) is available nor a Legal Entity Identifier (LEI) is available, the European unique identifier (EUID; as referred to in Article 16 of Directive (EU) 2017/1132 of the European Parliament and of the Council). |
| 19 | `ForeignTaxId` | Conditional | Text (max 35) | Tax identification number assigned to the tax voucher person by its country of tax residency. |

### 7 Custody Chain

**Significance.** The ordered chain of custodians / intermediaries between the beneficiary and the German paying agent. Each link carries its name, address, tax identification, BIC, account number, account type and the nominal held.

**Cardinality.** 0..20 rows per RequestId, ordered by NumberInChain (1 = the custodian closest to the beneficiary).

**When to fill.** Required for Request records; add one row per intermediary link in the custody chain.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `NumberInChain` | Required | Integer | Order in the custody chain. 1 is the custodian with the securities account for the beneficiary of person holding in favor of the beneficiary on its account. |
| 3 | `NameOfIntermediary` | Required | Text (max 256) | Name of the depository/(sub-)custodian. |
| 4 | `StreetOrPostalCode` | Optional | Text (max 80) | The street name of the address. |
| 5 | `HouseNumber` | Optional | Integer (0 - 99999) | Possible range 0 – 99999. Specifying the house number “0” as a default, if no house number has been assigned, is not permissible. Specifying it as such is only permissible if the municipality has assigned the number “0”. |
| 6 | `HouseNumberAddition` | Optional | Text (max 20) | Possible additions to the house number in the address: With a house number “5a”, the “a” would be mentioned here, the “5” must be indicated in the house number field. With a house number “105-109”, the “-109” would be mentioned here. |
| 7 | `AddressAddition` | Optional | Text (max 50) | Possible addition to foreign addresses. |
| 8 | `Postcode` | Optional | Text (max 5) | The postcode of the address. For German addresses only five digits are allowed. |
| 9 | `City` | Required | Text (max 80) | The place name of the address. |
| 10 | `Country` | Optional | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | The contry of the address in ISO 3166-1 alpha-2. |
| 11 | `AccountNumber` | Required | Text (max 200) | Account number or securities account in which the securities are held by the customer of an intermediary (i.e. the beneficiary or the person holding the position of the beneficiary on its account or the preceding intermediary). |
| 12 | `AccountType` | Required | Enum [`AccountType`](#accounttype): `A`, `B`, `Ct`, `D`, `E`, `F`, `G` | Account type. |
| 13 | `NominalInAccount` | Required | Decimal (19 digits total, 4 decimals) | Number of shares / nominal value held in the account of the respective account holder (i.e. the tax voucher person or of the third party holding the securities in the name of the tax voucher person or the preceding intermediary) (Number of shares held in the account). |
| 14 | `BIC` | Optional | BIC (ISO 9362, 8 or 11 alphanumeric) | BIC (Bank Identifier Code) is an 8 to 11-character code used to uniquely identify banks globally during international transactions, often called a SWIFT code. Structure: Comprised of 4 letters (bank code), 2 letters (country code), 2 letters/numbers (location code), and an optional 3-digit branch code (or 'XXX' for head office). |
| 15 | `CountryOfTaxResidence` | Required | Country code (ISO 3166-1 alpha-2, 2 uppercase letters) | Country of tax residency in ISO 3166-1 alpha-2. |
| 16 | `PersonTaxCategory` | Required | Enum [`PersonTaxCategory`](#persontaxcategory): `German`, `NonGerman` | 'German' or 'NonGerman'. Determines which tax-ID fields apply. |
| 17 | `InvestmentMarketBusinessId` | Conditional | Numeric string (German Wirtschafts-IdNr, 13 digits) | German business identification number. The business identification number of the non-natural person without a hyphen before the differentiating element. |
| 18 | `InvestmentMarketTaxNumber` | Conditional | Numeric string (German Steuernummer, 13 digits) | If a German business identification number hasn´t been assigned yet: The German tax number of the non-natural person. |
| 19 | `LEI` | Conditional | LEI (ISO 17442, 20 alphanumeric) | If neither a German business tax id number in the meaning of section 139c German General Tax Code nor a German tax id number (usually the Corporate Income Tax id number) is available, the Legal Entity Identifier (LEI). |
| 20 | `EUID` | Conditional | Text (max 200) | If neither a German business tax id number in the meaning of section 139c German General Tax Code nor a German tax id number (usually the Corporate Income Tax id number) is available nor a Legal Entity Identifier (LEI) is available, the European unique identifier (EUID; as referred to in Article 16 of Directive (EU) 2017/1132 of the European Parliament and of the Council). |
| 21 | `ForeignTaxId` | Conditional | Text (max 35) | Tax identification number assigned to the tax voucher person by its country of tax residency. |

### 8 FIFO Trades

**Significance.** Receipts and deliveries within the relevant window, already reduced with FiFo (first-in-first-out) calculation by the submitter. Receipts and deliveries share this sheet and are distinguished by the Direction column.

**Cardinality.** Up to 1000 Receipt rows and up to 1000 Delivery rows per RequestId.

**When to fill.** Only when ReceiptsAndDeliveriesMode = FiFo. Leave empty when the mode = All.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `Direction` | Required | Enum [`FifoDirection`](#fifodirection): `Receipt`, `Delivery` | 'Receipt' (purchase / delivery-in / loan / repo) or 'Delivery' (sale / delivery-out / loan / repo). Up to 1000 rows each per request. |
| 3 | `Nominal` | Required | Decimal (19 digits total, 4 decimals) | Number of shares / nominal value on which the transaction is based (= per receipt trade with acquisition date < 1 year prior to the day of the annual shareholders' meeting (day of the dividend distribution resolution). |
| 4 | `TradeDate` | Required | Date (YYYY-MM-DD) | Trade Date. |
| 5 | `TransactionType` | Required | Enum [`FifoTransactionType`](#fifotransactiontype): `PO`, `SO`, `DT`, `TL`, `TP`, `RL`, `RP` | Category of securities trading transacted. |
| 6 | `ContractualSettlementDate` | Required | Date (YYYY-MM-DD) | Agreed settlement date (Contractual settlement date). |
| 7 | `ActualSettlementDate` | Required | Date (YYYY-MM-DD) | Actual settlement date. |
| 8 | `TransactionReference` | Optional | Text (max 45) | Transaction reference beneficial owner/customer . |
| 9 | `TransactionReferencePayingAgent` | Optional | Text (max 45) | Transaction reference German Paying Agent. |

### 9 Raw Transactions All

**Significance.** The full, unreduced ledger of receipts and deliveries (no FiFo applied); the German paying agent performs the FiFo calculation. The opening balance is captured on the Security Related Information sheet; every movement is one row here.

**Cardinality.** Unbounded rows per RequestId.

**When to fill.** Only when ReceiptsAndDeliveriesMode = All. Leave empty when the mode = FiFo.

| # | Field | Requiredness | Type / Allowed values | Description |
| --- | --- | --- | --- | --- |
| 1 | `RequestId` | Required | Text (identifier used to link the sheets; any unique value) | Foreign key. Must match a RequestId in the '1 Requests Master' sheet. |
| 2 | `Nominal` | Required | Decimal (19 digits total, 4 decimals) | Number of shares / nominal value on which the transaction is based (= per deliver trade, if the trade date is within 47 calendar days after the date of the annual shareholders' meeting (AGM date; day of the dividend distribution resolution). |
| 3 | `TradeDate` | Required | Date (YYYY-MM-DD) | Trade Date. |
| 4 | `IntraDaySequence` | Required | Integer | Sortable number, for the case that more than one transaction per trade date is delivered. |
| 5 | `TransactionType` | Required | Enum [`RawTransactionType`](#rawtransactiontype): `Buy`, `Sell`, `Transfer`, `SlbOpen`, `SlbClose`, `RepoOpen`, `RepoClose`, `Dividend`, `Interest`, `Other` | Category of securities trading transacted. |
| 6 | `ContractualSettlementDate` | Required | Date (YYYY-MM-DD) | Agreed settlement date (Contractual settlement date). |
| 7 | `ActualSettlementDate` | Required | Date (YYYY-MM-DD) | Actual settlement date. |
| 8 | `COAF` | Conditional | Text (Corporate Action Event Reference, max 16) | Corporate action event reference (COAF). Must be provided, if dividend or interest transaction type. |
| 9 | `TransactionReference` | Optional | Text (max 45) | Transaction reference beneficial owner/customer . |
| 10 | `TransactionReferencePayingAgent` | Optional | Text (max 45) | Transaction reference German Paying Agent. |

## Enumerations reference

Every value that can be chosen from a dropdown, with its meaning and the fields that use it.

### Boolean

*Used in:* `1 Requests Master.IsCorrectionRequest`, `2 Security Related Information.IsDepositaryReceipt`, `2 Security Related Information.FifoReceiptsMoreThan1000Available`, `2 Security Related Information.FifoDeliveriesMoreThan1000Available`

| Value | Meaning |
| --- | --- |
| `true` | Yes - the condition applies. |
| `false` | No - the condition does not apply. |

### RecordType

*Used in:* `1 Requests Master.RecordType`

| Value | Meaning |
| --- | --- |
| `Request` | A MiKaDiv reporting-for-income disclosure (a new or corrective submission). |
| `Cancel` | Cancellation of a previously submitted disclosure request; only the master cancellation fields are filled and the child sheets stay empty. |

### RequestedService

*Used in:* `1 Requests Master.RequestedService`

| Value | Meaning |
| --- | --- |
| `TaxReportAndCertificate` | The custodian is to perform a reporting of type 11. For domestic taxpayers, a tax certificate shall be issued. |
| `Reclaim` | The custodian should create or forward the application for reclaim of withholding tax. Additional information for the application needs to be delivered. |
| `Relief` | The custodian provided relief at source and additional information gets provided via the request. |

### RequestedAttestationType

*Used in:* `1 Requests Master.RequestedAttestationType`

| Value | Meaning |
| --- | --- |
| `BV` | BV for template III. |
| `PV` | PV for template I. |
| `SB` | SB for collective tax voucher. |

### AccountType

*Used in:* `1 Requests Master.AccountType`, `7 Custody Chain.AccountType`

| Value | Meaning |
| --- | --- |
| `A` | A - Own Account |
| `B` | B – Third-party general account |
| `Ct` | C – Third-party individual account |
| `D` | D – Detail register account of a third-party general account |
| `E` | E – Third-party global account other than B |
| `F` | F – Individual account of a securities holder other than D or C |
| `G` | G – Other type of account |

### AccountRelationship

*Used in:* `1 Requests Master.AccountRelationship`

| Value | Meaning |
| --- | --- |
| `Trust` | Fiduciary account |
| `Usufruct` | Securities account held in usufruct |
| `Pledge` | Pledged securities account |

### TypeOfSecurity

*Used in:* `2 Security Related Information.TypeOfSecurity`

| Value | Meaning |
| --- | --- |
| `Equity` | Equity security (share). Represents ownership in a corporation and entitles the holder to dividends and voting rights. Capital income typically arises from dividend distributions. |
| `Bond` | Debt security (bond). Represents a creditor relationship with the issuer and entitles the holder to interest payments. Capital income typically arises from interest distributions. |
| `DepositaryReceipt` | Depositary receipt (e.g. ADR, GDR). A certificate issued by a depositary bank representing shares of a foreign company held in custody. Capital income arises from the underlying dividend distributions of the foreign security. |

### PayoutType

*Used in:* `2 Security Related Information.PayoutType`

| Value | Meaning |
| --- | --- |
| `Cash` | Payment in Cash. |
| `Shares` | Payment in Shares (stock dividend). |

### ReceiptsAndDeliveriesMode

*Used in:* `2 Security Related Information.ReceiptsAndDeliveriesMode`

| Value | Meaning |
| --- | --- |
| `FiFo` | Receipts and deliveries are declared WITH FiFo calculation already applied by the submitter - fill the FIFO Trades sheet. |
| `All` | Receipts and deliveries are declared WITHOUT FiFo (the German paying agent applies FiFo) - fill the Raw Transactions All sheet. |

### TVRelationship

*Used in:* `3 Tax Voucher Individuals.Relationship`, `4 Tax Voucher Legal Persons.Relationship`

| Value | Meaning |
| --- | --- |
| `Creditor` | Creditor (beneficial owner). |
| `AccountHolder` | Account holder (not the beneficial owner). |

### TPRelationship

*Used in:* `5 Third Party Individuals.Relationship`, `6 Third Party Legal Persons.Relationship`

| Value | Meaning |
| --- | --- |
| `Trustee` | Trustee. |
| `Pledgor` | Pledgor. |
| `Grantor of usufruct` | Grantor of usufruct. |

### ReceiverGroupType

*Used in:* `3 Tax Voucher Individuals.ReceiverGroupType`, `4 Tax Voucher Legal Persons.ReceiverGroupType`

| Value | Meaning |
| --- | --- |
| `Single` | A single tax-certificate receiver (one individual or one legal person). |
| `CommunityMember` | One member of a community of up to 10 persons; all members share the same CommunityGroupId and together form one receiver. |

### PersonTaxCategory

*Used in:* `3 Tax Voucher Individuals.PersonTaxCategory`, `4 Tax Voucher Legal Persons.PersonTaxCategory`, `5 Third Party Individuals.PersonTaxCategory`, `6 Third Party Legal Persons.PersonTaxCategory`, `7 Custody Chain.PersonTaxCategory`

| Value | Meaning |
| --- | --- |
| `German` | German-identified person: provide German identifiers (IdNr / Wirtschafts-IdNr / Steuernummer). |
| `NonGerman` | Non-German person: provide foreign identifiers (ForeignTaxId, LEI, EUID, or legal form + date of foundation, as applicable). |

### FifoDirection

*Used in:* `8 FIFO Trades.Direction`

| Value | Meaning |
| --- | --- |
| `Receipt` | Receipt trade: purchases, book-entry transfers in (delivery in), securities lending, and repo transactions. |
| `Delivery` | Delivery trade: sales, book-entry transfers out (delivery out), securities lending, and repo transactions. |

### FifoTransactionType

*Used in:* `8 FIFO Trades.TransactionType`

| Value | Meaning |
| --- | --- |
| `PO` | Acquisition of securities. |
| `SO` | Sale of securities. |
| `DT` | Book-entry transfer (delivery in). |
| `TL` | Transfer based on a securities loan. |
| `TP` | Transfer based on a repo transaction. |
| `RL` | Retransfer based on a securities loan. |
| `RP` | Retransfer based on a repo transaction. |

### RawTransactionType

*Used in:* `9 Raw Transactions All.TransactionType`

| Value | Meaning |
| --- | --- |
| `Buy` | Buy of securities. |
| `Sell` | Sell of securities. |
| `Transfer` | Book-entry transfer. |
| `SlbOpen` | Transfer based on a securities loan. |
| `SlbClose` | Retransfer based on a securities loan. |
| `RepoOpen` | Transfer based on a repo transaction. |
| `RepoClose` | Retransfer based on a repo transaction. |
| `Dividend` | Dividend distribution. |
| `Interest` | Interest payment. |
| `Other` | Other. |
