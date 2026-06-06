# Create arXiv submission package for MM-EPC paper

$BaseDir = "C:\Users\Administrator\Desktop\aettl-research"
$PaperDir = "$BaseDir\paper"
$FiguresDir = "$BaseDir\figures"
$OutputDir = "$BaseDir\arxiv_submission"
$TempDir = "$BaseDir\temp_arxiv"

Write-Host "=== Creating arXiv Submission Package ===" -ForegroundColor Green

# Create clean directories
Remove-Item -Path $OutputDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

# 1. Copy essential LaTeX files
Write-Host "[1/4] Copying LaTeX source files..." -ForegroundColor Cyan
$essentialFiles = @(
    "mm_epc_paper.tex",
    "mm_epc_paper.bib",
    "references.bib"
)

foreach ($file in $essentialFiles) {
    $source = Join-Path $PaperDir $file
    if (Test-Path $source) {
        Copy-Item $source $TempDir
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $file not found" -ForegroundColor Yellow
    }
}

# 2. Copy figures
Write-Host "[2/4] Copying figures..." -ForegroundColor Cyan
if (Test-Path $FiguresDir) {
    $figures = Get-ChildItem $FiguresDir -Filter "*.png" -File
    $figures += Get-ChildItem $FiguresDir -Filter "*.pdf" -File
    
    foreach ($fig in $figures) {
        Copy-Item $fig.FullName $TempDir
        Write-Host "  ✓ $($fig.Name)" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠ Figures directory not found: $FiguresDir" -ForegroundColor Yellow
}

# 3. Create required .bbl file if missing
Write-Host "[3/4] Generating .bbl file..." -ForegroundColor Cyan
$bblPath = Join-Path $TempDir "mm_epc_paper.bbl"
if (-not (Test-Path $bblPath)) {
    # Try to copy from paper directory
    $sourceBbl = Join-Path $PaperDir "mm_epc_paper.bbl"
    if (Test-Path $sourceBbl) {
        Copy-Item $sourceBbl $TempDir
        Write-Host "  ✓ Copied existing .bbl file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ .bbl file not found - arXiv may need it" -ForegroundColor Yellow
    }
}

# 4. Create README for arXiv
$readmeContent = @"
arXiv Submission: Multi-Modal Emergent Policy Contagion (MM-EPC)

Files included:
- mm_epc_paper.tex: Main LaTeX source
- mm_epc_paper.bib: Bibliography (BibTeX format)
- references.bib: Additional references
- *.png/*.pdf: Figures (5 total)

Compilation instructions:
1. pdflatex mm_epc_paper.tex
2. bibtex mm_epc_paper
3. pdflatex mm_epc_paper.tex
4. pdflatex mm_epc_paper.tex

Required packages (standard LaTeX):
- graphicx, booktabs, amsmath, amssymb, hyperref

The paper has been successfully compiled with MiKTeX 25.12.

Contact: [TODO: Add contact email]
"@

Set-Content -Path (Join-Path $TempDir "README.txt") -Value $readmeContent

# 5. Create tar.gz archive
Write-Host "[4/4] Creating tar.gz archive..." -ForegroundColor Cyan
$archivePath = Join-Path $OutputDir "mm_epc_arxiv_submission.tar.gz"

# Using 7zip if available
$7zipPath = "C:\Program Files\7-Zip\7z.exe"
if (Test-Path $7zipPath) {
    & $7zipPath a -ttar -so "$TempDir\*" | & $7zipPath a -si "$archivePath"
} else {
    # Fallback: create zip file
    $zipPath = Join-Path $OutputDir "mm_epc_arxiv_submission.zip"
    Compress-Archive -Path "$TempDir\*" -DestinationPath $zipPath -Force
    $archivePath = $zipPath
    Write-Host "  ⚠ Using zip instead of tar.gz (7-Zip not found)" -ForegroundColor Yellow
}

# 6. Copy PDF for reference
Copy-Item (Join-Path $PaperDir "mm_epc_paper.pdf") $OutputDir

# Summary
Write-Host "`n=== Package Created Successfully ===" -ForegroundColor Green
Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan

$files = Get-ChildItem $TempDir -File
Write-Host "`nFiles included ($($files.Count) total):" -ForegroundColor Cyan
$files | ForEach-Object { Write-Host "  • $($_.Name) ($([math]::Round($_.Length/1KB,1)) KB)" -ForegroundColor Gray }

Write-Host "`nArchive size: $([math]::Round((Get-Item $archivePath).Length/1KB,1)) KB" -ForegroundColor Green
Write-Host "PDF size: $([math]::Round((Get-Item (Join-Path $OutputDir "mm_epc_paper.pdf")).Length/1KB,1)) KB" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Upload $((Get-Item $archivePath).Name) to arXiv" -ForegroundColor White
Write-Host "2. Fill metadata: cs.AI + cs.LG categories" -ForegroundColor White
Write-Host "3. Add abstract and keywords" -ForegroundColor White
Write-Host "4. Submit for moderation" -ForegroundColor White

# Cleanup
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue