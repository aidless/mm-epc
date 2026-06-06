# PowerShell script to compile LaTeX paper with MikTeX
$MikTeXPath = "C:\Users\Administrator\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
$PaperDir = "C:\Users\Administrator\Desktop\aettl-research\paper"
$OutputDir = "C:\Users\Administrator\Desktop\aettl-research\paper"

# Add MikTeX to PATH for this session
$env:PATH = "$MikTeXPath;$env:PATH"

Write-Host "=== Compiling MM-EPC Paper ===" -ForegroundColor Green
Write-Host "Paper directory: $PaperDir"
Write-Host "MikTeX path: $MikTeXPath"

# Check if pdflatex is available
try {
    $pdflatex = Get-Command pdflatex -ErrorAction Stop
    Write-Host "Found pdflatex: $($pdflatex.Source)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: pdflatex not found in PATH" -ForegroundColor Red
    Write-Host "Current PATH: $env:PATH" -ForegroundColor Yellow
    exit 1
}

# Change to paper directory
Set-Location $PaperDir

# Step 1: First pdflatex pass
Write-Host "`n[1/4] First pdflatex pass..." -ForegroundColor Cyan
& pdflatex -interaction=nonstopmode -output-directory=$OutputDir mm_epc_paper.tex 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: First pdflatex pass had errors (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
}

# Step 2: BibTeX
Write-Host "[2/4] Running BibTeX..." -ForegroundColor Cyan
& bibtex mm_epc_paper 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: BibTeX had errors (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
}

# Step 3: Second pdflatex pass
Write-Host "[3/4] Second pdflatex pass..." -ForegroundColor Cyan
& pdflatex -interaction=nonstopmode -output-directory=$OutputDir mm_epc_paper.tex 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Second pdflatex pass had errors (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
}

# Step 4: Final pdflatex pass
Write-Host "[4/4] Final pdflatex pass..." -ForegroundColor Cyan
& pdflatex -interaction=nonstopmode -output-directory=$OutputDir mm_epc_paper.tex 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Final pdflatex pass had errors (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
}

# Check if PDF was created
$pdfPath = Join-Path $OutputDir "mm_epc_paper.pdf"
if (Test-Path $pdfPath) {
    $pdfSize = (Get-Item $pdfPath).Length / 1KB
    Write-Host "`n✅ SUCCESS: PDF generated: $pdfPath" -ForegroundColor Green
    Write-Host "   Size: $pdfSize KB" -ForegroundColor Green
    
    # Open PDF if requested
    if ($args[0] -eq "-open") {
        Write-Host "Opening PDF..." -ForegroundColor Cyan
        Start-Process $pdfPath
    }
} else {
    Write-Host "`n❌ ERROR: PDF not created" -ForegroundColor Red
    exit 1
}

# Clean up auxiliary files
Write-Host "`nCleaning up auxiliary files..." -ForegroundColor Gray
$auxFiles = @("*.aux", "*.log", "*.bbl", "*.blg", "*.out", "*.toc", "*.lof", "*.lot")
foreach ($pattern in $auxFiles) {
    Get-ChildItem -Path $OutputDir -Filter $pattern -ErrorAction SilentlyContinue | Remove-Item -Force
}

Write-Host "`n=== Compilation Complete ===" -ForegroundColor Green
Write-Host "To open PDF: Start-Process '$pdfPath'" -ForegroundColor Cyan