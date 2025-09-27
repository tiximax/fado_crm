# Start unified backend server (main_fixed) on 8000, wait for health, run VNPay tests, then stop server

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
  Write-Host 'Running Playwright VNPay tests...'
  npm --prefix "$projectRoot\e2e" run test -- --reporter=list --grep "VNPay"
} finally {
  if ($proc -and !$proc.HasExited) {
    Write-Host "Stopping backend server (PID=$($proc.Id))..."
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
  }
}
