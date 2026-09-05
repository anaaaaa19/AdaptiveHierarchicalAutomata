# PowerShell Setup Script for Adaptive Automata Engine
# Environment verification and dependency installation

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Adaptive Automata Engine — Environment Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check Python installation
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}
Write-Host "Detected Python: $pythonVersion" -ForegroundColor Green

# Install dependencies
Write-Host "Installing requirements from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements."
    exit 1
}

Write-Host "Environment setup completed successfully." -ForegroundColor Green
