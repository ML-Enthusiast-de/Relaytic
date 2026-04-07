param(
    [ValidateSet("core", "full", "dev")]
    [string]$Profile = "full",
    [switch]$LaunchControlCenter = $true,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RelayticArgs
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$venvDir = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\\python.exe"

if (-not (Test-Path $venvPython)) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & py -3.11 -m venv $venvDir
    } else {
        & python -m venv $venvDir
    }
}

Push-Location $repoRoot
try {
    & $venvPython -m pip install --upgrade pip
    $command = @("scripts/install_relaytic.py", "--profile", $Profile)
    if ($LaunchControlCenter) {
        $command += "--launch-control-center"
    }
    if ($RelayticArgs) {
        $command += $RelayticArgs
    }
    & $venvPython @command
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
