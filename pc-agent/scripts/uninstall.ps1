<#
.SYNOPSIS
  Removes the PC Guard service and its install folder. Run in an elevated PowerShell.
.PARAMETER InstallDir
  Install folder (default: 64-bit Program Files\PcGuard).
.PARAMETER Purge
  Also delete %ProgramData%\PcGuard (machine key, cached rules, usage queue). Without it they are kept.
  NOT TESTED: written without PowerShell available; run the VM checklist in README.md.
  Compatible with Windows PowerShell 5.1 and PowerShell 7.
#>
[CmdletBinding()]
param(
    [string]$InstallDir = (Join-Path $(if ($env:ProgramW6432) { $env:ProgramW6432 } else { $env:ProgramFiles }) 'PcGuard'),
    [switch]$Purge
)

$ErrorActionPreference = 'Stop'
$ServiceName = 'PcGuard'

function Invoke-Native {
    # Runs a native program without letting stderr text become a terminating error (Windows PowerShell 5.1).
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

try {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'This script must run elevated. Right-click PowerShell, choose "Run as administrator", and run it again.'
    }

    $target = [System.IO.Path]::GetFullPath($InstallDir).TrimEnd('\')
    if ($target -eq [System.IO.Path]::GetPathRoot($target).TrimEnd('\')) {
        throw "Refusing to delete a drive root: $target"
    }

    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        Write-Host 'Stopping and deleting the PcGuard service ...'
        $svc = Get-Service -Name $ServiceName
        if ($svc.Status -ne 'Stopped') {
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            try { $svc.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(30)) } catch { Write-Warning 'Service did not report Stopped within 30 s; continuing.' }
        }
        $out = Invoke-Native 'sc.exe' @('delete', $ServiceName)
        if ($script:NativeExit -ne 0) { throw "sc.exe delete failed (exit code $($script:NativeExit)): $($out -join ' ')" }
        $deadline = (Get-Date).AddSeconds(30)
        while ((Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
        if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
            Write-Warning 'The PcGuard service is still registered (marked for deletion because something holds an open handle, for example Services or Event Viewer windows).'
            Write-Warning 'Close those windows or reboot, then run uninstall.ps1 again. No files were deleted.'
            exit 1
        }
    }
    else {
        Write-Host 'No PcGuard service registered.'
    }

    # Remove the Safe Mode registration added by install.ps1 (best-effort; that feature is UNTESTED).
    foreach ($key in @('HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal\PcGuard',
                       'HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Network\PcGuard')) {
        try {
            if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key -Recurse -Force }
        }
        catch { Write-Warning "Could not remove the Safe Mode key ${key}: $($_.Exception.Message)" }
    }

    foreach ($name in @('PcGuard.Shell', 'PcGuard.Service')) {
        Stop-Process -Name $name -Force -ErrorAction SilentlyContinue
        if (Get-Process -Name $name -ErrorAction SilentlyContinue) {
            Invoke-Native 'taskkill.exe' @('/f', '/im', "$name.exe") | Out-Null
        }
    }
    Start-Sleep -Seconds 1

    if (Test-Path -LiteralPath $target) {
        Write-Host "Removing $target ..."
        try {
            Invoke-Native 'icacls.exe' @($target, '/reset', '/T', '/C', '/Q') | Out-Null
            Remove-Item -LiteralPath $target -Recurse -Force
        }
        catch {
            throw "Could not remove '$target': $($_.Exception.Message). A file may still be in use; stop PcGuard processes and run again."
        }
    }

    $data = Join-Path $env:ProgramData 'PcGuard'
    if ($Purge) {
        if (Test-Path -LiteralPath $data) {
            Write-Host "Purging $data ..."
            # No "icacls /reset" here: it would briefly expose machine.key through inherited rights.
            # Administrators already have full control of this folder.
            try {
                Remove-Item -LiteralPath $data -Recurse -Force
            }
            catch {
                throw "Could not remove '$data': $($_.Exception.Message)"
            }
        }
    }
    elseif (Test-Path -LiteralPath $data) {
        Write-Host "Kept $data (machine key, rules, usage queue). Use -Purge to delete it."
    }

    Write-Host 'PC Guard uninstalled.' -ForegroundColor Green
    Write-Host 'Per-user shell logs in %LocalAppData%\PcGuard\shell.log of each student are not removed.'
    exit 0
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
