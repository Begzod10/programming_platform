#!/usr/bin/env bash
# Tests tools/package-zip.sh with a tiny fake dist (no 160 MB rebuild) and an obviously fake code.
# Everything lives in a temp dir OUTSIDE the repository. Usage: tools/test-package-zip.sh
set -uo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
pkg="$here/tools/package-zip.sh"
FAKE='FAKE-TEST-CODE-0001'
T="$(mktemp -d "${TMPDIR:-/tmp}/pkgzip-test.XXXXXX")"
trap 'rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fail=1; }

mkdir -p "$T/dist" "$T/bin"
for f in PcGuard.Service.exe PcGuard.Shell.exe appsettings.json; do echo x > "$T/dist/$f"; done
echo s > "$T/bin/Setup-PcGuard.exe"; echo c > "$T/bin2.exe"; mv "$T/bin2.exe" "$T/bin/Cleanup-PcGuard.exe"
mkdir -p "$T/secret"
printf '%s\n' "$FAKE" > "$T/secret/code.txt"
WITH="PcGuard-win-x64-WITH-DEFAULT-CODE.zip"
n=0
new() { n=$((n+1)); OUTDIR="$T/o$n"; mkdir -p "$OUTDIR"; }
run() { # args after fixed ones; sets RC and OUT
  local out="$OUTDIR"
  OUT="$("$pkg" --dist "$T/dist" --setup "$T/bin/Setup-PcGuard.exe" --cleanup "$T/bin/Cleanup-PcGuard.exe" \
      --stage "$out/stage" "$@" 2>&1 </dev/null)"; RC=$?
  ALL="$ALL$OUT"
}
ALL=
new

# 1 clean build works and has no file
run --out "$OUTDIR/PcGuard-win-x64.zip"
[ $RC -eq 0 ] && [ -f "$OUTDIR/PcGuard-win-x64.zip" ] && echo "$OUT" | grep -q 'contains default-recovery-code.txt: no' && ok "clean build, contains: no" || bad "clean build ($RC)"

# 2 default refuses when the file is in dist
cp "$T/secret/code.txt" "$T/dist/default-recovery-code.txt"
new; run --out "$OUTDIR/PcGuard-win-x64.zip"
[ $RC -eq 3 ] && [ ! -e "$OUTDIR/PcGuard-win-x64.zip" ] && ok "default refuses when the file is in dist" || bad "default refuse ($RC)"
rm -f "$T/dist/default-recovery-code.txt"

# 3 opt-in with repo-internal path refuses
cp "$T/secret/code.txt" "$here/tools/.fake-inrepo-code.txt"
new; run --out "$OUTDIR/$WITH" --default-code-file "$here/tools/.fake-inrepo-code.txt" --yes
rm -f "$here/tools/.fake-inrepo-code.txt"
[ $RC -eq 3 ] && echo "$OUT" | grep -q 'inside the git repository' && [ ! -e "$OUTDIR/$WITH" ] && ok "repo-internal path refuses" || bad "repo-internal ($RC)"

# 4 symlink refuses
ln -s "$T/secret/code.txt" "$T/secret/link.txt"
new; run --out "$OUTDIR/$WITH" --default-code-file "$T/secret/link.txt" --yes
[ $RC -eq 3 ] && echo "$OUT" | grep -q 'symbolic link' && ok "symlink refuses" || bad "symlink ($RC)"

# 5 too short / too long
printf 'short' > "$T/secret/short.txt"
new; run --out "$OUTDIR/$WITH" --default-code-file "$T/secret/short.txt" --yes
[ $RC -eq 3 ] && ok "too short refuses" || bad "too short ($RC)"
head -c 131 /dev/zero | tr '\0' 'A' > "$T/secret/long.txt"
new; run --out "$OUTDIR/$WITH" --default-code-file "$T/secret/long.txt" --yes
[ $RC -eq 3 ] && ok "too long refuses" || bad "too long ($RC)"

# 6 missing / directory
new; run --out "$OUTDIR/$WITH" --default-code-file "$T/secret/nope.txt" --yes
[ $RC -eq 3 ] && ok "missing file refuses" || bad "missing ($RC)"

# 7 wrong zip names
new; run --out "$OUTDIR/PcGuard-win-x64.zip" --default-code-file "$T/secret/code.txt" --yes
[ $RC -eq 2 ] && ok "opt-in with the clean zip name refuses" || bad "name1 ($RC)"
new; run --out "$OUTDIR/$WITH"
[ $RC -eq 2 ] && ok "clean build with the WITH name refuses" || bad "name2 ($RC)"

# 8 answer other than YES aborts
new
OUT="$(echo no | "$pkg" --dist "$T/dist" --setup "$T/bin/Setup-PcGuard.exe" --cleanup "$T/bin/Cleanup-PcGuard.exe" --stage "$OUTDIR/stage" --out "$OUTDIR/$WITH" --default-code-file "$T/secret/code.txt" 2>&1)"; RC=$?
ALL="$ALL$OUT"
[ $RC -eq 4 ] && [ ! -e "$OUTDIR/$WITH" ] && echo "$OUT" | grep -q 'PLAIN-TEXT recovery code' && ok "warning shown, 'no' aborts" || bad "confirm ($RC)"

# 9 valid opt-in with YES typed
new
OUT="$(echo YES | "$pkg" --dist "$T/dist" --setup "$T/bin/Setup-PcGuard.exe" --cleanup "$T/bin/Cleanup-PcGuard.exe" --stage "$OUTDIR/stage" --out "$OUTDIR/$WITH" --default-code-file "$T/secret/code.txt" 2>&1)"; RC=$?
ALL="$ALL$OUT"
[ $RC -eq 0 ] && [ -f "$OUTDIR/$WITH" ] && ok "opt-in with typed YES builds" || bad "YES build ($RC)"
cnt="$(unzip -Z1 "$OUTDIR/$WITH" | grep -c '^PcGuard/default-recovery-code.txt$')"
tot="$(unzip -Z1 "$OUTDIR/$WITH" | grep -ic 'default-recovery-code.txt')"
[ "$cnt" = 1 ] && [ "$tot" = 1 ] && ok "file exactly once at PcGuard/default-recovery-code.txt" || bad "entry count $cnt/$tot"
[ ! -e "$OUTDIR/PcGuard-win-x64.zip" ] && ok "clean zip name not produced" || bad "clean name exists"
echo "$OUT" | grep -q 'contains default-recovery-code.txt: yes' && echo "$OUT" | grep -q 'sha256:' && ok "report lines printed" || bad "report lines"
# not in dist/ or scripts/ inside the zip
unzip -Z1 "$OUTDIR/$WITH" | grep -E '/(dist|scripts)/default-recovery-code.txt' >/dev/null && bad "file leaked to dist/scripts" || ok "not in dist/ or scripts/"

# 10 --yes variant
new
OUT="$("$pkg" --dist "$T/dist" --setup "$T/bin/Setup-PcGuard.exe" --cleanup "$T/bin/Cleanup-PcGuard.exe" --stage "$OUTDIR/stage" --out "$OUTDIR/$WITH" --default-code-file "$T/secret/code.txt" --yes 2>&1 </dev/null)"; RC=$?
ALL="$ALL$OUT"
[ $RC -eq 0 ] && ok "--yes skips the prompt" || bad "--yes ($RC)"

# 11 content never in any output
echo "$ALL" | grep -q "$FAKE" && bad "fake content appeared in script output" || ok "script output never contains the fake content"

echo
[ $fail -eq 0 ] && echo "ALL PASSED" || { echo "SOME FAILED"; exit 1; }
