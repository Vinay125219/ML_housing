#!/usr/bin/env bash
set -euo pipefail

SKIP_DOCKER=false
SKIP_TRIVY=true
VERBOSE=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-docker) SKIP_DOCKER=true; shift;;
    --skip-trivy) SKIP_TRIVY=true; shift;;
    --verbose) VERBOSE=true; shift;;
    *) shift;;
  esac
done

section() { echo -e "\n==== $1 ====\n"; }
run() {
  $VERBOSE && echo "> $*" >&2 || true
  eval "$@"
}

# 1) Python setup
section "Check Python"
run python --version
run python -m pip --version

# 2) Install dependencies (like GH Actions)
section "Install dependencies"
run python -m pip install --upgrade pip
run pip install -r requirements.txt

# 3) Linting (same as workflow)
section "Linting (flake8)"
run flake8 src api --count --select=E9,F63,F7,F82 --show-source --statistics
run flake8 src api --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# 4) Prepare directories and data (as in workflow)
section "Prepare directories and data"
mkdir -p models data housinglogs irislogs mlruns
run python src/load_data.py

# 5) Train models (as in workflow)
section "Train models"
run python src/train_and_track.py
run python src/train_iris.py

# 6) Run validation tests
section "Run validation tests"
run python test_validation.py

# 7) Run API endpoint tests
section "Run API endpoint tests"
run python test_api_endpoints.py

# 8) Docker build & optional security scan (simulate workflow)
if ! $SKIP_DOCKER; then
  section "Docker build"
  run docker --version
  run docker build -t local/mlops-housing-pipeline:latest .

  if ! $SKIP_TRIVY; then
    section "Security scan (Trivy)"
    run trivy --version || true
    run trivy image --exit-code 0 --format sarif --output trivy-results.sarif local/mlops-housing-pipeline:latest || true
    echo "Trivy scan completed and saved to trivy-results.sarif"
  fi
fi

section "Summary"
echo "All local CI/CD steps completed successfully."

