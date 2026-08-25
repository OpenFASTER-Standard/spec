# KaFE OpenFASTER module — design

Status: brainstormed and approved 2026-08-25. Not yet planned/implemented.

Ecosystem placement: this is bulk-platform's item 8, sub-project 5 ("Build a
new `kafe/` OpenFASTER module ... with its own proper lifecycle state
machine"). It is the direct KaFE analog of sub-project 4's already-shipped
`mikadiv-vib` module (index/request/response split, XSD-vendoring +
Bikeshed-doc-generation pipeline). It does **not** cover sub-project 9
(KaFE submission backend) — that is `bulk-platform`'s own separate,
not-yet-started sub-project, exactly as sub-project 8 (MiKaDiv backend) is
kept separate from sub-project 4 here.

## 1. Context and motivation

Divizend already publishes a hand-authored, Google-Docs-maintained KaFE
interface document (`Documentation Divizend KaFE Interface`, currently
v4.3.1, 77 pages, exported to PDF via Google Docs' own renderer — no
DOCVERSION macro, no schema-driven generation, no build tooling at all).
This sub-project ports that document's real content into the same
XSD-vendoring + Bikeshed-doc-generation pipeline `mikadiv-vib` already
uses, fixing real accuracy bugs along the way, and adds documentation for
the response side (`kafe-rm.xsd`/`kafe-va.xsd`) that the existing document
doesn't cover at all today.

This design is grounded in a deep primary-source research pass, not the
BZSt handbook's own paraphrase of itself (the same discipline that caught
5 real bugs in MiKaDiv's prior module): the real, current BZSt-published
KaFE v1.4.0 XSD family (`kafe.xsd`, `kafe-rm.xsd`, `kafe-va.xsd`,
`kafe-standardtypes.xsd`, `kafe-statustypes.xsd`, `kafe-isotypes.xsd`,
sourced from the operator's own "what BZSt originally published" Drive
folder — confirmed current, not the stale, locally-flattened v1.3.0 copy
that happens to be bundled inside an unrelated prototype repo,
`mikadiv-demo-clone`), the 212-page official English communication
handbook, the existing 77-page Divizend document itself (read in full),
and Divizend's own real production KaFE-DIP code and data model in the
`app` monorepo (`column-defs.json`, `kafe-claim.ts`'s Valibot validation
rules, `kafe-dip-internals.md`).

## 2. The real KaFE process shape

KaFE's real structure is meaningfully simpler and flatter than MiKaDiv's,
confirmed independently across the XSD, the handbook, and production code:

- **One submission type, not a taxonomy.** The root submission element is
  `Erstattungsantrag` (refund application) — there is no `RequestType`
  enum, no Meldeart-style report-type taxonomy. Differentiation happens on
  two orthogonal axes instead: `Anspruch` (legal basis of claim — 7
  independent booleans: `Abkommen`/DTA, `Par43bEStG`, `Par44aEStG`,
  `Par50gEStG`, `Par32Abs6KStG`, `Art63AEUV`, `IntOrg`, combinable except
  `IntOrg` which is exclusive) and `KapArt` (a 10-value capital-income-type
  enum per income line, not a submission-level type).
- **No correction/cancellation typing on the submission side, confirmed
  three independent ways.** Grepping the real XSD family for
  `Korrektur|Stornier|Storno|Berichtigung|Rücknahme|Widerruf|PreviousRequest`
  returns zero hits anywhere in the taxpayer-facing schema. The handbook's
  entire description of error recovery is one paragraph (§2.4, quoted
  verbatim): *"Files that contain non-valid data are rejected... After
  correcting the errors, an error-free file can be resubmitted.
  Alternatively, a file containing only the error-free records can be
  transmitted."* Production code (`kafe-dip/common.ts`) confirms there is
  no formal state machine today — just boolean bookkeeping
  (`validation.success`, `submission.success`/`rejected`) with a
  documented dead-end: a claim rejected *after* being accepted is neither
  resubmittable nor archivable.
- **A typed correction concept exists, but only on BZSt's own outgoing
  side.** `kafe-va.xsd`'s `Bescheid_CType.BescheidArt` is an enum
  (`ERSTBESCHEID`/`KORREKTUR` — first vs. corrected decision notice), not
  chained to the specific prior notice it corrects (only back to the
  original `Antrag` via `Bezugsantrag`). Any prose that says "KaFE has no
  correction typing at all" is only true for the request side.
- **No 6-stage `ProcessingStatus` pipeline like MiKaDiv.** Instead: a
  synchronous per-delivery response (`kafe-rm.xsd`, "Rückmeldung") with a
  file-level `processStatus` (`OK`/`ERROR`/`PARTIALLY_REJECTED`) and, per
  `Antrag` (correlated by the submitter's own `AntragId` UUID), either a
  `RegistrierNr` (accepted) or a `ValidierungsergebnisListe` (rejected,
  `StatusCode`+`Hinweis` pairs) — then, separately and later, decision
  notice retrieval (`kafe-va.xsd`). Approval is a positive
  `SummeAbrechnung`; clawback is an explicit negative amount plus a
  mandatory `Faelligkeit` due date and a late-payment-penalty warning.
- **A real, current gap in BZSt's own spec worth disclosing, not
  papering over:** the handbook states outright (§6.2) that *"the DIP
  envelope scheme for the notification of administrative files is not
  available yet."* BZSt has published `kafe-va.xsd`'s payload shape but
  not the transport for delivering it. The response document (§7 below)
  is scoped around this honestly.
- **§50j EStG (the cum-ex/securities-lending block) is real and precisely
  specified** — 45-day/1-year holding-period math, a 70%-risk-retention
  test, forwarding/return obligations, and a per-depot transaction ledger
  spanning exactly one year before to two months after the inflow date,
  with a 6-value transaction-type taxonomy (`PO`/`SO`/`TL`/`RL`/`TP`/`RP`
  — purchase/sale/securities-lending transfer+retransfer/repo
  transfer+retransfer). Confirmed identically in the real XSD, the
  handbook's own prose, and production's `kafe-claim.ts` cross-entity
  validation rules — high triangulated confidence.
- **Critical generation-architecture consequence:** almost the entire
  §50j block is `minOccurs="0"` at the raw XSD level. Its real
  conditional-mandatory logic (e.g. "required only when country/legal-form
  is in the §8.1 matrix," "required only when `HaltedauerMin45T > 0`")
  lives entirely in a separate, 213-entry status-code catalog (plus
  code `0000`/OK, outside the numbered ranges) — corrected from an
  initial ~219 research-phase estimate once fully transcribed and
  verified against the handbook
  (`kafe-statustypes.xsd`'s `StatusCode_ENUM`, documented in the
  handbook's appendix), not in the XSD's own cardinalities. Unlike
  MiKaDiv, where the real VIB XSD's own documentation/facets were the
  complete story, a pure "vendor the XSD, generate docs" pass here would
  misrepresent §50j as almost entirely optional. §4 below designs
  explicitly around this.

## 3. Site structure

Mirrors `mikadiv-vib`'s already-shipped landing + sub-document split:

- **`/kafe`** (`index.bs`, `Shortname: kafe`) — landing page, links to
  Request and Response, no `DOCVERSION`, matching `mikadiv-vib/index.bs`'s
  style. The root portal's own `index.html` needs no change — its
  `/kafe` link, reserved when `mikadiv-vib` shipped, already resolves.
- **`/kafe/request`** (`request.bs`, `Shortname: kafe-request`) —
  bank/producer-facing. Keeps `DOCVERSION`, PDF, and Excel-template
  download, mirroring `mikadiv-vib/request.bs`. Covers: the real
  submission field shape (all 7 Excel sheets), the legal-basis and
  capital-income-type axes, the §50j block, and — moved here per
  operator decision, since it's the synchronous half of what a bank
  actually experiences submitting data — the `kafe-rm.xsd` accept/reject
  receipt (validation-error appendix, `RegistrierNr` assignment).
- **`/kafe/response`** (`response.bs`, `Shortname: kafe-response`) —
  implementer-facing, HTML only (no PDF/Excel, mirroring
  `mikadiv-vib/response.bs`). Scoped to `kafe-va.xsd` only: the decision
  notice/clawback schema (`BescheidArt`, `SummeAbrechnung`/`Faelligkeit`
  semantics, per-income refund breakdown via `Ertraege`/`Ertrag`).
  Explicitly and visibly marked provisional throughout, per §2's BZSt
  transport-gap disclosure — this document describes what the payload
  will contain once retrieval is possible, not a working integration.

## 4. Generation architecture — source-of-truth chaining

Extends the existing `engine/xsd_model.py` → `mapping.py` →
`engine/generator.py` layering (Layer 1/2/3, per `README.md`'s own
description) with one new piece, per operator decision (XSD primary,
status-code catalog fills the gaps XSD alone can't determine):

- **`KafeXsdModel`** (new, in `kafe/` — either a KaFE-specific subclass or
  a second instantiation of the existing generic `XsdModel`, TBD in the
  plan) loads `kafe.xsd`/`kafe-standardtypes.xsd`/`kafe-isotypes.xsd` the
  same way `XsdModel` already loads `ThirdPartyDisclosureRequest.xsd` —
  field descriptions, types, base cardinality, all sourced from the XSD's
  own `xs:documentation` and facets, never hand-typed.
- **New `engine/status_codes.py`** (or a KaFE-local equivalent) — a small,
  hand-transcribed but structured table of all 213 status codes (plus
  code `0000`/OK) from the handbook's appendix (code → section/range →
  message), since the codes exist only inside a 212-page PDF with no
  machine-readable source.
  Complete coverage of every real code, per operator decision — not just
  the subset that drives requiredness — because the same transcription
  effort serves two purposes at once: (a) real conditional-mandatory
  logic for the ~40 fields (mostly §50j) where the XSD alone says
  `minOccurs="0"` but the real rule is conditional-required, and (b) a
  full status/error-code reference appendix in the Request document's
  error-handling section (banks see these codes today via
  `ValidierungsergebnisListe` — the existing v4.3.1 document has no such
  appendix at all, so this is a genuine improvement, not scope creep).
  Organized by the same numeric ranges the handbook itself uses (1xxx
  file-level, 2xxx `Anliegen`/`Anspruch`, 3xxx `AllgAngaben`, 4xxx
  `SteuerlicheBehandlung`, 5xxx `Zahlungsweg`, 6xxx `Ertrag`, 7xxx
  `Par50jEStG`).
- **`kafe/mapping.py`** — the shape layer, mirroring `mikadiv-vib`'s own
  `mapping.py`: declares which of the 7 real sheets exist, column order,
  and — the one real extension beyond MiKaDiv's pattern — layers real
  conditional requiredness from `status_codes.py` on top of the XSD's own
  `required=` wherever they disagree (the §50j fields), via the same kind
  of explicit `SYN()`-style override convention `mapping.py` already uses
  for presentation-layer facts the XSD can't express on its own.
- **No Excel-template narrowing step.** Since KaFE has no request-type
  taxonomy to begin with (§2), there's no MiKaDiv-style "drop the
  Cancel/RecordType column" narrowing — the whole template stays
  Excel-driven, unchanged in shape from what production's
  `column-defs.json` already defines.

## 5. Excel template

Regenerates the same 7 real sheets `column-defs.json` and the existing
v4.3.1 document both already define (`meta`, `creditorsNatural`,
`creditorsJuridical`, `certificatesOfResidence`, `income`,
`investmentChain`, `transactionData`) — **field/column shape is
unchanged**, per the operator's explicit constraint. What changes is the
presentation/tooling layer, harmonized with `mikadiv-vib`'s richer,
already-shipped conventions (confirmed KaFE's current template lacks all
of these — no legend sheet, no dropdown validation, no hidden lookup-list
sheet; today's "legend" is just prose baked into rows 2–3 of each sheet):

- A "0 Legend Notes" sheet (requiredness legend, cardinality, linking
  rules), matching `mikadiv-vib`'s own front sheet.
- Real dropdown validation sourced from the actual XSD enums (`KapArt`,
  `TransaktionArt`, `Geschaeft`, the `Anspruch` legal-basis booleans,
  etc.) via a hidden `_Lists` sheet, rather than the current prose-only
  convention.
- A capitalized "Meta" sheet, last, carrying the unified `DOCVERSION` (§6)
  — resolving the current, confirmed inconsistency between the document's
  own version number and the Excel template's independently-tracked
  "meta" version (4.3.1 vs. 4.1-then-silently-4.3, with no explanation
  anywhere of why the two diverge).

## 6. Versioning and changelog

- **Unify the two currently-independent version tracks** into one
  `DOCVERSION` macro in `kafe/request.bs`, mirroring
  `mikadiv-vib`'s own `engine/version.py` pattern — single source of
  truth for the document version, the Excel template's own "Meta" sheet
  version, and the PDF/Excel filenames (`kafe-v4.3.2.{pdf,xlsx}`).
- **Final published version: 4.3.2.**
- **The full existing changelog is carried forward verbatim** (1.0.0
  2023-08-29 through 4.3.1 2026-06, already transcribed in full during
  research), with a new 4.3.2 entry appended describing this
  restructuring itself — ported to OpenFASTER's schema-driven structure,
  added the provisional Response/`kafe-va` document, confirmed and
  upgraded schema references to current v1.4.0 — following the existing
  changelog's own established MAJOR/MINOR/PATCH classification
  convention.

## 7. Response document scope (provisional)

`/kafe/response` documents `kafe-va.xsd` only — `Bescheid_CType`'s real
structure (`BescheidId`, `Bezugsantrag` back-reference via
`TransferticketId`+`AntragId`+`RegistrierNr`+`KennNr`, `BescheidArt`,
`SummeAbrechnung`'s sign convention, `Faelligkeit`'s clawback-only
semantics, `BescheidPdf` as the only carrier of substantive legal
reasoning, `Ertraege`/`Ertrag` per-income refund breakdown). The document
opens with an explicit, prominent disclosure — mirroring how MiKaDiv's
own response document discloses schema oddities — that BZSt has not yet
published the DIP transport envelope for retrieving this payload (handbook
§6.2, quoted directly), so this document describes payload shape only,
not a working retrieval flow.

## 8. Known accuracy bugs to fix while porting

Found during the research pass, cross-checked against the real schema and
production code, to be corrected as the content moves into the new
generated structure (the same "fix while restructuring" pattern MiKaDiv's
own module followed):

1. **§11 InvStG self-contradiction.** The existing document states
   (§2.1) that claims under §11 InvStG cannot be submitted via KaFE at
   all, yet documents a field, `Affirmations/ApplicationPar11InvStG`
   (creditorsJuridical, LegalForm=INVF), whose entire purpose concerns
   that exact legal basis. Resolve by re-checking against
   `column-defs.json`/the real XSD which claim is correct, and fixing
   whichever side is wrong.
2. **Requiredness-column convention break.** `LegalBasis/Par32Abs6KStG`'s
   "Required" column value ("Only required for submissions occurring
   after 15.04.2025") is free-text-conditional, breaking the document's
   own documented four-value convention (§4.4) for that column. Fold this
   into the new status-code-driven conditional-requiredness model instead
   of leaving it as an outlier free-text cell.
3. **Duplicated-prose drift risk.** Many conditional-requiredness clauses
   are hand-copy-pasted near-identically across `creditorsNatural` and
   `creditorsJuridical` (e.g. `AuthorizedRep`/`Bank`/`Address` blocks) —
   a real, already-latent drift risk the same way MiKaDiv's old
   hand-written prose drifted from its real XSD. Generating both sheets'
   shared fields from the one `mapping.py`/status-code source eliminates
   this class of bug structurally, not just for the specific instances
   found.
4. **Stray pagination artifact.** A garbled cross-reference fragment
   ("...GermanCorporationKStGPage 97 least in part...") on p.59 of the
   existing PDF, a leftover from the Google Docs export pipeline — simply
   won't exist in the new Bikeshed-generated output.
5. **`TransactionNumber`/sequence scope ambiguity.** The existing
   document never clarifies whether `TransaktionId` sequencing restarts
   per depot or increments globally; the real XSD's own `xs:unique`
   constraint (`kafe.xsd`) and production's validation rule (sequential,
   non-gapped, checked *per depot*) resolve this precisely — state it
   explicitly in the new prose instead of leaving it ambiguous.

## Non-goals

- Curated, realistic demo/synthetic data for the Lombard Odier POC — that
  is `bulk-platform` item 8 sub-project 15's job, sequenced after both
  KaFE and MiKaDiv's backend sub-projects settle. This sub-project ships
  a correctly-shaped, minimally-illustrative template only, the same way
  `mikadiv-vib`'s shipped Excel template is not filled demo content.
- The actual `bulk-platform` KaFE submission backend (trackable entity,
  BZSt transport/JWT+XMLDSig signing, decision-notice ingestion) — that
  is sub-project 9, entirely separate, not started.
- Any Divizend-internal concept: the BNY/Clearstream/Euroclear ingestion
  parsers (confirmed during research — "the KaFE spreadsheet for
  Clearstream" refers to one of these upload-format parsers, stripping 4
  field-groups Clearstream's own uploads omit, not any BZSt-side
  relationship; Clearstream has no KaFE counterparty role, unlike its
  real MiKaDiv one), the internal "approved" reviewer checkbox, bulk-edit
  and archive/unarchive workflow, container/encryption internals. None of
  this is BZSt wire format and none of it belongs in a public spec-level
  document.
- The separate `kafe-bop-general` (RPA/BOP-based) submission path —
  confirmed structurally distinct from the DIP-based path this module
  documents (different generation approach entirely: auto-generated from
  an internal OpenAPI spec, not hand-maintained against BZSt's own
  schema). Out of scope for a BZSt-wire-format spec document.
- Full BZSt handbook-level KaFE lifecycle richness beyond what the real
  XSD family + status-code catalog actually specify — same discipline
  MiKaDiv's own module already established: document what's verifiable
  against real primary sources, not what a handbook merely implies.
