@echo off
echo ================================================
echo   Order Watcher 자동 시작 설치
echo ================================================
echo.

REM Windows 시작 프로그램 폴더에 바로가기 생성
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set TARGET_SCRIPT=%~dp0order_watcher.ps1

echo 시작 프로그램 폴더: %STARTUP_FOLDER%
echo 대상 스크립트: %TARGET_SCRIPT%
echo.

REM VBScript로 바로가기 생성
set VBS_FILE=%TEMP%\CreateShortcut.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > %VBS_FILE%
echo sLinkFile = "%STARTUP_FOLDER%\OrderWatcher.lnk" >> %VBS_FILE%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %VBS_FILE%
echo oLink.TargetPath = "powershell.exe" >> %VBS_FILE%
echo oLink.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File ""%TARGET_SCRIPT%""" >> %VBS_FILE%
echo oLink.WorkingDirectory = "%~dp0" >> %VBS_FILE%
echo oLink.Description = "Order Sheet Watcher - 자동 알림" >> %VBS_FILE%
echo oLink.Save >> %VBS_FILE%

cscript //nologo %VBS_FILE%
del %VBS_FILE%

echo.
echo ================================================
echo   설치 완료!
echo ================================================
echo.
echo Order Watcher가 Windows 시작 시 자동으로 실행됩니다.
echo.
echo 바로가기 위치:
echo %STARTUP_FOLDER%\OrderWatcher.lnk
echo.
echo 지금 바로 실행하시겠습니까? (Y/N)
set /p ANSWER=

if /i "%ANSWER%"=="Y" (
    echo.
    echo Order Watcher를 백그라운드로 실행합니다...
    start /min powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "%TARGET_SCRIPT%"
    echo 실행됨! 시스템 트레이에서 PowerShell이 실행 중입니다.
)

echo.
pause
