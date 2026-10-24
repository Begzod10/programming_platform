<#
.SYNOPSIS
  Removes the PC Guard service and its install folder. Run in an elevated PowerShell.
.PARAMETER InstallDir
  Install folder (default %ProgramFiles%\PcGuard).
.PARAMETER Purge
  Also delete %ProgramData%\PcGuard (machine key, cached rules, usage queue). Without it they are kept.
  NOT TESTED: written without PowerShell available; run the VM checklist in README.md.
#>
[CmdletBinding()]
param(
    [string]$InstallDir = (Join-Path $env:ProgramFiles 'PcGuard'),
    [switch]$Purge
)

$ErrorActionPreference = 'Stop'
$ServiceName = 'PcGuard'

try {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'This script must run elevated. Right-click PowerShell, choose "Run as administrator", and run it again.'
    }

    $target = [System.IO.Path]::GetFullPath($InstallDir)
    if ($target.TrimEnd('\') -eq [System.IO.Path]::GetPathRoot($target).TrimEnd('\')) {
        throw "Refusing to delete a drive root: $target"
    }

    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        Write-Host 'Stopping and deleting the PcGuard service ...'
        $svc = Get-Service -Name $ServiceName
        if ($svc.Status -ne 'Stopped') {
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            try { $svc.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(30)) } catch { Write-Warning 'Service did not report Stopped within 30 s; continuing.' }
        }
        $output = & sc.exe delete $ServiceName 2>&1
        if ($LASTEXITCODE -ne 0) { throw "sc.exe delete failed (exit code $LASTEXITCODE): $($output -join ' ')" }
        $deadline = (Get-Date).AddSeconds(30)
        while ((Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
    }
    else {
        Write-Host 'No PcGuard service registered.'
    }

    foreach ($name in @('PcGuard.Shell', 'PcGuard.Service')) {
        Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
            try { $_.Kill(); $_.WaitForExit(5000) | Out-Null } catch { Write-Warning "Could not stop $name pid $($_.Id): $($_.Exception.Message)" }
        }
    }

    if (Test-Path -LiteralPath $target) {
        Write-Host "Removing $target ..."
        # The folder ACL gives Users read-only; Administrators/SYSTEM have full control, but reset first to be safe.
        & icacls.exe $target /reset /T /C /Q | Out-Null
        Remove-Item -LiteralPath $target -Recurse -Force
    }

    $data = Join-Path $env:ProgramData 'PcGuard'
    if ($Purge) {
        if (Test-Path -LiteralPath $data) {
            Write-Host "Purging $data ..."
            & icacls.exe $data /reset /T /C /Q | Out-Null   # ASSUMPTION: Administrators may take it; the folder grants them full control already
            Remove-Item -LiteralPath $data -Recurse -Force
        }
    }
    elseif (Test-Path -LiteralPath $data) {
        Write-Host "Kept $data (machine key, rules, usage queue). Use -Purge to delete it."
    }

    Write-Host 'PC Guard uninstalled.' -ForegroundColor Green
    Write-Host "Per-user shell logs in %LocalAppData%\PcGuard\shell.log of each student are not removed."
    exit 0
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
