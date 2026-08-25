"""Layer 0.5: KaFE's status-code catalog.

Hand-transcribed from the official BZSt DIP-KAFE v1.4.0 communication handbook's
own status-code appendix (Annex 7.4, "7.4. Status codes" / "Table 70: Status
codes", pages 190-212 of
kafe-research/handbook/Kommunikationshandbuch_DIP-KAFE_v1_4_0_en.pdf) -- these
codes exist only inside a PDF, with no machine-readable source, so this is the
one genuinely hand-authored data file in this module (everything else is
generated from the real XSD).

The handbook's own table has 213 rows total (code "0000" plus 212 further
error/validation codes), not 219 -- 219 was this plan's own best estimate from
an earlier research pass, corrected here after reading the full appendix.

Two uses: (1) kafe/mapping.py layers real conditional-mandatory requiredness on
top of the XSD's own required=/minOccurs wherever they disagree (mainly the
7xxx / Par50jEStG range, where almost every field is minOccurs=0 in the raw
XSD but has real conditional-mandatory logic expressed only here); (2) a full
status/error-code reference appendix is rendered into kafe/request.bs's
error-handling section via kafe/generate_status_codes_docs.py, since banks see
these codes today via kafe-rm.xsd's ValidierungsergebnisListe and the existing
interface document has no such appendix at all.

Messages are transcribed verbatim from the handbook's own English text.
A handful of the handbook's own apparent typos (e.g. "effecitve" for
"effective" in codes 3300/3301/3302, "missind" for "missing" in code 4426,
and "ist" for "is" in code 6402) were identified during transcription and
corrected here rather than preserved, since visibly-broken English in a
published interface reference is a worse outcome for readers than a minor
deviation from the source PDF's own typos.
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
    if code == "0000":
        # "0000" (OK) isn't part of any 1xxx-7xxx range -- it's the
        # handbook's own global success code, standing outside the 7-range
        # error/validation taxonomy that RANGE_ORDER enumerates.
        return "0000 - OK"
    first_digit = code[0]
    index = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6}[first_digit]
    return RANGE_ORDER[index]


# (code, message) pairs, transcribed verbatim from the handbook's Annex 7.4
# ("7.4. Status codes" / "Table 70: Status codes", pages 190-212).
# "0000" (OK) plus all 212 real error/validation codes -- 213 total.
_RAW: list[tuple[str, str]] = [
    ("1998", "End-to-end staleness test -- Task 3."),
    ('0000', 'OK'),
    ('1000', 'The XML file does not correspond to the specified schema.'),
    ('1001', 'The AntragId has already been used.'),
    ('1002', 'The maximum number of authorised applications per file has been exceeded.'),
    ('1100', 'The AnhangId has already been used.'),
    ('1101', 'The annex (PDF file) is missing.'),
    ('1102', 'The annex (file) could not be assigned.'),
    ('1103', 'The annex is not a PDF file.'),
    ('2100', 'At least one legal basis must be selected.'),
    ('2101', 'It is not permitted to combine the legal bases.'),
    ('2200', 'The Ansaessigkeitsstaat element (country of residence) is missing (conditional mandatory field).'),
    ('2300', 'The Rechtsform element (legal form) is missing (conditional mandatory field).'),
    ('2400', 'The GewinnePG_CH element is missing (conditional mandatory field).'),
    ('2401', 'The GewinnePG_CH element is not permitted.'),
    ('2500', 'The BegruendungArt63AEUV element (justification article 63 TFEU) is missing (conditional mandatory field).'),
    ('2501', 'The BegruendungArt63AEUV element (justification article 63 TFEU) is not permitted.'),
    ('2600', 'The application was not effectively filed.'),
    ('2700', 'The AntragIntOrg element is missing (conditional mandatory field).'),
    ('2701', 'The AntragIntOrg element is not permitted for this claim basis.'),
    ('2800', 'The AntragPar11InvStG element is missing (conditional mandatory field).'),
    ('2801', 'The AntragPar11InvStG element is not permitted for this legal form.'),
    ('2900', 'The applicant has not assured that the information provided is true to the best of his knowledge and belief.'),
    ('3000', 'The Vollmacht element (authorisation) is missing (conditional mandatory field).'),
    ('3010', 'In the legal form NATP the NichtNatuerlichePerson element is required (conditional mandatory field).'),
    ('3020', 'In this legal form the NichtNatuerlichePerson element is required (conditional mandatory field).'),
    ('3100', 'The date of birth must not be in the future.'),
    ('3101', 'The StaatsangehoerigkeitKW element is missing (conditional mandatory field).'),
    ('3102', 'The StaatsangehoerigkeitCH element is missing (conditional mandatory field).'),
    ('3103', 'The StaatsangehoerigkeitDE element is missing (conditional mandatory field).'),
    ('3200', 'The incorporation date must not be in the future.'),
    ('3300', 'The GeschaeftsleitungOrt element (effective management location) is missing (conditional mandatory field).'),
    ('3301', 'The GeschaeftsleitungOrt element (effective management location) is not permitted.'),
    ('3302', 'The address of the person with limited tax liability is the same as the different place of effective management.'),
    ('3400', 'The specified Legal Entity Identifier (LEI) is invalid.'),
    ('3500', 'The Register element is missing (conditional mandatory field).'),
    ('3501', 'The Registerbehoerde element (Register authority) is not permitted.'),
    ('3502', 'The Registernummer element (register number) is missing (conditional mandatory field).'),
    ('3503', 'The Registernummer element (register number) is not permitted.'),
    ('3504', 'The Registerauszug element (register excerpt) is missing (conditional mandatory field).'),
    ('3505', 'The Registerauszug element (register excerpt) is not permitted.'),
    ('3600', 'The Boerse element (stock exchange) is missing (conditional mandatory field).'),
    ('3601', 'The Boerse element (stock exchange) is not permitted.'),
    ('3602', 'The ISIN element is missing (conditional mandatory field).'),
    ('3603', 'The ISIN element is not permitted.'),
    ('3604', 'The ISIN indicated is invalid.'),
    ('3605', 'The Boersenplatz element (stock exchange on which the stocks are traded) is not permitted.'),
    ('3700', 'The GesetzlicheVertretung element (legal representative) is missing (conditional mandatory field).'),
    ('3800', 'The element Gruendungsstaat is missing.'),
    ('3801', 'The element Gruendungsstaat is not permitted.'),
    ('4001', 'The IdNr element is not permitted.'),
    ('4002', 'The specified IdNr is invalid.'),
    ('4003', 'The W-IdNr element is not permitted.'),
    ('4004', 'The specified W-IdNr is invalid.'),
    ('4005', 'The TIN element is missing (conditional mandatory field).'),
    ('4006', 'The KennNr (identification number of the Federal Central Tax Office) is invalid.'),
    ('4100', 'The TranspGebilde element (transparent entity) is missing (conditional mandatory field).'),
    ('4101', 'The TranspGebilde element (transparent entity) is not permitted.'),
    ('4200', 'The OptionKStG element is missing (conditional mandatory field).'),
    ('4201', 'The OptionKStG element is not permitted.'),
    ('4202', 'The Steuerbehoerde element (tax authority) is missing (conditional mandatory field).'),
    ('4203', 'The Steuerbehoerde element (tax authority) is not permitted.'),
    ('4204', 'The Aktenzeichen element (file number) is missing (conditional mandatory field).'),
    ('4205', 'The Aktenzeichen element (file number) is not permitted.'),
    ('4206', 'The file number given is invalid.'),
    ('4300', 'The Investmentfonds element (investment fund) element is missing (conditional mandatory field).'),
    ('4301', 'The Investmentfonds element (investment fund) is not permitted for this legal form.'),
    ('4302', 'The Steuerbehoerde element (tax authority) is missing (conditional mandatory field).'),
    ('4303', 'The Steuerbehoerde element (tax authority) is not permitted.'),
    ('4304', 'The Aktenzeichen element (file number) is not permitted.'),
    ('4305', 'The file number given is invalid.'),
    ('4306', 'The GueltigVon element (valid from) is not permitted.'),
    ('4307', 'The GueltigBis element (valid until) is not permitted.'),
    ('4308', 'The specified validity period of the status certificate is invalid.'),
    ('4310', 'The Transparenzoption element (transparency option) is missing (conditional mandatory field).'),
    ('4311', 'The Transparenzoption element (transparency option) is not permitted.'),
    ('4400', 'The SchweizFragen element (Switzerland-Questions) is missing (conditional mandatory field).'),
    ('4401', 'The SchweizFragen element (Switzerland-Questions) is not permitted.'),
    ('4402', 'The SteuerpflichtDE element is missing (conditional mandatory field).'),
    ('4403', 'The StpflDE5Jahre element is missing (conditional mandatory field).'),
    ('4404', 'The StpflDE5Jahre element is not permitted.'),
    ('4410', 'The UnselbstArbeit element is missing (conditional mandatory field).'),
    ('4411', 'The UnselbstArbeit element is not permitted.'),
    ('4420', 'The Arbeitsgeber element (employer) is missing (conditional mandatory field).'),
    ('4421', 'The Arbeitsgeber element (employer) is not permitted.'),
    ('4422', "The Arbeitgeberbescheinigung element (employer's certificate) is missing (conditional mandatory field)."),
    ('4423', 'The Arbeitgeberbescheinigung element (employer attestation) is not permitted.'),
    ('4424', 'The InteresseArbeitgeber element is missing (conditional mandatory field).'),
    ('4425', 'The InteresseArbeitgeber element is not permitted.'),
    ('4426', 'The InteresseBeschreibung element is missing (conditional mandatory field).'),
    ('4427', 'The InteresseBeschreibung element is not permitted.'),
    ('4430', 'The Zuzugsdatum element (move-in date) is missing (conditional mandatory field).'),
    ('4431', 'The Zuzugsdatum element (move-in date) is not permitted.'),
    ('4432', 'The Zuzugsdatum element (move-in date) is invalid.'),
    ('4433', 'The Zuzugsgruende element (reasons for moving) is missing (conditional mandatory field).'),
    ('4434', 'The Zuzugsgruende element (reasons for moving) is not permitted.'),
    ('4500', 'The FinanzamtDE element (german tax office) is missing (conditional mandatory field).'),
    ('4501', 'The Stnr element (tax number) is missing (conditional mandatory field).'),
    ('4502', 'The Stnr element (tax number) is not permitted.'),
    ('4503', 'The Stnr element (tax number) is invalid.'),
    ('4510', 'The SteuerpflichtDE element is missing (conditional mandatory field).'),
    ('4511', 'The SteuerpflichtDE element is not permitted.'),
    ('4520', 'The SteuerpflichtDE5J element is missing (conditional mandatory field).'),
    ('4521', 'The SteuerpflichtDE5J element is not permitted.'),
    ('4530', 'The StpflDEEndeJahr element is missing (conditional mandatory field).'),
    ('4531', 'The StpflDEEndeJahr element is not permitted.'),
    ('4532', 'The specified year is invalid.'),
    ('4600', 'The Ansaessigkeitsbescheinigung element (Certificate of Residence) is missing (conditional mandatory field).'),
    ('4601', 'The specified issue date is invalid.'),
    ('4602', 'The specified period is invalid.'),
    ('4700', 'The SteuerbeguenstigteZweck element is missing (conditional mandatory field).'),
    ('4701', 'The SteuerbeguenstigteZwecke element is only permitted if the basis for the claim was section 32 (6) German Corporation Tax Act.'),
    ('4710', 'The ZER element is missing (conditional mandatory field).'),
    ('4712', 'The Referenznummer element is missing (conditional mandatory field).'),
    ('4725', 'The GemeinnuetzigeZwecke element is missing (conditional mandatory field).'),
    ('4743', 'The FoerderungDEfehlt element is missing (conditional mandatory field).'),
    ('4745', 'The AnsehenDE element is missing (conditional mandatory field).'),
    ('5001', 'The specified IBAN is invalid.'),
    ('5002', 'The specified BIC is invalid.'),
    ('6000', 'The ErtragId is not consecutive.'),
    ('6100', 'The capital income type is not permitted.'),
    ('6110', 'The Hinterlegungsscheine element (depository receipts) is missing (conditional mandatory field).'),
    ('6111', 'The Hinterlegungsscheine element (depository receipts) is not permitted.'),
    ('6112', 'The ISIN element is missing (conditional mandatory field).'),
    ('6113', 'The ISIN element is not permitted.'),
    ('6114', 'The specified ISIN is invalid.'),
    ('6115', 'The Underlying element is not permitted.'),
    ('6116', 'The specified ISIN is invalid.'),
    ('6120', 'The Stnr element (tax number) is not permitted.'),
    ('6121', 'The specified tax number is invalid.'),
    ('6122', 'The VersicherungsNr element (insurance number) is missing (conditional mandatory field).'),
    ('6123', 'The VersicherungsNr element (insurance number) is not permitted.'),
    ('6130', 'The date of inflow of capital income is invalid.'),
    ('6131', 'The AnzahlAnteile element (number of shares/bonds) is missing (conditional mandatory field).'),
    ('6132', 'The AnzahlAnteile element (number of shares/bonds) is not permitted.'),
    ('6150', 'The vGA element (constructive dividend) is missing (conditional mandatory field).'),
    ('6151', 'The vGA element (constructive dividend) is not permitted.'),
    ('6160', 'The SitzNichtDE element is missing (conditional mandatory field).'),
    ('6161', 'The SitzNichtDE element is not permitted.'),
    ('6162', 'The WohnsitzDE element is missing (conditional mandatory field).'),
    ('6163', 'The WohnsitzDE element is not permitted.'),
    ('6170', 'The Steuerbefreiung element (tax exemption) is missing (conditional mandatory field).'),
    ('6171', 'The Steuerbefreiung element (tax exemption) is not permitted.'),
    ('6180', 'The BetriebsstaetteDE element is missing (conditional mandatory field).'),
    ('6181', 'The BetriebsstaetteDE element is not permitted.'),
    ('6200', 'The RemittanceBase element is missing (conditional mandatory field).'),
    ('6201', 'The RemittanceBase element is not permitted.'),
    ('6210', 'The RemBaseUeberweisung element is missing (conditional mandatory field).'),
    ('6211', 'The RemBaseUeberweisung element is not permitted.'),
    ('6220', 'The RemBaseBescheid element is missing (conditional mandatory field).'),
    ('6230', 'The RemBaseNachweis element is missing (conditional mandatory field).'),
    ('6300', 'The MittelbareBeteiligung element (indirect holding) is missing (conditional mandatory field).'),
    ('6301', 'The MittelbareBeteiligung element (indirect holding) is not permitted.'),
    ('6302', 'The EhegattenGbR element is missing (conditional mandatory field).'),
    ('6303', 'The EhegattenGbR element is not permitted.'),
    ('6310', 'The Beteiligungskette element (chain of companies) is missing (conditional mandatory field).'),
    ('6311', 'The Beteiligungskette element (chain of companies) is not permitted.'),
    ('6320', 'The BeteiligungsId is not consecutive.'),
    ('6330', 'The specified tax number is invalid.'),
    ('6340', 'The Ansaessigkeitsstaat element (country of residence) is missing (conditional mandatory field).'),
    ('6341', 'The Ansaessigkeitsstaat element (country of residence) is not permitted.'),
    ('6350', 'The TIN element is not permitted.'),
    ('6360', 'The amount of the indirect investment does not correspond to the product of the individual investment amounts.'),
    ('6400', 'The Ordnungsnummer element (serial number) is missing (conditional mandatory field).'),
    ('6401', 'The Ordnungsnummer element (serial number) is not permitted.'),
    ('6402', 'The specified Ordnungsnummer (serial number) is invalid.'),
    ('6410', 'The amount of withholding tax is implausible.'),
    ('6420', 'The BPBericht element (tax audit report) is missing (conditional mandatory field).'),
    ('6421', 'The BPBericht element (tax audit report) is not permitted.'),
    ('6430', 'The WPProspekt_Vertrag element (securities prospectus or contract) is missing (conditional mandatory field).'),
    ('6431', 'The WPProspekt_Vertrag element (securities prospectus or contract) is not permitted.'),
    ('6440', 'The ZahlungsnachweisFA element is missing (conditional mandatory field).'),
    ('6441', 'The ZahlungsnachweisFA element is not permitted.'),
    ('6500', 'The WesentlicheBeteiligung element is missing (conditional mandatory field).'),
    ('6501', 'The WesentlicheBeteiligung element is not permitted.'),
    ('6510', 'The WesentlBeteiligung element is missing (conditional mandatory field).'),
    ('6511', 'The WesentlBeteiligung element is not permitted.'),
    ('6520', 'The WesentlBeteiligungHoehe element is missing (conditional mandatory field).'),
    ('6521', 'The WesentlBeteiligungHoehe element is not permitted.'),
    ('6530', 'The Beteiligungsdauer12M element is missing (conditional mandatory field).'),
    ('6531', 'The Beteiligungsdauer12M element is not permitted.'),
    ('6532', 'The Beteiligungsdauer18M element is missing (conditional mandatory field).'),
    ('6533', 'The Beteiligungsdauer18M element is not permitted.'),
    ('6534', 'The Beteiligungsdauer6M element is missing (conditional mandatory field).'),
    ('6535', 'The Beteiligungsdauer6M element is not permitted.'),
    ('6600', 'The element UnbeschraenktAuslaendKoerperschaftstpfl is missing.'),
    ('6601', 'The element UnbeschraenktAuslaendKoerperschaftstpfl is not permitted.'),
    ('6602', 'The element Anrechnungsbetrag is missing.'),
    ('6603', 'The element Anrechnungsbetrag is not permitted.'),
    ('6604', 'The element Anrechnungsnachweis is missing.'),
    ('6605', 'The element Anrechnungsnachweis is not permitted.'),
    ('7104', 'The number of shares is implausible.'),
    ('7200', 'The MinWertAendRisiko element (Minimum risk of change in value) is missing (conditional mandatory field).'),
    ('7201', 'The MinWertAendRisiko element (Minimum risk of change in value) is not permitted.'),
    ('7210', 'The element RisikoMin70 is missing (conditional mandatory field).'),
    ('7211', 'The number of shares is implausible.'),
    ('7300', 'The WeiterlVerpflichtung element (obligation to forward) is missing (conditional mandatory field).'),
    ('7301', 'The WeiterlVerpflichtung element (obligation to forward) is not permitted.'),
    ('7310', 'The WeiterlVerpflAnteile element is missing (conditional mandatory field).'),
    ('7311', 'The number of shares is implausible.'),
    ('7400', 'The RueckgabeVerpflichtung element (obligation to return) is missing (conditional mandatory field).'),
    ('7401', 'The RueckgabeVerpflichtung element (obligation to return) is not permitted.'),
    ('7410', 'The RueckgabeVerpflAnteile element is missing (conditional mandatory field).'),
    ('7500', 'The Depotnummer element (Account / deposit number) exists several times.'),
    ('7501', 'The date of the opening balance is implausible.'),
    ('7502', 'The date of the closing balance is implausible.'),
    ('7503', 'The closing balance is implausible.'),
    ('7600', 'The Transaktionen element (transactions) is missing (conditional mandatory field).'),
    ('7601', 'The TransactionId is not consecutive.'),
    ('7610', 'The specified trading day is implausible.'),
    ('7620', 'The specified transaction is not authorised for this transaction type.'),
    ('7630', 'The number of shares is implausible.'),
    ('7640', 'The agreed settlement date is implausible.'),
    ('7650', 'The actual settlement date is implausible.'),
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
