param(
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Crowdin Editor Button App Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Commit message: $CommitMessage" -ForegroundColor Yellow
Write-Host ""

try {
    # Step 1: Git operations
    Write-Host "[1/4] Git: Adding, committing, and pushing changes..." -ForegroundColor Blue
    
    & git add .
    if ($LASTEXITCODE -ne 0) { throw "Git add failed" }
    
    & git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) { throw "Git commit failed" }
    
    & git push
    if ($LASTEXITCODE -ne 0) { throw "Git push failed" }
    
    Write-Host "✅ Git operations completed successfully" -ForegroundColor Green
    Write-Host ""

    # Step 2: Vercel deployment
    Write-Host "[2/4] Vercel: Deploying to production..." -ForegroundColor Blue
    
    $deployOutput = & npx vercel --prod --yes 2>&1
    if ($LASTEXITCODE -ne 0) { 
        Write-Host $deployOutput -ForegroundColor Red
        throw "Vercel deployment failed" 
    }
    
    # Extract deployment URL
    $deploymentUrl = ($deployOutput | Select-String "Production:").ToString().Split()[1]
    if (-not $deploymentUrl) { throw "Could not extract deployment URL" }
    
    Write-Host "✅ Deployed to: $deploymentUrl" -ForegroundColor Green
    Write-Host ""

    # Step 3: Create alias
    Write-Host "[3/4] Vercel: Creating alias..." -ForegroundColor Blue
    
    & npx vercel alias $deploymentUrl editor-button-app.vercel.app
    if ($LASTEXITCODE -ne 0) { throw "Vercel alias failed" }
    
    Write-Host "✅ Aliased to: https://editor-button-app.vercel.app" -ForegroundColor Green
    Write-Host ""

    # Step 4: Final summary
    Write-Host "[4/4] Deployment Summary:" -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ Git: Changes committed and pushed" -ForegroundColor Green
    Write-Host "✅ Vercel: Deployed to production" -ForegroundColor Green
    Write-Host "✅ Alias: https://editor-button-app.vercel.app" -ForegroundColor Green
    Write-Host "✅ Inspect: https://vercel.com/digitalpros-projects/editor-button-app" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    Write-Host "The app is now live and ready for testing in Crowdin." -ForegroundColor Yellow
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Deployment failed. Please check the error above and try again." -ForegroundColor Yellow
    exit 1
}
