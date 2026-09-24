#!/usr/bin/env bash
# Copy the FireWatch mod files from the Whiskerwood modkit into this repo.
#
# Usage (Git Bash, from anywhere):
#   ./sync-from-modkit.sh            # copy .uasset files + uplugin into Mod/FireWatch/
#   ./sync-from-modkit.sh --release  # also stage FireWatch.pak + uplugin into workshop/content/
#
# Override the modkit location with:  MODKIT=/e/path/to/Whiskerwood-Project ./sync-from-modkit.sh
set -euo pipefail

MOD_NAME="FireWatch"
MODKIT="${MODKIT:-/e/modding/Whiskerwood-Project}"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$MODKIT/Content/Mods/$MOD_NAME"
DST="$REPO/Mod/$MOD_NAME"

RELEASE=0
[[ "${1:-}" == "--release" ]] && RELEASE=1

if [[ ! -d "$SRC" ]]; then
  echo "ERROR: modkit mod folder not found: $SRC" >&2
  echo "Set MODKIT=/path/to/Whiskerwood-Project if it lives elsewhere." >&2
  exit 1
fi
mkdir -p "$DST"

# --- assets -----------------------------------------------------------------
shopt -s nullglob
src_assets=("$SRC"/*.uasset)
if (( ${#src_assets[@]} == 0 )); then
  echo "ERROR: no .uasset files in $SRC" >&2
  exit 1
fi

echo "Copying assets from $SRC"
for f in "${src_assets[@]}"; do
  name="$(basename "$f")"
  if [[ -f "$DST/$name" ]] && cmp -s "$f" "$DST/$name"; then
    echo "  unchanged  $name"
  else
    cp "$f" "$DST/$name"
    echo "  updated    $name"
  fi
done

# remove assets that were deleted/renamed in the modkit
for f in "$DST"/*.uasset; do
  name="$(basename "$f")"
  if [[ ! -f "$SRC/$name" ]]; then
    rm "$f"
    echo "  removed    $name (no longer in modkit)"
  fi
done

# --- uplugin ------------------------------------------------------------------
# The repo copy is the "good" one (description, author). Only take the modkit's
# copy if it actually has a description, so an old blank one can't overwrite it.
UPL="$SRC/$MOD_NAME.uplugin"
if [[ -f "$UPL" ]]; then
  if grep -Eq '"Description"[[:space:]]*:[[:space:]]*""' "$UPL"; then
    echo "  skipped    $MOD_NAME.uplugin (modkit copy has an empty Description;"
    echo "             copy Mod/$MOD_NAME/$MOD_NAME.uplugin into the modkit instead)"
  elif ! cmp -s "$UPL" "$DST/$MOD_NAME.uplugin" 2>/dev/null; then
    cp "$UPL" "$DST/$MOD_NAME.uplugin"
    echo "  updated    $MOD_NAME.uplugin"
  else
    echo "  unchanged  $MOD_NAME.uplugin"
  fi
fi

# --- release (optional) -------------------------------------------------------
if (( RELEASE )); then
  if [[ -z "${LOCALAPPDATA:-}" ]]; then
    echo "ERROR: LOCALAPPDATA not set (run this from Git Bash on Windows)." >&2
    exit 1
  fi
  if command -v cygpath >/dev/null 2>&1; then
    LAD="$(cygpath -u "$LOCALAPPDATA")"
  else
    LAD="$LOCALAPPDATA"
  fi
  PAK="$LAD/Whiskerwood/Saved/mods/$MOD_NAME/$MOD_NAME.pak"
  if [[ ! -f "$PAK" ]]; then
    echo "ERROR: $PAK not found - run Cook & Install in the modkit first." >&2
    exit 1
  fi
  OUT="$REPO/workshop/content"
  mkdir -p "$OUT"
  cp "$PAK" "$OUT/"
  cp "$DST/$MOD_NAME.uplugin" "$OUT/"
  echo "Staged for Workshop upload in workshop/content/:"
  ls -l "$OUT"
  echo "Built: $(date -r "$PAK" '+%Y-%m-%d %H:%M')  - make sure that's your latest Cook & Install."
fi

echo
echo "Done. Review with: git status"
