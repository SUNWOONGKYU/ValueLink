@echo off
chcp 65001 >nul
title Voice Input for Claude Code

echo.
echo ================================================
echo    Voice Input for Claude Code
echo ================================================
echo.
echo Starting...
echo.
echo HOW TO USE:
echo   1. Press Win+Shift+H to open voice input
echo   2. Windows Voice Typing will activate
echo   3. Speak your command
echo   4. Click "Send" or press Enter
echo   5. Text will be pasted to Claude Code
echo.
echo ================================================
echo.

start "" "C:\Program Files\AutoHotkey\v2\AutoHotkey.exe" "%~dp0voice_clipboard.ahk"

echo Voice Input is running in background.
echo Press Win+Shift+H anytime to use voice input.
echo.
echo Close this window when done.
pause
