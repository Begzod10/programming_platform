#!/usr/bin/env bash
# Builds PcGuard-win-x64.zip (top folder PcGuard/) from already built parts. Runs on macOS or Linux.
#
#   tools/package-zip.sh --dist <dist dir> --setup <Setup-PcGuard.exe> --cleanup <Cleanup-PcGuard.exe> \
#                        --stage <empty staging dir> --out <zip path> \
#                        [--default-code-file <path> [--yes]]
#
# README.md and scripts/ come from this repository (pc-agent/README.md, pc-agent/scripts/).
# A default-recovery-code.txt holds a plain-text recovery code and must NEVER be packaged: it is
# excluded explicitly, and the packaging FAILS if one is found in any source, in the staging folder
# or in the finished zip.
#
# EXPLICIT OPT-IN: --default-code-file <path> puts the owner's own file into the zip as
# PcGuard/default-recovery-code.txt. The file is only checked (exists, regular file, not a symlink,
# 12-130 bytes, outside the git working tree) and copied; its content is never read, printed or logged.
# The zip must then be named PcGuard-win-x64-WITH-DEFAULT-CODE.zip (a clean build must not use that name).
set -euo pipefail

SECRET='default-recovery-code.txt'
here="$(cd "$(dirname "$0")/.." && pwd)"
dist= setup= cleanup= stage= out= codefile= yes=0
WITH_NAME='PcGuard-win-x64-WITH-DEFAULT-CODE.zip'
while [ $# -gt 0 ]; do
  case "$1" in
    --dist) dist="$2"; shift 2 ;;
    --setup) setup="$2"; shift 2 ;;
    --cleanup) cleanup="$2"; shift 2 ;;
    --stage) stage="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
    --default-code-file) [ $# -ge 2 ] || { echo "--default-code-file needs a path" >&2; exit 2; }; codefile="$2"; shift 2 ;;
    --yes) yes=1; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
for v in dist setup cleanup stage out; do
  [ -n "${!v}" ] || { echo "--$v is required" >&2; exit 2; }
done
[ -f "$dist/PcGuard.Service.exe" ] && [ -f "$dist/PcGuard.Shell.exe" ] && [ -f "$dist/appsettings.json" ] \
  || { echo "dist folder incomplete: $dist" >&2; exit 2; }
[ -f "$setup" ] && [ -f "$cleanup" ] || { echo "Setup or Cleanup exe missing" >&2; exit 2; }
[ ! -e "$out" ] || { echo "Output exists (move it away first): $out" >&2; exit 2; }
outname="$(basename "$out")"
if [ -n "$codefile" ]; then
  [ "$outname" = "$WITH_NAME" ] || { echo "With --default-code-file the zip must be named $WITH_NAME (got: $outname)" >&2; exit 2; }
else
  case "$outname" in *WITH-DEFAULT-CODE*) echo "A zip without --default-code-file must not be named *WITH-DEFAULT-CODE* (got: $outname)" >&2; exit 2 ;; esac
  [ "$yes" = 0 ] || { echo "--yes only makes sense with --default-code-file" >&2; exit 2; }
fi

if [ -n "$codefile" ]; then
  # Checks that never look at the content.
  [ ! -L "$codefile" ] || { echo "REFUSED: --default-code-file is a symbolic link: $codefile" >&2; exit 3; }
  [ -e "$codefile" ] || { echo "REFUSED: --default-code-file does not exist: $codefile" >&2; exit 3; }
  [ -f "$codefile" ] || { echo "REFUSED: --default-code-file is not a regular file: $codefile" >&2; exit 3; }
  size="$(wc -c < "$codefile" | tr -d ' ')"
  if [ "$size" -lt 12 ] || [ "$size" -gt 130 ]; then
    echo "REFUSED: --default-code-file must be 12 to 130 bytes (it is $size bytes)." >&2; exit 3
  fi
  cdir="$(cd "$(dirname "$codefile")" && pwd -P)"
  repo="$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$repo" ]; then
    repo="$(cd "$repo" && pwd -P)"
    case "$cdir/" in
      "$repo"/*) echo "REFUSED: --default-code-file is inside the git repository ($repo). Keep it outside so it can never be committed." >&2; exit 3 ;;
    esac
  fi
  codefile="$cdir/$(basename "$codefile")"
  {
    echo "=================================================================================="
    echo " WARNING: this zip will contain a PLAIN-TEXT recovery code (default-recovery-code.txt)."
    echo " Anyone who holds the zip can disable PC Guard on EVERY PC installed from it."
    echo " Keep the zip off shared drives and chat. Use it only for test/admin PCs."
    echo " Output: $out"
    echo "=================================================================================="
  } >&2
  if [ "$yes" != 1 ]; then
    printf 'Type YES: ' >&2
    ans=
    read -r ans || true
    [ "$ans" = "YES" ] || { echo "Aborted. Nothing was built." >&2; exit 4; }
  fi
fi

mkdir -p "$stage"
[ -z "$(ls -A "$stage")" ] || { echo "Staging folder is not empty: $stage" >&2; exit 2; }

guard() { # $1 = folder to search
  local hits
  hits="$(find "$1" -iname "$SECRET" 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    echo "REFUSED: $SECRET found (it holds a plain-text recovery code and must never be packaged):" >&2
    echo "$hits" >&2
    exit 3
  fi
}
guard "$dist"
guard "$here/scripts"
guard "$(dirname "$setup")"
guard "$(dirname "$cleanup")"

root="$stage/PcGuard"
mkdir -p "$root/scripts" "$root/dist"
cp -p "$setup" "$root/Setup-PcGuard.exe"
cp -p "$cleanup" "$root/Cleanup-PcGuard.exe"
cp -p "$here/README.md" "$root/README.md"
for f in install.ps1 uninstall.ps1 publish.ps1 cleanup.ps1 CLEANUP.md selftest.ps1 SELFTEST.md; do
  cp -p "$here/scripts/$f" "$root/scripts/$f"
done
(cd "$dist" && tar cf - --exclude="$SECRET" .) | (cd "$root/dist" && tar xpf -)
guard "$stage"

if [ -n "$codefile" ]; then
  # Only into the staging folder, as restrictive as the zip format allows (unix mode 600, folder 700).
  cp "$codefile" "$root/$SECRET"
  chmod 600 "$root/$SECRET"
  chmod 700 "$root"
  (cd "$stage" && zip -r -X -q "$out" PcGuard -x "*.DS_Store")
else
  (cd "$stage" && zip -r -X -q "$out" PcGuard -x "*/$SECRET" -x "*.DS_Store")
fi

# Capture the listing first: with `set -o pipefail`, `unzip -Z1 | grep -q` fails with SIGPIPE (141)
# on a big zip because grep -q exits at the first match.
listing="$(unzip -Z1 "$out")"
count="$(grep -ic "$SECRET" <<<"$listing" || true)"
if [ -n "$codefile" ]; then
  if [ "$count" != 1 ] || ! grep -qx "PcGuard/$SECRET" <<<"$listing"; then
    echo "REFUSED: $SECRET is not exactly once at PcGuard/$SECRET in $out; deleting the zip." >&2
    rm -f "$out"; exit 3
  fi
  has=yes
else
  if [ "$count" != 0 ]; then
    echo "REFUSED: $SECRET ended up in $out; deleting the zip." >&2
    rm -f "$out"; exit 3
  fi
  has=no
fi
unzip -tq "$out"
echo "OK: $out"
echo "size: $(wc -c < "$out" | tr -d ' ') bytes"
echo "sha256: $(shasum -a 256 "$out" | cut -d' ' -f1)"
echo "contains default-recovery-code.txt: $has"
if [ "$has" = yes ]; then
  echo "WARNING: this zip holds a plain-text recovery code. Do not share it; delete it when the PCs are installed."
fi
