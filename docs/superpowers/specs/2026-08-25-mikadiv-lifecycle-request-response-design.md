# MiKaDiv lifecycle: Request/Response split — Design

**Status:** Design approved 2026-08-25. Not yet implemented — this doc is the input to
an implementation plan (via the `writing-plans` process), not a plan itself.

**Ecosystem placement:** `bulk-platform`'s `docs/superpowers/PROGRESS.md`, item 8 sub-project
4 ("Extend the existing `mikadiv-vib/` OpenFASTER module with the lifecycle state machine").
This design covers only the OpenFASTER spec-side work (this repo); the backend data-model
implication for `bulk-platform` (a `RequestId`-chain-tracking entity) is explicitly out of
scope here and is recorded separately in that PROGRESS.md entry's own "Backend data-model
implication" note, to be designed when that sub-project reaches backend implementation.

## 1. Context and motivation

The current `mikadiv-vib` module (shipped in the site-structure-overview and
mikadiv-vib-rename-and-site-polish sub-projects) documents only the **outbound** side of
MiKaDiv third-party disclosure: everything is generated from `ThirdPartyDisclosureRequest.xsd`,
and its own "Source schema" section states this explicitly. It has never been checked against
VIB's real published material — the module's hand-written prose (as opposed to the
auto-generated data dictionary) was authored by hand, without access to VIB's actual sample
data or the response side of the protocol.

A shared VIB Google Drive folder (`Request/` + `Response/` subfolders — 9 real sample XMLs,
`ThirdPartyDisclosureRequest.xsd`, `ThirdPartyDisclosureResponse.xsd`, and one real response
sample) was deep-read and cross-verified against the live site via a 15-agent research pass.
Two things fell out of that research that reshape this sub-project's scope:

1. **VIB publishes a full second schema — the Response — that the site has zero
   representation of.** Not simplified, not partial: completely absent. A reader of the
   current site has no way to know how a submitted disclosure is ever acknowledged,
   confirmed, or rejected.
2. **The site's own hand-written prose contains real, verifiable errors**, all in the
   "Linking model" section and the Excel template's legend — not in the auto-generated data
   dictionary, which checked out accurate. See §6.

This design scopes strictly to what's **verifiable against VIB's own XSDs** — the BZSt
MiKaDiv-FM handbook's broader lifecycle claims (a prior version of this PROGRESS.md entry's
`Typ=E/K`/`MeldeartErg`/10-day-hold language) are explicitly out of scope: they can't yet be
checked against a schema this project actually has in hand, and — per operator direction —
aren't the concern of this pass regardless.

## 2. The real request-type taxonomy (grounded in the XSD + real samples)

VIB's `ThirdPartyDisclosureRequest.xsd` defines a root `<ThirdPartyDisclosureRequest>` whose
content is an unbounded choice between two element types. There is no third type, no
"supplement"/"amendment"/version-number vocabulary anywhere in this schema (confirmed via a
full-file read — the string "Erg" or any supplement concept does not appear):

- **New Report** — `RequestMiKaDivReportingForIncomeType`, `IsCorrectionRequest=false` (or
  omitted; the attribute is optional and defaults to representing a plain new submission).
  Carries the full disclosure payload (account owner, income, tax computation, custody chain,
  FIFO receipts/deliveries).
- **Correction** — the *same* `RequestMiKaDivReportingForIncomeType`, with
  `IsCorrectionRequest="true"` plus `PreviousRequestIdForCorrection` (a `UUIDType` reference to
  the `RequestId` being corrected) and an optional `ReportSerialNumber` (a second,
  paying-agent-issued reference, documented as an "(additional)" correlation key, usable only
  once the paying agent has already responded to the original). **A correction is a full
  resubmission, not a delta** — confirmed against the real sample `Sample8-Correction.xml`,
  which repeats the entire account-owner/income/custody-chain/FIFO payload verbatim, tagged
  only by the two correction attributes. The XSD itself enforces no co-occurrence constraint
  between `IsCorrectionRequest` and `PreviousRequestIdForCorrection` — both are independently
  optional at the schema level (prose-only requirement, not machine-enforced).
- **Cancellation** — a structurally distinct type, `CancelMiKaDivReportingForIncomeType`, whose
  `xs:sequence` is **empty**: no income/custody/receipts content is possible. It carries only
  the base `RequestDisclosureType` attributes (`RequestId`, `Timestamp`, `AccountNumber`) plus a
  **required** `PreviousRequestIdForCancellation` and an optional `ReportSerialNumber`.
  Cancellation intent is structurally unambiguous (the reference is `use="required"`); a real
  sample, `Sample9-Cancellation.xml`, is 13 lines / 699 bytes — the smallest sample in the set,
  confirming a cancellation payload is intentionally minimal.

**A real, coherent 3-hop lifecycle chain is demonstrated across the sample set**, discovered
by cross-referencing `RequestId`s across files: the Response sample's `RequestId`
(`6f6b6539-...`) is exactly `Sample8-Correction.xml`'s `PreviousRequestIdForCorrection`, and
`Sample8`'s own `RequestId` (`7d6b6539-...`) is exactly `Sample9-Cancellation.xml`'s
`PreviousRequestIdForCancellation`. This is genuinely useful worked-example material — original
request → success response → correction of it → cancellation of the correction — all wired
together purely by `RequestId` cross-references, with no lifecycle field inside the schema
itself naming which stage produced a given message. (The sample set's own dates are internally
inconsistent if read as a literal timeline — the correction/cancellation timestamps precede the
response's — so treat the chain as illustrative of the reference mechanism, not as a literally
ordered narrative, when reusing it as a worked example.)

**Two other, orthogonal correlation mechanisms exist and are worth documenting alongside the
three request types**, since they support cross-submission continuity independent of
correction/cancellation: `PersonType@PersonIdentifier` and `CapitalIncomeType@IncomeIdentifier`
are both documented as "must be unique over subsequent files... the same identifier must be
provided for a subsequent request to the same [person/income]" — a stable-identity convention
across a longer time series of separate submissions, distinct from the `RequestId`-chaining
used for correction/cancellation.

**No `xs:key`/`xs:keyref`/`xs:unique`/`xs:assert` constructs exist anywhere in the request
XSD** (confirmed via grep) — every referential-integrity rule (RequestId global uniqueness,
`Previous*RequestId` pointing at a real prior `RequestId`) is documented only in prose, not
machine-enforced by the schema itself. Worth noting explicitly in the doc: the wire format
trusts the producer to get this right.

## 3. Origination mechanism per type, and the Excel template change

Because Correction and Cancellation both **reference** an already-submitted `RequestId` the
platform already holds (it processed the original), and Correction requires the *entire* prior
payload resubmitted (data the platform already has on file), routing either through a fresh
Excel upload is redundant and error-prone. This design adopts an asymmetric split:

- **New Report → stays Excel-driven.** Bulk, many-creditors-at-once input via the existing
  template, matching the platform's established container/dataset ingestion pattern.
- **Correction / Cancellation → platform-UI-driven**, not Excel. The platform generates the
  correction's full-resubmission payload from its own stored data (the bank supplies only what
  changed) or the cancellation's bare reference, through a stage-then-apply flow: mark a
  reporting corrected/cancelled in the dashboard, then a single "Apply" action batch-generates
  and submits the resulting XML(s). (How this stages/batches, and the backend entity model
  behind it, is `bulk-platform`'s concern, not this spec's — see §1's scope note.)

**Consequence for the Excel template**: the `RecordType` field (currently `Request`/`Cancel`,
`mapping.py:235`, `mapping.py:255`, `mapping.py:430`) is dropped. Every row in the template is
now implicitly a New Report — Cancellation no longer routes through Excel at all, so the field
that let a producer flag a row as `Cancel` has no remaining purpose. This also removes
`CancelMiKaDivReportingForIncomeType`'s only representation in the generated Excel workbook
(currently `mapping.py:255`, `A("CancelMiKaDivReportingForIncomeType",
"PreviousRequestIdForCancellation", "Conditional")`).

**The Request *document* is unaffected by this narrowing** — it continues to fully describe
VIB's wire format, including Correction and Cancellation mechanics, since that's genuine,
useful reference material regardless of which UI surface constructs the XML. Only the *Excel
template*, whose job is specifically "what a bank fills in by hand," narrows to New-Report-only.

## 4. Site structure: `mikadiv-vib` splits into a landing page + two documents

Mirroring the established StreamLD pattern (module landing page + sibling documents,
`/streamld` + `/streamld/core` etc.):

- **`/mikadiv-vib`** — a new, short landing page (replacing the current full-content page at
  this URL), linking the two documents below. Structurally analogous to `streamld/index.bs`,
  including keeping the module-level `Shortname: mikadiv-vib` for itself (confirmed convention:
  `streamld/index.bs` keeps `Shortname: streamld`, while its documents get `<module>-<doc>`
  Shortnames, e.g. `streamld/core.bs` → `Shortname: streamld-core`).
- **`/mikadiv-vib/request`** — the corrected Request document (audience: banks/producers
  filling in data). This is today's `mikadiv-vib/index.bs` content, moved and fixed per §6, with
  `Shortname: mikadiv-vib-request` and the Downloads section (PDF + Excel links, unchanged
  mechanism from today) living here rather than on the landing page.
- **`/mikadiv-vib/response`** — a new document (audience: platform implementers — banks never
  see the raw response in this platform's design, so this document is written for whoever
  builds a MiKaDiv integration, not for producers), `Shortname: mikadiv-vib-response`. See §5
  for its content-generation approach. No PDF (HTML only — implementers read documentation
  online; a PDF adds a build step with no real audience need, revisit later if that changes).

Each document's own metadata block states its audience explicitly (e.g. an `Abstract` opening
line: "This document is for banks and other reporting institutes submitting MiKaDiv
disclosures" vs. "This document is for developers implementing a MiKaDiv integration against
this platform") — rather than leaving the reader to infer it, given both documents live under
the same module and could otherwise be assumed to share one audience.

Directory layout: both documents' source (`request.bs`, `response.bs`) and the landing page
(`index.bs`) live directly in `mikadiv-vib/`, following the same flat-siblings convention
`streamld/` already uses (`index.bs`, `core.bs`, `subscription.bs`, etc. — no subdirectory per
document).

## 5. Response document: auto-generated from the Response XSD

Reuses the existing engine's XSD-parsing layer (`engine/xsd_model.py`, today's Layer 1) rather
than being hand-written — the whole point of today's research was catching what hand-typed
documentation gets wrong, and building a second hand-typed document would reintroduce exactly
that risk. Layers 2/3 (Excel-template building) are **not** invoked for the Response side —
there's no template need since banks never fill in a response.

The generator gains a documentation-only mode: parse the XSD, render a Bikeshed include (the
element catalog, enums, and their real `xs:documentation` text) — no `Workbook`/`.xlsx` output.
Concretely, this needs `engine/generator.py`'s `Generator`/`ModuleConfig` (or a lighter sibling)
to support a config that only calls `_write_bikeshed_include`-equivalent logic, skipping
`_build_legend`/`_build_sheet`/the whole `Workbook` construction path — this is an
implementation-plan-level decision (whether that's a new `ModuleConfig` flag, a separate
`DocOnlyConfig`, or a distinct code path), not decided further here.

**Content to include, grounded in the real schema** (see the full research output for exact
`xs:documentation` text to transcribe, not paraphrase):

- `ThirdPartyDisclosureResponse` (root) → 1..unbounded `ResponseToDisclosureForIncomeType`
  (batching: one response file can answer many requests).
- `ResponseToDisclosureForIncomeType`'s three required attributes: `ResponseId` (custodian-
  assigned, must stay globally unique "even over subsequent files" — same cross-file uniqueness
  convention as the request side's `RequestId`), `RequestId` (correlates back to the originating
  request), `ResponseDate`.
- `ProcessingStatus` — a 6-stage enum pipeline: `Receive → StructureValidation →
  ContentValidation → Plausibilization → Reporting → TaxCertification`. A response can be
  emitted after *any* stage, not only at the end — an early-stage error represents a
  structural/format rejection, distinct from a later business-rule rejection or a final
  certificate-issuance failure.
- `ProcessingResult` (`Success`/`Error`) and `ProcessingCompleted` (boolean) — **document these
  as orthogonal**, not as one combined status: `ProcessingCompleted=false` is the schema's real
  mechanism for expressing "more responses to follow," independent of whether the current stage
  succeeded. There is no explicit `Pending`/`Rejected` enum value anywhere in the schema — both
  are inferred by combining all three fields, not read off one.
- `Messages`/`Message` (0..unbounded): `Code` (optional, custodian-defined — the one real sample
  uses `"000"` for success, implying a broader undocumented code catalog exists out-of-band),
  `Text` (required, human-readable — note in the doc that this is free-form/templated prose, not
  a controlled vocabulary: the one real sample's success text contains a genuine typo,
  "sucessfully"), `Level` (`Information`/`Warning`/`Error`), `Reference` (optional).
  `Message/Level` is the schema's actual granular severity signal, independent of the top-level
  `ProcessingResult`.
- `Records`/`Record` (0..unbounded): `Content` (the record's value — in the real sample, the
  official tax-document reference number, the "Ordnungsnummer"), `RecordType`
  (`TaxDocumentIdentifier`/`Other`), `RecordTypeInfo` (free-text label, always required even for
  the named `TaxDocumentIdentifier` case).
- `Documents`/`Document` (0..unbounded): `FilePath` (a bare string, not `xs:anyURI` — the doc
  should note the actual PDF bytes' delivery channel is undefined by this schema, presumably
  out-of-band alongside the response file), `ContentMimeType`, `DocumentType`
  (`TaxCertificate`/`Information`/`Other`), optional `Reference`.
- **Explicitly document three distinct identifiers and their scopes** (a real
  easy-to-conflate risk the research flagged): `ResponseId` (response-level, globally unique),
  `RequestId` (correlates to the originating request), and a `Record` of
  `RecordType=TaxDocumentIdentifier` (the tax certificate's own official reference number) — no
  formal relationship between the three is declared by the schema; the doc should say so
  plainly rather than let a reader assume one.
- **Note the schema's own "not for direct use" inconsistency**: `ResponseToDisclosureForIncomeType`
  is documented as a base type ("Not for direct use"), presumably meant to be subtyped per
  income category, but no derived subtype exists and the root element references this exact
  type directly — worth flagging as a real schema oddity rather than silently normalizing it
  away.
- **Note the one real sample only demonstrates the full-success path** — no Error/rejection or
  Pending/incomplete sample exists in the source material, so document that Error/pending
  behavior is derived from the XSD's structure, not confirmed against a real example.

## 6. Accuracy fixes landing in the Request document

All five, confirmed by independent adversarial verification against the real XSD and samples,
none present in the auto-generated data dictionary (which checked out accurate):

1. **`RequestId` uniqueness scope is stated wrong.** Current text (index.bs:85-87): "any value
   that is unique within a submission works." The real XSD's own documentation for `RequestId`
   states "Must be unique even over subsequent files" — global uniqueness across everything an
   institute ever submits, not per-file. Followed literally, the current wording would let a
   producer break the exact reference mechanism `PreviousRequestIdForCorrection`/
   `PreviousRequestIdForCancellation` depend on. Fix: state the real cross-file uniqueness
   requirement.
2. **Correction is entirely undocumented in the Linking model section** (index.bs:82-96) —
   only Cancellation and Community recipients are covered. Fix: add a Correction bullet
   alongside Cancellation's, describing `IsCorrectionRequest`/`PreviousRequestIdForCorrection`/
   `ReportSerialNumber` and the full-resubmission-not-a-delta behavior (§2), grounded in
   `Sample8-Correction.xml`.
3. **The Excel template's `RequestId` guidance is actively wrong, not just imprecise**
   (`mapping.py:429`, rendered into the legend): "it does not need to be a UUID... any unique
   value (e.g. a running number) is fine." The real XSD types `RequestId` as `UUIDType`,
   pattern-restricted to the standard UUID regex — a running-number value would fail real
   schema validation if carried through to submission. Fix: correct the legend text (this
   becomes moot for Cancellation once §3's Excel-template narrowing lands, but the New-Report
   Excel template still needs this fixed since `RequestId` is used there too).
4. **"Third Party Individuals / Legal Persons" is misdescribed** (index.bs:72, the Data model
   table): "Account holders who are not the beneficial owner." That description is actually
   `TaxCertificateReceiverPersonType.Relationship=AccountHolder`'s real documentation — a
   *different* field, in the Tax Voucher group. The real `ThirdPartyPersonType` represents the
   fiduciary counterpart tied to a beneficial-owner situation (`Relationship` enum:
   `Trustee`/`Pledgor`/`Grantor of usufruct`), confirmed against `Sample4-CreditorAndTrustee.xml`
   and `Sample5-Usufructury.xml` (both show the account holder as `Relationship=AccountHolder`
   on the Tax Voucher receiver, and the third party as `Trustee`/`Grantor of usufruct`). Fix:
   correct the table row to describe the fiduciary-role concept, not "account holders."
5. **`ReportSerialNumber` conflates two differently-documented XSD fields.** The generated
   field description (currently sourced from `mapping.py:246`, rendered in
   `generated/fields.include.bs`) only carries the correction-flavored wording ("reference for
   correction"), but the real XSD defines this attribute *twice* — once on
   `RequestMiKaDivReportingForIncomeType` ("...reference for correction") and once on
   `CancelMiKaDivReportingForIncomeType` ("...reference for cancellation") — with genuinely
   different documentation strings. The current single flattened description is wrong for the
   cancellation use case it's simultaneously instructing producers to use it for. This becomes
   moot for the Excel template once §3 drops `RecordType=Cancel`, but the *Request document's*
   prose (which continues to describe the full wire format per §3) should still get this right
   when explaining `ReportSerialNumber` in both contexts.

**Also disclose, rather than silently omit**: the "Source schema" section's claim that
everything is "generated directly from" the VIB XSD is undercut by the Linking model's use of
`RecordType`/`ReceiverGroupType`/`CommunityGroupId` — synthetic flattening field names
(confirmed via `mapping.py`'s own `SYN(...)` tagging) that don't exist in the real XSD at all.
Fix: add a one-sentence disclosure that these specific names are OpenFASTER's own presentation
choice, not VIB-sourced, where they're first introduced.

## Non-goals

- The BZSt MiKaDiv-FM handbook's broader lifecycle claims (this design deliberately narrows to
  what VIB's own XSD pair supports; per operator direction, not a concern of this pass).
- The other 7 MiKaDiv report types (Meldeart 11/13/ERG/21/22/23, ZAM) — this design covers only
  the one report type (`ThirdPartyDisclosure`) the researched Drive folder provides. Whether the
  others share this Request/Response structure is unconfirmed and out of scope here.
- Any `bulk-platform` backend implementation — the `RequestId`-chain trackable-entity data model,
  the stage-then-apply UI, and the actual Correction/Cancellation submission flow are flagged in
  `bulk-platform`'s own `PROGRESS.md` (item 8 sub-project 4) as a future backend design, not
  decided here.
- A PDF for the Response document (§4) — HTML only for now.
- Machine-enforcing referential integrity (`RequestId` uniqueness, valid prior-reference) that
  the real XSD itself only documents in prose — this spec documents the requirement accurately;
  enforcing it is an application-layer (i.e. `bulk-platform`) concern, not a spec-authoring one.
