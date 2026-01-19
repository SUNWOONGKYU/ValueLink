@echo off
chcp 65001 >nul
title Voice Realtime Input

net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
python -u voice_realtime.py

pause
