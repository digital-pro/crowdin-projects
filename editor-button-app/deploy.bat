@echo off
echo ========================================
echo  Crowdin Editor Button App Deployment
echo ========================================
echo.

REM Check if commit message was provided
if "%~1"=="" (
    echo Error: Please provide a commit message
    echo Usage: deploy.bat "Your commit message"
    pause
    exit /b 1
)

set COMMIT_MESSAGE=%~1
echo Commit message: %COMMIT_MESSAGE%
echo.

REM Step 1: Git add, commit, and push
echo [1/4] Git: Adding, committing, and pushing changes...
git add .
if errorlevel 1 (
    echo Error: Git add failed
    pause
    exit /b 1
)

git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 (
    echo Error: Git commit failed
    pause
    exit /b 1
)

git push
if errorlevel 1 (
    echo Error: Git push failed
    pause
    exit /b 1
)
echo ✅ Git operations completed successfully
echo.

REM Step 2: Deploy to Vercel
echo [2/4] Vercel: Deploying to production...
npx vercel --prod --yes > deploy_output.tmp 2>&1
if errorlevel 1 (
    echo Error: Vercel deployment failed
    type deploy_output.tmp
    del deploy_output.tmp
    pause
    exit /b 1
)

REM Extract deployment URL from output
for /f "tokens=2 delims= " %%a in ('findstr /c:"Production:" deploy_output.tmp') do set DEPLOYMENT_URL=%%a
del deploy_output.tmp

if "%DEPLOYMENT_URL%"=="" (
    echo Error: Could not extract deployment URL
    pause
    exit /b 1
)

echo ✅ Deployed to: %DEPLOYMENT_URL%
echo.

REM Step 3: Create alias
echo [3/4] Vercel: Creating alias...
npx vercel alias %DEPLOYMENT_URL% editor-button-app.vercel.app --yes
if errorlevel 1 (
    echo Error: Vercel alias failed
    pause
    exit /b 1
)
echo ✅ Aliased to: https://editor-button-app.vercel.app
echo.

REM Step 4: Final summary
echo [4/4] Deployment Summary:
echo ========================================
echo ✅ Git: Changes committed and pushed
echo ✅ Vercel: Deployed to production
echo ✅ Alias: https://editor-button-app.vercel.app
echo ✅ Inspect: https://vercel.com/digitalpros-projects/editor-button-app
echo ========================================
echo.
echo 🎉 Deployment completed successfully!
echo The app is now live and ready for testing in Crowdin.
echo.
pause
