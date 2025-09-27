# Start unified backend server (main_fixed) on 8000, wait for health, run ALL Playwright tests, then stop server

$ErrorActionPreference = 'Stop'

# Paths
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $root
$backendRunner = Join-Path $projectRoot 'backend\run_fixed_8000.py'
$healthUrl = 'http://127.0.0.1:8000/health'

# Start server
Write-Host 'Starting backend server on :8000...'
$proc = Start-Process -FilePath python -ArgumentList @("$backendRunner") -WindowStyle Hidden -PassThru

# Wait for health
$maxWait = 30
for ($i=0; $i -lt $maxWait; $i++) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $healthUrl -TimeoutSec 2
    if ($resp.StatusCode -eq 200) { break }
  } catch {}
  Start-Sleep -Seconds 1
}

try {
  # Set BACKEND_URL for tests
  $env:BACKEND_URL = 'http://127.0.0.1:8000'
  # Optional GREP filter: set E2E_GREP env var before calling this script
  if ($env:E2E_GREP) {
    Write-Host "Running Playwright tests with grep: $($env:E2E_GREP) ..."
    npm --prefix "$projectRoot\e2e" run test -- --reporter=list --grep "$env:E2E_GREP"
  } else {
    Write-Host 'Running ALL Playwright tests...'
    npm --prefix "$projectRoot\e2e" run test -- --reporter=list
  }
} finally {
  if ($proc -and !$proc.HasExited) {
    Write-Host "Stopping backend server (PID=$($proc.Id))..."
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
  }
}
