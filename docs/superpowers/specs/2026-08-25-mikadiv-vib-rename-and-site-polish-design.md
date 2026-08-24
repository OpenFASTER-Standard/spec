# MiKaDiv-VIB rename & site polish — Design

**Status:** Design approved 2026-08-25. Not yet implemented — this doc is the input to
an implementation plan (via the `writing-plans` process), not a plan itself.

**Ecosystem placement:** a follow-up to the OpenFASTER site structure/overview sub-project
(`2026-08-24-site-structure-overview-design.md`), which shipped `/mikadiv`, `/about`, the
shared visual shell, and the CI workflow. This design covers a batch of naming, content, and
build-pipeline fixes surfaced immediately after that ship, plus one genuine reversal (the
`/about` page's scope) based on what the live result actually looked like.

## 1. Context and motivation

Six independent-but-related requests came in after the site-structure-overview sub-project
went live:

1. Unknown routes should redirect to root, not 404.
2. The MiKaDiv page should offer direct PDF/Excel downloads above the fold, not a mid-prose
   GitHub blob link (which requires an extra click through GitHub's file-preview UI).
3. The PDF filename should be `<slug>-v<version>.pdf`.
4. Alaa Eddine Cherif should be removed from the editor list — everywhere live, not just one
   file.
5. The Excel template should carry an identifying "Meta" sheet.
6. MiKaDiv's slug should be `mikadiv-vib` everywhere, not `mikadiv`.

Investigating (6) surfaced that it's not a one-file rename: `mikadiv` is the directory name,
the Bikeshed `Shortname`, the live URL path, and it's threaded through `README.md`, the CI
workflow, `vercel.json`'s implicit directory-index routing, and the generator scripts'
hardcoded paths. Since `/mikadiv` only shipped hours earlier with no external inbound links
yet, this is the cheapest point to ever make that change — deferring it only makes the rename
more expensive later.

Separately, reviewing `/about`'s live content surfaced that it doesn't actually hold family-wide
content — most of its "Terminology" and "Planned work" sections are MiKaDiv-specific concepts
that happened to get placed there during the previous sub-project's content split. This design
corrects that: `/about` is kept, but trimmed to content that's genuinely about the family as a
whole.

## 2. Slug rename: `mikadiv` → `mikadiv-vib`

Scope is total, including the public URL — confirmed explicitly rather than assumed, given the
previous sub-project's entire point was establishing `/mikadiv` as the stable clean URL. Since
no external links exist yet, no redirect from the old path is needed.

**Renamed:**
- Directory: `mikadiv/` → `mikadiv-vib/` (including `mikadiv-vib/generated/`,
  `mikadiv-vib/header.include`, `mikadiv-vib/mapping.py`,
  `mikadiv-vib/ThirdPartyDisclosureRequest.xsd`).
- Bikeshed `Shortname: mikadiv` → `Shortname: mikadiv-vib` in `mikadiv-vib/index.bs`.
- Live URL: `/mikadiv` → `/mikadiv-vib` (Vercel's existing directory-index convention handles
  this automatically once the directory is renamed — no new `vercel.json` rewrite needed).
- `generate_template.py`'s hardcoded `ROOT / "mikadiv" / ...` paths.
- `.github/workflows/spec.yml`'s build commands and `git add` file list.
- `README.md`'s repository-layout tree, build sequence, and prose references.
- Root portal (`index.html`)'s Standards-section link.
- `about.bs`'s prose example (`e.g. \`/mikadiv\`, ...` → `\`/mikadiv-vib\``).

**Not affected:** no `.bs` file uses `[[mikadiv#...]]`-style cross-doc biblio links to the old
Shortname (confirmed by search), so the rename doesn't break any incoming references.

## 3. `/about`: kept, trimmed to family-wide content only

Reversing the earlier "remove it entirely" direction once the actual live content was
reviewed: `/about` stays, but every section that's really about MiKaDiv specifically moves out
or is dropped.

**Kept, unchanged:** Introduction, Scope, Regulatory context (the MiKaDiv-2027/FASTER-2030
milestone table — kept because it's framed around the whole family's regulatory grounding, not
one module's data model), Versioning policy, the `Certified Financial Intermediary` term (a
family-wide actor type, not a MiKaDiv-only concept).

**Removed from Terminology, de-linked (not relocated) in `mikadiv-vib/index.bs`:**
`disclosure`, `RequestId`, `paying agent`, `tax voucher`. These four are genuinely
MiKaDiv-specific, but building real cross-document `<dfn>` infrastructure for them now would be
throwaway work — all such terms become part of the planned Thesaurus (PROGRESS.md sub-projects
6-7) eventually. Every current `[[openfaster#term|text]]` reference to these four — in
`mikadiv-vib/index.bs`'s hand-written prose (6 occurrences) **and** in
`engine/generator.py:472`'s hardcoded string inside the shared Bikeshed-include generator (1
occurrence, easy to miss since it's not in a `.bs` file) — becomes plain unlinked text.

**Dropped entirely, not relocated:** the "Planned work" section (bulk disclosure template,
multilingual vocabulary, UUID return format) — this is MiKaDiv's own roadmap, not family
direction, and none of it is urgent enough to justify finding it a new home right now. It can
be rewritten fresh, in the right document, whenever it's actually needed.

**Editor:** `Alaa Eddine Cherif` removed from `about.bs`'s `Editor:` line too (was previously
only planned for `mikadiv-vib/index.bs`).

## 4. Editor removal, full scope

`Alaa Eddine Cherif` is removed from every live document: `mikadiv-vib/index.bs` and
`documentation/about.bs` (their built `.html` update automatically on rebuild). The one other
occurrence in the repo — `docs/superpowers/plans/2026-08-24-site-structure-overview.md`, a
dated, already-executed plan document reproducing an old code snippet — is explicitly left
alone. That file is a historical record of what was done, not live content; editing it after
the fact would be rewriting history for no functional gain.

## 5. Version as a single source of truth

`mikadiv-vib/index.bs`'s existing `Text Macro: DOCVERSION 1.0.0` stays canonical. A small
addition to the Python build pipeline (`generate_template.py` or a small shared helper) parses
that value directly out of `mikadiv-vib/index.bs` via a simple regex on the `Text Macro:
DOCVERSION` line, rather than introducing a third independent copy of the version string. That
parsed value drives:

- The PDF filename: `mikadiv-vib-v1.0.0.pdf`.
- The Excel filename: `mikadiv-vib-v1.0.0.xlsx` (replacing
  `MiKaDiv_ThirdPartyDisclosure_Template.xlsx` — confirmed in scope, not just the PDF).
- The new Excel "Meta" sheet's version field (section 7).

**Known, accepted gap:** the root portal (`index.html`)'s status badge (currently a hardcoded
`v1.0.0` string, independently discovered to already be out of sync with `DOCVERSION` in spirit
— it's a second, manually-maintained copy) stays a manually-maintained literal. Building
extraction machinery into the hand-authored static portal is more infrastructure than this
round of work justifies. This is a documented tradeoff, not an oversight: if the portal badge
and `DOCVERSION` drift apart in the future, that's a known, accepted risk, not a regression to
silently reintroduce and forget.

## 6. Download section on the MiKaDiv page

A new section is added to `mikadiv-vib/index.bs`, positioned directly above "Abstract" (i.e.
the very first thing a visitor sees after the title). It contains two links:

- `https://raw.githubusercontent.com/OpenFASTER-Standard/spec/main/mikadiv-vib/generated/mikadiv-vib-v1.0.0.pdf`
- `https://raw.githubusercontent.com/OpenFASTER-Standard/spec/main/mikadiv-vib/generated/mikadiv-vib-v1.0.0.xlsx`

These are real, unversioned-by-Git-ref raw-content URLs (not GitHub's blob/file-preview page),
so clicking either downloads the file directly with no intermediate GitHub UI step. This
replaces the existing mid-prose blob-link mention of the Excel template
(`mikadiv/index.bs:44` today), which pointed at a `.../blob/main/...` URL — exactly the
"push a separate button in the GitHub UI" problem being fixed.

**Site-served PDF dropped:** since downloads now go through GitHub directly, the existing
`vercel.json` rewrite serving the PDF at `openfaster.org/openfaster.pdf` is removed rather than
updated to the new filename. It shipped only hours ago with no external links depending on it,
and keeping it would mean one more path to keep in sync for no real benefit now that a working
download path exists.

## 7. Excel "Meta" sheet

A new sheet, containing the standard's name, slug, version, and canonical spec URL, is added by
`engine/generator.py`. Per explicit correction, it's the **last** sheet in the workbook — added
after `_Lists` (today the final sheet, holding hidden dropdown-validation data), not first as
originally proposed. `wb.move_sheet` (already used today to position `_Lists` last) handles the
reordering the same way.

## 8. Unknown routes redirect to root

**Correction 2026-08-25** (during plan-writing, after live research): a `vercel.json`
`redirects` catch-all (`{"source": "/(.*)", "destination": "/"}`) was the original plan here,
but Vercel's own documentation confirms `redirects` are **not** filesystem-aware the way
`rewrites` are — a pattern like that matches *every* request, including real existing pages,
and even redirect-loops on `/` itself (`.*` matches the empty string too). This would have
broken the site. Confirmed via Vercel's own official example, which uses that exact pattern
specifically to redirect an *entire* site elsewhere.

The corrected mechanism: a static `404.html` file at the repository root. Vercel serves this
only as a genuine last-resort fallback — strictly after real files, directory-index resolution,
`rewrites`, and `redirects` have all failed to match — so it can never shadow an existing page,
and needs no maintained exclusion list as new pages are added later (e.g. the future `kafe/`
module). The tradeoff: the *first* HTTP response for an unmatched path carries a real `404`
status (Vercel's own behavior for a served 404 page), with the actual navigation to `/`
happening a moment later via a small inline script in `404.html` (a `<meta
http-equiv="refresh">` fallback covers non-JS clients/crawlers too). This differs slightly from
a true server-side `30x` redirect as the very first response, but was chosen over the
alternative — a `redirects` rule with a manually maintained exclusion list for every real
top-level path — since that reintroduces exactly the kind of ongoing sync burden this batch of
fixes is otherwise trying to eliminate.

This also cleanly subsumes the old `/mikadiv` URL (no separate redirect needed — once the
directory is renamed, `/mikadiv` simply becomes an "unknown route" and falls through to the same
`404.html` fallback) and the never-relinked `/openfaster.pdf` (same treatment, once its rewrite
is removed per section 6).

## 9. Root portal copy

The lede paragraph changes from describing scope narrowly ("EU withholding-tax and
dividend-reporting data exchange under MiKaDiv and FASTER") to the broader framing:

> "OpenFASTER is a vendor-independent family of open standards for the harmonized data exchange
> of regulatory reporting, tax compliance and audit data, starting with MiKaDiv and FASTER."

Since `/about` is being kept (section 3), the portal's existing "About" nav link and the lede's
pointer sentence to it both stay as they are today — only the first sentence's wording changes.

## 10. Build pipeline impact (implementation-plan input, not new design)

Consequences of sections 2-9 that the implementation plan needs to account for, listed here so
none get lost between design and planning:

- `.github/workflows/spec.yml`: build-step names, paths, and the `git add` list all move from
  `mikadiv/*` to `mikadiv-vib/*`; the weasyprint step's output target changes from
  `documentation/openfaster.pdf` to `mikadiv-vib/generated/mikadiv-vib-v1.0.0.pdf` (version
  interpolated, not literal — see section 5); the Excel filename change flows through
  automatically once `generate_template.py`'s config changes.
- `vercel.json`: remove the `/openfaster.pdf` rewrite; the `/about` rewrite is unchanged; add
  the catch-all redirect (section 8) last, after the more specific rules, so it only catches
  what nothing else matched.
- `README.md`: needs another accuracy pass — repository-layout tree, build sequence, and prose
  all currently say `mikadiv`.
- `engine/generator.py`: the hardcoded `[[openfaster#disclosure|disclosure]]` string
  (section 3) and the new Meta-sheet-writing logic (section 7) both land here, since it's the
  shared generator both `mikadiv-vib`'s pipeline and (eventually) other XSD-based modules use.

## Non-goals

- No redirect is added from the old `/mikadiv` path specifically — the general catch-all
  (section 8) already covers it, and a dedicated redirect would be one more rule to maintain
  for a URL that was never externally linked.
- The Thesaurus (formal `<dfn>` infrastructure for `disclosure`/`RequestId`/`paying
  agent`/`tax voucher`/etc.) is not built here — this design deliberately de-links rather than
  re-homes those terms, consistent with PROGRESS.md's existing deferral of the Thesaurus to its
  own future sub-project.
- The root portal's version badge does not gain automated sync with `DOCVERSION` (section 5) —
  documented as an accepted gap, not solved here.
