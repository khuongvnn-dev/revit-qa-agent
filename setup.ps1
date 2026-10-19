# ==============================================================================
# SCRIPT CÀI ĐẶT TỰ ĐỘNG CHO THÀNH VIÊN MỚI (ONE-CLICK SETUP)
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   KHOI TAO MOI TRUONG CHO REVIT-QA-AGENT" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Kiểm tra Python
Write-Host "[1/4] Kiem tra phien ban Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "  -> Tim thay: $pyVersion" -ForegroundColor Green
} catch {
    Write-Error "Khong tim thay Python! Vui long cai dat Python 3.10 tro len."
    exit 1
}

# 2. Khoi tao Virtual Environment .venv
$venvDir = Join-Path $PSScriptRoot ".venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "[2/4] Dang tao moi truong ao (.venv)..." -ForegroundColor Yellow
    python -m venv $venvDir
    Write-Host "  -> Da tao moi truong ao tai: $venvDir" -ForegroundColor Green
} else {
    Write-Host "[2/4] Moi truong ao (.venv) da ton tai san." -ForegroundColor Green
}

# 3. Cai dat thu vien phu thuoc bang uv hoac pip
Write-Host "[3/4] Dang cai dat cac thu vien phu thuoc..." -ForegroundColor Yellow
$pyExe = Join-Path $venvDir "Scripts\python.exe"

$hasUv = Get-Command uv -ErrorAction SilentlyContinue
if ($hasUv) {
    Write-Host "  -> Su dung uv de tang toc cai dat..." -ForegroundColor Cyan
    & uv pip install -r (Join-Path $PSScriptRoot "requirements.txt") --python $pyExe
} else {
    Write-Host "  -> Su dung pip tieu chuan de cai dat..." -ForegroundColor Cyan
    & $pyExe -m pip install --upgrade pip
    & $pyExe -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
}

# 4. Khoi tao file config.yaml neu chua co
Write-Host "[4/4] Kiem tra file cau hinh config.yaml..." -ForegroundColor Yellow
$configFile = Join-Path $PSScriptRoot "config.yaml"
$exampleConfig = Join-Path $PSScriptRoot "config.example.yaml"

if (-not (Test-Path $configFile)) {
    if (Test-Path $exampleConfig) {
        Copy-Item -Path $exampleConfig -Destination $configFile
        Write-Host "  -> Da sao chep config.example.yaml -> config.yaml!" -ForegroundColor Green
        Write-Host "  -> VUI LONG MO config.yaml VA DIEN DUONG DAN REVIT CUA BAN!" -ForegroundColor Magenta
    }
} else {
    Write-Host "  -> File config.yaml da co san tren may cua ban." -ForegroundColor Green
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "   CAI DAT HOAN TAT THANH CONG!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Cach su dung:" -ForegroundColor White
Write-Host "  1. Kich hoat moi truong:  .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  2. Xem danh sach test:    python main.py --list" -ForegroundColor Gray
Write-Host "  3. Chay thu nghiem demo:  python main.py --test test_catalog/mep_tools/tc_42554_scopebox.yaml" -ForegroundColor Gray
