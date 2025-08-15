param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Git Version Tagging Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Creating tag: v$Version" -ForegroundColor Yellow
Write-Host "Message: $Message" -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "[1/2] Creating annotated tag..." -ForegroundColor Green
    
    # Create the annotated tag
    git tag -a "v$Version" -m "$Message"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tag created successfully" -ForegroundColor Green
    } else {
        throw "Failed to create tag"
    }
    
    Write-Host ""
    Write-Host "[2/2] Pushing tag to remote..." -ForegroundColor Green
    
    # Push the tag to remote
    git push origin "v$Version"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tag pushed to remote successfully" -ForegroundColor Green
    } else {
        throw "Failed to push tag"
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ Version tagged successfully!" -ForegroundColor Green
    Write-Host "✅ Tag: v$Version" -ForegroundColor Green
    Write-Host "✅ Pushed to remote: origin/v$Version" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
