# OpenFASTER Site Structure/Overview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the MiKaDiv-spec-as-homepage with a real portal linking every
standard (MiKaDiv, StreamLD) and reference implementation (Riptide) as
first-class content, give StreamLD (currently a fully-built but completely
orphaned module) real navigation, settle a clean-URL/no-premature-versioning
convention, add a shared visual shell, and fix the confirmed gap where
`README.md` claims automated CI that doesn't exist.

**Architecture:** Split today's single `documentation/index.bs` (root =
MiKaDiv's whole spec) into three documents — a new family-wide
`documentation/about.bs`, a MiKaDiv-only `mikadiv/index.bs`, and a
hand-authored static portal at repo-root `index.html` — plus give StreamLD's
already-built 4 documents a new `streamld/index.bs` landing page and fix
their cross-links. A shared header/nav/footer shell (new `documentation/shell.css`
+ an updated `documentation/header.template.include`) wraps every
Bikeshed-built page; the portal duplicates the same markup by hand (accepted,
documented duplication — see Task 4). A new GitHub Actions workflow rebuilds
and commits the complete output (both the XSD-based mikadiv pipeline and the
separate SHACL-based streamld pipeline) on every push to `main`.

**Tech Stack:** Python 3.12 (Bikeshed 7.1.1, WeasyPrint 66.0, xmlschema,
openpyxl, rdflib — all already pinned in `requirements.txt`/
`documentation/requirements-spec.txt`/`streamld/tests/requirements.txt`),
static HTML/CSS for the portal and shell, GitHub Actions, Vercel (existing
deploy target, unchanged).

**Spec:** `docs/superpowers/specs/2026-08-24-site-structure-overview-design.md`

## Global Constraints

- **Clean URLs, no trailing slash** — `vercel.json` already sets
  `"trailingSlash": false` and `"cleanUrls": true`. Every new/changed link in
  this plan uses the no-trailing-slash form: `/mikadiv`, `/streamld`,
  `/about`, `/streamld/core`, never `/mikadiv/` or `/streamld/core.html`.
  Directory-index pages are built as `<name>/index.html` (Vercel serves this
  at `/<name>`); leaf pages stay flat siblings relying on `cleanUrls`'
  extension-stripping (e.g. `streamld/core.html` → `/streamld/core`).
- **No version segment in any URL** — every page has exactly one "latest" URL,
  updated in place. Do not build a dated-snapshot mechanism in this plan (spec
  §5.5, Non-Goals).
- **No content changes** — MiKaDiv's/StreamLD's actual technical prose,
  tables, and generated data-dictionary content move file locations but are
  not otherwise edited. Do not "improve" wording while relocating it.
- **`--die-on=link-error` stays on** for every Bikeshed invocation — a broken
  cross-reference must fail the build loudly, matching the existing
  Dockerfile convention, not silently produce a dead link.
- **Never edit anything under `mikadiv/generated/` or `streamld/generated/`
  by hand** — these are machine-generated; only their source inputs (XSD,
  `mapping.py`, `envelope.ttl`) are hand-edited (existing repo convention,
  `README.md`'s own "Editing conventions" section).
- **KaFE gets no page in this plan** — only a documented, reserved `/kafe`
  path convention (spec §5.4, Non-Goals). Do not create a stub.
- **Thesaurus is out of scope entirely** — do not reference or place it
  anywhere (spec Non-Goals, deferred to a future sub-project).

---

### Task 1: Shared visual shell infrastructure

**Files:**
- Create: `documentation/shell.css`
- Modify: `documentation/header.template.include`
- Modify: `documentation/site.css` (one addition, see Step 3)

**Interfaces:**
- Produces: a shared header/nav/footer HTML block (embedded directly in
  `documentation/header.template.include`) and `documentation/shell.css`,
  consumed by every later task that builds or edits a Bikeshed document
  (Tasks 2, 3, 5, 6) via `Local Boilerplate: header yes`, and copied by hand
  into the portal (Task 4).

This task proves the shell mechanism works *before* any content is
restructured — verified by rebuilding the existing, unmodified
`documentation/index.bs` and confirming the new shell renders on today's
still-in-place root page.

- [ ] **Step 1: Verify Bikeshed's local-boilerplate file-discovery convention**

Do not assume — confirm directly. Run:

```bash
python -m pip install -r requirements.txt -r documentation/requirements-spec.txt
bikeshed update
```

Then read Bikeshed's own documentation for `Local Boilerplate` (run
`bikeshed --help` and search its output, or check the installed package's
docs, e.g. `python -c "import bikeshed; print(bikeshed.__file__)"` then look
in that package's `spec-data/readonly/boilerplate/` for the *default*
`header.include` it ships, to understand what a local override must match).
Confirm concretely: does Bikeshed look for `header.include` in the same
directory as the `.bs` source file being compiled, or relative to the
current working directory the `bikeshed` command is invoked from? This
matters because Task 2/3/5/6's `.bs` files live in different directories
(`documentation/`, `mikadiv/`, `streamld/`) than today's sole `.bs` file.
Record the answer in this task's own commit message or a one-line code
comment at the top of `header.template.include` — later tasks depend on
getting this right.

- [ ] **Step 2: Write `documentation/shell.css`**

```css
/* OpenFASTER shared site shell -- header/nav/footer, used on every page
   (Bikeshed-built module docs via header.template.include, and the
   hand-authored root portal by direct duplication -- see the portal task's
   own note on why this isn't further templated). */

.of-shell-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: #0b3d6e;
  color: #fff;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}

.of-shell-header a {
  color: #fff;
  text-decoration: none;
}

.of-shell-header a:hover {
  text-decoration: underline;
}

.of-shell-logo {
  font-weight: 800;
  font-size: 1.15rem;
  letter-spacing: 0.01em;
}

.of-shell-nav {
  display: flex;
  gap: 1.5rem;
  font-size: 0.95rem;
}

.of-shell-footer {
  margin-top: 3rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #d8d8d8;
  color: #555;
  font-size: 0.85rem;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}

.of-shell-footer a {
  color: #0b3d6e;
}
```

- [ ] **Step 3: Add one shared-asset-path fix to `documentation/site.css`**

`documentation/site.css`'s own top comment already says "OpenFASTER site
overrides (HTML + PDF via print.css @import)" — leave its existing two rule
blocks (`.head dl dd .spec-version`, `.changelog-top`) untouched. Do not
merge `shell.css`'s content into this file; they stay separate files with
separate responsibilities (spec-page chrome vs. site-wide shell), both
linked from the header template (Step 4).

- [ ] **Step 4: Update `documentation/header.template.include`**

Full replacement content — adds the shell's CSS links (root-relative paths,
required once module pages live in subdirectories — see the design's own
flagged gotcha) and the shared header/nav markup, keeping every existing
Bikeshed fill-slot (`data-fill-with="..."`) intact:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>[TITLE]</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="stylesheet" href="/documentation/site.css">
  <link rel="stylesheet" href="/documentation/shell.css">
  <style data-fill-with="stylesheet">
  </style>
</head>
<body class="h-entry">
<header class="of-shell-header">
  <a class="of-shell-logo" href="/">OpenFASTER</a>
  <nav class="of-shell-nav">
    <a href="/#standards">Standards</a>
    <a href="/#implementations">Implementations</a>
    <a href="/about">About</a>
  </nav>
</header>
<div class="head">
  <p data-fill-with="logo"></p>
  <h1 id="title" class="p-name no-ref">[TITLE]</h1>
  <h2 id="profile-and-date" class="no-num no-toc no-ref">[LONGSTATUS],
    <time class="dt-updated" datetime="[ISODATE]">[DATE]</time></h2>
  <div data-fill-with="spec-metadata"></div>
  <div data-fill-with="warning"></div>
  <p class='copyright' data-fill-with='copyright'></p>
  <hr title="Separator for header">
```

(Everything after the final `<hr title="Separator for header">` line in the
current file is Bikeshed's own remaining boilerplate machinery — leave it
untouched below this point; only the `<head>`'s stylesheet links and the new
`<header class="of-shell-header">` block, inserted right after `<body>` and
before the existing `<div class="head">`, are new.)

- [ ] **Step 5: Regenerate `documentation/header.include` and rebuild the existing root doc to verify**

```bash
python documentation/prepare_spec.py
python generate_template.py
bikeshed --allow-nonlocal-files --die-on=link-error spec documentation/index.bs index.html
```

Expected: builds cleanly (no link errors), and opening the resulting
`index.html` shows the new dark-blue header bar with "OpenFASTER" / Standards
/ Implementations / About links above the existing MiKaDiv spec content —
confirming the shell mechanism works before Task 2/3 restructure what's
*under* it. The nav's `/about` link will 404 until Task 2 lands, and
`/#standards`/`/#implementations` won't scroll anywhere until Task 4 lands —
expected at this point, not a bug in this task.

- [ ] **Step 6: Commit**

```bash
git add documentation/shell.css documentation/header.template.include documentation/header.include documentation/site.css index.html
git commit -m "feat: add shared header/nav shell, verified against the existing root doc"
```

---

### Task 2: Extract family-wide content into `documentation/about.bs`

**Files:**
- Create: `documentation/about.bs`
- Modify: `documentation/index.bs` (removes the sections moved out — see Task 3, which finishes converting this file)

**Interfaces:**
- Produces: `documentation/about.html` (built at `/about`), defining
  Bikeshed terms `Certified Financial Intermediary`, `disclosure`,
  `RequestId`, `paying agent`, `tax voucher` under Shortname `openfaster` —
  Task 3's `mikadiv/index.bs` cross-references these via
  `[[openfaster#certified-financial-intermediary]]`-style informative xrefs
  (exact anchor IDs come from Bikeshed's own auto-generated `<dfn>` anchors,
  confirmed in Step 3 below), not same-document `[=term=]` autolinks.

- [ ] **Step 1: Write `documentation/about.bs`**

Extracts Introduction (Scope + Regulatory context), Terminology, Planned
work, and the Versioning section verbatim from today's
`documentation/index.bs`, unchanged content, new metadata block and
document framing:

```
<pre class=metadata>
Title: About OpenFASTER
Shortname: openfaster
Level: 1
Status: DREAM
URL: https://openfaster.org/about
Repository: https://github.com/OpenFASTER-Standard/spec
Text Macro: LONGSTATUS Vendor-independent, interoperable protocol standard for EU withholding tax and dividend reporting data exchange under MiKaDiv and FASTER
Editor: Julian Nalenz, https://github.com/sigalor
Editor: Alaa Eddine Cherif, https://github.com/AlaaCherif
Abstract: OpenFASTER is a vendor-independent family of open standards for the
    exchange of EU withholding-tax and dividend-reporting data under MiKaDiv
    and FASTER. This document defines the family: its scope, shared
    terminology, versioning policy, and planned direction. The family's
    concrete modules -- currently MiKaDiv Third-Party Disclosure and StreamLD
    -- are each specified in their own document; see
    <a href="/">the OpenFASTER portal</a> for the full, current list.
Markup Shorthands: markdown yes, dfn yes, css no
Boilerplate: omit conformance
Local Boilerplate: header yes
Complain About: accidental-2119 yes, missing-example-ids yes
</pre>

<pre class=biblio>
{
  "MIKADIV": {
    "title": "MiKaDiv – Mitteilungsverfahren für Kapitalerträge und Steuerabzug (§45b EStG)",
    "publisher": "Bundeszentralamt für Steuern (BZSt)",
    "href": "https://www.bzst.de/"
  },
  "FASTER": {
    "title": "Council Directive (EU) on Faster and Safer Relief of Excess Withholding Taxes (FASTER)",
    "publisher": "Council of the European Union",
    "href": "https://taxation-customs.ec.europa.eu/faster_en"
  }
}
</pre>

Introduction {#intro}
=====================

OpenFASTER is a **vendor-independent family of open standards** for exchanging
the data required for EU withholding-tax and dividend reporting. It is designed
so that [=Certified Financial Intermediary|Certified Financial Intermediaries=]
(CFIs) — banks, custodians, central securities depositories, and other reporting
parties — can produce and exchange this data interoperably, regardless of which
vendor or in-house system they use.


Scope {#scope}
--------------

The scope of OpenFASTER is **purely operational**: defining the technical data
model, vocabulary, and (in future modules) the exchange mechanics that make
indirect reporting and the collection of supplementary data efficient and
standardized across the EU.

OpenFASTER deliberately does <em>not</em> address:

* legislative or business-logic questions (for example, whether anonymous
    reporting is permissible);
* the internal calculation of tax positions; or
* commercial or contractual arrangements between participants.

Regulatory context {#regulatory-context}
-----------------------------------------

OpenFASTER is developed against the timeline of the EU [[FASTER]] initiative and
the German [[MIKADIV]] reporting procedure.

<table class="data">
  <thead>
    <tr><th>Milestone<th>Date
  <tbody>
    <tr><td>Standardized dividend reporting (MiKaDiv)<td>2027-01-01
    <tr><td>Full regulatory reporting under FASTER<td>2030-01-01
</table>

The goals shared with these initiatives are harmonized dividend reporting,
reduced withholding-tax fraud, greater transparency for tax authorities, and
efficient cross-border tax-reclaim processing.


Terminology {#terminology}
==========================

<dfn>Certified Financial Intermediary</dfn> (CFI)
: A regulated party — such as a bank, custodian, or central securities
    depository — that participates in withholding-tax and dividend reporting and
    exchanges disclosure data with other participants.

A <dfn>disclosure</dfn>
: One complete third-party disclosure record for a single capital-income event,
    identified and linked together by a single [=RequestId=].

<dfn>RequestId</dfn>
: The identifier that ties together all parts of one [=disclosure=]. It is a
    linking key only: any value that is unique within the submission is valid, so
    it need not be a UUID.

<dfn>paying agent</dfn>
: The German institution responsible for the withholding-tax reporting for a
    given capital-income event.

<dfn>tax voucher</dfn>
: The tax certificate (Steuerbescheinigung) issued in respect of a
    capital-income event.

Planned work {#roadmap}
=======================

The following modules and improvements are planned. They are <em>not</em> part of
the normative content of any published module yet; they are recorded here to
describe the intended direction of the OpenFASTER family.

Bulk disclosure template {#roadmap-bulk}
----------------------------------------

A revised template (and matching schema) in which an arbitrary number of
beneficiaries, income lines, and related records can be entered, enabling
mass/batch processing of disclosures rather than one disclosure at a time.

Published multilingual vocabulary {#roadmap-vocabulary}
-------------------------------------------------------

A published <em>vocabulary</em> that fixes the (non-official) translations of the
field names and their explanations into several languages, each validated by
appropriate domain experts. This lets institutions across jurisdictions work
against a shared, authoritative set of terms while the official German schema
remains the legal reference.

UUID return format {#roadmap-uuid-return}
-----------------------------------------

A format (an XSD plus an equivalent Excel representation) with which a reporting
entity — for example Clearstream, or another reporting party — can report the
assigned UUIDs back to the foreign banks that originated the disclosures, closing
the loop between submission and acknowledgement.

Versioning {#versioning}
======================

Each OpenFASTER module is versioned independently using
[semantic versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):

* <b>MAJOR</b> — incompatible changes to the data model (for example, removing a
    field, or changing its meaning or requiredness).
* <b>MINOR</b> — backwards-compatible additions (for example, new optional
    fields or new enumeration values).
* <b>PATCH</b> — editorial or documentation-only corrections.

A module's own changelog is published at the top of its document. Every module
publishes at a single, stable "latest" URL (e.g. `/mikadiv`, `/streamld`),
updated in place as new versions are released — dated snapshot URLs for
citing a frozen historical version are minted only once a module actually
reaches a second version.
```

Note the one deliberate content change beyond pure relocation: "This
document defines the family. This version specifies only the first
module—the MiKaDiv Third-Party Disclosure format..." (old, single-module
framing) becomes "The family's concrete modules... are each specified in
their own document" (new, multi-module framing) in the Abstract, and the old
`Versioning` section's "This document is version [DOCVERSION]" (root-level
single version number) becomes "Each OpenFASTER module is versioned
independently" (per-module versioning, matching spec §5.5's decision). These
two edits are structural consequences of the redesign itself, not scope
creep — flag them explicitly in this task's commit message so a reviewer
can see they're deliberate.

- [ ] **Step 2: Build and verify `about.bs` standalone**

```bash
bikeshed --allow-nonlocal-files --die-on=link-error spec documentation/about.bs documentation/about.html
```

Expected: builds cleanly. Open `documentation/about.html` and confirm the
shared shell header (Task 1) renders, and the five `<dfn>` terms
(`Certified Financial Intermediary`, `disclosure`, `RequestId`,
`paying agent`, `tax voucher`) are present with real anchor IDs — inspect
the rendered HTML for each term's `id="..."` attribute (Bikeshed
auto-generates these from the `<dfn>` text, typically kebab-cased) and write
down the exact five anchor IDs found; Task 3 needs them verbatim to build
correct `[[openfaster#anchor-id]]` cross-references.

- [ ] **Step 3: Commit**

```bash
git add documentation/about.bs documentation/about.html
git commit -m "feat: extract family-wide content into documentation/about.bs"
```

---

### Task 3: Move MiKaDiv's module content into `mikadiv/index.bs`

**Files:**
- Create: `mikadiv/index.bs`
- Delete: `documentation/index.bs`
- Modify: `generate_template.py` (no functional change needed — `ModuleConfig`
  already points at `mikadiv/generated/`, unaffected by the `.bs` source
  file's own location; confirm this in Step 3, don't assume)
- Modify: `Dockerfile` (build command now targets `mikadiv/index.bs` instead
  of `documentation/index.bs` — full rewrite in Task 7, this task only needs
  its own build command to prove the new file works, see Step 2)

**Interfaces:**
- Consumes: the five anchor IDs recorded in Task 2 Step 2.
- Produces: `mikadiv/index.html`, built at clean URL `/mikadiv`.

- [ ] **Step 1: Write `mikadiv/index.bs`**

MiKaDiv-specific content only (source schema, data model, linking model,
conformance requirements, the generated-include pull), new metadata block,
`[=term=]` autolinks replaced with `[[openfaster#anchor-id]]` cross-document
references using Task 2's recorded anchor IDs (shown below as
`{{CFI_ANCHOR}}`, `{{DISCLOSURE_ANCHOR}}`, `{{REQUESTID_ANCHOR}}`,
`{{PAYING_AGENT_ANCHOR}}`, `{{TAX_VOUCHER_ANCHOR}}` — replace each with the
real anchor ID recorded in Task 2 Step 2 before committing; do not leave
these placeholder tokens in the committed file):

```
<pre class=metadata>
Title: MiKaDiv Third-Party Disclosure
Shortname: mikadiv
Level: 1
Status: DREAM
URL: https://openfaster.org/mikadiv
Repository: https://github.com/OpenFASTER-Standard/spec
Text Macro: LONGSTATUS MiKaDiv Third-Party Disclosure -- a module of the OpenFASTER family
Text Macro: DOCVERSION 1.0.0
Metadata Order: This version, Issue Tracking, Editor, *
!This version: <p class="spec-version">Version <strong>[DOCVERSION]</strong></p>
Editor: Julian Nalenz, https://github.com/sigalor
Editor: Alaa Eddine Cherif, https://github.com/AlaaCherif
Abstract: The MiKaDiv Third-Party Disclosure format is a module of the
    <a href="/about">OpenFASTER</a> family: a self-documenting data model
    (with an accompanying Excel template) that mirrors the German MiKaDiv
    (§45b EStG) capital-income disclosure schema.
Markup Shorthands: markdown yes, dfn yes, css no
Boilerplate: omit conformance
Local Boilerplate: header yes
Complain About: accidental-2119 yes, missing-example-ids yes
</pre>

The MiKaDiv Third-Party Disclosure module {#mikadiv-module}
===========================================================

The MiKaDiv (§45b EStG) **third-party disclosure** module defines the data
required to describe a capital-income event, the securities involved, every
party in the chain, and the receipts and deliveries that support a
first-in-first-out (FIFO) determination.

An accompanying self-documenting Excel template is published alongside this
specification:
[MiKaDiv Third-Party Disclosure Template](https://github.com/OpenFASTER-Standard/spec/blob/main/mikadiv/generated/MiKaDiv_ThirdPartyDisclosure_Template.xlsx).
Each sheet mirrors one logical group below; every field carries its English
description, type constraints, and requiredness in the header rows.

Source schema {#source-schema}
------------------------------

The data model of this module is derived from the XML Schema Definition (XSD)
produced by the VIB (Verband Internationaler Banken e.V.), the
association representing internationally active banks in Germany. The VIB is
developing this schema to standardize the electronic exchange of MiKaDiv
third-party disclosure data between banks and towards the German
[[openfaster#{{PAYING_AGENT_ANCHOR}}|paying agent]].

OpenFASTER treats the VIB XSD as the machine source of truth: the field
definitions, requiredness, enumerations, the [[#data-dictionary|data dictionary]]
in this document, and the accompanying Excel template are all generated directly
from it. As the VIB schema evolves, regenerating from the updated XSD keeps this
specification and the template in lock-step with the VIB source.

Data model {#data-model}
------------------------

A [[openfaster#{{DISCLOSURE_ANCHOR}}|disclosure]] is decomposed into several
logical groups (rendered as separate sheets in the Excel template). Every
group carries the [[openfaster#{{REQUESTID_ANCHOR}}|RequestId]] so that the
groups can be recombined into one record.

<table class="data">
  <thead>
    <tr><th>Group<th>Rows per RequestId<th>Purpose
  <tbody>
    <tr><td>Requests Master<td>1<td>Request-level metadata; new request vs cancellation; account owner scalars.
    <tr><td>Security Related Information<td>0..1<td>The capital-income event, security identification, tax breakdown, and depositary-receipt block.
    <tr><td>Tax Voucher Individuals / Legal Persons<td>up to 2 receivers total<td>The recipients of the [[openfaster#{{TAX_VOUCHER_ANCHOR}}|tax voucher]].
    <tr><td>Third Party Individuals / Legal Persons<td>up to 5 total<td>Account holders who are not the beneficial owner.
    <tr><td>Custody Chain<td>up to 20<td>The ordered intermediary chain, closest-to-beneficiary first.
    <tr><td>FIFO Trades<td>up to 1000 each way<td>Receipts and deliveries with FIFO already applied by the submitter.
    <tr><td>Raw Transactions All<td>unbounded<td>The unreduced ledger when the paying agent performs the FIFO calculation.
</table>

When the raw ledger is supplied, the German
[[openfaster#{{PAYING_AGENT_ANCHOR}}|paying agent]] performs the FIFO
determination; when the submitter applies FIFO itself, the reduced trades are
supplied directly.

Linking model {#linking-model}
------------------------------

The [[openfaster#{{REQUESTID_ANCHOR}}|RequestId]] is the key on the *Requests
Master* group and the first column of every other group. Because it is used
only to join the groups, any value that is unique within a submission works.

* <b>Cancellations.</b> Set `RecordType` = `Cancel` on the master group, fill
    `PreviousRequestIdForCancellation` (and optionally `ReportSerialNumber`), and
    leave every other group empty for that RequestId.
* <b>Community recipients.</b> A community tax-voucher receiver (up to 10
    members) is captured by setting `ReceiverGroupType` = `CommunityMember` on
    the tax-voucher groups and giving all members of one community the same
    `CommunityGroupId`. A community counts as one receiver.

Conformance requirements {#module-conformance}
----------------------------------------------

A conforming producer MUST populate every field marked `Required` for each group
it emits. Fields marked `Conditional` MUST be populated when the condition stated
in their description holds, and MUST otherwise be omitted or left empty. Fields
marked `Optional` MAY be omitted.

Enum-typed fields MUST carry one of the values enumerated for that field in
[[#enumerations|Enumerations]]. A conforming consumer MUST reject a
disclosure whose enum-typed field carries a value outside the enumerated set.

<pre class=include>
path: generated/fields.include.bs
</pre>
```

Note the include path changed from `../mikadiv/generated/fields.include.bs`
(correct when the `.bs` source lived in `documentation/`, one level away
from `mikadiv/`) to `generated/fields.include.bs` (correct now that the `.bs`
source lives directly inside `mikadiv/`, a sibling of `generated/`).

Also note: the changelog/versioning boilerplate (`Metadata Order`,
`!This version`, `Text Macro: DOCVERSION`) is retained here (unlike
`about.bs`, which dropped it) since MiKaDiv is the module that actually has
a real version history — its own `documentation/changelog.include.bs`-style
mechanism is addressed in Task 7 (the changelog stays associated with the
module it describes, not the family-wide `about.bs`).

- [ ] **Step 2: Build and verify `mikadiv/index.bs` standalone**

```bash
python generate_template.py
bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv/index.bs mikadiv/index.html
```

Expected: builds cleanly with zero link errors — this is the real proof the
five `[[openfaster#...]]` cross-references resolve correctly against
`documentation/about.html`'s actual anchor IDs. If Bikeshed reports an
unresolved cross-reference, re-check the anchor ID recorded in Task 2 Step 2
against what `about.html` actually contains (`grep 'id="' documentation/about.html`
to list every real anchor) rather than guessing at the right ID.

- [ ] **Step 3: Confirm `generate_template.py` needs no change**

Read `generate_template.py`'s `ModuleConfig` for mikadiv: `xsd_path` and
`output_dir` are both already expressed relative to `ROOT` (the repository
root, via `Path(__file__).resolve().parent`), pointing at
`mikadiv/ThirdPartyDisclosureRequest.xsd` and `mikadiv/generated/` — neither
depends on where the `.bs` source file lives. Confirm this by re-reading the
file; no edit needed here.

- [ ] **Step 4: Delete the old `documentation/index.bs` and its build output**

```bash
git rm documentation/index.bs
rm -f index.html   # old MiKaDiv-as-root output; the URL slot is reclaimed by Task 4's portal
```

- [ ] **Step 5: Commit**

```bash
git add mikadiv/index.bs mikadiv/index.html
git commit -m "feat: move MiKaDiv module content from documentation/index.bs to mikadiv/index.bs"
```

---

### Task 4: Hand-authored root portal

**Files:**
- Create: `index.html` (repo root — reclaimed from Task 3's deletion)

**Interfaces:**
- Produces: the site root at `/`, linking `/mikadiv`, `/streamld`, `/about`,
  and Riptide's GitHub repo.

- [ ] **Step 1: Write `index.html`**

Plain static HTML — not Bikeshed-compiled (per spec §5.1, it isn't a spec
document, it's a directory of them). Duplicates the shared shell's header
markup by hand (Task 1's `documentation/header.template.include` produces
the same header for every Bikeshed-built page; this file is the one place
that markup is repeated rather than templated — see the note at the end of
this step for why that's an accepted, deliberate choice, not an oversight).

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>OpenFASTER</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="stylesheet" href="/documentation/site.css">
  <link rel="stylesheet" href="/documentation/shell.css">
  <style>
    body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; margin: 0; color: #1a1a1a; }
    main { max-width: 52rem; margin: 0 auto; padding: 2rem 1.5rem; }
    .of-portal-lede { font-size: 1.05rem; color: #333; margin-bottom: 2.5rem; }
    .of-portal-lede a { color: #0b3d6e; }
    .of-portal-section h2 { border-bottom: 1px solid #d8d8d8; padding-bottom: 0.4rem; }
    .of-portal-item { display: flex; align-items: baseline; gap: 0.75rem; padding: 0.6rem 0; border-bottom: 1px solid #f0f0f0; }
    .of-portal-item:last-child { border-bottom: none; }
    .of-portal-item-name { font-weight: 700; min-width: 8rem; }
    .of-portal-item-name a { color: #0b3d6e; text-decoration: none; }
    .of-portal-item-name a:hover { text-decoration: underline; }
    .of-portal-item-desc { flex: 1; color: #444; }
    .of-portal-item-status { font-size: 0.8rem; padding: 0.15rem 0.5rem; border-radius: 0.75rem; background: #eef2f7; color: #0b3d6e; white-space: nowrap; }
  </style>
</head>
<body class="h-entry">
<header class="of-shell-header">
  <a class="of-shell-logo" href="/">OpenFASTER</a>
  <nav class="of-shell-nav">
    <a href="#standards">Standards</a>
    <a href="#implementations">Implementations</a>
    <a href="/about">About</a>
  </nav>
</header>
<main>
  <p class="of-portal-lede">
    OpenFASTER is a vendor-independent family of open standards for EU
    withholding-tax and dividend-reporting data exchange under MiKaDiv and
    FASTER. See <a href="/about">About OpenFASTER</a> for scope, terminology,
    and versioning policy.
  </p>

  <section class="of-portal-section" id="standards">
    <h2>Standards</h2>
    <div class="of-portal-item">
      <span class="of-portal-item-name"><a href="/mikadiv">MiKaDiv Third-Party Disclosure</a></span>
      <span class="of-portal-item-desc">Data model for German MiKaDiv (§45b EStG) capital-income third-party disclosure.</span>
      <span class="of-portal-item-status">v1.0.0</span>
    </div>
    <div class="of-portal-item">
      <span class="of-portal-item-name"><a href="/streamld">StreamLD</a></span>
      <span class="of-portal-item-desc">A protocol for real-time, resumable Linked Data event streaming.</span>
      <span class="of-portal-item-status">CG-Draft</span>
    </div>
  </section>

  <section class="of-portal-section" id="implementations">
    <h2>Reference Implementations</h2>
    <div class="of-portal-item">
      <span class="of-portal-item-name"><a href="https://github.com/OpenFASTER-Standard/riptide">Riptide</a></span>
      <span class="of-portal-item-desc">Elixir/Phoenix reference implementation of StreamLD -- an event-driven Solid/LDP-compatible pod server.</span>
      <span class="of-portal-item-status">Reference impl.</span>
    </div>
  </section>
</main>
<footer class="of-shell-footer">
  <p>OpenFASTER is licensed <a href="https://creativecommons.org/licenses/by/4.0/deed.en">CC BY 4.0</a>. Source at <a href="https://github.com/OpenFASTER-Standard/spec">github.com/OpenFASTER-Standard/spec</a>.</p>
</footer>
</body>
</html>
```

**On the accepted header duplication:** this file's `<header class="of-shell-header">...</header>` block is byte-for-byte the same markup Task 1 put in `documentation/header.template.include`. Building a templating mechanism just to share ~10 lines of static HTML between one hand-authored page and Bikeshed's own boilerplate system (which has no native "include a non-Bikeshed HTML file verbatim" mechanism suited to this) would be over-engineering for a site this size. If the header markup ever changes, both places must be updated by hand — acceptable for a two-copy duplication; revisit only if a third hand-authored (non-Bikeshed) page is ever added.

- [ ] **Step 2: Verify locally**

Open `index.html` directly in a browser (or serve the repo root with
`python -m http.server` and visit it). Confirm: the header renders
identically to Task 1's verification screenshot/description, both sections
list the right items, and — since Tasks 5/6 haven't run yet — the
`/streamld` link may 404 for now (expected at this point).

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: hand-authored root portal replacing MiKaDiv-as-homepage"
```

---

### Task 5: Fix StreamLD's 4 existing documents

**Files:**
- Modify: `streamld/core.bs`
- Modify: `streamld/subscription.bs`
- Modify: `streamld/binding-sse.bs`
- Modify: `streamld/binding-websocket.bs`

**Interfaces:**
- Produces: `streamld/core.html`, `streamld/subscription.html`,
  `streamld/binding-sse.html`, `streamld/binding-websocket.html`, each now
  reachable at clean URLs (`/streamld/core`, etc.), each using the shared
  shell, each linking back to `/streamld` (Task 6's new index page — build
  order note: Task 6 must land before these 4 pages' back-links resolve
  without a link error, so do Task 6 first if building incrementally, or
  treat Tasks 5+6 as one combined build-and-verify pass).

- [ ] **Step 1: Update `streamld/core.bs`**

Change the metadata block's `URL:` line and add `Local Boilerplate: header
yes`; change internal cross-links from `.html`-suffixed to extension-less;
add a back-link to the module index. Full new metadata block:

```
<pre class='metadata'>
Title: StreamLD Core
Shortname: streamld-core
Level: 1
Status: w3c/CG-DRAFT
URL: https://openfaster.org/streamld/core
Local Boilerplate: header yes
Editor: OpenFASTER Editors
Abstract: StreamLD is a protocol for real-time, resumable Linked Data event streaming. This document defines the core event envelope and cursor model that every StreamLD transport binding builds on. Part of the <a href="/streamld">StreamLD module</a>.
</pre>
```

Then, in the document body, find every `href="subscription.html"`,
`href="binding-sse.html"`, `href="binding-websocket.html"` (if any appear in
`core.bs`'s body beyond the Abstract — check by reading the full file, not
just the metadata block) and change to the extension-less form
(`href="subscription"`, `href="binding-sse"`, `href="binding-websocket"`).
Add one line near the top of the document body (right after the metadata/
biblio blocks, before the first `#` heading) linking back to the module
index:

```
<p><a href="/streamld">← Back to the StreamLD module index</a></p>
```

- [ ] **Step 2: Update `streamld/subscription.bs`**

Same pattern. New metadata block:

```
<pre class='metadata'>
Title: StreamLD Subscription and Discovery
Shortname: streamld-subscription
Level: 1
Status: w3c/CG-DRAFT
URL: https://openfaster.org/streamld/subscription
Local Boilerplate: header yes
Editor: OpenFASTER Editors
Abstract: Defines how a client discovers a stream's subscription endpoint(s), independent of which transport binding (<a href="binding-sse">StreamLD SSE Binding</a> or <a href="binding-websocket">StreamLD WebSocket Replication Binding</a>) it then uses. Part of the <a href="/streamld">StreamLD module</a>.
</pre>
```

Fix any body-level `href="binding-sse.html"`/`href="binding-websocket.html"`/
`href="core.html"` links the same way (extension-less), and add the same
`<p><a href="/streamld">← Back to the StreamLD module index</a></p>` line
near the top of the body.

- [ ] **Step 3: Update `streamld/binding-sse.bs`**

```
<pre class='metadata'>
Title: StreamLD SSE Binding
Shortname: streamld-sse
Level: 1
Status: w3c/CG-DRAFT
URL: https://openfaster.org/streamld/binding-sse
Local Boilerplate: header yes
Editor: OpenFASTER Editors
Abstract: Defines how StreamLD's cursor-based subscription model (see <a href="core">StreamLD Core</a>) is carried over Server-Sent Events, for server-to-client delivery. Part of the <a href="/streamld">StreamLD module</a>.
</pre>
```

Fix body-level `href="core.html"` links to `href="core"`, add the back-link
line.

- [ ] **Step 4: Update `streamld/binding-websocket.bs`**

```
<pre class='metadata'>
Title: StreamLD WebSocket Replication Binding
Shortname: streamld-websocket
Level: 1
Status: w3c/CG-DRAFT
URL: https://openfaster.org/streamld/binding-websocket
Local Boilerplate: header yes
Editor: OpenFASTER Editors
Abstract: Defines StreamLD's server-to-server replication binding over WebSockets — the transport a downstream server uses to mirror an upstream stream in full, in order, with explicit resumption. Part of the <a href="/streamld">StreamLD module</a>.
</pre>
```

Fix body-level `href="binding-sse.html"` links to `href="binding-sse"`, add
the back-link line.

- [ ] **Step 5: Build all 4 and verify**

```bash
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/core.bs streamld/core.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/subscription.bs streamld/subscription.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-sse.bs streamld/binding-sse.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-websocket.bs streamld/binding-websocket.html
```

Expected: all 4 build cleanly. Open each and confirm the shared shell header
renders and the back-link to `/streamld` is present (it will 404 until Task
6 lands — expected if building Task 5 and 6 as genuinely separate commits;
acceptable since this is a link-target-not-yet-existing situation, not a
malformed link, and Bikeshed's `--die-on=link-error` only checks
Bikeshed-resolvable cross-references, not arbitrary `<a href>` targets, so
this doesn't fail the build).

- [ ] **Step 6: Commit**

```bash
git add streamld/*.bs streamld/*.html
git commit -m "feat: fix StreamLD's 4 documents -- clean URLs, shared shell, back-links"
```

---

### Task 6: New StreamLD module index (`streamld/index.bs`)

**Files:**
- Create: `streamld/index.bs`

**Interfaces:**
- Produces: `streamld/index.html`, built at clean URL `/streamld`, linking
  the 4 documents Task 5 fixed and back to `/`.

- [ ] **Step 1: Write `streamld/index.bs`**

```
<pre class=metadata>
Title: StreamLD
Shortname: streamld
Level: 1
Status: w3c/CG-DRAFT
URL: https://openfaster.org/streamld
Local Boilerplate: header yes
Editor: OpenFASTER Editors
Abstract: StreamLD is a protocol for real-time, resumable Linked Data event
    streaming, incubating within the <a href="/about">OpenFASTER</a> family.
    This page indexes its four documents. The reference implementation is
    <a href="https://github.com/OpenFASTER-Standard/riptide">Riptide</a>
    (Elixir/Phoenix).
Markup Shorthands: markdown yes, dfn yes, css no
Boilerplate: omit conformance
</pre>

StreamLD {#streamld-module}
============================

StreamLD defines an append-only, per-stream Linked Data event log with
real-time subscription. It is split into four documents:

* [StreamLD Core](core) — the event envelope and cursor model every binding
    builds on.
* [StreamLD Subscription and Discovery](subscription) — how a client
    discovers a stream's subscription endpoint(s).
* [StreamLD SSE Binding](binding-sse) — the Server-Sent Events transport for
    server-to-client delivery.
* [StreamLD WebSocket Replication Binding](binding-websocket) — the
    server-to-server replication transport.

<p><a href="/">← Back to the OpenFASTER portal</a></p>
```

- [ ] **Step 2: Build and verify**

```bash
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/index.bs streamld/index.html
```

Expected: builds cleanly. Open the result and confirm all 4 links resolve to
the right pages (extension-less, matching Task 5's fixed `URL:` metadata)
and the shared shell renders.

- [ ] **Step 3: Re-verify Task 5's 4 documents now that this index exists**

Re-run all 4 `bikeshed spec` commands from Task 5 Step 5. Confirm each
page's `/streamld` back-link now resolves (open each page, click the
back-link, confirm it lands on this new index page — a manual browser check
since Bikeshed's own link checker doesn't validate arbitrary `<a href>`
targets against the filesystem, only its own cross-reference syntax).

- [ ] **Step 4: Commit**

```bash
git add streamld/index.bs streamld/index.html
git commit -m "feat: add streamld/index.bs -- StreamLD module landing page"
```

---

### Task 7: Complete CI workflow

**Files:**
- Create: `.github/workflows/spec.yml`
- Delete: `Dockerfile` (superseded — see Step 4 for why, and what replaces
  its "run this locally on Windows" use case)

**Interfaces:**
- Consumes: every build command established in Tasks 1-6 (about.bs,
  mikadiv/index.bs, streamld/index.bs, streamld's 4 documents), plus
  `streamld/generator/generate_streamld_docs.py` (StreamLD's SHACL-based
  generator, parallel to `generate_template.py` but never previously wired
  into any documented build command — confirmed via `git log`/`README.md`
  grep, this is a real, pre-existing gap this task closes).
- Produces: on every push to `main`, a workflow that rebuilds every output
  file from source and commits the result if anything changed — closing the
  actual, confirmed gap between `README.md`'s current claim (a
  `.github/workflows/spec.yml` that doesn't exist) and reality.

- [ ] **Step 1: Write `.github/workflows/spec.yml`**

```yaml
name: Build OpenFASTER site

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install system dependencies (WeasyPrint's native libs)
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends \
            libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libfontconfig1 libcairo2

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt -r documentation/requirements-spec.txt -r streamld/tests/requirements.txt
          bikeshed update

      - name: Build MiKaDiv (XSD -> generated include -> Excel template)
        run: python generate_template.py

      - name: Build StreamLD (SHACL -> generated include + JSON Schema)
        run: python -m streamld.generator.generate_streamld_docs

      - name: Regenerate header boilerplate (embeds the changelog)
        run: python documentation/prepare_spec.py

      - name: Build documentation/about.html
        run: bikeshed --allow-nonlocal-files --die-on=link-error spec documentation/about.bs documentation/about.html

      - name: Build mikadiv/index.html + PDF
        run: |
          bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv/index.bs mikadiv/index.html
          weasyprint --stylesheet documentation/print.css mikadiv/index.html documentation/openfaster.pdf

      - name: Build streamld/index.html
        run: bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/index.bs streamld/index.html

      - name: Build StreamLD's 4 documents
        run: |
          bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/core.bs streamld/core.html
          bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/subscription.bs streamld/subscription.html
          bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-sse.bs streamld/binding-sse.html
          bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-websocket.bs streamld/binding-websocket.html

      - name: Run streamld's own test suite
        run: |
          pip install -r streamld/tests/requirements.txt
          python -m pytest streamld/tests/

      - name: Commit regenerated output (main branch only)
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add index.html mikadiv/index.html mikadiv/generated/ documentation/about.html documentation/header.include documentation/openfaster.pdf streamld/index.html streamld/core.html streamld/subscription.html streamld/binding-sse.html streamld/binding-websocket.html streamld/generated/
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "chore: rebuild site [skip ci]"
            git push
          fi
```

Note `[skip ci]` in the auto-commit message — without it, the bot's own
push would re-trigger this same workflow, looping forever. Confirm GitHub
Actions actually honors `[skip ci]` in a commit message for this repo's
default configuration (it does by default for `push` events, per GitHub's
own documented convention — but verify live in Step 3 rather than trust
this note alone, since a misconfigured branch-protection rule could
override it).

Note `index.html` is included in the commit list even though Task 4's
portal is hand-authored, not built by this workflow — this is intentional:
including it in `git add` is a no-op if it's unchanged (the common case),
and only matters if a future task's build step ever needs to touch it; do
not add a build step that regenerates `index.html` from anything, since
none exists.

- [ ] **Step 2: Delete the Dockerfile**

```bash
git rm Dockerfile
```

The Dockerfile's stated purpose ("reproducible spec + PDF build... notably
on Windows, where WeasyPrint's native dependencies are otherwise awkward")
is superseded for the *automated* path by this GitHub Actions workflow
(runs on Linux, no Windows-specific awkwardness applies to CI). A
Windows-based contributor building locally still has `README.md`'s
documented "Option A - local Python" instructions plus a note that Docker
is no longer provided — update `README.md`'s own "Option B - Docker" section
in Task 8 to remove this now-dead option rather than leaving a reference to
a deleted file.

- [ ] **Step 3: Push to a branch and verify the workflow runs correctly (before merging to `main`)**

This is real, live verification, not a written-and-assumed step:

```bash
git checkout -b verify-ci-workflow
git push -u origin verify-ci-workflow
```

Open a draft/test PR against `main` (or check the Actions tab directly for
the branch push) and confirm: the workflow runs, every build step succeeds,
`pytest streamld/tests/` passes, and — since this is a `pull_request` event,
not a `push` to `main` — the "Commit regenerated output" step is correctly
skipped (confirm the `if:` condition evaluates false, not that the step
silently no-ops for some other reason). Do not merge to `main` until this
live run is confirmed green.

- [ ] **Step 4: Commit the workflow itself**

```bash
git add .github/workflows/spec.yml
git commit -m "feat: add complete CI workflow -- mikadiv + streamld + about, closing the gap README.md already claimed was fixed"
```

---

### Task 8: Fix `README.md`

**Files:**
- Modify: `README.md`

**Interfaces:** none (documentation only).

- [ ] **Step 1: Update the repository layout diagram**

Change the "Repository layout" ASCII tree (lines 13-40 of the current file)
to reflect the new locations: `mikadiv/index.bs` (was
`documentation/index.bs`), add `documentation/about.bs`/`about.html`, add
`streamld/index.bs`/`index.html` and the existing 4 documents, note
`index.html` at repo root is now the hand-authored portal (not generated),
and add `.github/workflows/spec.yml` to the tree (it exists now).

- [ ] **Step 2: Fix the "Building the specification" section**

Update "Option A - local Python" to reflect the real, complete build
sequence established in Tasks 1-6 (about.bs, mikadiv/index.bs,
streamld/index.bs, streamld's 4 documents, both generators). Remove "Option
B - Docker" entirely (Task 7 deleted the Dockerfile). Update "Option C - CI"
to describe what `.github/workflows/spec.yml` actually does now (rebuilds
and auto-commits on push to `main` — not "publishes to GitHub Pages"; the
real deploy target is still Vercel, serving the committed output, per the
spec's own §7 Approach A).

- [ ] **Step 3: Fix the "Deploying to openfaster.org" section**

Remove the "or let the CI workflow deploy them to GitHub Pages" sentence —
this was never true and Approach A doesn't make it true; CI commits, Vercel
deploys from the commit, as it already does today.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: fix README to describe the real build/deploy pipeline"
```

---

### Task 9: Live deployment verification

**Files:** none (verification only, per spec §8).

- [ ] **Step 1: Merge to `main` and confirm the CI workflow runs and auto-commits**

Only after Task 7 Step 3's separate-branch dry run was confirmed green.
Merge (or push directly to `main`, matching this repo's own convention —
confirm with the operator which is expected before doing this step, since
it's the first genuinely live-deploying action in this plan). Watch the
Actions tab; confirm the auto-commit lands.

- [ ] **Step 2: Confirm Vercel actually redeploys from the new commit**

Check Vercel's dashboard (or `vercel ls`/`vercel inspect` if CLI access is
available) for a new deployment triggered by the auto-commit. Do not assume
Vercel's GitHub integration picks up a bot-authored commit the same way as
a human one — confirm live.

- [ ] **Step 3: Verify every clean URL actually resolves as designed**

Live, against the deployed site, not assumed from `vercel.json`'s
configured flags (per spec §8's explicit "Clean-URL verification"
requirement):

```bash
for path in / /about /mikadiv /streamld /streamld/core /streamld/subscription /streamld/binding-sse /streamld/binding-websocket; do
  echo "=== $path ==="
  curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" -L "https://www.openfaster.org$path"
done
```

Expected: every path returns `200` with no unexpected redirect chain
(watch for an accidental trailing-slash redirect loop, given
`trailingSlash: false` — confirm the *first* response for each path is
already `200`, not a `308`-then-`200` two-hop that would indicate a link
somewhere still uses the wrong form).

- [ ] **Step 4: Verify the PDF still builds and downloads correctly**

```bash
curl -s -o /dev/null -w "%{http_code}\n" -L "https://www.openfaster.org/openfaster.pdf"
```

Expected: `200`. Open the downloaded PDF and confirm it's MiKaDiv's content
(matching Task 3's `weasyprint` target), not stale content from before this
plan's changes.

- [ ] **Step 5: Full link-integrity walkthrough**

Starting from `/`, click through every link a real visitor would: Standards
→ MiKaDiv, Standards → StreamLD → each of its 4 documents → back-link →
StreamLD index → back-link → portal, Implementations → Riptide (external,
confirm it lands on the real GitHub repo), About → confirm the 5 terms
render with working same-document anchors. Confirm nothing 404s.

---

## Self-Review Notes (from plan authoring)

- **Spec coverage:** every numbered section of the spec (§5.1-§5.5 site
  structure, §6 visual shell, §7 CI/deploy, §8 testing) maps to a task
  above. The spec's own open question about where root's family-wide prose
  goes (flagged in §5.1-§5.2 as left slightly open) is resolved by Task 2
  (a standalone `documentation/about.bs`) with explicit reasoning recorded
  in that task's own text.
- **Placeholder scan:** the only bracketed placeholders in this plan
  (`{{CFI_ANCHOR}}` etc. in Task 3) are explicitly flagged as
  must-be-replaced-before-commit, with the exact mechanism (grep
  `about.html` for real anchor IDs) to replace them — not a "TBD left for
  later."
- **Type/interface consistency:** every `URL:` metadata value introduced
  across Tasks 2/3/5/6 uses the same no-trailing-slash clean-URL form
  established in Global Constraints; every module's back-link target
  (`/streamld`, `/about`, `/`) matches the producing task's own declared
  output URL exactly. The CI workflow's `git add` file list (Task 7) matches
  every output file named across Tasks 1-6 exactly (cross-checked file by
  file while writing Task 7 Step 1).
