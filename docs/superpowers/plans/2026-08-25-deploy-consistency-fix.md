# Deploy Consistency Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate a confirmed production bug where Vercel deploys a bare merge commit (source changed, generated HTML/Excel/PDF not yet regenerated) before CI's own follow-up rebuild commit lands, serving genuinely incomplete content for ~60-90 seconds on every merge that touches `.bs`/`.py` source.

**Architecture:** A new `pull_request`-triggered CI job regenerates all build output and diffs it against what's committed on the PR branch; if stale, it auto-commits the fix onto the PR branch itself (default `GITHUB_TOKEN`, no PAT) so every commit that ever reaches `main` is already self-consistent. A secondary, best-effort `vercel.json` cache-header change is added for defense-in-depth. The existing post-merge rebuild step is left unchanged as a no-op safety net.

**Tech Stack:** GitHub Actions (bash + Python), `stefanzweifel/git-auto-commit-action`, Bikeshed, WeasyPrint, openpyxl, Vercel static hosting.

**Spec:** `docs/superpowers/specs/2026-08-25-deploy-consistency-fix-design.md`

## Global Constraints

- Never use `--no-verify` or skip git hooks.
- This repo has **no branch protection and no required status checks on `main`** today — do not assume either exists; do not silently add them as a side effect of this plan.
- The repo's Actions default token permission is `read`; any new job needs its own `permissions: contents: write` block (the existing `build` job already does this — mirror the same pattern, don't invent a different one).
- This box has no Vercel API token or dashboard access. All Vercel-side verification in this plan uses plain HTTPS requests (`curl`), never the Vercel CLI/API.
- Two prior "fixes" to this exact area were declared verified via shallow checks (HTTP status/grep only) and were wrong in production both times. Every verification step in this plan must produce and show real evidence (actual header values, actual diffs, actual multi-request logs) — never "looks right."
- Confirmed via direct testing (not assumption): `generate_template.py`'s `.xlsx` output, Bikeshed's HTML output (absent an explicit `Date:` metadata line), and WeasyPrint's PDF output are non-deterministic across otherwise-identical runs. KaFE's 3 generator scripts, MiKaDiv's response-doc generator, StreamLD's generator, and `documentation/prepare_spec.py` are confirmed byte-identical across repeated runs — no special handling needed for those.
- The venv at `.venv312` (Python 3.12) is a **local-only** development convenience on this box — CI's own `build` job installs dependencies directly (no venv). Any script this plan adds must work correctly in CI's plain-`python`-on-PATH environment; `.venv312` only matters when a task's own local testing steps say so.

---

### Task 1: Staleness-detection script + xlsx timestamp normalizer

**Files:**
- Create: `ci/normalize_xlsx.py`
- Create: `ci/check-generated-up-to-date.sh`
- Test: `ci/tests/test_normalize_xlsx.py`

**Interfaces:**
- Consumes: nothing from other tasks (first task).
- Produces: `ci/normalize_xlsx.py`'s `normalize(path: Path) -> None` function (mutates the given `.xlsx` file in place, stripping `docProps/core.xml`'s `dcterms:created`/`dcterms:modified` timestamps to a fixed placeholder) — invoked as a CLI script (`python3 ci/normalize_xlsx.py <path> [<path> ...]`) by `ci/check-generated-up-to-date.sh` (this task) and later reused unchanged by Task 2's CI job. `ci/check-generated-up-to-date.sh` — a standalone, locally-runnable script; exit 0 means "generated output matches source", exit 1 means "stale" with a diff printed to stdout. Task 2 wires this script into CI without modifying it.

- [ ] **Step 1: Write `ci/normalize_xlsx.py`**

```python
#!/usr/bin/env python3
"""Strip openpyxl's per-run created/modified timestamps from an xlsx's
docProps/core.xml so two builds of otherwise-identical content compare
equal. Mutates each given file in place.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

TIMESTAMP_RE = re.compile(
    rb"<dcterms:(created|modified)([^>]*)>[^<]*</dcterms:\1>"
)
PLACEHOLDER = rb"<dcterms:\1\2>1970-01-01T00:00:00Z</dcterms:\1>"


def normalize(path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".normalizing")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                data = TIMESTAMP_RE.sub(PLACEHOLDER, data)
            zout.writestr(item, data)
    tmp.replace(path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: normalize_xlsx.py <path.xlsx> [<path.xlsx> ...]", file=sys.stderr)
        raise SystemExit(2)
    for arg in sys.argv[1:]:
        normalize(Path(arg))
```

- [ ] **Step 2: Write the failing test**

```python
# ci/tests/test_normalize_xlsx.py
from __future__ import annotations

import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from normalize_xlsx import normalize  # noqa: E402

from openpyxl import Workbook


def _write_xlsx(path: Path) -> None:
    wb = Workbook()
    wb.active["A1"] = "hello"
    wb.save(path)


def test_normalize_makes_two_runs_identical(tmp_path):
    path_a = tmp_path / "a.xlsx"
    path_b = tmp_path / "b.xlsx"
    _write_xlsx(path_a)
    time.sleep(1.1)  # openpyxl's embedded timestamp has 1-second resolution
    _write_xlsx(path_b)

    with zipfile.ZipFile(path_a) as za, zipfile.ZipFile(path_b) as zb:
        assert za.read("docProps/core.xml") != zb.read("docProps/core.xml")

    normalize(path_a)
    normalize(path_b)

    with zipfile.ZipFile(path_a) as za, zipfile.ZipFile(path_b) as zb:
        assert za.read("docProps/core.xml") == zb.read("docProps/core.xml")


def test_normalize_preserves_non_timestamp_content(tmp_path):
    path = tmp_path / "a.xlsx"
    _write_xlsx(path)
    with zipfile.ZipFile(path) as z:
        before = z.read("xl/worksheets/sheet1.xml")
    normalize(path)
    with zipfile.ZipFile(path) as z:
        after = z.read("xl/worksheets/sheet1.xml")
    assert before == after
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd /work/openfaster-spec && .venv312/bin/python -m pytest ci/tests/test_normalize_xlsx.py -v`
Expected: FAIL — `ci/normalize_xlsx.py` doesn't exist yet (this step's numbering assumes Step 1 hasn't actually been written to disk yet when you run this; if you followed steps in order and already wrote Step 1's file, temporarily rename it aside, confirm the FAIL, then restore it — the point is proving the test actually exercises real behavior, not a trivial pass).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /work/openfaster-spec && .venv312/bin/python -m pytest ci/tests/test_normalize_xlsx.py -v`
Expected: PASS, both tests.

- [ ] **Step 5: Write `ci/check-generated-up-to-date.sh`**

```bash
#!/usr/bin/env bash
# Regenerates all build output and reports whether it differs from what's
# committed -- i.e. whether the current commit's generated output is stale
# relative to its own source. Never permanently mutates .bs source files
# (the temporary Date: injection below is always reverted before exiting,
# including on error, via the trap). PDFs are excluded from the diff gate --
# see docs/superpowers/specs/2026-08-25-deploy-consistency-fix-design.md
# for why (WeasyPrint/fonttools embed non-deterministic per-run timestamps
# that can't be cleanly stripped; a successful weasyprint build is treated
# as sufficient, since the PDF's real content is a deterministic function
# of the HTML this script already verified fresh).
#
# Usage: ci/check-generated-up-to-date.sh
# Exit 0: output is up to date.
# Exit 1: output is stale -- diff summary printed to stdout.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

BS_FILES=(
  documentation/about.bs
  kafe/index.bs kafe/request.bs kafe/response.bs
  mikadiv-vib/index.bs mikadiv-vib/request.bs mikadiv-vib/response.bs
  streamld/index.bs streamld/core.bs streamld/subscription.bs
  streamld/binding-sse.bs streamld/binding-websocket.bs
)

COMMIT_DATE=$(git log -1 --format=%cd --date=short HEAD)

inject_date() {
  local f="$1"
  if grep -q '^Date:' "$f"; then
    return
  fi
  awk -v d="Date: $COMMIT_DATE" '
    /<pre class=metadata>/ && !done { print; print d; done=1; next }
    { print }
  ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
}

revert_bs_files() {
  git checkout -- "${BS_FILES[@]}"
}
trap revert_bs_files EXIT

for f in "${BS_FILES[@]}"; do
  inject_date "$f"
done

echo "==> Regenerating all build output..."
python generate_template.py
python -m kafe.generate_rm_docs
python -m kafe.generate_status_codes_docs
python -m kafe.generate_va_docs
PYTHONPATH=. python mikadiv-vib/generate_response_docs.py
PYTHONPATH=streamld python -m generator.generate_streamld_docs
python documentation/prepare_spec.py

bikeshed --allow-nonlocal-files --die-on=link-error spec documentation/about.bs documentation/about.html
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/index.bs kafe/index.html
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/request.bs kafe/request.html
bikeshed --allow-nonlocal-files --die-on=link-error spec kafe/response.bs kafe/response.html
bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv-vib/index.bs mikadiv-vib/index.html
bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv-vib/request.bs mikadiv-vib/request.html
bikeshed --allow-nonlocal-files --die-on=link-error spec mikadiv-vib/response.bs mikadiv-vib/response.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/index.bs streamld/index.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/core.bs streamld/core.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/subscription.bs streamld/subscription.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-sse.bs streamld/binding-sse.html
bikeshed --allow-nonlocal-files --die-on=link-error spec streamld/binding-websocket.bs streamld/binding-websocket.html

KAFE_VERSION=$(python -m engine.version kafe/request.bs)
weasyprint --stylesheet documentation/print.css kafe/request.html "kafe/generated/kafe-v${KAFE_VERSION}.pdf"
MIKADIV_VIB_VERSION=$(python -m engine.version mikadiv-vib/request.bs)
weasyprint --stylesheet documentation/print.css mikadiv-vib/request.html "mikadiv-vib/generated/mikadiv-vib-v${MIKADIV_VIB_VERSION}.pdf"

echo "==> Normalizing non-deterministic xlsx timestamps..."
python3 ci/normalize_xlsx.py kafe/generated/*.xlsx mikadiv-vib/generated/*.xlsx

echo "==> Reverting temporary Date: injection in .bs sources..."
revert_bs_files
trap - EXIT

GENERATED_PATHS=(
  index.html 404.html
  documentation/about.html documentation/header.include
  mikadiv-vib/header.include mikadiv-vib/index.html mikadiv-vib/request.html
  mikadiv-vib/response.html mikadiv-vib/generated/
  kafe/header.include kafe/index.html kafe/request.html kafe/response.html
  kafe/generated/
  streamld/header.include streamld/index.html streamld/core.html
  streamld/subscription.html streamld/binding-sse.html
  streamld/binding-websocket.html streamld/generated/
)

echo "==> Checking for a stale diff (PDFs excluded from the gate)..."
if ! git diff --exit-code -- "${GENERATED_PATHS[@]}" ':!*.pdf' \
   || [ -n "$(git status --porcelain -- "${GENERATED_PATHS[@]}" ':!*.pdf')" ]; then
  echo "STALE: generated output does not match source. Diff summary:"
  git diff --stat -- "${GENERATED_PATHS[@]}" ':!*.pdf' || true
  git status --porcelain -- "${GENERATED_PATHS[@]}" ':!*.pdf' || true
  exit 1
fi

echo "UP TO DATE."
exit 0
```

- [ ] **Step 6: Make the script executable**

```bash
chmod +x ci/check-generated-up-to-date.sh
```

- [ ] **Step 7: Test against a deliberately-staged STALE case**

Activate the local venv first (this script needs `bikeshed`/`weasyprint`/`shacl2code` on PATH, which `.venv312` provides locally — CI gets these directly since it installs without a venv):

```bash
source .venv312/bin/activate
```

Stage a real stale case: edit `kafe/status_codes.py`'s `_RAW` list to append a harmless new tuple (e.g. `("9999", "Test staleness detection.")`) WITHOUT regenerating `kafe/generated/status-codes.include.bs` to match, then run the script:

```bash
cd /work/openfaster-spec
python3 -c "
import re
p = 'kafe/status_codes.py'
s = open(p).read()
s = s.replace('_RAW: list[tuple[str, str]] = [', '_RAW: list[tuple[str, str]] = [\n    (\"9999\", \"Test staleness detection.\"),', 1)
open(p, 'w').write(s)
"
ci/check-generated-up-to-date.sh; echo "exit code: $?"
```
Expected: the script prints `STALE: ...` and its diff summary includes `kafe/generated/status-codes.include.bs`, and the process exits with code 1.

- [ ] **Step 8: Revert the staged stale case and test the FRESH case**

```bash
git checkout -- kafe/status_codes.py
ci/check-generated-up-to-date.sh; echo "exit code: $?"
```
Expected: the script prints `UP TO DATE.` and exits 0. If it doesn't (e.g. it reports stale on an actually-clean tree), investigate before proceeding — this would mean a false positive that will block every future PR.

- [ ] **Step 9: Confirm the working tree is clean after both test runs**

```bash
git status --short
```
Expected: no output (the script's own trap-based revert of the `Date:` injection, plus git's own generated-output tracking, should leave nothing dirty). If anything unexpected shows up, investigate before committing.

- [ ] **Step 10: Commit**

```bash
git add ci/normalize_xlsx.py ci/check-generated-up-to-date.sh ci/tests/test_normalize_xlsx.py
git commit -m "feat: add staleness-detection script for generated build output"
```

---

### Task 2: Wire the staleness check into a new pull_request CI job

**Files:**
- Modify: `.github/workflows/spec.yml`

**Interfaces:**
- Consumes: `ci/check-generated-up-to-date.sh` (Task 1) — invoked as a CI step, unmodified.
- Produces: a new job (name it `check-generated-up-to-date`) in `.github/workflows/spec.yml`, triggered on `pull_request` targeting `main`.

- [ ] **Step 1: Read the existing `build` job's setup steps first**

Read `.github/workflows/spec.yml` in full to confirm the exact lines below still match — they were read directly from the file when this plan was written (lines 14-31), but confirm nothing has changed since, since a mismatch here would mean the new job's environment silently diverges from the existing `build` job's.

- [ ] **Step 2: Add the new job**

Add this job to `.github/workflows/spec.yml` (as a sibling to the existing `build` job, under the same top-level `jobs:` key):

```yaml
  check-generated-up-to-date:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
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

      - name: Check generated output is up to date
        id: check
        run: |
          if ci/check-generated-up-to-date.sh; then
            echo "stale=false" >> "$GITHUB_OUTPUT"
          else
            echo "stale=true" >> "$GITHUB_OUTPUT"
          fi

      - name: Auto-commit regenerated output onto this PR branch
        if: steps.check.outputs.stale == 'true'
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: regenerate build output to match source changes"
          commit_user_name: github-actions[bot]
          commit_user_email: github-actions[bot]@users.noreply.github.com

      - name: Report result
        run: |
          if [ "${{ steps.check.outputs.stale }}" = "true" ]; then
            echo "::warning::Generated output was stale relative to this PR's source changes -- it has been auto-corrected in a new commit on this branch. Pull the latest commit before merging."
          else
            echo "Generated output already matches source. Nothing to do."
          fi
```

Note on why this job always exits 0 (never hard-fails) even when it had to auto-fix: `GITHUB_TOKEN`-authored pushes never retrigger a new workflow run (GitHub's own built-in behavior, confirmed during this plan's own research phase), so if this job failed after auto-committing, the PR would show a permanently-red check that never re-evaluates against the corrected commit — misleading, since the auto-commit already made the branch safe to merge. The `::warning::` annotation surfaces the same information visibly in the PR's checks UI without that problem. This is intentional, not an oversight — don't change it to `exit 1` without re-reading the spec's own reasoning on this trade-off.

- [ ] **Step 3: Validate the YAML**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/spec.yml'))" && echo "YAML valid"
```
Expected: `YAML valid`, no exception.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/spec.yml
git commit -m "feat: add pull_request job that auto-corrects stale generated output before merge"
```

---

### Task 3: Real end-to-end verification via a throwaway PR

**Files:** none (verification only).

**Interfaces:**
- Consumes: Task 2's new CI job, live on GitHub Actions.
- Produces: real evidence (a real PR, a real CI run, a real auto-commit) that the mechanism works end to end — not a local simulation.

- [ ] **Step 1: Push this plan's own branch and open a real PR**

The two prior commits from Tasks 1-2 are themselves a real, non-trivial source change (a new CI job) — but they don't by themselves exercise "source changed, generated output didn't get regenerated," since neither task touched anything that produces generated output. So this task needs a SEPARATE, deliberate staleness case, layered on top:

```bash
cd /work/openfaster-spec
git push -u origin deploy-consistency-fix
```

- [ ] **Step 2: Stage a real staleness case as a THIRD commit on this same branch**

```bash
python3 -c "
p = 'kafe/status_codes.py'
s = open(p).read()
s = s.replace('_RAW: list[tuple[str, str]] = [', '_RAW: list[tuple[str, str]] = [\n    (\"9998\", \"End-to-end staleness test -- Task 3.\"),', 1)
open(p, 'w').write(s)
"
git add kafe/status_codes.py
git commit -m "test: stage a deliberate staleness case for Task 3's end-to-end verification"
git push origin deploy-consistency-fix
```

- [ ] **Step 3: Open the PR and watch the new job run for real**

```bash
gh pr create --repo OpenFASTER-Standard/spec --base main --head deploy-consistency-fix \
  --title "Fix deploy-consistency race + add pre-merge self-consistency check" \
  --body "See docs/superpowers/specs/2026-08-25-deploy-consistency-fix-design.md. Includes a deliberately-staged staleness case (kafe/status_codes.py's new 9998 entry, not yet regenerated into kafe/generated/status-codes.include.bs) to real-world-verify the new pre-merge check actually catches and auto-corrects it -- see the plan's Task 3."
gh pr checks --repo OpenFASTER-Standard/spec <PR-number> --watch --interval 15
```

Expected: the `check-generated-up-to-date` job runs, its "Check generated output is up to date" step reports staleness (exit 1 internally, captured into `stale=true`), the "Auto-commit regenerated output onto this PR branch" step runs and pushes a new commit, and the "Report result" step shows the `::warning::` annotation. The job's own overall status is still green (per Task 2's design).

- [ ] **Step 4: Confirm the auto-commit actually landed, with real evidence**

```bash
git fetch origin deploy-consistency-fix
git log --oneline origin/deploy-consistency-fix -5
git show origin/deploy-consistency-fix:kafe/generated/status-codes.include.bs | grep -c "9998"
```
Expected: a new commit authored by `github-actions[bot]` (message: "chore: regenerate build output to match source changes") appears on top of your Step 2 commit, and the regenerated `status-codes.include.bs` now contains the `9998` test entry — real, git-verified proof the mechanism works, not an assumption.

- [ ] **Step 5: Pull the auto-commit locally and remove the test staleness case**

```bash
git pull origin deploy-consistency-fix
python3 -c "
p = 'kafe/status_codes.py'
s = open(p).read()
s = s.replace('    (\"9998\", \"End-to-end staleness test -- Task 3.\"),\n', '', 1)
open(p, 'w').write(s)
"
source .venv312/bin/activate
ci/check-generated-up-to-date.sh
```
Expected: the script now reports STALE again (since removing the 9998 entry from source, without regenerating, is itself a fresh staleness case) — confirm this, then actually regenerate and commit the reversion properly:
```bash
python generate_template.py
python -m kafe.generate_rm_docs
python -m kafe.generate_status_codes_docs
python -m kafe.generate_va_docs
git add kafe/status_codes.py kafe/generated/
git status --short  # confirm only the 9998-removal-related files changed
git commit -m "test: remove Task 3's staged staleness test case now that end-to-end verification is complete"
git push origin deploy-consistency-fix
```

- [ ] **Step 6: Watch CI run clean on this final state**

```bash
gh pr checks --repo OpenFASTER-Standard/spec <PR-number> --watch --interval 15
```
Expected: the `check-generated-up-to-date` job reports "Generated output already matches source. Nothing to do." (no further auto-commit), and the existing `build` job passes too.

---

### Task 4: Vercel cache-header change (defense-in-depth)

**Files:**
- Modify: `vercel.json`

**Interfaces:**
- Consumes: nothing from other tasks (independent of Tasks 1-3).
- Produces: `vercel.json`'s new `headers` block, consumed only by Vercel itself at deploy/serve time.

- [ ] **Step 1: Modify `vercel.json`**

Current content (read it first to confirm nothing has changed since this plan was written):
```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    { "source": "/about", "destination": "/documentation/about" }
  ]
}
```

New content:
```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    { "source": "/about", "destination": "/documentation/about" }
  ],
  "headers": [
    {
      "source": "/:path((?!.*\\.(xlsx|pdf)$).*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store" }
      ]
    }
  ]
}
```

This forces `Cache-Control: no-store` on every route except `.xlsx`/`.pdf` downloads (matched via a negative-lookahead on file extension — the same `path-to-regexp` idiom Vercel's own docs use elsewhere for path exclusions), leaving Excel/PDF downloads on Vercel's normal caching. Per the spec's own honest framing: this is expected to reliably control browser/downstream caching, but is *not* confirmed to override Vercel's own static-file edge caching (its docs describe that as bypass-proof "by design") — implemented anyway as defense-in-depth, verified empirically in Task 5, not assumed to work.

- [ ] **Step 2: Validate the JSON**

```bash
python3 -c "import json; json.load(open('vercel.json'))" && echo "JSON valid"
```
Expected: `JSON valid`.

- [ ] **Step 3: Commit**

```bash
git add vercel.json
git commit -m "feat: force Cache-Control: no-store on HTML routes (defense-in-depth against CDN staleness)"
```

---

### Task 5: Final gate — merge, then real live verification with evidence

**Files:** none (merge + verification only).

- [ ] **Step 1: STOP — this step requires the operator's explicit go-ahead**

Do NOT merge without asking first. Present the PR's state (Tasks 1-4's commits, Task 3's real end-to-end auto-commit proof) and ask the operator how they want it merged — matching this session's own established pattern for every prior merge today.

- [ ] **Step 2: (after go-ahead) Merge**

```bash
gh pr merge <PR-number> --repo OpenFASTER-Standard/spec --squash --delete-branch
```

- [ ] **Step 3: Watch the push-to-main CI run to completion**

```bash
gh run list --repo OpenFASTER-Standard/spec --branch main --limit 3
gh run watch <run-id> --repo OpenFASTER-Standard/spec --exit-status
```
Expected: the existing `build` job runs (this is a `push` to `main`, not a `pull_request`, so the new `check-generated-up-to-date` job correctly does NOT run here — confirm this in the run's own job list, don't just assume), and its "Commit regenerated output" step reports "No changes to commit" (since the PR branch was already self-consistent before merge, per this whole plan's point) — confirm this specific log line, don't just check the job passed.

- [ ] **Step 4: Real, repeated header verification (not a single check)**

```bash
for i in $(seq 1 20); do
  curl -s -D - -o /dev/null "https://www.openfaster.org/documentation/about" \
    | grep -Ei "^(cache-control|age|x-vercel-cache|x-vercel-id):"
  echo "---"
  sleep 30
done
```
This takes 10 minutes — let it run to completion, don't interrupt early. Expected: `cache-control: no-store` on every response; `x-vercel-cache` is never `HIT`; `age` never exceeds a few seconds on any response. Save the full output as your evidence.

- [ ] **Step 5: Confirm no regression on every other live page**

```bash
for path in / /kafe /kafe/request /kafe/response /mikadiv-vib /mikadiv-vib/request /mikadiv-vib/response /streamld /streamld/core /streamld/subscription /streamld/binding-sse /streamld/binding-websocket /about; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -L "https://www.openfaster.org$path?cb=$(date +%s%N)")
  echo "$path -> $code"
done
```
Expected: every path returns `200`.

- [ ] **Step 6: Report the full evidence trail, including what was NOT independently verified**

Write up, for the operator: (a) Task 3's real auto-commit proof (the actual commit SHA and its content, from a real throwaway PR against the real repo), (b) Step 4's full 20-request header log, (c) Step 5's URL check results, (d) an explicit, honest list of anything NOT independently re-confirmed — at minimum: this box has no way to check Vercel's CDN behavior from a second geographic region (no multi-region probe access), so Step 4's evidence is from a single vantage point only; state this plainly rather than implying broader coverage than what was actually checked.
