@echo off
title Push Funda to GitHub
echo ========================================================
echo Pushing Funda to GitHub (https://github.com/Amphy2000/Funda.git)...
echo ========================================================
cd /d "%~dp0"
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pushed to GitHub successfully!
    echo Now open https://vercel.com to import your Funda repo.
) else (
    echo [ERROR] Push failed. 
    echo Please ensure you have created the empty repo 'Funda' on https://github.com/new
)
pause
