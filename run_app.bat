@echo off
title XAU/USD Macro & News Predictor
echo ========================================================
echo Starting XAU/USD Macro & News Directional Predictor...
echo ========================================================
cd /d "%~dp0"
streamlit run app.py
pause
