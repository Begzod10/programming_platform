<#
.SYNOPSIS
  Installs (or upgrades) the PC Guard service. Run in an elevated PowerShell.
.DESCRIPTION
  Copies the published folder to the install directory, writes Backend:BaseUrl into the installed
  appsettings.json, locks the folder down, registers the PcGuard service (LocalSystem, automatic start,
  restart on failure) and starts it. The shell (PcGuard.Shell.exe) is launched ONLY by the service:
  this script deliberately registers no Run key, scheduled task or Startup shortcut for it.
  The service is also registered for Safe Mode (SafeBoot\Minimal and SafeBoot\Network keys with the
  default value "Service"); this is best-effort and UNTESTED.
  Upgrade: the old folder is renamed to <InstallDir>.old-<timestamp>; if any later step fails, the new
  files and service are removed and the old version is restored. The old folder is deleted only after
  the new service started.
  NOT TESTED: written without PowerShell available; run the VM checklist in README.md.
  Compatible with Windows PowerShell 5.1 and PowerShell 7 (no ternary, no && / ||).
.PARAMETER BackendBaseUrl
  Backend API base URL including the /api/v1 prefix, e.g. https://example.uz/api/v1.
  Must be https, except for localhost / 127.0.0.1 / [::1].
.PARAMETER DistDir
  Output folder of publish.ps1 (default ..\dist relative to this script).
.PARAMETER InstallDir
  Target folder (default: 64-bit Program Files\PcGuard).
.PARAMETER ExtraAllowedApps
  Optional. Exe names kept running on THIS PC in every state, even while it is locked (for example
  anydesk.exe on a test PC), written as Allowlist:ExtraApps into the installed appsettings.json.
  Each must be a bare file name ending in .exe, 5-64 characters, only letters A-Z, digits, '.', '-'
  and '_' (no path, spaces or wildcards); at most 16. Accepts an array or one comma separated string
  (Setup-PcGuard.exe passes "a.exe,b.exe"). Any invalid value stops the script with exit code 1
  before anything is changed. Not given: an upgrade keeps the extra apps of the existing install.
  Given as '' (empty): the extra apps are cleared.
  SECURITY: these apps bypass the lock on this PC. Remote-control software kept running lets anyone
  at the PC use it while the PC is locked. Use it only on test/admin PCs.
.PARAMETER RecoveryCodeHash
  Optional. The HASH of this PC's offline recovery code, exactly as Setup-PcGuard.exe computes it:
  pbkdf2-sha256$<iterations>$<salt base64>$<hash base64> (PBKDF2-HMAC-SHA256, 310000-5000000
  iterations, 16-byte salt, 32-byte hash). NEVER the code itself: the plain code is typed hidden in
  Setup and never reaches this script, a command line or a file. An invalid value stops the script with
  exit code 1 before anything is changed. Written to %ProgramData%\PcGuard\recovery.hash (SYSTEM and
  Administrators only). Not given: an upgrade keeps an existing recovery.hash.
.PARAMETER ClearRecoveryCode
  Removes %ProgramData%\PcGuard\recovery.hash (no offline way out any more). Cannot be combined with
  -RecoveryCodeHash.
.EXAMPLE
  .\install.ps1 -BackendBaseUrl https://example.uz/api/v1
.EXAMPLE
  .\install.ps1 -BackendBaseUrl https://example.uz/api/v1 -ExtraAllowedApps anydesk.exe
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BackendBaseUrl,
    [string]$DistDir = (Join-Path $PSScriptRoot '..\dist'),
    [string]$InstallDir = (Join-Path $(if ($env:ProgramW6432) { $env:ProgramW6432 } else { $env:ProgramFiles }) 'PcGuard'),
    [string[]]$ExtraAllowedApps,
    [string]$RecoveryCodeHash,
    [switch]$ClearRecoveryCode
)

$ErrorActionPreference = 'Stop'
$ServiceName = 'PcGuard'
$ServiceKey = 'HKLM:\SYSTEM\CurrentControlSet\Services\PcGuard'

# State used by the rollback in the catch block.
$script:hadService = $false
$script:oldServiceRemoved = $false
$script:backupDir = $null
$script:newFolderCreated = $false
$script:target = $null
$script:NativeExit = 0
$script:hadSafeBoot = $false
$MaxExtraApps = 16
$script:oldStartDisabled = $false
$script:recoveryTouched = $false
$script:oldRecoveryHash = $null
# Same folder the service uses (SecureStore): the real CommonApplicationData path, not $env:ProgramData.
$DataDir = Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'PcGuard'
$RecoveryHashFile = Join-Path $DataDir 'recovery.hash'
$SidSystem = 'S-1-5-18'
$SidAdmins = 'S-1-5-32-544'

function Test-Base64Exact {
    # canonical base64 of exactly $Bytes bytes
    param([string]$Text, [int]$Bytes)
    try { $raw = [Convert]::FromBase64String($Text) } catch { return $false }
    if ($raw.Length -ne $Bytes) { return $false }
    return ([Convert]::ToBase64String($raw) -ceq $Text)
}

function Test-RecoveryHash {
    # Same rule as PcGuard.Core RecoveryCode.IsWellFormedStored. -cmatch and \z: no case folding, no trailing newline.
    param([string]$Value)
    if ($null -eq $Value -or $Value.Length -gt 128) { return $false }
    if (-not ($Value -cmatch '^pbkdf2-sha256\$([1-9][0-9]{0,6})\$([A-Za-z0-9+/=]{24})\$([A-Za-z0-9+/=]{44})\z')) { return $false }
    $iter = [int]$Matches[1]
    $salt = $Matches[2]
    $hash = $Matches[3]
    if ($iter -lt 310000 -or $iter -gt 5000000) { return $false }
    if (-not (Test-Base64Exact $salt 16)) { return $false }
    return (Test-Base64Exact $hash 32)
}

function New-AdminOnlySecurity {
    # Owner Administrators, inheritance removed, SYSTEM and Administrators full control only (as the service's SecureStore).
    param([bool]$Container)
    if ($Container) {
        $sec = New-Object System.Security.AccessControl.DirectorySecurity
        $inherit = [System.Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit'
    }
    else {
        $sec = New-Object System.Security.AccessControl.FileSecurity
        $inherit = [System.Security.AccessControl.InheritanceFlags]::None
    }
    $sec.SetOwner((New-Object System.Security.Principal.SecurityIdentifier($SidAdmins)))
    $sec.SetAccessRuleProtection($true, $false)
    foreach ($sid in @($SidSystem, $SidAdmins)) {
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            (New-Object System.Security.Principal.SecurityIdentifier($sid)),
            [System.Security.AccessControl.FileSystemRights]::FullControl, $inherit,
            [System.Security.AccessControl.PropagationFlags]::None, [System.Security.AccessControl.AccessControlType]::Allow)
        $sec.AddAccessRule($rule)
    }
    return $sec
}

function Test-AdminOnlyAcl {
    # True when the owner is SYSTEM or Administrators and every Allow ACE is for SYSTEM or Administrators.
    param($Security)
    $owner = $Security.GetOwner([System.Security.Principal.SecurityIdentifier])
    if ($null -eq $owner -or ($owner.Value -ne $SidSystem -and $owner.Value -ne $SidAdmins)) { return $false }
    foreach ($r in $Security.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])) {
        if ($r.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow) { continue }
        $v = $r.IdentityReference.Value
        if ($v -ne $SidSystem -and $v -ne $SidAdmins) { return $false }
    }
    return $true
}

function Initialize-DataDir {
    # The service's data folder, secured exactly like the service does it (SecureStore.EnsureDirectory):
    # an existing folder that is a link, or whose owner/ACL is not SYSTEM/Administrators-only, is never
    # trusted (a standard user may have pre-created it) and is moved aside; a fresh one is created with
    # the admin-only ACL in one step (no window with inherited ProgramData rights).
    $di = New-Object System.IO.DirectoryInfo($DataDir)
    if ($di.Exists) {
        $trusted = $false
        try {
            if (($di.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq 0) {
                $trusted = Test-AdminOnlyAcl (Get-Acl -LiteralPath $DataDir)
            }
        }
        catch { $trusted = $false }
        if (-not $trusted) {
            $quarantine = $DataDir + '.untrusted-' + [Guid]::NewGuid().ToString('N')
            Write-Warning "The data folder $DataDir has an unexpected owner or ACL (or is a link); moving it aside to $quarantine."
            [System.IO.Directory]::Move($DataDir, $quarantine)
            $di = New-Object System.IO.DirectoryInfo($DataDir)
        }
    }
    $sec = New-AdminOnlySecurity $true
    if (-not $di.Exists) {
        if ($PSVersionTable.PSVersion.Major -lt 6) { [System.IO.Directory]::CreateDirectory($DataDir, $sec) | Out-Null }
        else { [System.IO.FileSystemAclExtensions]::Create($di, $sec) }
    }
    else {
        Set-Acl -LiteralPath $DataDir -AclObject $sec   # re-assert (as the service does at every start)
    }
}

function Write-RecoveryHashFile {
    # Writes $Value (a hash, never a plain code) as recovery.hash with an explicit admin-only ACL, then
    # reads it back. Never prints the value.
    param([string]$Value)
    Initialize-DataDir
    $tmp = $RecoveryHashFile + '.tmp'
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force }
    [System.IO.File]::WriteAllText($tmp, $Value, (New-Object System.Text.ASCIIEncoding))   # no BOM, no newline
    Set-Acl -LiteralPath $tmp -AclObject (New-AdminOnlySecurity $false)
    if (Test-Path -LiteralPath $RecoveryHashFile) { Remove-Item -LiteralPath $RecoveryHashFile -Force }
    Move-Item -LiteralPath $tmp -Destination $RecoveryHashFile
    if ([System.IO.File]::ReadAllText($RecoveryHashFile) -cne $Value) {
        throw "The recovery code hash was not written correctly to $RecoveryHashFile."
    }
    if (-not (Test-AdminOnlyAcl (Get-Acl -LiteralPath $RecoveryHashFile))) {
        throw "$RecoveryHashFile does not have the SYSTEM/Administrators-only permissions."
    }
}

function Test-ExtraAppName {
    # Same rule as PcGuard.Core ExtraAllowlist.IsValidName: bare exe file name, 5-64 chars, ASCII letters,
    # digits, '.', '-', '_' only. -cmatch and \z: no case-folding tricks, no trailing newline.
    param([string]$Name)
    if ($null -eq $Name -or $Name.Length -lt 5 -or $Name.Length -gt 64) { return $false }
    if (-not $Name.EndsWith('.exe', [System.StringComparison]::OrdinalIgnoreCase)) { return $false }
    return [bool]($Name -cmatch '^[A-Za-z0-9._-]+\z')
}

function Invoke-Native {
    # Runs a native program without letting stderr text turn into a terminating error (Windows PowerShell 5.1).
    # NOTE: "sc" alone is an alias of Set-Content in PowerShell, so always call sc.exe.
    param([string]$Exe, [string[]]$ExeArgs)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = & $Exe @ExeArgs 2>&1
        $script:NativeExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $old
    }
    return $out
}

function Invoke-Sc {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ScArgs)
    $out = Invoke-Native 'sc.exe' $ScArgs
    if ($script:NativeExit -ne 0) {
        throw "sc.exe $($ScArgs -join ' ') failed (exit code $($script:NativeExit)): $($out -join ' ')"
    }
}

function Test-ServiceExists {
    return [bool](Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)
}

function Wait-ServiceGone {
    $deadline = (Get-Date).AddSeconds(30)
    while ((Test-ServiceExists) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
    if (Test-ServiceExists) {
        throw ('The PcGuard service is still registered after 30 s (marked for deletion; something holds a handle, a reboot may be required).' + " If the PC is now UNGUARDED (no PcGuard service running): reboot, then run install.ps1 again, or restore the '<InstallDir>.old-*' folder and re-create the service.")
    }
}

function Stop-PcGuardService {
    $svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -ne 'Stopped') {
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        try { $svc.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(30)) } catch { Write-Warning 'Service did not report Stopped within 30 s; continuing.' }
    }
}

function Stop-PcGuardProcesses {
    # Stop-Process first, taskkill as a fallback. Returns the names still running.
    foreach ($name in @('PcGuard.Shell', 'PcGuard.Service')) {
        Stop-Process -Name $name -Force -ErrorAction SilentlyContinue
        if (Get-Process -Name $name -ErrorAction SilentlyContinue) {
            Invoke-Native 'taskkill.exe' @('/f', '/im', "$name.exe") | Out-Null
        }
    }
    Start-Sleep -Seconds 1
    $left = @()
    foreach ($name in @('PcGuard.Shell', 'PcGuard.Service')) {
        if (Get-Process -Name $name -ErrorAction SilentlyContinue) { $left += $name }
    }
    return $left
}

function Get-NormalizedDir {
    param([string]$Path)
    return ([System.IO.Path]::GetFullPath($Path).TrimEnd('\') + '\')
}

function Register-PcGuardService {
    param([string]$ExePath)
    $expected = '"' + $ExePath + '"'
    # New-Service goes through the Win32 API (no command-line re-parsing, same in PS 5.1 and 7).
    # The default account is LocalSystem.
    New-Service -Name $ServiceName -BinaryPathName $expected -DisplayName 'PC Guard' -StartupType Automatic `
        -Description 'PC Guard: controls which programs students may run on this computer.' | Out-Null

    # Read the raw ImagePath back. An unquoted path containing a space in a SYSTEM service is a privilege-escalation hole.
    $actual = (Get-ItemProperty -Path $ServiceKey -Name ImagePath).ImagePath
    if ($actual -cne $expected) {
        Set-ItemProperty -Path $ServiceKey -Name ImagePath -Value $expected
        $actual = (Get-ItemProperty -Path $ServiceKey -Name ImagePath).ImagePath
    }
    if ($actual -cne $expected -or ($actual.Contains(' ') -and -not $actual.StartsWith('"'))) {
        Invoke-Native 'sc.exe' @('delete', $ServiceName) | Out-Null
        throw "The service ImagePath is not the expected quoted path (found: $actual). The service was removed. Installation aborted."
    }

    Invoke-Sc failure $ServiceName 'reset=' '0' 'actions=' 'restart/5000/restart/5000/restart/5000'
    Invoke-Sc failureflag $ServiceName 1
}

# Safe Mode registration. BEST-EFFORT and UNTESTED: a service runs in Safe Mode only if a key with its
# name exists under SafeBoot\Minimal (plain Safe Mode) or SafeBoot\Network (Safe Mode with Networking),
# with the default value "Service" (REG_SZ). Whether the shell and enforcement then work is unverified;
# see the Safe Mode test in README.md.
$SafeBootKeys = @(
    'HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal\PcGuard',
    'HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Network\PcGuard'
)

function Register-PcGuardSafeBoot {
    foreach ($key in $SafeBootKeys) {
        try {
            if (-not (Test-Path -LiteralPath $key)) { New-Item -Path $key -Force | Out-Null }
            Set-Item -LiteralPath $key -Value 'Service'   # sets the key's (Default) value as REG_SZ
        }
        catch { Write-Warning "Could not register PcGuard for Safe Mode ($key): $($_.Exception.Message)" }
    }
}

function Unregister-PcGuardSafeBoot {
    foreach ($key in $SafeBootKeys) {
        try {
            if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key -Recurse -Force }
        }
        catch { Write-Warning "Could not remove the Safe Mode key ${key}: $($_.Exception.Message)" }
    }
}

function Assert-FolderAcl {
    # Fails if Users, Authenticated Users or Everyone have any write-type right on the folder or anything inside it.
    param([string]$Root)
    $badSids = @('S-1-5-32-545', 'S-1-5-11', 'S-1-1-0')
    $bad = [int]([System.Security.AccessControl.FileSystemRights]'WriteData, AppendData, WriteExtendedAttributes, WriteAttributes, Delete, DeleteSubdirectoriesAndFiles, ChangePermissions, TakeOwnership')
    $items = @(Get-Item -LiteralPath $Root -Force) + @(Get-ChildItem -LiteralPath $Root -Recurse -Force)
    foreach ($item in $items) {
        foreach ($ace in (Get-Acl -LiteralPath $item.FullName).Access) {
            if ($ace.AccessControlType -ne 'Allow') { continue }
            $sid = $null
            try { $sid = $ace.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value } catch { continue }
            if ($badSids -contains $sid -and (([int]$ace.FileSystemRights) -band $bad) -ne 0) {
                throw "Unsafe permission on '$($item.FullName)': $($ace.IdentityReference) has $($ace.FileSystemRights). Installation aborted."
            }
        }
    }
}

function Invoke-Rollback {
    Write-Host 'Rolling back ...' -ForegroundColor Yellow
    Unregister-PcGuardSafeBoot   # best-effort; never throws
    if ($script:recoveryTouched) {
        try {
            if ($null -ne $script:oldRecoveryHash) { Write-RecoveryHashFile $script:oldRecoveryHash; Write-Host 'Restored the previous recovery code hash.' }
            elseif (Test-Path -LiteralPath $RecoveryHashFile) { Remove-Item -LiteralPath $RecoveryHashFile -Force; Write-Host 'Removed the new recovery code hash.' }
        }
        catch { Write-Warning "Could not restore the previous recovery code hash: $($_.Exception.Message)" }
    }
    try {
        if ($script:oldServiceRemoved) {
            # A service that exists now is the new one (or a half-created one): remove it.
            if (Test-ServiceExists) {
                Stop-PcGuardService
                Invoke-Native 'sc.exe' @('delete', $ServiceName) | Out-Null
                try { Wait-ServiceGone } catch { Write-Warning $_.Exception.Message }
            }
        }
        Stop-PcGuardProcesses | Out-Null
        if ($script:newFolderCreated -and $script:target -and (Test-Path -LiteralPath $script:target)) {
            try {
                Invoke-Native 'icacls.exe' @($script:target, '/reset', '/T', '/C', '/Q') | Out-Null
                Remove-Item -LiteralPath $script:target -Recurse -Force
            }
            catch { Write-Warning "Could not remove the half-installed folder '$($script:target)': $($_.Exception.Message)" }
        }
        if ($script:backupDir -and (Test-Path -LiteralPath $script:backupDir)) {
            if (-not (Test-Path -LiteralPath $script:target)) {
                Move-Item -LiteralPath $script:backupDir -Destination $script:target
                Write-Host "Restored the previous install folder: $($script:target)"
            }
            else {
                Write-Warning "Could not restore the old folder: '$($script:target)' still exists. The old files are in '$($script:backupDir)'."
            }
        }
        if ($script:hadService) {
            if ($script:oldServiceRemoved) {
                $oldExe = Join-Path $script:target 'PcGuard.Service.exe'
                if (Test-Path -LiteralPath $oldExe) { Register-PcGuardService -ExePath $oldExe }
            }
            if (Test-ServiceExists) {
                # restore the previous install's Safe Mode registration only if it had one
                if ($script:hadSafeBoot) { Register-PcGuardSafeBoot }
                if ($script:oldStartDisabled -and -not $script:oldServiceRemoved) {
                    # released with the recovery code or disabled by Cleanup: Start-Service would fail; leave it as it was
                    Write-Host 'The previous PcGuard service was disabled and is left disabled and stopped (this PC is NOT protected).' -ForegroundColor Yellow
                }
                else {
                    Start-Service -Name $ServiceName
                    Write-Host 'The previous PcGuard service was restarted.'
                }
            }
        }
    }
    catch {
        Write-Host "Rollback problem: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "WARNING: this PC may now be UNGUARDED (no PcGuard service running). Reboot, then run install.ps1 again; or restore the '<InstallDir>.old-*' folder and re-create the service." -ForegroundColor Red
    }
}

try {
    # --- elevation ---
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'This script must run elevated. Right-click PowerShell, choose "Run as administrator", and run it again.'
    }

    # --- validate the URL (https required, except localhost) ---
    $uri = $null
    if (-not [Uri]::TryCreate($BackendBaseUrl, [UriKind]::Absolute, [ref]$uri)) {
        throw "BackendBaseUrl is not a valid absolute URL: $BackendBaseUrl"
    }
    $isLocal = ($uri.Host -eq 'localhost' -or $uri.Host -eq '127.0.0.1' -or $uri.Host -eq '[::1]' -or $uri.Host -eq '::1')
    if ($uri.Scheme -ne 'https' -and -not ($isLocal -and $uri.Scheme -eq 'http')) {
        throw 'BackendBaseUrl must use https (http is allowed only for localhost).'
    }
    if ($uri.AbsolutePath.TrimEnd('/') -eq '') {
        Write-Warning 'BackendBaseUrl has no path. It should include the API prefix, e.g. https://example.uz/api/v1'
    }
    $baseUrl = $BackendBaseUrl.TrimEnd('/')

    # --- validate -ExtraAllowedApps (refuse before anything is changed) ---
    $extraGiven = $PSBoundParameters.ContainsKey('ExtraAllowedApps')
    $extraApps = New-Object System.Collections.Generic.List[string]
    if ($extraGiven) {
        foreach ($item in @($ExtraAllowedApps)) {
            if ($null -eq $item) { continue }
            foreach ($piece in $item.Split(',')) {
                $name = $piece.Trim()
                if ($name.Length -eq 0) { continue }
                if (-not (Test-ExtraAppName $name)) {
                    throw "Invalid -ExtraAllowedApps value '$name': it must be a bare exe file name ending in .exe, 5-64 characters, only letters A-Z, digits, '.', '-' and '_' (no path, spaces or wildcards). Nothing was changed."
                }
                $lower = $name.ToLowerInvariant()
                if (-not $extraApps.Contains($lower)) { $extraApps.Add($lower) }
            }
        }
        if ($extraApps.Count -gt $MaxExtraApps) {
            throw "Too many -ExtraAllowedApps values ($($extraApps.Count)): at most $MaxExtraApps are allowed. Nothing was changed."
        }
    }

    # --- validate the recovery code hash (refuse before anything is changed; the value is never printed) ---
    $recoveryGiven = $PSBoundParameters.ContainsKey('RecoveryCodeHash')
    if ($recoveryGiven -and $ClearRecoveryCode) {
        throw '-RecoveryCodeHash and -ClearRecoveryCode cannot be combined. Nothing was changed.'
    }
    if ($recoveryGiven -and -not (Test-RecoveryHash $RecoveryCodeHash)) {
        throw ('Invalid -RecoveryCodeHash value: it must be the hash computed by Setup-PcGuard.exe (pbkdf2-sha256$<iterations>$<salt>$<hash>), never the recovery code itself. Nothing was changed.')
    }

    # --- validate the dist folder and the paths ---
    if (-not (Test-Path -LiteralPath $DistDir)) { throw "DistDir not found: $DistDir. Run publish.ps1 first, or pass -DistDir." }
    $dist = (Resolve-Path -LiteralPath $DistDir).Path
    foreach ($f in @('PcGuard.Service.exe', 'PcGuard.Shell.exe', 'appsettings.json')) {
        if (-not (Test-Path -LiteralPath (Join-Path $dist $f))) {
            throw "'$f' not found in DistDir '$dist'. Run publish.ps1 first, or pass -DistDir."
        }
    }
    $target = [System.IO.Path]::GetFullPath($InstallDir).TrimEnd('\')
    $script:target = $target
    if ($target -eq [System.IO.Path]::GetPathRoot($target).TrimEnd('\')) {
        throw "Refusing to install into a drive root: $target"
    }
    $distN = Get-NormalizedDir $dist
    $targetN = Get-NormalizedDir $target
    if ($distN.StartsWith($targetN, [System.StringComparison]::OrdinalIgnoreCase) -or $targetN.StartsWith($distN, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "DistDir ('$dist') and InstallDir ('$target') must not be the same or inside each other."
    }

    # --- upgrade without -ExtraAllowedApps: keep the extra apps of the existing install (re-validated) ---
    if (-not $extraGiven) {
        $oldSettings = Join-Path $target 'appsettings.json'
        if (Test-Path -LiteralPath $oldSettings) {
            try {
                $oldJson = Get-Content -LiteralPath $oldSettings -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($oldJson.PSObject.Properties['Allowlist'] -and $oldJson.Allowlist.PSObject.Properties['ExtraApps']) {
                    foreach ($name in @($oldJson.Allowlist.ExtraApps)) {
                        if ($null -eq $name) { continue }
                        $name = [string]$name
                        if (-not (Test-ExtraAppName $name)) { Write-Warning "Existing extra app '$name' is not a valid name and is dropped."; continue }
                        $lower = $name.ToLowerInvariant()
                        if ($extraApps.Contains($lower)) { continue }
                        if ($extraApps.Count -ge $MaxExtraApps) { Write-Warning "More than $MaxExtraApps existing extra apps; '$name' is dropped."; continue }
                        $extraApps.Add($lower)
                    }
                    if ($extraApps.Count -gt 0) { Write-Host "Keeping the extra apps of the existing install: $($extraApps -join ', ')" }
                }
            }
            catch { Write-Warning "Could not read the extra apps of the existing install ($($_.Exception.Message)); none are kept." }
        }
    }

    # --- stop the old service and shells; abort before touching any folder if they will not die ---
    # remember the current recovery.hash so a failed install can put it back
    if (($recoveryGiven -or $ClearRecoveryCode) -and (Test-Path -LiteralPath $RecoveryHashFile)) {
        $script:oldRecoveryHash = [System.IO.File]::ReadAllText($RecoveryHashFile)
    }

    $script:hadService = Test-ServiceExists
    $script:hadSafeBoot = [bool](Test-Path -LiteralPath $SafeBootKeys[0])
    if ($script:hadService) {
        try { $script:oldStartDisabled = ([int](Get-ItemProperty -LiteralPath $ServiceKey -Name Start -ErrorAction Stop).Start -eq 4) } catch { $script:oldStartDisabled = $false }
        if ($script:oldStartDisabled) {
            Write-Host 'Existing PcGuard service is DISABLED (released with the recovery code, or by Cleanup): it is replaced by a new service with automatic start.'
        }
        Write-Host 'Existing PcGuard service found: stopping it ...'
        Stop-PcGuardService
    }
    $left = @(Stop-PcGuardProcesses)
    if ($left.Count -gt 0) {
        throw "Could not stop: $($left -join ', '). Nothing was changed. Stop them manually (Task Manager as administrator) and run again."
    }

    # --- move the old folder aside ---
    if (Test-Path -LiteralPath $target) {
        $script:backupDir = $target + '.old-' + (Get-Date -Format 'yyyyMMddHHmmss')
        Move-Item -LiteralPath $target -Destination $script:backupDir
    }

    # --- remove the old service registration ---
    if ($script:hadService) {
        Invoke-Sc delete $ServiceName
        $script:oldServiceRemoved = $true
        Wait-ServiceGone
    }
    else {
        $script:oldServiceRemoved = $true   # from here on any service that exists is ours
    }

    # --- copy files into a fresh folder ---
    Write-Host "Copying files to $target ..."
    New-Item -ItemType Directory -Path $target | Out-Null
    $script:newFolderCreated = $true
    Copy-Item -Path (Join-Path $dist '*') -Destination $target -Recurse -Force

    # --- write Backend:BaseUrl into the installed appsettings.json ---
    $settingsPath = Join-Path $target 'appsettings.json'
    $json = Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (-not $json.PSObject.Properties['Backend']) {
        $json | Add-Member -MemberType NoteProperty -Name 'Backend' -Value ([pscustomobject]@{ BaseUrl = $baseUrl })
    }
    elseif (-not $json.Backend.PSObject.Properties['BaseUrl']) {
        $json.Backend | Add-Member -MemberType NoteProperty -Name 'BaseUrl' -Value $baseUrl
    }
    else {
        $json.Backend.BaseUrl = $baseUrl
    }

    # --- write Allowlist:ExtraApps (always an array, possibly empty) ---
    [string[]]$extraArray = $extraApps.ToArray()
    if (-not $json.PSObject.Properties['Allowlist']) {
        $json | Add-Member -MemberType NoteProperty -Name 'Allowlist' -Value ([pscustomobject]@{ ExtraApps = $extraArray })
    }
    elseif (-not $json.Allowlist.PSObject.Properties['ExtraApps']) {
        $json.Allowlist | Add-Member -MemberType NoteProperty -Name 'ExtraApps' -Value $extraArray
    }
    else {
        $json.Allowlist.ExtraApps = $extraArray
    }
    # Windows PowerShell 5.1 can serialise arrays as {"value":[...],"Count":n} because of an extended type
    # definition for System.Array; removing it for this process is the documented workaround.
    if ($PSVersionTable.PSVersion.Major -lt 6) { Remove-TypeData -TypeName System.Array -ErrorAction SilentlyContinue }
    $text = $json | ConvertTo-Json -Depth 10
    # UTF-8 without BOM (Windows PowerShell 5.1 "-Encoding UTF8" would add a BOM).
    [System.IO.File]::WriteAllText($settingsPath, $text, (New-Object System.Text.UTF8Encoding($false)))
    # read it back: the service must see exactly these names as a JSON array
    $check = [System.IO.File]::ReadAllText($settingsPath) | ConvertFrom-Json
    $written = @($check.Allowlist.ExtraApps | Where-Object { $null -ne $_ } | ForEach-Object { [string]$_ })
    if (($written -join ',') -cne ($extraArray -join ',') -or ($extraArray.Count -gt 0 -and $text -notmatch '"ExtraApps"\s*:\s*\[')) {
        throw "Allowlist:ExtraApps was not written correctly to $settingsPath (found: $($written -join ', ')). Installation aborted."
    }

    # --- lock down the install folder ---
    # Well-known SIDs avoid localized group names: S-1-5-18 SYSTEM, S-1-5-32-544 Administrators, S-1-5-32-545 Users.
    # (OI)(CI) = inherit to files and folders; RX = read and execute; F = full control.
    Write-Host 'Setting folder permissions ...'
    Invoke-Native 'icacls.exe' @($target, '/inheritance:r', '/grant:r', '*S-1-5-18:(OI)(CI)F', '*S-1-5-32-544:(OI)(CI)F', '*S-1-5-32-545:(OI)(CI)RX') | Out-Null
    if ($script:NativeExit -ne 0) { throw "icacls failed (exit code $($script:NativeExit))." }
    Assert-FolderAcl -Root $target

    # --- create the service (verifies the quoted ImagePath; throws and removes the service otherwise) ---
    Write-Host 'Registering the PcGuard service ...'
    Register-PcGuardService -ExePath (Join-Path $target 'PcGuard.Service.exe')

    # --- Safe Mode registration (best-effort, UNTESTED; warnings only, never aborts the install) ---
    Register-PcGuardSafeBoot

    # --- recovery code hash (%ProgramData%\PcGuard\recovery.hash; read by the service on each attempt) ---
    if ($recoveryGiven) {
        $script:recoveryTouched = $true
        Write-RecoveryHashFile $RecoveryCodeHash
        $recoveryState = 'set (new)'
    }
    elseif ($ClearRecoveryCode) {
        if (Test-Path -LiteralPath $RecoveryHashFile) {
            $script:recoveryTouched = $true
            Remove-Item -LiteralPath $RecoveryHashFile -Force
        }
        $recoveryState = 'cleared: NOT set (no offline way out)'
    }
    elseif (Test-Path -LiteralPath $RecoveryHashFile) {
        $recoveryState = 'kept (set before)'
    }
    else {
        $recoveryState = 'NOT set (no offline way out)'
    }

    # --- start ---
    Start-Service -Name $ServiceName
    (Get-Service -Name $ServiceName).WaitForStatus('Running', [TimeSpan]::FromSeconds(30))

    # --- success: the old folder is no longer needed ---
    if ($script:backupDir -and (Test-Path -LiteralPath $script:backupDir)) {
        try {
            Invoke-Native 'icacls.exe' @($script:backupDir, '/reset', '/T', '/C', '/Q') | Out-Null
            Remove-Item -LiteralPath $script:backupDir -Recurse -Force
        }
        catch { Write-Warning "The new version is running, but the old folder '$($script:backupDir)' could not be deleted: $($_.Exception.Message)" }
    }

    # --- BEST-EFFORT warning when the signed-in user is an administrator ---
    # Domain / Azure AD / nested-group administrators and RDP sessions may be missed. The operator must verify
    # that student accounts are standard users.
    try {
        $console = (Get-CimInstance -ClassName Win32_ComputerSystem).UserName   # DOMAIN\user of the console user, or $null
        if ($console) {
            $admins = Get-LocalGroupMember -SID 'S-1-5-32-544' -ErrorAction Stop
            $isAdmin = $false
            foreach ($m in $admins) {
                if ($m.Name -ieq $console) { $isAdmin = $true }
            }
            if ($isAdmin) {
                Write-Warning "The signed-in user '$console' is a member of the local Administrators group."
                Write-Warning 'PC Guard assumes students use STANDARD accounts: an administrator can stop the service and bypass it.'
                Write-Warning 'To fix: create a standard account for the student (Settings > Accounts > Other users), or run'
                Write-Warning "  net localgroup Administrators `"$console`" /delete"
                Write-Warning 'as another administrator, then sign out and in again.'
            }
        }
    }
    catch {
        Write-Warning "Could not check whether the signed-in user is an administrator: $($_.Exception.Message)"
    }
    Write-Host 'NOTE: the administrator check above is best-effort (domain, Azure AD, nested-group admins and RDP sessions may be missed).'
    Write-Host 'Verify yourself that every student account is a standard user.'

    Write-Host ''
    Write-Host 'PC Guard installed.' -ForegroundColor Green
    Write-Host "  Install folder : $target"
    Write-Host "  Backend        : $baseUrl"
    if ($extraApps.Count -gt 0) {
        Write-Host "  Extra apps     : $($extraApps -join ', ')"
        Write-Warning 'These extra apps are kept running on this PC even while it is locked. Remote-control software lets anyone at the PC use it while locked: use this only on test/admin PCs.'
    }
    else {
        Write-Host '  Extra apps     : none'
    }
    Write-Host "  Recovery code  : $recoveryState"
    if ($recoveryState -like '*NOT set*') {
        Write-Warning 'No recovery code: if this PC gets stuck on the lock screen without the backend, only Safe Mode or Cleanup-PcGuard.exe (administrator) can free it.'
    }
    Write-Host "  Service        : $ServiceName ($((Get-Service -Name $ServiceName).Status))"
    Write-Host '  The shell is started by the service when a student is signed in to Windows.'
    exit 0
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($script:oldServiceRemoved -or $script:backupDir -or $script:newFolderCreated -or $script:hadService) {
        Invoke-Rollback
    }
    exit 1
}
