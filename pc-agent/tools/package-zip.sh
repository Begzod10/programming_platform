#!/usr/bin/env bash
# Builds PcGuard-win-x64.zip (top folder PcGuard/) from already built parts. Runs on macOS or Linux.
#
#   tools/package-zip.sh --dist <dist dir> --setup <Setup-PcGuard.exe> --cleanup <Cleanup-PcGuard.exe> \
#                        --stage <empty staging dir> --out <zip path>
#
# README.md and scripts/ come from this repository (pc-agent/README.md, pc-agent/scripts/).
# A default-recovery-code.txt holds a plain-text recovery code and must NEVER be packaged: it is
# excluded explicitly, and the packaging FAILS if one is found in any source, in the staging folder
# or in the finished zip.
set -euo pipefail

SECRET='default-recovery-code.txt'
here="$(cd "$(dirname "$0")/.." && pwd)"
dist= setup= cleanup= stage= out=
while [ $# -gt 0 ]; do
  case "$1" in
    --dist) dist="$2"; shift 2 ;;
    --setup) setup="$2"; shift 2 ;;
    --cleanup) cleanup="$2"; shift 2 ;;
    --stage) stage="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
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

(cd "$stage" && zip -r -X -q "$out" PcGuard -x "*/$SECRET" -x "*.DS_Store")

if unzip -Z1 "$out" | grep -qi "$SECRET"; then
  echo "REFUSED: $SECRET ended up in $out; deleting the zip." >&2
  rm -f "$out"
  exit 3
fi
unzip -tq "$out"
echo "OK: $out"
