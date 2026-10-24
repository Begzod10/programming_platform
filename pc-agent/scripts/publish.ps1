<#
.SYNOPSIS
  Builds PC Guard (service + shell) into one self-contained folder for win-x64.
.DESCRIPTION
  Run on a build machine with the .NET 8 SDK (Windows; WPF needs the Windows desktop targeting pack).
  PcGuard.Service.exe and PcGuard.Shell.exe end up side by side in the output folder, because the
  service launches <its own folder>\PcGuard.Shell.exe.
  NOT TESTED: this script was written on a machine without PowerShell and has never been run.
.PARAMETER OutputDir
  Output folder (default: ..\dist next to the scripts folder). It is deleted and recreated.
.PARAMETER Configuration
  Build configuration (default Release).
#>
[CmdletBinding()]
param(
    [string]$OutputDir = (Join-Path $PSScriptRoot '..\dist'),
    [string]$Configuration = 'Release'
)

$ErrorActionPreference = 'Stop'

try {
    if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
        throw 'dotnet was not found. Install the .NET 8 SDK on this build machine.'
    }

    $root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    $service = Join-Path $root 'src\PcGuard.Service\PcGuard.Service.csproj'
    $shell = Join-Path $root 'src\PcGuard.Shell\PcGuard.Shell.csproj'
    foreach ($p in @($service, $shell)) {
        if (-not (Test-Path $p)) { throw "Project not found: $p" }
    }

    $out = [System.IO.Path]::GetFullPath($OutputDir)
    # Safety: refuse to wipe a drive root or the repo root.
    if ($out.TrimEnd('\') -eq [System.IO.Path]::GetPathRoot($out).TrimEnd('\') -or $out.TrimEnd('\') -eq $root.TrimEnd('\')) {
        throw "Refusing to use '$out' as output folder."
    }
    if (Test-Path $out) { Remove-Item -LiteralPath $out -Recurse -Force }
    New-Item -ItemType Directory -Path $out | Out-Null

    # Plain self-contained folder output. Deliberately NO PublishSingleFile / PublishTrimmed:
    # trimming breaks WPF, and a plain folder keeps StartupHookSupport=false (set in the Shell csproj) in effect.
    # Both projects are published into the SAME folder; the runtime files are identical so overwrites are harmless.
    foreach ($proj in @($service, $shell)) {
        Write-Host "Publishing $(Split-Path $proj -Leaf) ..."
        & dotnet publish $proj -c $Configuration -r win-x64 --self-contained true -o $out
        if ($LASTEXITCODE -ne 0) { throw "dotnet publish failed for $proj (exit code $LASTEXITCODE)." }
    }

    foreach ($exe in @('PcGuard.Service.exe', 'PcGuard.Shell.exe', 'appsettings.json')) {
        if (-not (Test-Path (Join-Path $out $exe))) { throw "Expected file missing in output: $exe" }
    }

    # The shell must keep startup hooks disabled (injection hardening): fail the build otherwise.
    $rc = Join-Path $out 'PcGuard.Shell.runtimeconfig.json'
    if (-not (Test-Path -LiteralPath $rc)) { throw 'PcGuard.Shell.runtimeconfig.json missing in the output.' }
    $cfg = Get-Content -LiteralPath $rc -Raw -Encoding UTF8 | ConvertFrom-Json
    $hookSwitch = $null
    if ($cfg.runtimeOptions -and $cfg.runtimeOptions.configProperties) {
        $hookSwitch = $cfg.runtimeOptions.configProperties.'System.Runtime.EnableStartupHookSupport'
    }
    if ($hookSwitch -ne $false) {
        throw 'PcGuard.Shell.runtimeconfig.json does not set System.Runtime.EnableStartupHookSupport to false. Check StartupHookSupport in PcGuard.Shell.csproj.'
    }

    Write-Host ''
    Write-Host "Done. Output: $out"
    Write-Host 'Next: copy this folder to the target PC and run install.ps1 as Administrator.'
    exit 0
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
