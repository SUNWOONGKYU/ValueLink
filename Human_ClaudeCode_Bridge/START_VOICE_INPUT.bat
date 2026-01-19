@echo off
chcp 65001 >nul
title Voice Input for Claude Code

echo.
echo ================================================
echo    Voice Input for Claude Code
echo ================================================
echo.
echo Starting voice input...
echo.
echo IMPORTANT:
echo   1. Run this script FIRST
echo   2. Then click on your Claude Code window
echo   3. Speak - your words will be typed automatically
echo.
echo ================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0voice_input.ps1"

pause
