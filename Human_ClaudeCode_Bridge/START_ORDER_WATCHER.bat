@echo off
echo Starting Order Watcher...
powershell -ExecutionPolicy Bypass -File "%~dp0order_watcher.ps1"
pause
