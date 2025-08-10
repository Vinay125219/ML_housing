param(
  [switch]$SkipDocker = $false,
  [switch]$SkipTrivy = $true,
  [switch]$VerboseLogs = $true
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Section($name) {
  Write-Host "`n==== $name ====\n" -ForegroundColor Cyan
}

function Run($cmd, $cwd = $PWD) {
  if ($VerboseLogs) { Write-Host "> $cmd" -ForegroundColor DarkGray }
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = 'powershell'
  $psi.Arguments = ('-NoProfile -ExecutionPolicy Bypass -Command "' + $cmd + '"')
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $psi.WorkingDirectory = $cwd
  $proc = New-Object System.Diagnostics.Process
  $proc.StartInfo = $psi
  [void]$proc.Start()
  $stdout = $proc.StandardOutput.ReadToEnd()
  $stderr = $proc.StandardError.ReadToEnd()
  $proc.WaitForExit()
  if ($stdout) { Write-Host $stdout }
  if ($stderr) { Write-Host $stderr -ForegroundColor Yellow }
  if ($proc.ExitCode -ne 0) {
    throw "Command failed ($($proc.ExitCode)): $cmd"
  }
}

# 1) Python setup
Section "Check Python"
Run "python --version"
Run "python -m pip --version"

# 2) Install dependencies (like GH Actions)
Section "Install dependencies"
Run "python -m pip install --upgrade pip"
Run "pip install -r requirements.txt"

# 3) Linting (same as workflow)
Section "Linting (flake8)"
Run "flake8 src api --count --select=E9,F63,F7,F82 --show-source --statistics"
Run "flake8 src api --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics"

# 4) Prepare directories and data (as in workflow)
Section "Prepare directories and data"
New-Item -ItemType Directory -Force -Path models,data,housinglogs,irislogs,mlruns | Out-Null
Run "python src/load_data.py"

# 5) Train models (as in workflow)
Section "Train models"
Run "python src/train_and_track.py"
Run "python src/train_iris.py"

# 6) Run validation tests
Section "Run validation tests"
Run "python test_validation.py"

# 7) Run API endpoint tests
Section "Run API endpoint tests"
Run "python test_api_endpoints.py"

# 8) Docker build & optional security scan (simulate workflow)
if (-not $SkipDocker) {
  Section "Docker build"
  try {
    Run "docker --version"
    Run "docker build -t local/mlops-housing-pipeline:latest ."
  } catch {
    Write-Warning "Docker build failed: $($_.Exception.Message). You can rerun with -SkipDocker to bypass or fix Docker Desktop."
    throw
  }

  if (-not $SkipTrivy) {
    Section "Security scan (Trivy)"
    try {
      Run "trivy --version"
      Run "trivy image --exit-code 0 --format sarif --output trivy-results.sarif local/mlops-housing-pipeline:latest"
      Write-Host "Trivy scan completed and saved to trivy-results.sarif"
    } catch {
      Write-Warning "Trivy scan failed or not installed: $($_.Exception.Message)"
    }
  }
}

Section "Summary"
Write-Host "All local CI/CD steps completed successfully." -ForegroundColor Green
exit 0

