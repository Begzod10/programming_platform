<#
.SYNOPSIS
  Installs (or upgrades) the PC Guard service. Run in an elevated PowerShell.
.DESCRIPTION
  Copies the published folder to the install directory, writes Backend:BaseUrl into the installed
  appsettings.json, locks the folder down, registers the PcGuard service (LocalSystem, automatic start,
  restart on failure) and starts it. The shell (PcGuard.Shell.exe) is launched ONLY by the service:
  this script deliberately registers no Run key, scheduled task or Startup shortcut for it.
  NOT TESTED: written without PowerShell available; run the VM checklist in README.md.
.PARAMETER BackendBaseUrl
  Backend API base URL including the /api/v1 prefix, e.g. https://example.uz/api/v1.
  Must be https, except for localhost / 127.0.0.1 / [::1].
.PARAMETER DistDir
  Output folder of publish.ps1 (default ..\dist relative to this script).
.PARAMETER InstallDir
  Target folder (default %ProgramFiles%\PcGuard).
.EXAMPLE
  .\install.ps1 -BackendBaseUrl https://example.uz/api/v1
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BackendBaseUrl,
    [string]$DistDir = (Join-Path $PSScriptRoot '..\dist'),
    [string]$InstallDir = (Join-Path $env:ProgramFiles 'PcGuard')
)

$ErrorActionPreference = 'Stop'
$ServiceName = 'PcGuard'

function Invoke-Sc {
    # Runs sc.exe (NOT "sc", which is an alias of Set-Content in PowerShell) and fails on a non-zero exit code.
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ScArgs)
    $output = & sc.exe @ScArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "sc.exe $($ScArgs -join ' ') failed (exit code $LASTEXITCODE): $($output -join ' ')"
    }
}

function Test-ServiceExists {
    return [bool](Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)
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

    # --- validate the dist folder ---
    $dist = [System.IO.Path]::GetFullPath($DistDir)
    foreach ($f in @('PcGuard.Service.exe', 'PcGuard.Shell.exe', 'appsettings.json')) {
        if (-not (Test-Path -LiteralPath (Join-Path $dist $f))) {
            throw "'$f' not found in DistDir '$dist'. Run publish.ps1 first, or pass -DistDir."
        }
    }
    $target = [System.IO.Path]::GetFullPath($InstallDir)
    if ($target.TrimEnd('\') -eq [System.IO.Path]::GetPathRoot($target).TrimEnd('\')) {
        throw "Refusing to install into a drive root: $target"
    }
    if ($target.TrimEnd('\') -eq $dist.TrimEnd('\')) {
        throw 'InstallDir and DistDir must be different folders.'
    }

    # --- stop and remove an existing service (upgrade path) ---
    if (Test-ServiceExists) {
        Write-Host 'Existing PcGuard service found: stopping and removing it ...'
        $svc = Get-Service -Name $ServiceName
        if ($svc.Status -ne 'Stopped') {
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            try { $svc.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(30)) } catch { Write-Warning 'Service did not report Stopped within 30 s; continuing.' }
        }
        Invoke-Sc delete $ServiceName
        # The SCM keeps a service "marked for deletion" until handles close; wait until it is gone.
        $deadline = (Get-Date).AddSeconds(30)
        while ((Test-ServiceExists) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
        if (Test-ServiceExists) { throw 'The old PcGuard service is still registered after 30 s. Close Services/Event Viewer windows or reboot, then run again.' }
    }

    # --- kill leftover shells (they may hold the exe open) ---
    Get-Process -Name 'PcGuard.Shell' -ErrorAction SilentlyContinue | ForEach-Object {
        try { $_.Kill(); $_.WaitForExit(5000) | Out-Null } catch { Write-Warning "Could not stop shell pid $($_.Id): $($_.Exception.Message)" }
    }
    Get-Process -Name 'PcGuard.Service' -ErrorAction SilentlyContinue | ForEach-Object {
        try { $_.Kill(); $_.WaitForExit(5000) | Out-Null } catch { Write-Warning "Could not stop service process pid $($_.Id): $($_.Exception.Message)" }
    }

    # --- copy files ---
    Write-Host "Copying files to $target ..."
    if (Test-Path -LiteralPath $target) {
        # Reset ACLs first so the (possibly locked-down) old folder can be overwritten, then replace the contents.
        & icacls.exe $target /reset /T /C /Q | Out-Null
        Get-ChildItem -LiteralPath $target -Force | Remove-Item -Recurse -Force
    }
    else {
        New-Item -ItemType Directory -Path $target | Out-Null
    }
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
    & icacls.exe $target /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "icacls failed (exit code $LASTEXITCODE)." }

    # --- create the service ---
    $exe = Join-Path $target 'PcGuard.Service.exe'
    Write-Host 'Registering the PcGuard service ...'
    # ASSUMPTION: the embedded literal quotes make the SCM store a quoted path (Program Files contains a space).
    # The result is verified below with "sc.exe qc".
    Invoke-Sc create $ServiceName 'binPath=' "`"$exe`"" 'start=' 'auto' 'obj=' 'LocalSystem' 'DisplayName=' 'PC Guard'
    Invoke-Sc description $ServiceName 'PC Guard: controls which programs students may run on this computer.'
    Invoke-Sc failure $ServiceName 'reset=' '0' 'actions=' 'restart/5000/restart/5000/restart/5000'
    Invoke-Sc failureflag $ServiceName 1

    $qc = (& sc.exe qc $ServiceName 2>&1) -join "`n"
    if ($qc -notmatch [regex]::Escape($exe)) {
        Write-Warning "sc.exe qc does not show the expected binary path. Check it by hand:`n$qc"
    }

    # --- start ---
    Start-Service -Name $ServiceName
    (Get-Service -Name $ServiceName).WaitForStatus('Running', [TimeSpan]::FromSeconds(30))

    # --- warn when the signed-in user is an administrator ---
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
    exit 1
}
