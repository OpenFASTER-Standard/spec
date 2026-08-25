# Deploy Consistency Fix — Design Spec

**Status:** Approved by operator, pending implementation.

## Problem

Two rounds of "fixed and live-verified" changelog work on openfaster.org
turned out not to be reliably true in production, eroding trust in this
project's own verification process. Root-caused via a dedicated
investigation (5 parallel research agents, capped by explicit operator
request) rather than another guess.

### Root cause 1: deploy race (confirmed, real, reproducible)

This repo's CI (`.github/workflows/spec.yml`) regenerates all Bikeshed
HTML / Excel / PDF output and commits it in a **separate follow-up
commit** after a feature PR's merge commit lands on `main`
(`chore: rebuild site [skip ci]`). Vercel deploys on every push to
`main`, including the bare merge commit itself — before that follow-up
commit exists. Confirmed with exact evidence on PR #15's merge:

- Merge commit `1b2d7b8` landed 12:32:35Z; at that exact commit,
  `mikadiv-vib/request.html` had **zero** occurrences of "Version
  history" in git — the compiled HTML genuinely didn't have the section
  yet, because only the `.bs` source had changed.
- Vercel deployed that commit, live by ~12:32:42Z.
- CI's own rebuild commit (`0c45352`, confirmed via direct `git show` to
  actually contain the fix) didn't land until 12:33:56Z, live by
  ~12:34:03Z.

So there is a real ~60-90 second window, on every merge that changes
`.bs`/`.py` source affecting generated output, where production serves
genuinely incomplete/wrong content.

### Root cause 2 (partially confirmed, real but smaller than first assumed): CDN caching

A live check found a response served `x-vercel-cache: HIT` with
`age: 829` (13+ minutes stale) despite the app declaring
`cache-control: public, max-age=0, must-revalidate`, which should force
revalidation on every request. Deep research (see Approaches section)
found this is *expected* Vercel behavior for static-file deployments —
Vercel's own docs state static assets are cached "for the lifetime of
the deployment" and that Vercel "doesn't allow bypassing the cache for
static files by design." Crucially, the research also found the CDN
cache key is **scoped per-deployment** — a stale edge entry can only
ever reflect a *past* deployment's content, and switching production to
a new deployment forces a fresh cache-key lookup. This meaningfully
narrows the real risk: this mechanism should not be able to serve
content from an old deployment indefinitely once a newer one is
promoted. It does not, however, rule out a caching/propagation
contribution to what the operator observed, and there's a plausible
secondary explanation (browser/proxy caching outside Vercel's control,
or the operator's check landing inside the root-cause-1 window). Given
this uncertainty, this is treated as a defense-in-depth fix, not the
primary one.

## Goals

1. Categorically eliminate the possibility of an inconsistent
   (source-changed-but-output-stale) commit ever being deployed to
   production, by construction — not by racing to overwrite it quickly.
2. Do this without dependency on Vercel account/dashboard access this
   box does not have (no `VERCEL_TOKEN`, no way to verify dashboard
   settings).
3. Do this without introducing new unmanaged secrets/infrastructure
   where a simpler, equally-effective option exists.
4. Apply real, multi-vantage-point verification before declaring this
   fixed — not a repeat of today's shallow single-check failures.

## Non-goals

- Migrating off Vercel (raised and explicitly deferred by the operator
  pending this fix's own outcome).
- Guaranteeing zero Vercel-CDN-level caching (research found no
  authoritative confirmation this is achievable for static files on
  this plan; treated as best-effort).
- Setting up GitHub branch protection / required status checks (no
  branch protection exists on `main` today; the chosen design does not
  require it — see Approach below).

## Approach

### Fix 1 (primary): pre-merge self-consistency check

Add a new job triggered on `pull_request` (targeting `main`) that:

1. Runs the exact same regeneration pipeline the existing post-merge
   step runs (all Bikeshed/Excel/PDF generation across kafe,
   mikadiv-vib, streamld, documentation).
2. Diffs the regenerated output against what's currently committed on
   the PR branch, correctly handling two confirmed sources of
   non-determinism found by directly running each generator twice and
   diffing byte-for-byte:
   - **Excel (`.xlsx`)**: openpyxl stamps `dcterms:created`/`modified`
     timestamps into `docProps/core.xml` on every save, even with
     identical content. Normalize (strip to a fixed placeholder) before
     comparing, rather than skipping the file entirely — everything
     else in the file (sheet data, styles) is real, comparable content.
   - **Bikeshed HTML**: embeds `datetime.utcnow().date()` unless a
     `Date:` metadata line is set, so comparing across a UTC day
     boundary produces a false-positive diff with zero source change.
     Fix: inject a temporary `Date:` line (matching HEAD's commit date)
     into scratch copies of each `.bs` file before building **only
     within this check's own comparison**, then revert before diffing
     — this does not change the real site's own dynamic "today" date
     behavior for actual builds, only neutralizes noise in this one
     comparison.
   - **PDF**: WeasyPrint/fonttools stamp a fresh trailer `/ID` hash and
     per-run timestamps into each embedded subsetted font's `head`
     table on every build, confirmed via a `qpdf --qdf` decompress-and-
     diff of two builds from byte-identical HTML input. Not cleanly
     stripped (scattered through binary font data). Excluded from the
     byte-diff gate; a successful `weasyprint` exit is treated as
     sufficient, since the PDF's real content is a deterministic
     function of the HTML this check already verified fresh.
   - Every other generator (KaFE's 3 scripts, MiKaDiv's response-doc
     generator, StreamLD's generator, `prepare_spec.py`) confirmed
     fully deterministic — direct diffs, byte-identical.
3. If a real diff is found, auto-commits the regenerated output onto
   the **PR's own branch** (`stefanzweifel/git-auto-commit-action`,
   checking out `${{ github.head_ref }}`, not the default detached
   merge ref) using the **default `GITHUB_TOKEN`** — no new PAT/secret.

**Why the default token, not a PAT (a real design choice, not an
oversight):** confirmed via a real live test (Task 3 of this plan's
implementation — see PR #16, run `32856864966`) rather than documentation
alone: a `GITHUB_TOKEN`-authored push from a `pull_request`-triggered
workflow does create a new run object for that event, but GitHub gates
it in a built-in, non-configurable "approval-required" state that never
auto-executes — a human with write access has to explicitly approve it
before any job runs. (This refines an earlier, less precise research
claim that such pushes "never retrigger any workflow" — that holds for
`push`-triggered workflows, but for `pull_request`-triggered ones,
specifically, a gated-but-inert run is created instead of no run at
all.) The practical effect is the same either way — no infinite
auto-commit loop, no extra actor-guard logic needed — and is actually
reinforced by a second, independent property: even if that gated run
were manually approved, the check would find nothing left to fix (the
first run already corrected it) and no-op, since the fix is
self-terminating by construction, not just by the approval gate. The
cost: the auto-commit does not re-trigger *other* required checks on
the new commit. Since this repo currently has **no branch protection
and no required checks on `main` at all**, that cost is zero today. The
trade-off: this is a soft-enforced guarantee (the merger must wait for
the `pull_request` workflow to finish, so the auto-commit lands, before
merging) rather than a hard-blocking one. In this repo's actual
practice, PRs are authored and merged by an agent that already watches
CI to green before
every merge (established pattern this session) — so the soft
enforcement matches how merges actually happen here. If that practice
ever changes, revisit with a PAT + branch protection (documented as a
deferred option below, not implemented now, to avoid unmanaged
complexity for a risk that doesn't exist yet).

The existing post-merge `chore: rebuild site [skip ci]` step is **kept
as a defense-in-depth no-op safety net** (e.g. for a hypothetical direct
push to `main` bypassing a PR) — with the pre-merge check in place it
should always find nothing to commit, confirmed harmless by its own
existing `if git diff --staged --quiet` guard.

### Fix 2 (secondary, defense-in-depth): Vercel cache headers

Add a `headers` block to `vercel.json` forcing
`Cache-Control: no-store` on all HTML-serving routes (matched via a
negative-lookahead path pattern excluding `.xlsx`/`.pdf`, the same
idiom Vercel's own docs use elsewhere for exclusions), leaving
Excel/PDF downloads on normal caching. Framed honestly per the research
findings: this is expected to correctly control **browser/downstream**
caching (a legitimate, documented use), but is *not* confirmed to
override Vercel's own static-file edge caching, which its docs describe
as bypass-proof "by design." Implemented anyway as defense-in-depth
(harmless if it has no effect on the edge, given Fix 1 already
eliminates the actual risk of *wrong* content being cacheable in the
first place) but not relied upon as the real fix.

## Testing & verification plan

Directly targets the two failure modes that already happened today
(shallow single-check verification; edge/timing-dependent inconsistency
invisible to a single check). Every check below inspects actual
response headers or content, from more than one point in time and more
than one vantage point where relevant — never HTTP status/grep alone.

**Before merging this fix:**
- Confirm the staleness-check script correctly flags a deliberately
  staged stale case (a scratch commit with source changed, output not
  regenerated) and correctly passes on a genuinely fresh case, tested
  locally.
- Confirm `git-auto-commit-action` successfully pushes to a real
  throwaway PR branch in this repo (same-repo PR, so no fork
  restrictions apply) — test on an actual PR, not just documentation.

**After merging, before declaring done:**
- Real end-to-end test: open a throwaway PR with a real source change
  that would trip the original failure class, confirm the pre-merge
  check runs, detects staleness if present, and the branch is
  self-consistent before merge.
- For the cache header change: repeated (≥20 requests over ≥10 minutes)
  direct checks that `x-vercel-cache` is never `HIT` and `age` stays
  low, from this box; if feasible, a multi-region cross-check (e.g. via
  a public probe network) since the original bug was specifically
  edge-dependent and invisible to a single vantage point.
- Explicitly published alongside the "verified" list: what was *not*
  independently re-confirmed (e.g. anything only tested from this box's
  own network location).

## Deferred / explicitly out of scope for this fix

- PAT + branch protection + required status checks, if the
  soft-enforcement trade-off above ever stops holding (e.g. a human
  starts merging PRs without waiting for CI).
- `Vercel-CDN-Cache-Control`/explicit `vercel cache purge` as a stronger
  CDN-cache lever, if Fix 2's header change is later confirmed
  ineffective at the edge and stronger guarantees become necessary.
- Migrating off Vercel entirely.
- Pinning `Date:` in the real `.bs` source files permanently (would
  freeze the site's own "last generated" display, a real behavior
  regression, not a fix) — the temporary injection stays scoped to the
  CI comparison script only.
