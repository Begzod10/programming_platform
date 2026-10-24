<#
.SYNOPSIS
  Installs (or upgrades) the PC Guard service. Run in an elevated PowerShell.
.DESCRIPTION
  Copies the published folder to the install directory, writes Backend:BaseUrl into the installed
  appsettings.json, locks the folder down, registers the PcGuard service (LocalSystem, automatic start,
  restart on failure) and starts it. The shell (PcGuard.Shell.exe) is launched ONLY by the service:
  this script deliberately registers no Run key, scheduled task or Startup shortcut for it.
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
.EXAMPLE
  .\install.ps1 -BackendBaseUrl https://example.uz/api/v1
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BackendBaseUrl,
    [string]$DistDir = (Join-Path $PSScriptRoot '..\dist'),
    [string]$InstallDir = (Join-Path $(if ($env:ProgramW6432) { $env:ProgramW6432 } else { $env:ProgramFiles }) 'PcGuard')
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
                Start-Service -Name $ServiceName
                Write-Host 'The previous PcGuard service was restarted.'
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

    # --- stop the old service and shells; abort before touching any folder if they will not die ---
    $script:hadService = Test-ServiceExists
    if ($script:hadService) {
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
    $text = $json | ConvertTo-Json -Depth 10
    # UTF-8 without BOM (Windows PowerShell 5.1 "-Encoding UTF8" would add a BOM).
    [System.IO.File]::WriteAllText($settingsPath, $text, (New-Object System.Text.UTF8Encoding($false)))

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
