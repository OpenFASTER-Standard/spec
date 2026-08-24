# OpenFASTER site structure/overview — Design

**Status:** Design approved 2026-08-24. Not yet implemented — this doc is the input to
an implementation plan (via the `writing-plans` process), not a plan itself.

**Ecosystem placement:** sub-project 3 of the KaFE DIP + MiKaDiv reporting — Lombard Odier
POC initiative tracked in `bulk-platform`'s `docs/superpowers/PROGRESS.md` (item 8). Unlike
sub-projects 1-2 (adapter-dispatch infrastructure, credential manager), this sub-project's
work is entirely in this repo (`OpenFASTER-Standard/spec`) and `OpenFASTER-Standard/riptide`,
not `bulk-platform` — it's about what's actually hosted at openfaster.org.

## 1. Context and motivation

Today, `openfaster.org`'s root (`index.html`, the compiled output of `documentation/index.bs`)
is not a "buried Abstract" as originally assumed when this sub-project was scoped — it's a
fully generated, W3C-style Bikeshed spec document with a real internal table of contents. The
actual problem is different: **the root page entirely *is* the MiKaDiv module's spec text**,
with no concept of "OpenFASTER as a family of standards" anywhere on it.

Meanwhile `streamld/` — a second, fully-built module (4 Bikeshed documents: `core`,
`subscription`, `binding-sse`, `binding-websocket`; its own SHACL-based generator pipeline;
tests) — exists, is committed, and is even reachable at its own URLs, but is a **completely
orphaned island**: nothing in `index.html` links to it, and none of its own four pages link
back to the root or to each other's family membership. A visitor needs to already know the
exact URL to find it at all.

There is no `kafe/` module yet (sub-project 5, not started). Riptide (`OpenFASTER-Standard/riptide`,
StreamLD's Elixir/Phoenix reference implementation) has **zero HTML presence of its own** — it
serves only JSON/Turtle/JSON-LD over LDP, SSE, and WebSocket — so "reference implementations
as first-class, browsable content" needs to be hand-authored on the spec site, not pulled from
Riptide's own code.

Separately, and discovered during this design's own research rather than flagged in the
original sub-project text: `README.md` claims a `.github/workflows/spec.yml` builds the site
on every push and publishes to GitHub Pages. **No such file, and no `.github/` directory at
all, exists in this repository.** The actual live site is served by Vercel (`vercel.json`)
directly from whatever static files (`index.html`, `streamld/*.html`,
`mikadiv/generated/MiKaDiv_ThirdPartyDisclosure_Template.xlsx`, `documentation/openfaster.pdf`)
happen to be committed — built and committed manually/locally by whoever last ran the Docker
build. This is a real reliability gap for a site that's about to gain real navigation structure
depending on every module's build staying in sync, and is explicitly in scope for this
sub-project (confirmed with the operator).

## 2. Research summary

This design was grounded in two rounds of real research, not first-principles guessing about
"how standards sites usually work":

1. **How established standards bodies structure multi-document families**: W3C's `/TR/`
   (categorized index; three-URI-per-doc pattern: unversioned Editor's Draft → dated "this
   version" snapshot → unversioned "latest version" pointer), IETF's RFC series (flat numeric,
   immutable, `Obsoletes`/`Updates` cross-refs doing relationship work instead of grouping) plus
   `httpwg.org/specs/` (a small working group's own **lightweight, hand-curated, categorized
   one-line-per-document family index** sitting on top of the canonical numbered RFCs — the
   closest structural analog to OpenFASTER's actual scale), OASIS (filterable card grid;
   multi-part standards get `/[project]/[component]/v[version]/[stage]/` paths), schema.org (no
   versioning in URLs at all — a different kind of family, not directly applicable here), and
   W3C Community Group reports (status token embedded in the URL path itself,
   `CG-DRAFT`/`CG-FINAL`, matching StreamLD's own already-declared `Status: w3c/CG-DRAFT`
   Bikeshed metadata).

2. **URL versioning best practice, specifically**: Tim Berners-Lee's "Cool URIs don't change"
   (keep status words like "latest"/"draft" out of *permanent* identifiers, but a separate
   "latest" pointer is legitimate); W3C's own binding editorial convention (pubrules + editor's
   guide) — the concrete precedent every small analog copies; **Solid Protocol**, **ActivityPub**,
   **JSON Schema** (which explicitly *moved away* from sequential `draft-07`-style numbering to
   dated snapshots specifically because ordinal numbers caused "confusing mismatches" and
   "controversial fix-in-place" bugs), and **IndieWeb's** "Living Standard" specs — all
   independently converge on the same two-tier shape. On *when* to start versioning at all:
   Google Cloud's own API design guidance ("ignore versioning initially and only add it if and
   when you need it"), Roy Fielding's REST arguments, and WHATWG's living-standard rationale all
   argue against premature versioning — don't mint a versioned URL until there's an actual
   second thing to distinguish from the first.

## 3. Goals

- A real root portal at `/` presenting every published standard and reference implementation as
  first-class, browsable, linked content — replacing MiKaDiv's spec text, which moves to its
  own subpage.
- Every standard gets its own subpage (`/mikadiv/`, `/streamld/`), and every subpage that has
  more than one document gets its own internal index linking its sub-documents (StreamLD's 4
  documents need this; MiKaDiv doesn't, since it's one document).
- StreamLD stops being an orphaned island: linked from the root, links back to the root, and its
  4 documents cross-link consistently with a shared "part of the StreamLD module" identity.
- A URL convention new modules (KaFE, sub-project 5) can drop into without another site redesign.
- Real, working CI: every push to `main` actually rebuilds the site from source and deploys it —
  closing the gap between what `README.md` claims and what's actually true today.
- Visual/branding cohesion across the portal and every module page, done now — not deferred to a
  separate future pass.

## 4. Non-Goals

- **Thesaurus placement** — explicitly deferred to sub-project 6 (Thesaurus publishing
  mechanism), which decides subpage-vs-subdomain informed by the conventions this sub-project
  settles.
- **KaFE's actual content** — sub-project 5's job. This design only reserves and documents the
  URL convention (`/kafe/`) it will use; no stub/"coming soon" page is built now (an empty
  placeholder is dead weight to maintain and re-verify every time the real module lands, and two
  real working modules on the portal reads as more credible than two real plus one placeholder).
- **MiKaDiv/StreamLD spec *content* changes** — this is a structure/navigation/tooling
  redesign, not a respec of either module's actual technical content.
- **Dated version-snapshot mechanism** — deferred until an actual second version of some module
  exists to snapshot against (see §6). Building the snapshot machinery today, before there's
  anything to snapshot, is exactly the premature-versioning trap the research in §2 argues
  against.
- **A full custom design system replacing Bikeshed's own document rendering** — see §7; only
  reached for if the shared-shell approach (the actual design) proves visually unsatisfying in
  practice.

## 5. Site structure

### 5.1 Root portal (`/`)

Replaces the current MiKaDiv-spec-as-homepage. Modeled on `httpwg.org/specs/`'s pattern
(lightweight, hand-curated, categorized one-line list) rather than W3C's heavier `/TR/` index
or OASIS's filterable card grid — OpenFASTER has a handful of items, not hundreds, so a simple
structure fits better and is easier to keep accurate by hand.

Two sections:

- **Standards** — one line per module: name, one-sentence description, status (e.g. "Stable" /
  "CG-Draft"), link to the module's own subpage.
  - MiKaDiv → `/mikadiv/`, status "Stable" (matches its existing v1.0.0 changelog entry).
  - StreamLD → `/streamld/`, status "CG-Draft" (matches its own Bikeshed `Status:` metadata).
  - (KaFE not listed until sub-project 5 actually ships it — see Non-Goals.)
- **Reference Implementations** — one line per implementation: name, one-sentence description,
  link out to its repo (GitHub, since e.g. Riptide serves no HTML of its own to link into).
  - Riptide → link to `OpenFASTER-Standard/riptide` on GitHub.

The root page itself is hand-authored (not Bikeshed-generated) — it isn't a spec document, it's
a directory of them.

### 5.2 MiKaDiv (`/mikadiv/`)

MiKaDiv's spec content (currently §3 "The MiKaDiv Third-Party Disclosure module" of the root
`index.html`, generated the same way as today: `documentation/index.bs` pulling
`mikadiv/generated/fields.include.bs`) moves to its own Bikeshed source and its own compiled
output at `/mikadiv/`. Single document, single URL — no internal index page needed (the module
subpage *is* the document). The `mikadiv/generated/MiKaDiv_ThirdPartyDisclosure_Template.xlsx`
link moves from the current raw-GitHub-blob URL to a real `/mikadiv/...` path served by the
site itself.

### 5.3 StreamLD (`/streamld/`)

Gains an index page it doesn't have today, linking its 4 existing documents:

- `/streamld/` — new landing page: what StreamLD is, links to the 4 documents below, link back
  to `/` (the portal).
- `/streamld/core` (was `core.html`)
- `/streamld/subscription` (was `subscription.html`)
- `/streamld/binding-sse` (was `binding-sse.html`)
- `/streamld/binding-websocket` (was `binding-websocket.html`)

Each of the 4 documents' `<pre class='metadata'>` block gets its declared `URL:` updated to the
new clean-URL form (e.g. `URL: https://openfaster.org/streamld/core`) and gains a link back to
`/streamld/` (none currently link to any parent/index — confirmed via research, zero matches
either direction).

### 5.4 KaFE (`/kafe/`, reserved, not built)

Sub-project 5 builds the real module. This design only reserves the path and documents the
convention it must follow: a `/kafe/` subpage (single document, like MiKaDiv, or an index +
sub-documents, like StreamLD — sub-project 5's own call once it knows its document count),
listed on the root portal's Standards section only once it actually exists.

### 5.5 URL conventions

- **Clean URLs everywhere** — no `.html` extension in any published link, leaning into
  `vercel.json`'s already-configured `cleanUrls: true` (today only really exercised by
  `index.html` → `/`). StreamLD's 4 `.bs` files get their declared `URL:` metadata updated to
  match; no new module should declare a `.html`-suffixed URL going forward.
- **No version segment in any URL, for now** — every module/page has exactly one "latest" URL
  that its maintainers update in place (e.g. `/mikadiv/`, `/streamld/core`). This matches every
  small-project precedent in §2's research and the "don't version prematurely" consensus found
  there. When a module actually reaches a real second version, mint a **dated** snapshot path
  (e.g. `/mikadiv/2026/mikadiv-20260705/`) at that point — not a sequential `/v2/`-style path
  (JSON Schema's own documented rationale for abandoning ordinal draft numbers: they caused
  "confusing mismatches" and made bugfix releases awkward to give a fresh, uniquely
  dereferenceable identity). This snapshot mechanism is **not built now** — see Non-Goals.

## 6. Visual/branding

**Approach:** keep Bikeshed's own document rendering for every module's actual spec content —
its table-of-contents/status-banner/section-numbering conventions are themselves a recognizable
"this is a real spec" signal shared with W3C, Solid, and ActivityPub, and there's no reason to
fight or replace it. Instead, wrap **every** page — the hand-authored root portal and every
Bikeshed-generated module page alike — in a shared, hand-designed site shell: a consistent
header (OpenFASTER name/logo), a nav bar (Standards / Implementations, linking back to `/`), a
shared color scheme, and a shared footer. This is injected via one shared HTML partial/include
repeated across the portal and every module page (mechanically: a shared header/footer include
pulled into `documentation/index.bs`-equivalent sources the same way `fields.include.bs` is
today, plus wrapped around the hand-authored portal page directly).

This gets real cross-page cohesion (every page visibly belongs to the same site) without a
framework migration or fighting Bikeshed's internal markup. A full custom design system
replacing Bikeshed's rendering entirely is a much bigger lift with real risk, for a site with
2-3 modules — reach for it only if the shared-shell approach turns out visually unsatisfying in
practice, not as the starting design.

## 7. CI / deploy

Confirmed via direct inspection (`git ls-files`): `index.html`, `streamld/*.html`,
`mikadiv/generated/*` (including the `.xlsx` template), and `documentation/openfaster.pdf` are
all committed to git today — built and committed manually/locally, contradicting `README.md`'s
claim of an automated GitHub Actions → GitHub Pages pipeline (no `.github/` directory exists at
all). The real live deploy is Vercel, serving whatever static files are currently committed.

**Approach A (recommended, build now):** a GitHub Actions workflow (`.github/workflows/spec.yml`,
actually building what the README already claims exists) runs the existing Dockerfile's build
chain (`generate_template.py` → `bikeshed spec` → WeasyPrint PDF, now extended to also render
the new root portal + StreamLD index through the shared site-shell) on every push to `main`,
regenerates every output file, and commits the result back. Vercel keeps doing exactly what it
does today — serve committed static files — so this fixes the actual reliability gap (a
forgotten manual rebuild silently leaving the live site stale) with no change to the working
deploy path, and no new technical risk to validate.

**Approach B (cleaner, deferred):** move the build into Vercel's own `buildCommand`, stop
committing generated HTML/PDF entirely — single source of truth becomes the `.bs`/mapping/SHACL
sources. Cleaner, but WeasyPrint (used for the PDF) needs system-level libraries (Pango, Cairo,
GDK-Pixbuf) that may not be available in Vercel's build sandbox — **not verified**, and not
worth committing to without a spike first. Approach A is a fully working starting point;
Approach B is a strict upgrade that doesn't change the site's structure or any URL, so it can
land later without blocking this sub-project or requiring another design pass.

## 8. Testing / verification

- **Link integrity**: every internal link the new structure introduces (portal → each module,
  each module's index → its own sub-documents, each sub-document → back to its module index and
  to the root) must be verified live, not just written — Bikeshed itself already supports
  `--die-on=link-error` (used today in the Dockerfile's build command for intra-document links);
  extend this discipline to the new cross-document/cross-page links too.
- **Build reproducibility**: the CI workflow (§7, Approach A) is itself the test that the whole
  build chain — XSD/SHACL → generator → Bikeshed → shared site-shell → committed output — stays
  in sync; a broken build should fail the workflow loudly, not silently leave stale output live
  (today's actual, confirmed failure mode).
- **Clean-URL verification**: confirm Vercel's `cleanUrls: true` genuinely serves every new
  extension-less path (`/mikadiv/`, `/streamld/core`, etc.) as expected, live, not just assumed
  from the config flag's documented behavior.

## 9. Open Questions / Explicitly Deferred

- **Exact visual design details** (specific colors, typography, logo) — this design settles the
  *architecture* (shared shell wrapping Bikeshed output), not the specific visual system; that's
  an implementation-time decision within the shared-shell approach.
- **Approach B (Vercel-native build)** — worth spiking once Approach A is live and stable, not
  before; see §7.
- **KaFE's own internal structure** (single document vs. index + sub-documents) — sub-project
  5's decision, once it knows its own document count; this design only reserves `/kafe/`.
