<#
.SYNOPSIS
  Automated on-PC self-test for an installed PC Guard. Run in an ELEVATED Windows PowerShell.
.DESCRIPTION
  Runs the checks of the README VM checklist that need no human and no backend, on a PC where PC Guard
  is installed (typically with a dummy http://localhost backend, nobody signed in to PC Guard, so the
  PC is locked in the "no_student" state). Prints one line per check:
    [PASS] id title
    [FAIL] id title - detail
    [SKIP] id title - reason
  then a summary, and writes the same plus environment information (Windows build, PowerShell version,
  install folder listing and exe hashes, service configuration, recent PC Guard event log lines) to
  $env:USERPROFILE\Desktop\pcguard-selftest-<yyyyMMdd-HHmmss>.txt (or -OutFile).

  Read-only except for the enforcement probes (section D): they start notepad.exe, mspaint.exe,
  taskmgr.exe and an allowlisted cmd.exe window from THIS elevated session with Start-Process and
  expect PC Guard to close the first three within 20 s. The service treats an elevated administrator's
  processes in the console session like any other user process, so no scheduled task is needed. Only
  test processes started by this script are ever closed by it (cleanup at the end of section D).
  -NoProbes skips section D.

  It never prints or writes secrets: the content of recovery.hash (only "present, format ok, N bytes"),
  the recovery code, or the machine key value (only "GUID ok"). It never attempts a recovery release
  and never changes the service, its files or its settings.

  Exit code: 0 when no check FAILED, 1 when at least one FAILED, 2 when not elevated.
  Compatible with Windows PowerShell 5.1 and PowerShell 7, but run it with Windows PowerShell
  (powershell.exe): it is allowlisted, PowerShell 7 (pwsh.exe) is NOT and is closed while the PC is locked.
  NOT TESTED on Windows: written and parse-checked on macOS. See scripts\SELFTEST.md.
.PARAMETER Quiet
  Console shows only FAIL lines and the summary (the report file still gets everything).
.PARAMETER NoProbes
  Skip the enforcement probes (section D): nothing is started.
.PARAMETER OutFile
  Report file path. Default: $env:USERPROFILE\Desktop\pcguard-selftest-<yyyyMMdd-HHmmss>.txt.
.PARAMETER InstallDir
  PC Guard install folder (default: 64-bit Program Files\PcGuard, as install.ps1).
.PARAMETER ExpectedBaseUrl
  Optional. When given, Backend:BaseUrl in the installed appsettings.json must equal it (trailing / ignored).
.PARAMETER ExpectedExtraApps
  Optional. When given, Allowlist:ExtraApps must hold exactly these names (any order, case-insensitive).
  Accepts an array or one comma separated string.
.PARAMETER LogHours
  How far back the Application event log is read (default 2 hours).
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\selftest.ps1
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\selftest.ps1 -ExpectedBaseUrl http://localhost:8001/api/v1 -ExpectedExtraApps anydesk.exe
#>
[CmdletBinding()]
param(
    [switch]$Quiet,
    [switch]$NoProbes,
    [string]$OutFile,
    [string]$InstallDir = (Join-Path $(if ($env:ProgramW6432) { $env:ProgramW6432 } else { $env:ProgramFiles }) 'PcGuard'),
    [string]$ExpectedBaseUrl,
    [string[]]$ExpectedExtraApps,
    [ValidateRange(1, 168)][int]$LogHours = 2
)

# Script level: never stop on a non-terminating error. Every check sets 'Stop' inside its own try/catch
# (Invoke-Check), so one failing check never aborts the run.
$ErrorActionPreference = 'Continue'

$SelfTestVersion = '1'
$ServiceName = 'PcGuard'
$ServiceKey = 'HKLM:\SYSTEM\CurrentControlSet\Services\PcGuard'
$SafeBootKeys = @(
    'HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal\PcGuard',
    'HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Network\PcGuard'
)
# Event log provider: the .NET host registers the application name (assembly PcGuard.Service);
# 'PcGuard' is accepted too in case the source was registered under the short name.
$ProviderNames = @('PcGuard.Service', 'PcGuard')
$PipeName = 'PcGuard.Pipe'
$DataDir = Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'PcGuard'
$MaxHashFileBytes = 136        # RecoveryCode.MaxStoredFileBytes
$MaxAttemptsFileBytes = 256    # SecureStore
$MaxExtraApps = 16             # ExtraAllowlist.MaxEntries
$ProbeSeconds = 20

$SidSystem = 'S-1-5-18'
$SidAdmins = 'S-1-5-32-544'
$SidTrustedInstaller = 'S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464'
# Users, Authenticated Users, Everyone, INTERACTIVE
$BroadSids = @('S-1-5-32-545', 'S-1-5-11', 'S-1-1-0', 'S-1-5-4')

$InstallDir = [System.IO.Path]::GetFullPath($InstallDir).TrimEnd('\')

# ---------------------------------------------------------------------------------------------------
# result bookkeeping and output
# ---------------------------------------------------------------------------------------------------

$script:Results = New-Object System.Collections.Generic.List[object]
$script:ReportLines = New-Object System.Collections.Generic.List[string]
$script:EnvLines = New-Object System.Collections.Generic.List[string]
# Secret values used ONLY for the privacy scan of the event log; never printed or written.
$script:Needles = New-Object System.Collections.Generic.List[string]
$script:NeedleKinds = New-Object System.Collections.Generic.List[string]

function Format-OneLine {
    param([string]$Text)
    if ($null -eq $Text) { return '' }
    $t = ($Text -replace "(`r`n|`r|`n)+", ' | ').Trim()
    if ($t.Length -gt 900) { $t = $t.Substring(0, 900) + ' ...' }
    return $t
}

function Write-Out {
    # A report line: always into the file, on the console unless -Quiet (FAIL lines and the summary are
    # always shown).
    param([string]$Text, [string]$Color, [switch]$Always)
    $script:ReportLines.Add($Text)
    if ($Quiet -and -not $Always) { return }
    if ($Color) { Write-Host $Text -ForegroundColor $Color } else { Write-Host $Text }
}

function New-Result {
    param([string]$Status, [string]$Detail)
    $o = New-Object PSObject -Property @{ Status = $Status; Detail = $Detail }
    $o.PSObject.TypeNames.Insert(0, 'PgSelfTest.Result')
    return $o
}
function Pass { param([string]$Detail) return (New-Result 'PASS' $Detail) }
function Fail { param([string]$Detail) return (New-Result 'FAIL' $Detail) }
function Skip { param([string]$Detail) return (New-Result 'SKIP' $Detail) }

function Add-Result {
    param([string]$Id, [string]$Title, [string]$Status, [string]$Detail)
    $Detail = Format-OneLine $Detail
    $script:Results.Add((New-Object PSObject -Property @{ Id = $Id; Title = $Title; Status = $Status; Detail = $Detail }))
    switch ($Status) {
        'PASS' {
            Write-Out ('[PASS] {0} {1}' -f $Id, $Title) 'Green'
            if ($Detail) { Write-Out ('       {0}' -f $Detail) }
        }
        'FAIL' { Write-Out ('[FAIL] {0} {1} - {2}' -f $Id, $Title, $Detail) 'Red' -Always }
        default { Write-Out ('[SKIP] {0} {1} - {2}' -f $Id, $Title, $Detail) 'Yellow' }
    }
}

function Invoke-Check {
    # Runs one self-contained check. The body returns Pass/Fail/Skip; anything it throws is a FAIL of
    # this check only.
    param([string]$Id, [string]$Title, [scriptblock]$Body)
    $status = 'FAIL'
    $detail = 'the check returned no result'
    try {
        $ErrorActionPreference = 'Stop'
        $out = @(& $Body)
        $res = $null
        foreach ($o in $out) {
            if ($null -ne $o -and $o.PSObject.TypeNames -contains 'PgSelfTest.Result') { $res = $o }
        }
        if ($null -ne $res) { $status = $res.Status; $detail = $res.Detail }
    }
    catch {
        $status = 'FAIL'
        $detail = 'unexpected error: ' + $_.Exception.Message
    }
    Add-Result $Id $Title $status $detail
}

function Add-Env {
    param([string]$Text)
    $script:EnvLines.Add($Text)
}

# ---------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------

function Invoke-Native {
    # Runs a native program; stderr never becomes a terminating error (Windows PowerShell 5.1).
    # "sc" alone is an alias of Set-Content, so always sc.exe.
    param([string]$Exe, [string[]]$ExeArgs)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = @(& $Exe @ExeArgs 2>&1 | ForEach-Object { [string]$_ })
        $script:NativeExit = $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $old }
    return $out
}

function Test-ContainsText {
    # Literal, case-insensitive substring test (no wildcards: -like treats [ ] ? * specially).
    param([string]$Text, [string]$Needle)
    if ([string]::IsNullOrEmpty($Text) -or [string]::IsNullOrEmpty($Needle)) { return $false }
    return ($Text.IndexOf($Needle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0)
}

function Get-SidOwner {
    param($Security)
    $o = $Security.GetOwner([System.Security.Principal.SecurityIdentifier])
    if ($null -eq $o) { return '' }
    return $o.Value
}

function Get-SidName {
    param([string]$Sid)
    try { return (New-Object System.Security.Principal.SecurityIdentifier($Sid)).Translate([System.Security.Principal.NTAccount]).Value }
    catch { return $Sid }
}

function Test-AdminOnlyAcl {
    # Same rule as the service (SecureStore.IsTrusted) and install.ps1: owner SYSTEM or Administrators,
    # every Allow ACE (explicit or inherited) for SYSTEM or Administrators only. Returns '' when ok,
    # otherwise a short reason (SIDs only, no content).
    param($Security)
    $owner = Get-SidOwner $Security
    if ($owner -ne $SidSystem -and $owner -ne $SidAdmins) { return ('owner is {0}' -f (Get-SidName $owner)) }
    $others = @()
    foreach ($r in $Security.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])) {
        if ($r.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow) { continue }
        $v = $r.IdentityReference.Value
        if ($v -ne $SidSystem -and $v -ne $SidAdmins) { $others += ('{0} ({1})' -f (Get-SidName $v), $r.FileSystemRights) }
    }
    if ($others.Count -gt 0) { return ('other Allow entries: ' + ($others -join '; ')) }
    return ''
}

function Test-IsReparse {
    param([string]$Path)
    $attr = [System.IO.File]::GetAttributes($Path)
    return (($attr -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Get-StringSha256 {
    param([string]$Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $h = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Text)) } finally { $sha.Dispose() }
    return ([BitConverter]::ToString($h) -replace '-', '')
}

function Test-ExtraAppName {
    # Same rule as PcGuard.Core ExtraAllowlist.IsValidName and install.ps1.
    param([string]$Name)
    if ($null -eq $Name -or $Name.Length -lt 5 -or $Name.Length -gt 64) { return $false }
    if (-not $Name.EndsWith('.exe', [System.StringComparison]::OrdinalIgnoreCase)) { return $false }
    return [bool]($Name -cmatch '^[A-Za-z0-9._-]+\z')
}

function Get-ProcOwnerSid {
    param([int]$ProcId)
    try {
        $p = Get-CimInstance -ClassName Win32_Process -Filter ('ProcessId={0}' -f $ProcId) -OperationTimeoutSec 30 -ErrorAction Stop
        if ($null -eq $p) { return $null }
        $r = Invoke-CimMethod -InputObject $p -MethodName GetOwnerSid -OperationTimeoutSec 30 -ErrorAction Stop
        if ($r.ReturnValue -eq 0) { return [string]$r.Sid }
    }
    catch { }
    return $null
}

function Get-ProcPath {
    param([int]$ProcId)
    try {
        $p = Get-CimInstance -ClassName Win32_Process -Filter ('ProcessId={0}' -f $ProcId) -OperationTimeoutSec 30 -ErrorAction Stop
        if ($null -ne $p) { return [string]$p.ExecutablePath }
    }
    catch { }
    return $null
}

function Get-NewInstances {
    # Processes named $Name that did not exist before the probe and started after $Since.
    param([string]$Name, [int[]]$Before, [datetime]$Since)
    $found = @()
    foreach ($p in @(Get-Process -Name $Name -ErrorAction SilentlyContinue)) {
        if ($Before -contains $p.Id) { continue }
        $st = $null
        try { $st = $p.StartTime } catch { $st = $null }
        if ($null -ne $st -and $st -lt $Since.AddSeconds(-2)) { continue }
        $found += $p
    }
    return $found
}

# Small, safe native helpers: no waits, no callbacks, nothing that can hang.
$NativeSource = @'
using System;
using System.Runtime.InteropServices;
namespace PcGuardSelfTest
{
    public static class Native
    {
        [DllImport("kernel32.dll")]
        public static extern uint WTSGetActiveConsoleSessionId();

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr OpenProcess(uint access, bool inherit, int pid);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool CloseHandle(IntPtr handle);

        [DllImport("advapi32.dll", SetLastError = true)]
        private static extern bool GetKernelObjectSecurity(IntPtr handle, uint info, byte[] sd, uint length, out uint needed);

        // Self-relative security descriptor (owner + DACL) of a process, read with READ_CONTROL only.
        public static byte[] GetProcessSecurity(int pid, out int error)
        {
            error = 0;
            IntPtr h = OpenProcess(0x00020000, false, pid);
            if (h == IntPtr.Zero) { error = Marshal.GetLastWin32Error(); return null; }
            try
            {
                uint needed = 0;
                GetKernelObjectSecurity(h, 5, null, 0, out needed);
                if (needed == 0 || needed > 65536) { error = Marshal.GetLastWin32Error(); return null; }
                byte[] buf = new byte[needed];
                if (!GetKernelObjectSecurity(h, 5, buf, needed, out needed)) { error = Marshal.GetLastWin32Error(); return null; }
                return buf;
            }
            finally { CloseHandle(h); }
        }
    }
}
'@

function Initialize-Native {
    if ($null -ne ('PcGuardSelfTest.Native' -as [type])) { return $true }
    try {
        Add-Type -TypeDefinition $NativeSource -Language CSharp -ErrorAction Stop
        return $true
    }
    catch {
        $script:NativeError = $_.Exception.Message
        return $false
    }
}

function Get-ProcessSd {
    # RawSecurityDescriptor of a process, or a string with the reason it could not be read.
    param([int]$ProcId)
    if (-not (Initialize-Native)) { return ('native helper unavailable: ' + $script:NativeError) }
    $err = 0
    $bytes = [PcGuardSelfTest.Native]::GetProcessSecurity($ProcId, [ref]$err)
    if ($null -eq $bytes) { return ('could not read the process security (Win32 error {0})' -f $err) }
    return (New-Object System.Security.AccessControl.RawSecurityDescriptor -ArgumentList $bytes, 0)
}

function Get-EvText {
    param($Ev)
    $m = $null
    try { $m = $Ev.Message } catch { $m = $null }
    if ([string]::IsNullOrEmpty($m)) {
        try { $m = (@($Ev.Properties | ForEach-Object { [string]$_.Value }) -join ' ') } catch { $m = '' }
    }
    return [string]$m
}

function Get-EvLine {
    # The logged message without the "Category:" / "EventId:" header the .NET event log logger adds.
    param([string]$Text)
    foreach ($l in ($Text -split "`r?`n")) {
        $t = $l.Trim()
        if ($t.Length -eq 0) { continue }
        if ($t -match '^(Category|EventId):') { continue }
        return $t
    }
    return ''
}

function Get-PgEvents {
    # PC Guard entries of the Application log since $Since, oldest first, as simple objects.
    param([datetime]$Since)
    $raw = @()
    try {
        $raw = @(Get-WinEvent -FilterHashtable @{ LogName = 'Application'; ProviderName = $ProviderNames; StartTime = $Since } -ErrorAction Stop)
    }
    catch {
        if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { $raw = @() }
        else {
            try {
                $raw = @(Get-WinEvent -FilterHashtable @{ LogName = 'Application'; StartTime = $Since } -ErrorAction Stop |
                        Where-Object { $ProviderNames -contains $_.ProviderName })
            }
            catch {
                if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { $raw = @() } else { throw }
            }
        }
    }
    $list = @()
    foreach ($e in @($raw | Sort-Object TimeCreated, RecordId)) {
        $text = Get-EvText $e
        $list += (New-Object PSObject -Property @{
                Time = $e.TimeCreated; Level = [int]$e.Level; Text = $text; Line = (Get-EvLine $text); RecordId = $e.RecordId
            })
    }
    return $list
}

function Find-LastEvent {
    param($Events, [string]$Needle)
    $last = $null
    foreach ($e in @($Events)) { if (Test-ContainsText $e.Text $Needle) { $last = $e } }
    return $last
}

function Get-EventsAfter {
    param($Events, $After)
    if ($null -eq $After) { return @($Events) }
    return @(@($Events) | Where-Object { $_.RecordId -ge $After.RecordId })
}

function Format-EvTime {
    param($Ev)
    if ($null -eq $Ev) { return '-' }
    return $Ev.Time.ToString('yyyy-MM-dd HH:mm:ss')
}

# ---------------------------------------------------------------------------------------------------
# start
# ---------------------------------------------------------------------------------------------------

$startedAt = Get-Date
$stamp = $startedAt.ToString('yyyyMMdd-HHmmss')
if (-not $OutFile) {
    $desk = Join-Path $env:USERPROFILE 'Desktop'
    if (-not (Test-Path -LiteralPath $desk)) { $desk = [Environment]::GetFolderPath('Desktop') }
    if ([string]::IsNullOrEmpty($desk) -or -not (Test-Path -LiteralPath $desk)) { $desk = $env:TEMP }
    $OutFile = Join-Path $desk ('pcguard-selftest-{0}.txt' -f $stamp)
}

Write-Out ('PC Guard self-test v{0}  {1}' -f $SelfTestVersion, $startedAt.ToString('yyyy-MM-dd HH:mm:ss')) -Always

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host 'This self-test must run elevated: right-click Windows PowerShell, "Run as administrator", and run it again.' -ForegroundColor Red
    exit 2
}

# ---------------------------------------------------------------------------------------------------
# environment information (report file only; no secrets)
# ---------------------------------------------------------------------------------------------------

try {
    $cv = Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' -ErrorAction Stop
    $disp = ''
    if ($cv.PSObject.Properties['DisplayVersion']) { $disp = $cv.DisplayVersion } elseif ($cv.PSObject.Properties['ReleaseId']) { $disp = $cv.ReleaseId }
    $ubr = ''
    if ($cv.PSObject.Properties['UBR']) { $ubr = '.' + $cv.UBR }
    Add-Env ('Windows         : {0} {1} build {2}{3}' -f $cv.ProductName, $disp, $cv.CurrentBuild, $ubr)
}
catch { Add-Env ('Windows         : (could not read: {0})' -f $_.Exception.Message) }
Add-Env ('PowerShell      : {0} ({1}), host process {2}.exe pid {3}' -f $PSVersionTable.PSVersion, $PSVersionTable.PSEdition, (Get-Process -Id $PID).ProcessName, $PID)
Add-Env ('User            : {0} (elevated)' -f [Security.Principal.WindowsIdentity]::GetCurrent().Name)
Add-Env ('Computer        : {0}' -f $env:COMPUTERNAME)
Add-Env ('Install folder  : {0}' -f $InstallDir)
Add-Env ('Data folder     : {0}' -f $DataDir)
Add-Env ('Parameters      : NoProbes={0} Quiet={1} LogHours={2} ExpectedBaseUrl={3} ExpectedExtraApps={4}' -f [bool]$NoProbes, [bool]$Quiet, $LogHours, $ExpectedBaseUrl, (@($ExpectedExtraApps) -join ','))

$script:ConsoleSession = $null
try {
    if (Initialize-Native) {
        $cs = [PcGuardSelfTest.Native]::WTSGetActiveConsoleSessionId()
        if ($cs -ne [uint32]::MaxValue) { $script:ConsoleSession = [int]$cs }
    }
}
catch { $script:ConsoleSession = $null }
$sessionNote = ''
if ($null -eq $script:ConsoleSession) {
    # native helper unavailable (for example Add-Type blocked): the explorer session, if there is only one
    $exSessions = @(Get-Process -Name explorer -ErrorAction SilentlyContinue | ForEach-Object { $_.SessionId } | Sort-Object -Unique)
    if ($exSessions.Count -eq 1) { $script:ConsoleSession = [int]$exSessions[0]; $sessionNote = ' (guessed from explorer.exe: ' + $script:NativeError + ')' }
}
$script:MySession = (Get-Process -Id $PID).SessionId
Add-Env ('Sessions        : console {0}, this script {1}{2}' -f $script:ConsoleSession, $script:MySession, $sessionNote)
Add-Env ''

# ===================================================================================================
# A. Install facts
# ===================================================================================================

$script:Svc = $null
$script:SvcRunning = $false

Invoke-Check 'A01' 'Service PcGuard is registered (VM 8, 70)' {
    $s = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($null -eq $s) { return (Fail 'no service named PcGuard: PC Guard is not installed (or was removed by uninstall/Cleanup)') }
    if ($s.Name -cne $ServiceName) { return (Fail ('service name is {0}, expected PcGuard' -f $s.Name)) }
    $script:Svc = $s
    return (Pass ('display name "{0}"' -f $s.DisplayName))
}

Invoke-Check 'A02' 'Service runs as LocalSystem (VM 8)' {
    if ($null -eq $script:Svc) { return (Skip 'service not registered') }
    $obj = (Get-ItemProperty -LiteralPath $ServiceKey -Name ObjectName).ObjectName
    if ($obj -eq 'LocalSystem') { return (Pass '') }
    return (Fail ('ObjectName is {0}, expected LocalSystem' -f $obj))
}

Invoke-Check 'A03' 'Service start type is Automatic (VM 8, 70)' {
    if ($null -eq $script:Svc) { return (Skip 'service not registered') }
    $p = Get-ItemProperty -LiteralPath $ServiceKey
    $start = [int]$p.Start
    $delayed = $false
    if ($p.PSObject.Properties['DelayedAutostart']) { $delayed = ([int]$p.DelayedAutostart -eq 1) }
    switch ($start) {
        2 {
            if ($delayed) { return (Pass 'Automatic (delayed start; install.ps1 sets plain Automatic)') }
            return (Pass 'Automatic')
        }
        4 { return (Fail 'DISABLED: PC Guard was switched off, by a recovery code release (event log: "Recovery code accepted"), by Cleanup or by an administrator. This PC is NOT protected; run Setup-PcGuard.exe install again (with a NEW recovery code)') }
        3 { return (Fail 'Manual (demand start): it does not start at boot; expected Automatic. Run install.ps1 again or sc.exe config PcGuard start= auto') }
        default { return (Fail ('start type {0}, expected 2 (Automatic)' -f $start)) }
    }
}

Invoke-Check 'A04' 'Service is Running (VM 8, 70)' {
    if ($null -eq $script:Svc) { return (Skip 'service not registered') }
    $s = Get-Service -Name $ServiceName
    $script:Svc = $s
    if ($s.Status -eq 'Running') { $script:SvcRunning = $true; return (Pass '') }
    if ($s.Status -eq 'Stopped') {
        return (Fail 'Stopped: an administrator stopped it (Stop-Service), or a recovery code release stopped and disabled it (see A03 and the event log). Start-Service PcGuard if it was not a release')
    }
    return (Fail ('state {0}, expected Running' -f $s.Status))
}

Invoke-Check 'A05' 'Binary path is quoted and points to the install folder (VM 8, 70)' {
    if ($null -eq $script:Svc) { return (Skip 'service not registered') }
    $expected = '"' + (Join-Path $InstallDir 'PcGuard.Service.exe') + '"'
    $img = [string](Get-ItemProperty -LiteralPath $ServiceKey -Name ImagePath).ImagePath
    $qc = Invoke-Native 'sc.exe' @('qc', $ServiceName)
    $bin = $null
    foreach ($l in $qc) { if ($l -match '^\s*BINARY_PATH_NAME\s*:\s*(.*)$') { $bin = $Matches[1].Trim() } }
    $problems = @()
    if (-not ($img.StartsWith('"') -and $img.EndsWith('"'))) { $problems += ('registry ImagePath is NOT quoted: {0}' -f $img) }
    elseif ($img -ne $expected) { $problems += ('registry ImagePath is {0}, expected {1}' -f $img, $expected) }
    if ($null -eq $bin) { $problems += 'sc.exe qc printed no BINARY_PATH_NAME line' }
    elseif (-not $bin.StartsWith('"')) { $problems += ('sc.exe qc BINARY_PATH_NAME is not quoted: {0}' -f $bin) }
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    return (Pass $img)
}

Invoke-Check 'A06' 'Failure actions: 3 restarts after 5000 ms, reset 0 (VM 3, 70)' {
    if ($null -eq $script:Svc) { return (Skip 'service not registered') }
    $out = Invoke-Native 'sc.exe' @('qfailure', $ServiceName)
    $restarts = @($out | Where-Object { $_ -match 'RESTART\s*--\s*Delay\s*=\s*5000\b' }).Count
    $resetZero = @($out | Where-Object { $_ -match '^\s*RESET_PERIOD.*:\s*0\s*$' }).Count -gt 0
    $scOk = ($restarts -eq 3 -and $resetZero)
    # registry form: SERVICE_FAILURE_ACTIONS (reset, rebootMsg, command, cActions, actions) + cActions x (type, delay)
    $regOk = $false
    $regText = 'no FailureActions value'
    $p = Get-ItemProperty -LiteralPath $ServiceKey
    if ($p.PSObject.Properties['FailureActions']) {
        $fa = [byte[]]$p.FailureActions
        if ($fa.Length -ge 20) {
            $reset = [BitConverter]::ToUInt32($fa, 0)
            $n = [BitConverter]::ToUInt32($fa, 12)
            $acts = @()
            for ($i = 0; $i -lt $n -and (28 + 8 * $i) -le $fa.Length; $i++) {
                $acts += ('{0}/{1}' -f [BitConverter]::ToUInt32($fa, 20 + 8 * $i), [BitConverter]::ToUInt32($fa, 24 + 8 * $i))
            }
            $regText = ('reset {0}, actions {1}' -f $reset, ($acts -join ' '))
            $regOk = ($reset -eq 0 -and $n -eq 3 -and ($acts -join ' ') -eq '1/5000 1/5000 1/5000')
        }
    }
    if ($scOk -or $regOk) { return (Pass ('sc.exe: {0} restarts/5000 ms, reset 0: {1}; registry: {2}' -f $restarts, $resetZero, $regText)) }
    return (Fail ('sc.exe qfailure: {0} RESTART/5000 lines, reset 0: {1}; registry: {2} (expected reset 0, 1/5000 x3)' -f $restarts, $resetZero, $regText))
}

Invoke-Check 'A07' 'Failure flag is set (restart also on non-crash failures) (VM 70)' {
    if ($null -eq $script:Svc) { return (Skip 'service not registered') }
    $out = Invoke-Native 'sc.exe' @('qfailureflag', $ServiceName)
    $scOk = @($out | Where-Object { $_ -match 'FAILURE_ACTIONS_ON_NONCRASH_FAILURES\s*:\s*TRUE' }).Count -gt 0
    $p = Get-ItemProperty -LiteralPath $ServiceKey
    $reg = $null
    if ($p.PSObject.Properties['FailureActionsOnNonCrashFailures']) { $reg = [int]$p.FailureActionsOnNonCrashFailures }
    if ($scOk -or $reg -eq 1) { return (Pass '') }
    return (Fail ('sc.exe qfailureflag does not say TRUE; registry FailureActionsOnNonCrashFailures = {0}' -f $reg))
}

Invoke-Check 'A08' 'Safe Mode keys Minimal\PcGuard and Network\PcGuard = Service (VM 70)' {
    $bad = @()
    foreach ($k in $SafeBootKeys) {
        if (-not (Test-Path -LiteralPath $k)) { $bad += ('{0} missing' -f $k); continue }
        $item = Get-Item -LiteralPath $k
        $v = $item.GetValue('')
        $kind = $null
        try { $kind = $item.GetValueKind('') } catch { $kind = $null }
        if ([string]$v -ne 'Service' -or [string]$kind -ne 'String') { $bad += ('{0} (Default) = "{1}" ({2}), expected "Service" (REG_SZ)' -f $k, $v, $kind) }
    }
    if ($bad.Count -gt 0) { return (Fail ($bad -join '; ')) }
    return (Pass '')
}

$script:InstallItems = @()
Invoke-Check 'A09' 'Install folder: inheritance removed, no write access for Users/Authenticated Users/Everyone/INTERACTIVE (VM 48, 71)' {
    if (-not (Test-Path -LiteralPath $InstallDir -PathType Container)) { return (Fail ('install folder not found: {0}' -f $InstallDir)) }
    if (Test-IsReparse $InstallDir) { return (Fail 'the install folder is a link/junction') }
    $rootAcl = Get-Acl -LiteralPath $InstallDir
    $problems = @()
    if (-not $rootAcl.AreAccessRulesProtected) { $problems += 'inheritance is NOT removed on the install folder' }
    # write-type rights, including generic write/all as shown on inherit-only entries
    $bad = [int64]([System.Security.AccessControl.FileSystemRights]'WriteData, AppendData, WriteExtendedAttributes, WriteAttributes, Delete, DeleteSubdirectoriesAndFiles, ChangePermissions, TakeOwnership')
    $bad = $bad -bor 0x10000000 -bor 0x40000000
    $items = @(Get-Item -LiteralPath $InstallDir -Force) + @(Get-ChildItem -LiteralPath $InstallDir -Recurse -Force)
    $script:InstallItems = $items
    $offenders = 0
    foreach ($it in $items) {
        if (($it.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            $offenders++
            if ($problems.Count -lt 6) { $problems += ('link/junction inside the install folder: {0}' -f $it.FullName) }
            continue
        }
        $acl = Get-Acl -LiteralPath $it.FullName
        foreach ($r in $acl.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])) {
            if ($r.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow) { continue }
            if ($BroadSids -notcontains $r.IdentityReference.Value) { continue }
            if ((([int64][int]$r.FileSystemRights) -band $bad) -ne 0) {
                $offenders++
                if ($problems.Count -lt 6) { $problems += ('{0}: {1} has {2}' -f $it.FullName, (Get-SidName $r.IdentityReference.Value), $r.FileSystemRights) }
            }
        }
    }
    if ($problems.Count -gt 0) { return (Fail (('{0} problem(s): ' -f [Math]::Max($offenders, $problems.Count)) + ($problems -join '; '))) }
    return (Pass ('{0} entries checked; Users read/execute only' -f $items.Count))
}

Invoke-Check 'A10' 'Every exe/dll in the install folder is owned by SYSTEM, Administrators or TrustedInstaller' {
    if (-not (Test-Path -LiteralPath $InstallDir -PathType Container)) { return (Skip 'install folder not found') }
    $files = @(Get-ChildItem -LiteralPath $InstallDir -Recurse -Force -File | Where-Object { $_.Extension -eq '.exe' -or $_.Extension -eq '.dll' })
    if ($files.Count -eq 0) { return (Fail 'no exe/dll files found') }
    $bad = @()
    foreach ($f in $files) {
        $o = Get-SidOwner (Get-Acl -LiteralPath $f.FullName)
        if ($o -ne $SidSystem -and $o -ne $SidAdmins -and $o -ne $SidTrustedInstaller) {
            $bad += ('{0} (owner {1})' -f $f.Name, (Get-SidName $o))
        }
    }
    if ($bad.Count -gt 0) {
        $shown = @($bad | Select-Object -First 5)
        return (Fail ('{0} file(s) with another owner (the owner can change the permissions): {1}' -f $bad.Count, ($shown -join '; ')))
    }
    return (Pass ('{0} files' -f $files.Count))
}

Invoke-Check 'A11' 'Shell runtimeconfig disables startup hooks (VM 47)' {
    foreach ($f in @('PcGuard.Service.exe', 'PcGuard.Shell.exe', 'appsettings.json')) {
        if (-not (Test-Path -LiteralPath (Join-Path $InstallDir $f))) { return (Fail ('{0} is missing in the install folder' -f $f)) }
    }
    $rc = Join-Path $InstallDir 'PcGuard.Shell.runtimeconfig.json'
    if (-not (Test-Path -LiteralPath $rc)) { return (Fail 'PcGuard.Shell.runtimeconfig.json is missing') }
    $j = Get-Content -LiteralPath $rc -Raw -Encoding UTF8 | ConvertFrom-Json
    $val = $null
    if ($j.PSObject.Properties['runtimeOptions'] -and $j.runtimeOptions.PSObject.Properties['configProperties']) {
        $cp = $j.runtimeOptions.configProperties
        if ($cp.PSObject.Properties['System.StartupHookProvider.IsSupported']) { $val = $cp.'System.StartupHookProvider.IsSupported' }
    }
    if ($val -eq $false) { return (Pass 'System.StartupHookProvider.IsSupported = false') }
    return (Fail ('System.StartupHookProvider.IsSupported is {0}, expected false' -f $val))
}

$script:Settings = $null
$script:SettingsRaw = $null
$script:BaseUrl = $null
$script:ExtraApps = @()
Invoke-Check 'A12' 'appsettings.json parses and has a valid Backend:BaseUrl (VM 70)' {
    $path = Join-Path $InstallDir 'appsettings.json'
    if (-not (Test-Path -LiteralPath $path)) { return (Fail 'appsettings.json not found in the install folder') }
    $script:SettingsRaw = [System.IO.File]::ReadAllText($path)
    $script:Settings = $script:SettingsRaw | ConvertFrom-Json
    if (-not ($script:Settings.PSObject.Properties['Backend'] -and $script:Settings.Backend.PSObject.Properties['BaseUrl'])) {
        return (Fail 'Backend:BaseUrl is missing')
    }
    $url = [string]$script:Settings.Backend.BaseUrl
    $script:BaseUrl = $url
    $u = $null
    if (-not [Uri]::TryCreate($url, [UriKind]::Absolute, [ref]$u) -or ($u.Scheme -ne 'https' -and $u.Scheme -ne 'http')) {
        return (Fail ('Backend:BaseUrl is not an absolute http(s) URL: {0}' -f $url))
    }
    if (Test-ContainsText $u.Host 'CHANGE-ME') { return (Fail 'Backend:BaseUrl is still the CHANGE-ME placeholder (install.ps1 did not write it)') }
    if ($ExpectedBaseUrl -and ($url.TrimEnd('/') -ne $ExpectedBaseUrl.TrimEnd('/'))) {
        return (Fail ('Backend:BaseUrl is {0}, expected {1}' -f $url, $ExpectedBaseUrl))
    }
    $note = ''
    if (-not $u.AbsolutePath.TrimEnd('/').EndsWith('/api/v1')) { $note = ' (note: does not end in /api/v1)' }
    return (Pass ($url + $note))
}

Invoke-Check 'A13' 'Allowlist:ExtraApps is a valid JSON array of exe names (VM 138, 140)' {
    if ($null -eq $script:Settings) { return (Skip 'appsettings.json could not be read') }
    $s = $script:Settings
    if (-not ($s.PSObject.Properties['Allowlist'] -and $s.Allowlist.PSObject.Properties['ExtraApps'])) {
        if ($ExpectedExtraApps) { return (Fail 'Allowlist:ExtraApps is absent but -ExpectedExtraApps was given') }
        return (Pass 'absent (no extra apps)')
    }
    if ($script:SettingsRaw -notmatch '"ExtraApps"\s*:\s*\[') { return (Fail 'Allowlist:ExtraApps is not a JSON array (Windows PowerShell 5.1 serialisation problem?)') }
    $names = @($s.Allowlist.ExtraApps | Where-Object { $null -ne $_ } | ForEach-Object { [string]$_ })
    $script:ExtraApps = $names
    $invalid = @($names | Where-Object { -not (Test-ExtraAppName $_) })
    $problems = @()
    if ($invalid.Count -gt 0) { $problems += ('invalid names (ignored by the service): ' + ($invalid -join ', ')) }
    if ($names.Count -gt $MaxExtraApps) { $problems += ('{0} entries, the service uses only the first {1}' -f $names.Count, $MaxExtraApps) }
    if ($ExpectedExtraApps) {
        $exp = @()
        foreach ($item in @($ExpectedExtraApps)) { foreach ($piece in ([string]$item).Split(',')) { if ($piece.Trim()) { $exp += $piece.Trim().ToLowerInvariant() } } }
        $have = @($names | ForEach-Object { $_.ToLowerInvariant() })
        # compare as sorted, joined text (Compare-Object refuses empty arrays)
        $expText = (@($exp | Sort-Object -Unique) -join ',')
        $haveText = (@($have | Sort-Object -Unique) -join ',')
        if ($expText -ne $haveText) { $problems += ('ExtraApps [{0}] differ from the expected [{1}]' -f ($have -join ', '), ($exp -join ', ')) }
    }
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    if ($names.Count -eq 0) { return (Pass '[] (no extra apps)') }
    return (Pass ('[' + ($names -join ', ') + '] (these bypass the lock on this PC: test/admin PCs only)'))
}

Invoke-Check 'A14' 'Data folder %ProgramData%\PcGuard is SYSTEM/Administrators-only, inheritance removed (VM 22)' {
    if (-not (Test-Path -LiteralPath $DataDir -PathType Container)) { return (Fail ('{0} does not exist (the service creates it at start)' -f $DataDir)) }
    if (Test-IsReparse $DataDir) { return (Fail 'the data folder is a link/junction') }
    $acl = Get-Acl -LiteralPath $DataDir
    $why = Test-AdminOnlyAcl $acl
    $problems = @()
    if ($why) { $problems += $why }
    if (-not $acl.AreAccessRulesProtected) { $problems += 'inheritance is NOT removed' }
    $quarantined = @(Get-ChildItem -LiteralPath ([Environment]::GetFolderPath('CommonApplicationData')) -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'PcGuard.untrusted-*' })
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    $note = ''
    if ($quarantined.Count -gt 0) { $note = (' (note: {0} quarantined PcGuard.untrusted-* folder(s) exist: an untrusted data folder was moved aside earlier)' -f $quarantined.Count) }
    return (Pass ('owner ' + (Get-SidName (Get-SidOwner $acl)) + $note))
}

$script:MachineKeyOk = $false
Invoke-Check 'A15' 'machine.key exists and holds a GUID (VM 22)' {
    $mk = Join-Path $DataDir 'machine.key'
    if (-not (Test-Path -LiteralPath $mk -PathType Leaf)) { return (Fail 'machine.key not found (the service writes it at first start; fail-closed mode writes nothing)') }
    $fi = New-Object System.IO.FileInfo($mk)
    if ($fi.Length -gt 256) { return (Fail ('machine.key is {0} bytes, expected a GUID' -f $fi.Length)) }
    $text = [System.IO.File]::ReadAllText($mk).Trim()
    $g = [Guid]::Empty
    if (-not [Guid]::TryParse($text, [ref]$g)) { $text = $null; return (Fail 'machine.key is not a GUID (the service would generate a new key)') }
    # kept only in memory for the privacy scan (C08); never printed
    $script:Needles.Add($g.ToString('D')); $script:NeedleKinds.Add('machine key')
    $text = $null
    $script:MachineKeyOk = $true
    return (Pass 'GUID ok')
}

Invoke-Check 'A16' 'No Run key, scheduled task or Startup shortcut starts the shell (VM 72)' {
    $hits = @()
    $runKeys = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
    )
    # also the console user's own Run keys (hive is loaded while signed in)
    $consoleSid = $null
    if ($null -ne $script:ConsoleSession) {
        $ex = @(Get-Process -Name explorer -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $script:ConsoleSession }) | Select-Object -First 1
        if ($ex) { $consoleSid = Get-ProcOwnerSid $ex.Id }
    }
    $script:ConsoleUserSid = $consoleSid
    if ($consoleSid) {
        $runKeys += ('Registry::HKEY_USERS\{0}\Software\Microsoft\Windows\CurrentVersion\Run' -f $consoleSid)
        $runKeys += ('Registry::HKEY_USERS\{0}\Software\Microsoft\Windows\CurrentVersion\RunOnce' -f $consoleSid)
    }
    foreach ($k in $runKeys) {
        if (-not (Test-Path -LiteralPath $k)) { continue }
        $item = Get-Item -LiteralPath $k
        foreach ($n in $item.GetValueNames()) {
            $v = [string]$item.GetValue($n)
            if ((Test-ContainsText $v 'PcGuard') -or (Test-ContainsText $n 'PcGuard')) { $hits += ('Run value {0} in {1}' -f $n, $k) }
        }
    }
    try {
        foreach ($t in @(Get-ScheduledTask -ErrorAction Stop)) {
            $match = Test-ContainsText $t.TaskName 'PcGuard'
            foreach ($a in @($t.Actions)) {
                if ($a.PSObject.Properties['Execute'] -and (Test-ContainsText ([string]$a.Execute) 'PcGuard')) { $match = $true }
                if ($a.PSObject.Properties['Arguments'] -and (Test-ContainsText ([string]$a.Arguments) 'PcGuard.Shell')) { $match = $true }
            }
            if ($match) { $hits += ('scheduled task {0}{1}' -f $t.TaskPath, $t.TaskName) }
        }
    }
    catch { $hits += ('(scheduled tasks could not be listed: {0})' -f $_.Exception.Message) }
    $folders = @([Environment]::GetFolderPath('CommonStartup'), [Environment]::GetFolderPath('Startup'))
    if ($consoleSid) {
        try {
            $prof = Get-CimInstance -ClassName Win32_UserProfile -Filter ("SID='{0}'" -f $consoleSid) -OperationTimeoutSec 30 -ErrorAction Stop
            if ($prof -and $prof.LocalPath) { $folders += (Join-Path $prof.LocalPath 'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup') }
        }
        catch { }
    }
    $wsh = $null
    foreach ($f in ($folders | Sort-Object -Unique)) {
        if ([string]::IsNullOrEmpty($f) -or -not (Test-Path -LiteralPath $f)) { continue }
        foreach ($file in @(Get-ChildItem -LiteralPath $f -Force -File -ErrorAction SilentlyContinue)) {
            $target = ''
            if ($file.Extension -eq '.lnk') {
                try {
                    if ($null -eq $wsh) { $wsh = New-Object -ComObject WScript.Shell }
                    $target = [string]$wsh.CreateShortcut($file.FullName).TargetPath
                }
                catch { $target = '' }
            }
            if ((Test-ContainsText $file.Name 'PcGuard') -or (Test-ContainsText $target 'PcGuard')) { $hits += ('Startup entry {0}' -f $file.FullName) }
        }
    }
    if ($hits.Count -gt 0) { return (Fail ($hits -join '; ')) }
    return (Pass ('{0} Run keys, scheduled tasks and {1} Startup folders checked' -f $runKeys.Count, @($folders | Sort-Object -Unique).Count))
}

Invoke-Check 'A17' 'rules.json does not contain the extra apps (VM 138)' {
    if (@($script:ExtraApps).Count -eq 0) { return (Skip 'no extra apps configured') }
    $rules = Join-Path $DataDir 'rules.json'
    if (-not (Test-Path -LiteralPath $rules -PathType Leaf)) { return (Skip 'no rules.json yet (no rules were ever received from the backend)') }
    $text = [System.IO.File]::ReadAllText($rules)
    $found = @($script:ExtraApps | Where-Object { Test-ContainsText $text $_ })
    if ($found.Count -gt 0) { return (Fail ('rules.json contains: ' + ($found -join ', '))) }
    return (Pass '')
}

# ===================================================================================================
# F. Recovery code surface (static only: never a release, never the code)
# ===================================================================================================

Invoke-Check 'F01' 'recovery.hash: absent, or well formed and SYSTEM/Administrators-only (VM 145)' {
    $path = Join-Path $DataDir 'recovery.hash'
    if (-not (Test-Path -LiteralPath $path)) { return (Pass 'absent (no recovery code set, or it was used)') }
    if (Test-Path -LiteralPath $path -PathType Container) { return (Fail 'recovery.hash is a folder') }
    if (Test-IsReparse $path) { return (Fail 'recovery.hash is a link (the service does not trust it)') }
    $fi = New-Object System.IO.FileInfo($path)
    $len = $fi.Length
    $why = Test-AdminOnlyAcl (Get-Acl -LiteralPath $path)
    $problems = @()
    if ($why) { $problems += ('ACL: ' + $why) }
    if ($len -gt $MaxHashFileBytes) { $problems += ('{0} bytes, more than {1}' -f $len, $MaxHashFileBytes) }
    if ($len -le $MaxHashFileBytes) {
        # Value handled only with .NET calls (no cmdlet or function parameter ever carries it: module
        # logging); never printed. Same rule as RecoveryCode.IsWellFormedStored / install.ps1.
        $bytes = [System.IO.File]::ReadAllBytes($path)
        $text = [System.Text.Encoding]::ASCII.GetString($bytes).Trim()
        [Array]::Clear($bytes, 0, $bytes.Length)
        $m = [regex]::Match($text, '^pbkdf2-sha256\$([1-9][0-9]{0,6})\$([A-Za-z0-9+/=]{24})\$([A-Za-z0-9+/=]{44})\z')
        $ok = ($text.Length -le 128 -and $m.Success)
        if ($ok) {
            $iter = [int]$m.Groups[1].Value
            if ($iter -lt 310000 -or $iter -gt 5000000) { $ok = $false }
        }
        if ($ok) {
            $parts = @($m.Groups[2].Value, $m.Groups[3].Value)
            $sizes = @(16, 32)
            for ($i = 0; $i -lt 2; $i++) {
                $raw = $null
                try { $raw = [Convert]::FromBase64String($parts[$i]) } catch { $raw = $null }
                if ($null -eq $raw -or $raw.Length -ne $sizes[$i] -or [Convert]::ToBase64String($raw) -cne $parts[$i]) { $ok = $false }
                if ($ok) { $script:Needles.Add($parts[$i]); $script:NeedleKinds.Add('recovery hash') }
            }
            $parts = $null
        }
        $text = $null
        $m = $null
        if (-not $ok) { $problems += 'content is not in the stored hash format pbkdf2-sha256$<310000-5000000>$<16-byte salt>$<32-byte hash> (the service answers "not configured")' }
    }
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    return (Pass ('present, format ok, {0} bytes' -f $len))
}

Invoke-Check 'F02' 'recovery.attempts: absent, or SYSTEM/Administrators-only and well formed (VM 160, 161)' {
    $path = Join-Path $DataDir 'recovery.attempts'
    if (-not (Test-Path -LiteralPath $path)) { return (Pass 'absent (no wrong recovery code since the last reset)') }
    if (Test-Path -LiteralPath $path -PathType Container) { return (Fail 'recovery.attempts is a folder: the service locks recovery attempts out for 24 hours') }
    if (Test-IsReparse $path) { return (Fail 'recovery.attempts is a link: the service locks recovery attempts out for 24 hours') }
    $fi = New-Object System.IO.FileInfo($path)
    if ($fi.Length -gt $MaxAttemptsFileBytes) { return (Fail ('{0} bytes, more than {1}: the service locks recovery attempts out for 24 hours' -f $fi.Length, $MaxAttemptsFileBytes)) }
    $why = Test-AdminOnlyAcl (Get-Acl -LiteralPath $path)
    if ($why) { return (Fail ('ACL: ' + $why + ' (untrusted: the service locks recovery attempts out for 24 hours)')) }
    # The counter is not a secret (no code, no hash): v1;failures=N;lockouts=N;until=UNIXSECONDS
    $text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::ASCII)
    $m = [regex]::Match($text, '^v1;failures=([0-9]{1,9});lockouts=([0-9]{1,9});until=([0-9]{1,12})\z')
    if (-not $m.Success) { return (Fail 'content is not v1;failures=N;lockouts=N;until=S (corrupt: the service locks recovery attempts out for 24 hours)') }
    $until = [int64]$m.Groups[3].Value
    $state = 'no lockout'
    if ($until -gt 0) {
        $end = [DateTimeOffset]::FromUnixTimeSeconds($until).ToLocalTime()
        if ($end -gt [DateTimeOffset]::Now) { $state = ('LOCKED OUT until {0} (an administrator can delete recovery.attempts and restart the service)' -f $end.ToString('yyyy-MM-dd HH:mm')) }
        else { $state = 'lockout over' }
    }
    return (Pass ('failures {0}, lockouts {1}, {2}' -f $m.Groups[1].Value, $m.Groups[2].Value, $state))
}

# ===================================================================================================
# E. Config sanity
# ===================================================================================================

Invoke-Check 'E01' 'Backend:BaseUrl scheme is https (http only for localhost) (VM 69, 135)' {
    if (-not $script:BaseUrl) { return (Skip 'Backend:BaseUrl could not be read (see A12)') }
    $u = $null
    if (-not [Uri]::TryCreate($script:BaseUrl, [UriKind]::Absolute, [ref]$u)) { return (Fail 'not an absolute URL') }
    $isLocal = ($u.Host -eq 'localhost' -or $u.Host -eq '127.0.0.1' -or $u.Host -eq '[::1]' -or $u.Host -eq '::1')
    if ($u.Scheme -eq 'https') { return (Pass 'https') }
    if ($u.Scheme -eq 'http' -and $isLocal) {
        return (Pass 'WARNING: plain http to localhost (dummy/test backend): passwords and tokens travel unencrypted and maintenance codes are refused; never on a student PC')
    }
    return (Fail ('{0}://{1}: plain http to a remote host (install.ps1 refuses this; the file was edited by hand)' -f $u.Scheme, $u.Host))
}

Invoke-Check 'E02' 'No secrets in appsettings.json' {
    if ($null -eq $script:Settings) { return (Skip 'appsettings.json could not be read') }
    $hits = @()
    $stack = New-Object System.Collections.Stack
    $stack.Push(@('', $script:Settings))
    $n = 0
    while ($stack.Count -gt 0 -and $n -lt 5000) {
        $n++
        $pair = $stack.Pop()
        $path = [string]$pair[0]
        $node = $pair[1]
        if ($null -eq $node) { continue }
        if ($node -is [System.Management.Automation.PSCustomObject]) {
            foreach ($p in $node.PSObject.Properties) {
                $child = $path + ':' + $p.Name
                if ($p.Name -match '(?i)pass|secret|token|api.?key|credential|private|pbkdf2|recovery|machine.?key|connectionstring|cookie|bearer') { $hits += ('key ' + $child.TrimStart(':')) }
                $stack.Push(@($child, $p.Value))
            }
        }
        elseif ($node -is [System.Array]) {
            for ($i = 0; $i -lt $node.Length; $i++) { $stack.Push(@(('{0}[{1}]' -f $path, $i), $node[$i])) }
        }
        else {
            $v = [string]$node
            if ($v -match '(?i)pbkdf2|bearer\s|-----BEGIN|^[A-Za-z0-9+/=_-]{40,}$') { $hits += ('value of ' + $path.TrimStart(':')) }
            if ($v -match '^https?://[^/]*@') { $hits += ('user info in the URL ' + $path.TrimStart(':')) }
        }
    }
    # the machine key must not have been copied into the settings either (literal search, never printed)
    for ($i = 0; $i -lt $script:Needles.Count; $i++) {
        if ($script:SettingsRaw.IndexOf($script:Needles[$i], [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $hits += ('the {0} value' -f $script:NeedleKinds[$i]) }
    }
    $top = @($script:Settings.PSObject.Properties | ForEach-Object { $_.Name })
    $unknown = @($top | Where-Object { @('Backend', 'Allowlist', 'Logging') -notcontains $_ })
    if ($hits.Count -gt 0) { return (Fail ('secret-like entries (names only): ' + (($hits | Sort-Object -Unique) -join ', '))) }
    $note = ''
    if ($unknown.Count -gt 0) { $note = ('note: unexpected top-level keys ' + ($unknown -join ', ')) }
    return (Pass $note)
}

Invoke-Check 'E03' 'machine.key is not readable by standard users (VM 22)' {
    $mk = Join-Path $DataDir 'machine.key'
    if (-not (Test-Path -LiteralPath $mk -PathType Leaf)) { return (Skip 'machine.key not found (see A15)') }
    $why = Test-AdminOnlyAcl (Get-Acl -LiteralPath $mk)
    if ($why) { return (Fail $why) }
    return (Pass 'SYSTEM/Administrators only')
}

# ===================================================================================================
# B. Process facts
# ===================================================================================================

$script:ServicePid = $null
$script:ShellPid = $null
$script:ShellUserSid = $null

Invoke-Check 'B01' 'PcGuard.Service.exe runs as SYSTEM in session 0 from the install folder (VM 8)' {
    $procs = @(Get-Process -Name 'PcGuard.Service' -ErrorAction SilentlyContinue)
    if ($procs.Count -eq 0) { return (Fail 'no PcGuard.Service.exe process (service not running)') }
    if ($procs.Count -gt 1) { return (Fail ('{0} PcGuard.Service.exe processes, expected 1' -f $procs.Count)) }
    $p = $procs[0]
    $script:ServicePid = $p.Id
    $problems = @()
    if ($p.SessionId -ne 0) { $problems += ('session {0}, expected 0' -f $p.SessionId) }
    $sid = Get-ProcOwnerSid $p.Id
    if ($sid -ne $SidSystem) { $problems += ('owner {0}, expected SYSTEM' -f $sid) }
    $path = Get-ProcPath $p.Id
    $exp = Join-Path $InstallDir 'PcGuard.Service.exe'
    if ($path -and $path -ne $exp) { $problems += ('image {0}, expected {1}' -f $path, $exp) }
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    return (Pass ('pid {0}' -f $p.Id))
}

Invoke-Check 'B02' 'PcGuard.Shell.exe runs in the console session as the console user (VM 10, 86)' {
    if ($null -eq $script:ConsoleSession) { return (Skip 'no active console session (or it could not be read)') }
    $explorer = @(Get-Process -Name explorer -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $script:ConsoleSession })
    $shells = @(Get-Process -Name 'PcGuard.Shell' -ErrorAction SilentlyContinue)
    $inConsole = @($shells | Where-Object { $_.SessionId -eq $script:ConsoleSession })
    if ($inConsole.Count -eq 0) {
        if ($explorer.Count -eq 0) { return (Skip ('nobody is signed in to Windows in console session {0} (logon screen): the service launches no shell there (VM 9)' -f $script:ConsoleSession)) }
        return (Fail ('no PcGuard.Shell.exe in console session {0} (shells elsewhere: {1})' -f $script:ConsoleSession, $shells.Count))
    }
    $problems = @()
    if ($inConsole.Count -gt 1) { $problems += ('{0} shells in the console session, expected 1' -f $inConsole.Count) }
    $s = $inConsole[0]
    $script:ShellPid = $s.Id
    $sid = Get-ProcOwnerSid $s.Id
    $script:ShellUserSid = $sid
    if ($explorer.Count -gt 0) {
        $exSid = Get-ProcOwnerSid $explorer[0].Id
        if ($sid -and $exSid -and $sid -ne $exSid) { $problems += ('shell runs as {0}, the console desktop (explorer) as {1}' -f (Get-SidName $sid), (Get-SidName $exSid)) }
    }
    $path = Get-ProcPath $s.Id
    $exp = Join-Path $InstallDir 'PcGuard.Shell.exe'
    if ($path -and $path -ne $exp) { $problems += ('image {0}, expected {1}' -f $path, $exp) }
    $others = @($shells | Where-Object { $_.SessionId -ne $script:ConsoleSession })
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    $note = ''
    if ($others.Count -gt 0) { $note = (' (note: {0} shell(s) in other sessions, e.g. fast user switching)' -f $others.Count) }
    return (Pass ('pid {0}, user {1}{2}' -f $s.Id, (Get-SidName $sid), $note))
}

Invoke-Check 'B03' 'Named pipe \\.\pipe\PcGuard.Pipe exists (not connected to)' {
    if (-not $script:SvcRunning) { return (Skip 'service not running') }
    $pipes = $null
    try { $pipes = [System.IO.Directory]::GetFiles('\\.\pipe\') } catch { return (Skip ('the pipe list could not be read: {0}' -f $_.Exception.Message)) }
    foreach ($p in $pipes) { if ([System.IO.Path]::GetFileName($p) -eq $PipeName) { return (Pass '') } }
    return (Fail 'the service is running but its pipe does not exist (event log: "Pipe server error" or pipe squatting, VM 34)')
}

Invoke-Check 'B04' 'Shell process DACL denies terminate/suspend/inject to the user (VM 39, 41)' {
    if ($null -eq $script:ShellPid) { return (Skip 'no shell in the console session (see B02)') }
    if (-not $script:ShellUserSid) { return (Skip 'the shell user could not be read') }
    $sd = Get-ProcessSd $script:ShellPid
    if ($sd -is [string]) { return (Skip $sd) }
    $problems = @()
    $owner = ''
    if ($null -ne $sd.Owner) { $owner = $sd.Owner.Value }
    if ($owner -ne $SidAdmins) { $problems += ('process owner is {0}, expected Administrators (the user could rewrite the DACL)' -f (Get-SidName $owner)) }
    $aces = @()
    if ($null -ne $sd.DiscretionaryAcl) { $aces = @($sd.DiscretionaryAcl) }
    if ($aces.Count -eq 0) { return (Fail 'the shell process has no DACL entries (launched unprotected? event log "Shell process protection skipped")') }
    $denyMask = 0x0001 -bor 0x0002 -bor 0x0008 -bor 0x0020 -bor 0x0800   # ShellSecurity.ProcessDeniedRights
    $first = $aces[0]
    $firstOk = ($first -is [System.Security.AccessControl.CommonAce] -and
        $first.AceQualifier -eq [System.Security.AccessControl.AceQualifier]::AccessDenied -and
        $first.SecurityIdentifier.Value -eq $script:ShellUserSid -and
        (($first.AccessMask -band $denyMask) -eq $denyMask))
    if (-not $firstOk) { $problems += 'the first entry is not a deny of terminate/suspend/inject (0x82B) for the shell user' }
    $grant = 0x0001 -bor 0x0800 -bor 0x10000000 -bor 0x40000000 -bor 0x00040000   # terminate, suspend, GA, GW, WRITE_DAC
    foreach ($a in $aces) {
        if (-not ($a -is [System.Security.AccessControl.CommonAce])) { continue }
        if ($a.AceQualifier -ne [System.Security.AccessControl.AceQualifier]::AccessAllowed) { continue }
        $v = $a.SecurityIdentifier.Value
        if (($v -eq $script:ShellUserSid -or $BroadSids -contains $v) -and (($a.AccessMask -band $grant) -ne 0)) {
            $problems += ('{0} is allowed 0x{1:X}' -f (Get-SidName $v), $a.AccessMask)
        }
    }
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    return (Pass 'owner Administrators, deny 0x82B for the user first, no terminate/suspend grant (DACL structure only: a real standard-user attempt is VM 39)')
}

Invoke-Check 'B05' 'Service process DACL gives standard users no terminate right (VM 3)' {
    if ($null -eq $script:ServicePid) { return (Skip 'service process not found') }
    $sd = Get-ProcessSd $script:ServicePid
    if ($sd -is [string]) { return (Skip $sd) }
    $problems = @()
    $grant = 0x0001 -bor 0x0800 -bor 0x10000000 -bor 0x40000000 -bor 0x00040000 -bor 0x00080000   # + WRITE_OWNER
    $check = @($BroadSids)
    if ($script:ConsoleUserSid) { $check += $script:ConsoleUserSid }
    foreach ($a in @($sd.DiscretionaryAcl)) {
        if (-not ($a -is [System.Security.AccessControl.CommonAce])) { continue }
        if ($a.AceQualifier -ne [System.Security.AccessControl.AceQualifier]::AccessAllowed) { continue }
        $v = $a.SecurityIdentifier.Value
        if ($check -contains $v -and (($a.AccessMask -band $grant) -ne 0)) { $problems += ('{0} is allowed 0x{1:X}' -f (Get-SidName $v), $a.AccessMask) }
    }
    if ($problems.Count -gt 0) { return (Fail ($problems -join '; ')) }
    return (Pass 'DACL structure only: a real standard-user taskkill / sc stop is VM 3')
}

# ===================================================================================================
# C. Event log (provider PcGuard.Service, Application log)
# ===================================================================================================

$script:Ev = $null
$script:EvError = $null
$script:LastStart = $null
$script:SinceStart = @()

Invoke-Check 'C01' ('Event log readable; PC Guard entries in the last {0} h' -f $LogHours) {
    $since = (Get-Date).AddHours(-$LogHours)
    $script:Ev = @(Get-PgEvents $since)
    if ($script:Ev.Count -eq 0) {
        return (Skip ('no PC Guard entries in the last {0} h (run Restart-Service PcGuard, wait 45 s and run again, or use -LogHours)' -f $LogHours))
    }
    $script:LastStart = Find-LastEvent $script:Ev 'PC Guard started (queued usage events'
    $script:SinceStart = @(Get-EventsAfter $script:Ev $script:LastStart)
    $startText = 'no service start in this window'
    if ($null -ne $script:LastStart) { $startText = ('last service start {0}' -f (Format-EvTime $script:LastStart)) }
    return (Pass ('{0} entries; {1}' -f $script:Ev.Count, $startText))
}

Invoke-Check 'C02' 'SeDebugPrivilege enabled at service start (VM 24)' {
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    if ($null -eq $script:LastStart) { return (Skip 'the service start is not in the window (see C01)') }
    # logged just before "PC Guard started", so look from the entry before the start line
    $around = @($script:Ev | Where-Object { $_.Time -ge $script:LastStart.Time.AddSeconds(-30) -and $_.Time -le $script:LastStart.Time.AddSeconds(5) })
    if (Find-LastEvent $around 'SeDebugPrivilege enabled') { return (Pass '') }
    $err = Find-LastEvent $around 'SeDebugPrivilege'
    if ($err) { return (Fail $err.Line) }
    return (Fail 'no "SeDebugPrivilege enabled" entry around the last service start')
}

Invoke-Check 'C03' 'Shell launched and connected after the last service start (VM 10, 38)' {
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    $scope = $script:SinceStart
    $launched = Find-LastEvent $scope 'Launched shell (pid'
    $connected = Find-LastEvent $scope 'Shell connected (pid'
    $missing = Find-LastEvent $scope 'Shell executable is missing'
    if ($missing) { return (Fail $missing.Line) }
    if ($launched -and $connected) {
        return (Pass ('"{0}" at {1}; "{2}" at {3}' -f $launched.Line, (Format-EvTime $launched), $connected.Line, (Format-EvTime $connected)))
    }
    if ($null -eq $script:LastStart -and $null -ne $script:ShellPid) { return (Skip 'the service start and the shell launch are older than the window; a shell is running (B02)') }
    if ($null -eq $script:ConsoleUserSid -and $null -eq $script:ShellPid) { return (Skip 'nobody is signed in to Windows in the console session') }
    $parts = @()
    if (-not $launched) { $parts += 'no "Launched shell" entry' }
    if (-not $connected) { $parts += 'no "Shell connected" entry' }
    $warn = Find-LastEvent $scope 'Could not launch shell'
    if ($warn) { $parts += ('last launch warning: ' + $warn.Line) }
    return (Fail ($parts -join '; '))
}

Invoke-Check 'C04' 'Startup grace entries after the last service start (VM 155, 156)' {
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    if ($null -eq $script:LastStart) { return (Skip 'the service start is not in the window (see C01)') }
    $scope = $script:SinceStart
    $paused = Find-LastEvent $scope 'Startup grace: enforcement paused'
    $ended = Find-LastEvent $scope 'Startup grace ended: shell connected'
    $expired = Find-LastEvent $scope 'Startup grace expired without a shell'
    if (-not $paused) { return (Fail 'no "Startup grace: enforcement paused until the shell connects or 30 s pass" entry after the start') }
    if ($ended) {
        $grace = [int]($ended.Time - $paused.Time).TotalSeconds
        $kills = @($scope | Where-Object { $_.RecordId -lt $ended.RecordId -and (Test-ContainsText $_.Text 'Terminated ') })
        if ($kills.Count -gt 0) { return (Fail ('{0} "Terminated" entries during the grace (nothing may be killed before the shell connects)' -f $kills.Count)) }
        return (Pass ('paused, then "ended: shell connected" after about {0} s, no kills before it' -f $grace))
    }
    if ($expired) { return (Pass 'paused, then "expired without a shell: name-only enforcement" (normal when the service started at the logon screen or the shell could not start within 30 s)') }
    if (((Get-Date) - $paused.Time).TotalSeconds -lt 40) { return (Skip 'the service started less than 40 s ago; run again') }
    return (Fail 'grace started but neither "ended" nor "expired" was logged')
}

$script:Mode = 'unknown'
Invoke-Check 'C05' 'Enforcement mode is window-aware (snapshots from the shell) (VM 49, 51)' {
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    $last = $null
    foreach ($e in $script:Ev) {
        if ((Test-ContainsText $e.Text 'No fresh snapshot from the shell: name-only enforcement') -or
            (Test-ContainsText $e.Text 'Shell snapshots resumed: window-aware enforcement') -or
            (Test-ContainsText $e.Text 'Startup grace ended: shell connected') -or
            (Test-ContainsText $e.Text 'Startup grace expired without a shell') -or
            (Test-ContainsText $e.Text 'PC Guard started (queued usage events')) { $last = $e }
    }
    $resumed = Find-LastEvent $script:SinceStart 'Shell snapshots resumed'
    $resumedText = 'no "Shell snapshots resumed" entry since the start (it is logged only after a fallback period)'
    if ($resumed) { $resumedText = ('"Shell snapshots resumed" at {0}' -f (Format-EvTime $resumed)) }
    if ($null -eq $last) {
        if ($null -ne $script:ShellPid) { $script:Mode = 'window-aware (assumed)'; return (Pass ('no mode change in the window; a shell is running; ' + $resumedText)) }
        return (Skip 'no mode entries in the window')
    }
    if (Test-ContainsText $last.Text 'No fresh snapshot') {
        $age = [int]((Get-Date) - $last.Time).TotalSeconds
        $script:Mode = 'fallback'
        return (Fail ('name-only fallback since {0} ({1} s): the shell is missing, hung, or on another desktop/session' -f (Format-EvTime $last), $age))
    }
    if (Test-ContainsText $last.Text 'Startup grace expired') {
        if ($null -ne $script:ShellPid) { $script:Mode = 'window-aware (assumed)'; return (Pass ('grace expired earlier, shell running now; ' + $resumedText)) }
        $script:Mode = 'fallback'
        return (Fail 'grace expired without a shell and no shell is running: name-only enforcement')
    }
    if (Test-ContainsText $last.Text 'PC Guard started') {
        $script:Mode = 'grace'
        return (Skip 'the service has only just started (startup grace)')
    }
    $script:Mode = 'window-aware'
    return (Pass ('last mode entry: "{0}" at {1}; {2}' -f $last.Line, (Format-EvTime $last), $resumedText))
}

Invoke-Check 'C06' 'No Error or Critical entries (VM 9, 24, 41)' {
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    $errs = @($script:Ev | Where-Object { $_.Level -ge 1 -and $_.Level -le 2 })
    if ($errs.Count -eq 0) { return (Pass ('{0} entries, none Error/Critical' -f $script:Ev.Count)) }
    $groups = @($errs | Group-Object Line | Sort-Object Count -Descending | Select-Object -First 5 | ForEach-Object { '{0}x "{1}"' -f $_.Count, $_.Name })
    return (Fail ('{0} Error/Critical entries: {1}' -f $errs.Count, ($groups -join '; ')))
}

Invoke-Check 'C07' 'Warning entries (listed; the plain-http warning is expected with an http://localhost backend)' {
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    $warns = @($script:Ev | Where-Object { $_.Level -eq 3 })
    if ($warns.Count -eq 0) { return (Pass 'no warnings') }
    $groups = @($warns | Group-Object Line | Sort-Object Count -Descending | Select-Object -First 12 | ForEach-Object { '{0}x "{1}"' -f $_.Count, $_.Name })
    return (Pass ('{0} warnings: {1}' -f $warns.Count, ($groups -join '; ')))
}

Invoke-Check 'C08' 'Privacy: no entry holds "pbkdf2", the recovery hash, the machine key or "?token=" (VM 31, 87, 145)' {
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    $cPb = 0; $cTok = 0; $cHash = 0; $cKey = 0
    foreach ($e in $script:Ev) {
        $t = $e.Text
        if ($t.IndexOf('pbkdf2', [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $cPb++ }
        if ($t.IndexOf('?token=', [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $cTok++ }
        $hitHash = $false; $hitKey = $false
        for ($i = 0; $i -lt $script:Needles.Count; $i++) {
            if ($t.IndexOf($script:Needles[$i], [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                if ($script:NeedleKinds[$i] -eq 'machine key') { $hitKey = $true } else { $hitHash = $true }
            }
        }
        if ($hitHash) { $cHash++ }
        if ($hitKey) { $cKey++ }
    }
    $hashNote = ''
    if (-not ($script:NeedleKinds -contains 'recovery hash')) { $hashNote = ' (no recovery.hash to compare)' }
    $keyNote = ''
    if (-not $script:MachineKeyOk) { $keyNote = ' (no machine key to compare)' }
    $detail = ('{0} entries scanned: pbkdf2 {1}, recovery hash {2}{3}, machine key {4}{5}, ?token= {6}' -f $script:Ev.Count, $cPb, $cHash, $hashNote, $cKey, $keyNote, $cTok)
    if ($cPb + $cTok + $cHash + $cKey -gt 0) { return (Fail $detail) }
    return (Pass $detail)
}

Invoke-Check 'C09' 'Extra-apps warning logged at the last service start (VM 138, 142)' {
    if (@($script:ExtraApps).Count -eq 0) { return (Skip 'no extra apps configured') }
    if ($null -eq $script:Ev -or $script:Ev.Count -eq 0) { return (Skip 'no event log entries (see C01)') }
    if ($null -eq $script:LastStart) { return (Skip 'the service start is not in the window (see C01)') }
    $around = @($script:Ev | Where-Object { $_.Time -ge $script:LastStart.Time.AddSeconds(-30) -and $_.Time -le $script:LastStart.Time.AddSeconds(5) })
    $w = Find-LastEvent $around 'Extra allowed apps configured on this PC'
    if ($w) { return (Pass $w.Line) }
    return (Fail 'no "Extra allowed apps configured on this PC" warning around the last start (the service may not have read Allowlist:ExtraApps; restart it after editing)')
}

# ===================================================================================================
# D. Enforcement probes
# ===================================================================================================

$probeTitles = [ordered]@{
    'D01' = 'notepad.exe started now is terminated within 20 s (VM 1, 15, 19)'
    'D02' = 'mspaint.exe started now is terminated within 20 s (VM 15)'
    'D03' = 'taskmgr.exe started now is terminated within 20 s (documented: not allowlisted)'
    'D04' = 'Allowlisted cmd.exe started now still runs after 20 s'
    'D05' = 'explorer.exe (protected) still runs after 20 s (VM 15)'
    'D06' = 'This powershell.exe (allowlisted) still runs after 20 s'
    'D07' = 'Extra app AnyDesk.exe still runs after 20 s (VM 138)'
}

$probeSkip = $null
if ($NoProbes) { $probeSkip = '-NoProbes given' }
elseif (-not $script:SvcRunning) { $probeSkip = 'the service is not running' }
elseif ($null -eq $script:ShellPid) { $probeSkip = 'no shell is connected in the console session (see B02)' }
elseif ($script:MySession -ne $script:ConsoleSession) { $probeSkip = ('this script runs in session {0}, not in the console session {1} (RDP?): processes started here are not enforced' -f $script:MySession, $script:ConsoleSession) }
elseif ($script:Mode -eq 'fallback') { $probeSkip = 'name-only fallback is active (see C05): Windows inbox apps are spared in fallback, the probes would not mean anything' }
elseif ($script:Mode -eq 'grace') { $probeSkip = 'startup grace is active; run again in a minute' }
else {
    $scope = $script:SinceStart
    $in = Find-LastEvent $scope 'Student signed in'
    $out = Find-LastEvent $scope 'Student signed out'
    if ($in -and (-not $out -or $out.RecordId -lt $in.RecordId)) { $probeSkip = 'a student is signed in to PC Guard: the lock state is unknown (the probes expect the locked no_student state)' }
    $ms = Find-LastEvent $scope 'Maintenance mode started'
    $me = Find-LastEvent $scope 'Maintenance mode ended'
    if ($ms -and (-not $me -or $me.RecordId -lt $ms.RecordId)) { $probeSkip = 'maintenance mode is active: nothing is closed' }
    $rel = Find-LastEvent $scope 'Recovery code accepted'
    if ($rel) { $probeSkip = 'a recovery release happened: nothing is enforced' }
}

if ($probeSkip) {
    foreach ($k in $probeTitles.Keys) { Add-Result $k $probeTitles[$k] 'SKIP' $probeSkip }
}
else {
    Write-Out ('Running the enforcement probes ({0} s) ...' -f $ProbeSeconds)
    $probe = @{}
    $probeError = $null
    $kill = @(
        @{ Id = 'D01'; Exe = 'notepad.exe'; Name = 'notepad' },
        @{ Id = 'D02'; Exe = 'mspaint.exe'; Name = 'mspaint' },
        @{ Id = 'D03'; Exe = 'taskmgr.exe'; Name = 'Taskmgr' }
    )
    $probeStart = Get-Date
    $cmdProc = $null
    $explorerBefore = @()
    $extraBefore = @()
    $extraName = $null
    try {
        $ErrorActionPreference = 'Stop'
        foreach ($t in $kill) {
            $t.Before = @(Get-Process -Name $t.Name -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
            $t.Seen = $false
            $t.Started = $false
            $t.Error = $null
        }
        $explorerBefore = @(Get-Process -Name explorer -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $script:ConsoleSession } | ForEach-Object { $_.Id })
        foreach ($x in @($script:ExtraApps)) { if ($x -ieq 'anydesk.exe') { $extraName = 'AnyDesk' } }
        if ($extraName) {
            $extraBefore = @(Get-Process -Name $extraName -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $script:ConsoleSession } | ForEach-Object { $_.Id })
        }
        $probeStart = Get-Date
        foreach ($t in $kill) {
            try { Start-Process -FilePath $t.Exe -ErrorAction Stop | Out-Null; $t.Started = $true }
            catch { $t.Error = $_.Exception.Message }
        }
        try {
            $cmdProc = Start-Process -FilePath (Join-Path $env:SystemRoot 'System32\cmd.exe') -ArgumentList '/k', 'title PC Guard self-test: allowlisted cmd.exe probe (closed by the self-test)' -PassThru -ErrorAction Stop
        }
        catch { $probe.CmdError = $_.Exception.Message }
        for ($i = 0; $i -lt $ProbeSeconds; $i++) {
            Start-Sleep -Seconds 1
            foreach ($t in $kill) {
                if (@(Get-NewInstances $t.Name $t.Before $probeStart).Count -gt 0) { $t.Seen = $true }
            }
        }
        foreach ($t in $kill) { $t.Live = @(Get-NewInstances $t.Name $t.Before $probeStart) }
        $probe.Events = @(Get-PgEvents $probeStart.AddSeconds(-2))
        $probe.CmdAlive = $false
        if ($null -ne $cmdProc) { $probe.CmdAlive = -not $cmdProc.HasExited }
        $probe.ExplorerLeft = @($explorerBefore | Where-Object { $null -eq (Get-Process -Id $_ -ErrorAction SilentlyContinue) })
        $probe.ExtraLeft = @($extraBefore | Where-Object { $null -eq (Get-Process -Id $_ -ErrorAction SilentlyContinue) })
    }
    catch { $probeError = $_.Exception.Message }
    finally {
        # cleanup: only the test processes this script started (new instances since the probe start)
        foreach ($t in $kill) {
            try {
                foreach ($p in @(Get-NewInstances $t.Name $t.Before $probeStart)) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
            }
            catch { }
        }
        if ($null -ne $cmdProc) {
            try { if (-not $cmdProc.HasExited) { Stop-Process -Id $cmdProc.Id -Force -ErrorAction SilentlyContinue } } catch { }
        }
        $ErrorActionPreference = 'Continue'
    }

    $killedLines = @()
    if ($probe.Events) { $killedLines = @($probe.Events | Where-Object { Test-ContainsText $_.Text 'Terminated ' }) }

    foreach ($t in $kill) {
        $tt = $t
        Invoke-Check $tt.Id $probeTitles[$tt.Id] {
            if ($probeError) { return (Fail ('probe error: ' + $probeError)) }
            if (-not $tt.Started) { return (Skip ('{0} could not be started: {1}' -f $tt.Exe, $tt.Error)) }
            $ev = @($killedLines | Where-Object { Test-ContainsText $_.Text ('Terminated ' + $tt.Exe) })
            $live = @($tt.Live)
            if ($live.Count -gt 0) {
                return (Fail ('still running after {0} s (pid {1}); {2} "Terminated {3}" entries. Is the PC really locked (no student signed in, no maintenance)?' -f $ProbeSeconds, (($live | ForEach-Object { $_.Id }) -join ','), $ev.Count, $tt.Exe))
            }
            if ($ev.Count -eq 0) { return (Fail ('gone, but no "Terminated {0}" entry in the event log (closed by something else, or never started?)' -f $tt.Exe)) }
            return (Pass ('"{0}" at {1}' -f $ev[0].Line, (Format-EvTime $ev[0])))
        }
    }

    Invoke-Check 'D04' $probeTitles['D04'] {
        if ($probeError) { return (Fail ('probe error: ' + $probeError)) }
        if ($null -eq $cmdProc) { return (Skip ('cmd.exe could not be started: ' + $probe.CmdError)) }
        $ev = @($killedLines | Where-Object { Test-ContainsText $_.Text 'Terminated cmd.exe' })
        if (-not $probe.CmdAlive) { return (Fail ('cmd.exe pid {0} is gone; {1} "Terminated cmd.exe" entries' -f $cmdProc.Id, $ev.Count)) }
        if ($ev.Count -gt 0) { return (Fail ('{0} "Terminated cmd.exe" entries during the probe' -f $ev.Count)) }
        return (Pass ('pid {0} (closed by the self-test afterwards)' -f $cmdProc.Id))
    }

    Invoke-Check 'D05' $probeTitles['D05'] {
        if ($probeError) { return (Fail ('probe error: ' + $probeError)) }
        if ($explorerBefore.Count -eq 0) { return (Skip 'no explorer.exe in the console session') }
        $ev = @($killedLines | Where-Object { Test-ContainsText $_.Text 'Terminated explorer.exe' })
        if (@($probe.ExplorerLeft).Count -gt 0 -or $ev.Count -gt 0) { return (Fail ('explorer.exe pid(s) gone: {0}; {1} "Terminated explorer.exe" entries' -f (@($probe.ExplorerLeft) -join ','), $ev.Count)) }
        return (Pass ('pid(s) {0}' -f ($explorerBefore -join ',')))
    }

    Invoke-Check 'D06' $probeTitles['D06'] {
        if ($probeError) { return (Fail ('probe error: ' + $probeError)) }
        $me = Get-Process -Id $PID
        if ($me.ProcessName -ne 'powershell') { return (Skip ('this script runs in {0}.exe, not powershell.exe' -f $me.ProcessName)) }
        $ev = @($killedLines | Where-Object { Test-ContainsText $_.Text 'Terminated powershell.exe' })
        if ($ev.Count -gt 0) { return (Fail ('{0} "Terminated powershell.exe" entries during the probe' -f $ev.Count)) }
        return (Pass ('pid {0}' -f $PID))
    }

    Invoke-Check 'D07' $probeTitles['D07'] {
        if ($probeError) { return (Fail ('probe error: ' + $probeError)) }
        if (-not $extraName) { return (Skip 'anydesk.exe is not in Allowlist:ExtraApps') }
        if ($extraBefore.Count -eq 0) { return (Skip 'AnyDesk.exe is not running in the console session') }
        $ev = @($killedLines | Where-Object { Test-ContainsText $_.Text 'Terminated AnyDesk.exe' })
        if (@($probe.ExtraLeft).Count -gt 0 -or $ev.Count -gt 0) { return (Fail ('AnyDesk pid(s) gone: {0}; {1} "Terminated AnyDesk.exe" entries' -f (@($probe.ExtraLeft) -join ','), $ev.Count)) }
        return (Pass ('pid(s) {0}' -f ($extraBefore -join ',')))
    }
}

# ===================================================================================================
# summary, environment details, report file
# ===================================================================================================

$nPass = @($script:Results | Where-Object { $_.Status -eq 'PASS' }).Count
$nFail = @($script:Results | Where-Object { $_.Status -eq 'FAIL' }).Count
$nSkip = @($script:Results | Where-Object { $_.Status -eq 'SKIP' }).Count
Write-Out '' -Always
$summaryColor = 'Green'
if ($nFail -gt 0) { $summaryColor = 'Red' }
Write-Out ('Summary: {0} PASS, {1} FAIL, {2} SKIP ({3} checks, {4:N0} s)' -f $nPass, $nFail, $nSkip, $script:Results.Count, ((Get-Date) - $startedAt).TotalSeconds) $summaryColor -Always

# --- install folder listing and hashes (file only) ---
try {
    if (Test-Path -LiteralPath $InstallDir -PathType Container) {
        $files = @(Get-ChildItem -LiteralPath $InstallDir -Recurse -Force -File | Sort-Object FullName)
        $total = 0
        $listing = New-Object System.Collections.Generic.List[string]
        foreach ($f in $files) {
            $total += $f.Length
            $listing.Add(('{0}|{1}' -f $f.FullName.Substring($InstallDir.Length).TrimStart('\').ToLowerInvariant(), $f.Length))
        }
        Add-Env ('Install folder listing: {0} files, {1} bytes, listing sha256 (relative path|size) {2}' -f $files.Count, $total, (Get-StringSha256 ([string]::Join("`n", $listing.ToArray()))))
        foreach ($f in @($files | Where-Object { $_.Extension -eq '.exe' -or $_.Name -like 'PcGuard*.dll' -or $_.Name -like '*.runtimeconfig.json' })) {
            $h = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
            Add-Env ('  {0}  {1,10}  {2}' -f $h, $f.Length, $f.FullName.Substring($InstallDir.Length).TrimStart('\'))
        }
    }
    else { Add-Env 'Install folder listing: folder not found' }
}
catch { Add-Env ('Install folder listing: error {0}' -f $_.Exception.Message) }

try {
    if (Test-Path -LiteralPath $DataDir -PathType Container) {
        $names = @(Get-ChildItem -LiteralPath $DataDir -Force | ForEach-Object { '{0} ({1} bytes)' -f $_.Name, $_.Length })
        Add-Env ('Data folder entries (names and sizes only): ' + ($names -join ', '))
    }
}
catch { Add-Env ('Data folder entries: error {0}' -f $_.Exception.Message) }

if ($script:BaseUrl) { Add-Env ('Backend:BaseUrl : {0}' -f $script:BaseUrl) }
Add-Env ('Allowlist:ExtraApps: [{0}]' -f (@($script:ExtraApps) -join ', '))

# --- service configuration (file only; no secrets in it) ---
Add-Env ''
Add-Env 'Service configuration:'
foreach ($cmd in @(@('qc', $ServiceName), @('qfailure', $ServiceName), @('qfailureflag', $ServiceName), @('sdshow', $ServiceName))) {
    try {
        Add-Env ('> sc.exe {0}' -f ($cmd -join ' '))
        foreach ($l in (Invoke-Native 'sc.exe' $cmd)) { if ($l.Trim()) { Add-Env ('  ' + $l.TrimEnd()) } }
    }
    catch { Add-Env ('  error {0}' -f $_.Exception.Message) }
}
try {
    if (Test-Path -LiteralPath $ServiceKey) {
        $p = Get-ItemProperty -LiteralPath $ServiceKey
        $vals = @()
        foreach ($n in @('ImagePath', 'ObjectName', 'Start', 'DelayedAutostart', 'FailureActionsOnNonCrashFailures')) {
            if ($p.PSObject.Properties[$n]) { $vals += ('{0}={1}' -f $n, $p.$n) }
        }
        Add-Env ('> registry ' + ($vals -join '; '))
    }
}
catch { Add-Env ('  registry error {0}' -f $_.Exception.Message) }

# --- recent PC Guard event log lines (file only; an entry matching a privacy pattern is redacted) ---
$evLines = New-Object System.Collections.Generic.List[string]
if ($null -ne $script:Ev -and $script:Ev.Count -gt 0) {
    $recent = @($script:Ev | Select-Object -Last 300)
    $evLines.Add(('PC Guard event log, last {0} of {1} entries in {2} h (level 1/2 = critical/error, 3 = warning, 4 = information):' -f $recent.Count, $script:Ev.Count, $LogHours))
    foreach ($e in $recent) {
        $line = $e.Line
        $redact = ($e.Text.IndexOf('pbkdf2', [System.StringComparison]::OrdinalIgnoreCase) -ge 0) -or ($e.Text.IndexOf('?token=', [System.StringComparison]::OrdinalIgnoreCase) -ge 0)
        for ($i = 0; $i -lt $script:Needles.Count; $i++) {
            if ($e.Text.IndexOf($script:Needles[$i], [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $redact = $true }
        }
        if ($redact) { $line = '[redacted: the entry matched a privacy pattern, see C08]' }
        if ($line.Length -gt 300) { $line = $line.Substring(0, 300) + ' ...' }
        $evLines.Add(('  {0}  L{1}  {2}' -f (Format-EvTime $e), $e.Level, $line))
    }
}
else { $evLines.Add('PC Guard event log: no entries in the window') }

$script:Needles.Clear()

$fileText = New-Object System.Collections.Generic.List[string]
$fileText.Add(('PC Guard self-test report, {0}' -f $startedAt.ToString('yyyy-MM-dd HH:mm:ss')))
$fileText.Add('')
$fileText.AddRange([string[]]$script:EnvLines.ToArray())
$fileText.Add('')
$fileText.Add('Checks:')
$fileText.AddRange([string[]]$script:ReportLines.ToArray())
$fileText.Add('')
$fileText.AddRange([string[]]$evLines.ToArray())

try {
    $dir = [System.IO.Path]::GetDirectoryName([System.IO.Path]::GetFullPath($OutFile))
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    [System.IO.File]::WriteAllLines([System.IO.Path]::GetFullPath($OutFile), $fileText.ToArray(), (New-Object System.Text.UTF8Encoding($true)))
    Write-Host ('Report written to {0}' -f $OutFile)
}
catch {
    Write-Host ('Could not write the report file {0}: {1}' -f $OutFile, $_.Exception.Message) -ForegroundColor Red
}

if ($nFail -gt 0) { exit 1 }
exit 0
