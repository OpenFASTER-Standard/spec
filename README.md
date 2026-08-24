# OpenFASTER

**Vendor-independent, interoperable family of open standards for EU
withholding-tax and dividend-reporting data exchange under MiKaDiv and FASTER.**

OpenFASTER is designed as a suite of modular specifications (in the spirit of
families such as CSS or RDF), with the long-term ambition of maturing onto a
formal international standards track. Its first concrete module is the **MiKaDiv
Third-Party Disclosure format**, derived directly from
[`mikadiv-vib/ThirdPartyDisclosureRequest.xsd`](mikadiv-vib/ThirdPartyDisclosureRequest.xsd)
(German §45b EStG capital-income disclosure).

## Repository layout

The repository is organized by concern - a shared engine, one folder per module,
and the documentation/specification kept separate:

```
├── engine/                        # shared, module-agnostic generator
│   ├── xsd_model.py               #   Layer 1: XSD extractor (via xmlschema)
│   ├── generator.py               #   Layer 3: renders workbook + docs + include
│   └── version.py                 #   reads a module's canonical version from its .bs source
├── mikadiv-vib/                   # the MiKaDiv Third-Party Disclosure module
│   ├── ThirdPartyDisclosureRequest.xsd   # schema (machine source of truth)
│   ├── mapping.py                 #   Layer 2: template shape for this module
│   ├── index.bs                   #   Bikeshed source; built to index.html, served at /mikadiv-vib
│   └── generated/                 #   generated artifacts (do not edit by hand)
│       ├── mikadiv-vib-v<version>.xlsx
│       ├── mikadiv-vib-v<version>.pdf
│       ├── template_metadata.json
│       ├── TEMPLATE_FIELDS.md
│       └── fields.include.bs
├── documentation/                 # family-wide "About" page + shared build assets
│   ├── about.bs                   #   Bikeshed source; built to about.html, served at /about
│   ├── prepare_spec.py            #   embeds the changelog into header boilerplate
│   ├── requirements-spec.txt      #   spec build deps (bikeshed, weasyprint)
│   └── print.css                  #   PDF stylesheet
├── streamld/                      # the StreamLD module: a landing page + 4 documents
│   ├── index.bs                   #   module landing page; built to index.html, served at /streamld
│   ├── core.bs                    #   built to core.html, served at /streamld/core
│   ├── subscription.bs            #   built to subscription.html, served at /streamld/subscription
│   ├── binding-sse.bs             #   built to binding-sse.html, served at /streamld/binding-sse
│   ├── binding-websocket.bs       #   built to binding-websocket.html, served at /streamld/binding-websocket
│   ├── generator/                 #   SHACL -> generated include + JSON Schema
│   └── generated/                 #   generated artifacts (do not edit by hand)
├── index.html                     # hand-authored portal (NOT Bikeshed-compiled); served at site root
├── 404.html                       # hand-authored fallback (NOT Bikeshed-compiled); redirects to site root
├── generate_template.py           # MiKaDiv-VIB build entry point (wires engine + module)
├── requirements.txt               # engine deps (openpyxl, xmlschema)
├── .github/workflows/spec.yml     # CI: rebuilds every output on push/PR, auto-commits on push to main
└── vercel.json                    # deploy routing (clean URLs, rewrites)
```

Adding a future module (e.g. FASTER) means adding a sibling module folder with
its own XSD + `mapping.py`, and one `ModuleConfig` entry in
[`generate_template.py`](generate_template.py) - the engine and documentation
stay shared.

## Single source of truth

The **XSD is the machine source of truth**. All field-level content -
descriptions, type/format strings, requiredness, cardinality and enumerations
(values *and* their meanings) - is parsed directly out of each module's XSD;
none of it is hand-typed. Every human-facing artifact is **generated** from that
schema, so nothing can drift apart:

```mermaid
flowchart LR
  xsd["mikadiv-vib/ThirdPartyDisclosureRequest.xsd"] --> model["engine/xsd_model.py"]
  map["mikadiv-vib/mapping.py (template shape)"] --> gen["engine/generator.py"]
  model --> gen
  gen --> meta["mikadiv-vib/generated/template_metadata.json"]
  meta --> incl["mikadiv-vib/generated/fields.include.bs"]
  incl --> bs["mikadiv-vib/index.bs"]
  bs --> html["mikadiv-vib/index.html"]
  bs --> pdf["mikadiv-vib/generated/mikadiv-vib-v<version>.pdf"]
  meta --> xlsx["mikadiv-vib/generated/mikadiv-vib-v<version>.xlsx"]
```

Generation is layered so the schema stays authoritative while the template's
presentation stays controllable:

1. **`engine/xsd_model.py`** (Layer 1) - loads the XSD with
   [`xmlschema`](https://pypi.org/project/xmlschema/) and answers "what does the
   schema say about field X of type Y?" (documentation, format, requiredness,
   enums). No hand-typed content. Shared by every module.
2. **`mikadiv-vib/mapping.py`** (Layer 2) - declares the template *shape*: which
   sheets exist, their column order, how nested XSD choices flatten into columns,
   and the few presentation-only helper columns (e.g. `RecordType`,
   `PersonTaxCategory`) that model a schema choice as a flat column. It says
   *where* each column comes from, never *what it means*.
3. **`engine/generator.py`** (Layer 3) - renders the workbook, metadata, docs
   and Bikeshed include from the merged model. Shared by every module;
   parametrised per module by a `ModuleConfig` in `generate_template.py`.

| File | Role | Edited by hand? |
| --- | --- | --- |
| [`mikadiv-vib/ThirdPartyDisclosureRequest.xsd`](mikadiv-vib/ThirdPartyDisclosureRequest.xsd) | Schema; machine source for all field content | Yes (the schema) |
| [`mikadiv-vib/index.bs`](mikadiv-vib/index.bs) | Bikeshed specification source (prose, structure, roadmap) | Yes |
| [`engine/xsd_model.py`](engine/xsd_model.py) | Layer 1: XSD extractor (via `xmlschema`) | Yes |
| [`mikadiv-vib/mapping.py`](mikadiv-vib/mapping.py) | Layer 2: template shape + presentation-only columns | Yes |
| [`engine/generator.py`](engine/generator.py) | Layer 3: renders metadata, docs, Bikeshed include, and Excel template | Yes |
| [`engine/version.py`](engine/version.py) | Reads a module's canonical version from its `.bs` source | Yes |
| [`generate_template.py`](generate_template.py) | Build entry point; wires the engine to each module | Yes |
| `mikadiv-vib/generated/template_metadata.json` | Machine-readable field metadata store | Generated |
| `mikadiv-vib/generated/fields.include.bs` | Data dictionary + enumerations, pulled into `index.bs` | Generated |
| `mikadiv-vib/generated/TEMPLATE_FIELDS.md` | Human-readable field reference | Generated |
| `mikadiv-vib/generated/mikadiv-vib-v<version>.xlsx` | Fillable Excel template | Generated |
| `mikadiv-vib/index.html` | Built HTML spec, compiled from `mikadiv-vib/index.bs` | Generated |
| `mikadiv-vib/generated/mikadiv-vib-v<version>.pdf` | Built PDF, rendered from `mikadiv-vib/index.html` (downloadable via GitHub raw link, see `mikadiv-vib/index.bs`'s Downloads section) | Generated |
| `index.html` | Hand-authored site portal (NOT Bikeshed-compiled); served at site root | Yes (hand-authored, not built) |
| `404.html` | Hand-authored fallback (NOT Bikeshed-compiled); redirects unmatched paths to site root | Yes (hand-authored, not built) |

## Building the specification

The data dictionary in the spec is regenerated from the metadata, then compiled
by [Bikeshed](https://speced.github.io/bikeshed/) to HTML, and rendered to PDF.

### Option A - local Python

```bash
python -m pip install -r requirements.txt -r documentation/requirements-spec.txt -r streamld/tests/requirements.txt
bikeshed update            # first run only, fetches Bikeshed data files

python generate_template.py                                  # MiKaDiv-VIB: XSD -> generated include + Excel template
PYTHONPATH=streamld python -m generator.generate_streamld_docs   # StreamLD: SHACL -> generated include + JSON Schema

python documentation/prepare_spec.py              # embed changelog into header boilerplate

bikeshed --allow-nonlocal-files --die-on=link-error spec documentation/about.bs documentation/about.html

bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv-vib/index.bs mikadiv-vib/index.html
MIKADIV_VIB_VERSION=$(python -m engine.version mikadiv-vib/index.bs)
weasyprint --stylesheet documentation/print.css mikadiv-vib/index.html mikadiv-vib/generated/mikadiv-vib-v${MIKADIV_VIB_VERSION}.pdf   # PDF (see note)

bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/index.bs streamld/index.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/core.bs streamld/core.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/subscription.bs streamld/subscription.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-sse.bs streamld/binding-sse.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-websocket.bs streamld/binding-websocket.html

python -m pytest streamld/tests/          # StreamLD's own test suite
```

`index.html` and `404.html` at the repo root are both hand-authored (not built from a `.bs`
source) and need no build step - they're just static pages.

> Note: WeasyPrint needs native libraries (Pango/Cairo/HarfBuzz). These are
> present on Linux/CI; on Windows, installing them is more involved (see
> WeasyPrint's own install docs) - the PDF step can be skipped locally if
> you only need the HTML.

### Option B - CI

[`.github/workflows/spec.yml`](.github/workflows/spec.yml) runs the exact
sequence above (MiKaDiv-VIB, StreamLD, `about.html`, `mikadiv-vib/index.html`
+ PDF, `streamld/index.html` + its 4 documents, then the StreamLD test suite)
on every push to `main` and every PR against `main`. On `push` to `main`
specifically, it also commits any changed generated output back to the
branch (`chore: rebuild site [skip ci]`). It does not deploy anywhere itself
- see "Deploying to openfaster.org" below.

## Deploying to openfaster.org

openfaster.org is deployed on Vercel, which serves whatever is currently
committed to `main` (routing governed by [`vercel.json`](vercel.json)). You
do **not** need to edit the live site directly: author the `.bs`/mapping/SHACL
sources, build the outputs (Option A above, or let CI do it - see Option B),
commit the result, and Vercel picks it up automatically on the next deploy.

## Editing conventions

The specification follows W3C conventions so it can move toward a formal track
later:

- [W3C Manual of Style](https://w3c.github.io/manual-of-style/) for prose and
  conformance language (RFC 2119 keywords).
- [W3C Editor's Guide](https://w3c.github.io/guide/editor/) for structure.
- [W3C TR style sheets](https://www.w3.org/StyleSheets/TR/) applied by Bikeshed.

To change **field content** (a description, a type, an enum value or its
meaning), edit `mikadiv-vib/ThirdPartyDisclosureRequest.xsd` and re-run
`generate_template.py`. To change the **template shape** (add/re-order a column,
adjust a presentation-only helper column), edit `mikadiv-vib/mapping.py`. Never edit
anything under `mikadiv-vib/generated/` by hand.

---

# The Excel template

`generate_template.py` also builds a self-documenting Excel workbook that mirrors
the disclosure structure. It lets non-technical users capture disclosure data in
a spreadsheet, with each field annotated by its English description and expected
type, and enum fields presented as dropdowns.

## Quick start

```bash
python -m pip install -r requirements.txt
python generate_template.py
```

This writes, into `mikadiv-vib/generated/`:

- `mikadiv-vib-v<version>.xlsx` - the fillable template (`<version>` from
  `mikadiv-vib/index.bs`'s `DOCVERSION` text macro).
- `template_metadata.json` - the field metadata store (source for docs + spec).
- `TEMPLATE_FIELDS.md` - a human-readable field reference.
- `fields.include.bs` - the Bikeshed include consumed by `mikadiv-vib/index.bs`.

Re-run any time to regenerate everything (for example after the XSD changes).

> Note: if the `.xlsx` is open in Excel, close it first - Windows locks open
> files and the script cannot overwrite it. (The other outputs still refresh.)

Requirements: Python 3.9+, `openpyxl` and `xmlschema` (pinned in
[`requirements.txt`](requirements.txt)).

## How each sheet is laid out

Every data sheet uses four frozen header rows; data entry starts at row 5:

| Row | Meaning |
| --- | --- |
| 1 | Technical column name (as in the XSD) |
| 2 | Plain-English description of what to enter |
| 3 | Expected type / format / constraints (enum fields list the allowed values) |
| 4 | `Required` / `Optional` / `Conditional` |

The first column (`RequestId`) and the header rows are frozen so they stay
visible while scrolling. Enum-backed cells show a native in-cell dropdown and
reject values outside the allowed list.

## Sheets

| Sheet | Rows per RequestId | Purpose |
| --- | --- | --- |
| `0 Legend Notes` | - | How to read the template, requiredness legend, cardinality, linking rules |
| `1 Requests Master` | 1 | Request-level metadata; `RecordType` = Request or Cancel; account owner scalars |
| `2 Security Related Information` | 0..1 | Security identification + income / tax information, incl. the conditional depositary-receipt (e.g. ADR) block (required for Request; DR fields required when `IsDepositaryReceipt` = true) |
| `3 Tax Voucher Individuals` | up to 2 total (tax voucher) | Natural persons receiving tax vouchers |
| `4 Tax Voucher Legal Persons` | up to 2 total (tax voucher) | Corporate / institutional tax-voucher recipients |
| `5 Third Party Individuals` | up to 5 total (third party) | Natural persons serving as third-party owners |
| `6 Third Party Legal Persons` | up to 5 total (third party) | Corporate / institutional third-party entities |
| `7 Custody Chain` | up to 20 | Intermediary links, sorted by `NumberInChain` |
| `8 FIFO Trades` | up to 1000 each way | FIFO receipts & deliveries (`ReceiptsAndDeliveriesMode` = FiFo) |
| `9 Raw Transactions All` | unbounded | Non-FIFO raw ledger (`ReceiptsAndDeliveriesMode` = All) |

A hidden `_Lists` sheet backs any long dropdown lists.

## Linking model

`RequestId` is the key on `1 Requests Master` and appears as the first column on
every other sheet. It is used **only** to link the sheets together, so any
unique value works (it does not need to be a UUID). Use the same `RequestId`
value to join a request's data across all sheets and reconstruct one full
disclosure record.

- **Cancellations:** set `RecordType = Cancel` on `1 Requests Master`, fill
  `PreviousRequestIdForCancellation` (and optionally `ReportSerialNumber`), and
  leave all other sheets empty for that `RequestId`.
- **Community recipients:** a community tax-voucher receiver (up to 10 members)
  is captured by setting `ReceiverGroupType = CommunityMember` on the tax
  voucher sheets and giving all members of one community the same
  `CommunityGroupId`.

## Customising

The template is generated in three layers (see
[Single source of truth](#single-source-of-truth)):

- **Field content comes from the XSD.** A description, type/format, requiredness,
  or enum value/meaning is read from `mikadiv-vib/ThirdPartyDisclosureRequest.xsd` by
  [`engine/xsd_model.py`](engine/xsd_model.py). To change it, change the schema.
- **Template shape lives in [`mikadiv-vib/mapping.py`](mikadiv-vib/mapping.py):**
  - `SHEET_ORDER` and the per-sheet field lists - each column referencing an XSD
    element/attribute (`E`/`A`/`P`) or a presentation-only synthetic column
    (`SYN`), yielding `(name, description, type_display, requiredness, enum_key)`.
  - `ENUM_ORDER` / `XSD_NAMED_ENUMS` / `XSD_INLINE_ENUMS` / `SYNTHETIC_ENUMS` -
    where each dropdown's values and meanings come from.
  - `SHEET_INFO` and `LEGEND_ROWS` - the editorial sheet/legend prose.
- **Rendering lives in [`engine/generator.py`](engine/generator.py):**
  `_build_sheet()` (header rows, styling, freeze panes, dropdowns) and
  `_build_metadata()` / `_write_documentation_md()` / `_write_bikeshed_include()`
  (the JSON, Markdown and Bikeshed exports), parametrised per module by a
  `ModuleConfig` in [`generate_template.py`](generate_template.py).

Re-run the script to refresh every output at once - the Excel template, the
documentation, and the specification's data dictionary.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en)
