$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = "$StartupFolder\VoiceInput.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "`"C:\ValueLine\Human_ClaudeCode_Bridge\voice_realtime.py`""
$Shortcut.WorkingDirectory = "C:\ValueLine\Human_ClaudeCode_Bridge"
$Shortcut.WindowStyle = 7
$Shortcut.Save()

Write-Host "Registered to startup: $ShortcutPath"
