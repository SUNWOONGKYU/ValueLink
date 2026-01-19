@echo off
echo Starting Claude Code Auto-Typer...
echo This will automatically type into Claude Code when new orders arrive.
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0claude_auto_typer.ps1"
pause
