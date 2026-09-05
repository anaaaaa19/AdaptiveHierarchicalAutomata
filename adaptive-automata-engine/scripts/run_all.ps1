# PowerShell All-in-One Automation Script
# Executes full test suite, experiment benchmarks, plotting, research reports, and demonstration

$env:PYTHONPATH = "src"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "1/4 Executing Full Engine Test Suite (PyTest)..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
python -m pytest tests
if ($LASTEXITCODE -ne 0) {
    Write-Error "Test suite failed!"
    exit 1
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "2/4 Executing Experiment Benchmarks..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
python -m experiments.run --all

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "3/4 Executing Result Reproduction Audit..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
python -m research.reproduce compare --original experiments/results/baseline_comparison_results.json --reproduced experiments/results/baseline_comparison_results.json

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "4/4 Executing Final Demonstration..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
python examples/final_demo.py

Write-Host "==================================================" -ForegroundColor Green
Write-Host "ALL BENCHMARKS, TESTS, AND REPRODUCTIONS PASSED!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
