@echo off
echo ================================================
echo   ValueLink 자동 커밋 설치
echo ================================================
echo.
echo 5분마다 자동으로 GitHub에 커밋/푸시합니다.
echo.
pause
powershell -ExecutionPolicy Bypass -File "%~dp0install-auto-commit-simple.ps1"
