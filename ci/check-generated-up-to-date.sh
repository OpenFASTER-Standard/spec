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

# Back up each file's real current content (whether committed or not --
# NEVER assume "revert to git's index/HEAD" is correct here, since a
# caller may legitimately have real uncommitted edits to one of these
# files, e.g. mid-development. A blanket `git checkout -- ...` would
# silently destroy that work. Restore from this backup instead.
BACKUP_DIR=$(mktemp -d)
for f in "${BS_FILES[@]}"; do
  mkdir -p "$BACKUP_DIR/$(dirname "$f")"
  cp "$f" "$BACKUP_DIR/$f"
done

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
  for f in "${BS_FILES[@]}"; do
    cp "$BACKUP_DIR/$f" "$f"
  done
  rm -rf "$BACKUP_DIR"
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
