# Order Sheet Real-time Monitor
# Detects .new_order_notification file and shows instant alerts

$watchPath = "C:\Your_Project_Path\Web_ClaudeCode_Bridge"
$notificationFile = ".new_order_notification"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Order Sheet Watcher RUNNING" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Watch Path: $watchPath" -ForegroundColor Yellow
Write-Host "Target File: $notificationFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Waiting for new orders... Press Ctrl+C to stop." -ForegroundColor White
Write-Host ""

# Create FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $watchPath
$watcher.Filter = $notificationFile
$watcher.EnableRaisingEvents = $true
$watcher.IncludeSubdirectories = $false

# File creation/change event handler
$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Host "[$timestamp] DETECTED: $changeType - $path" -ForegroundColor Green

    # Wait for file write completion
    Start-Sleep -Milliseconds 100

    try {
        $content = Get-Content $path -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json

        $orderId = $content.order_id
        $orderName = $content.order_name
        $priority = $content.priority
        $contentKorean = $content.content_korean

        Write-Host ""
        Write-Host "================================================" -ForegroundColor Cyan
        Write-Host "   NEW ORDER ARRIVED!" -ForegroundColor Green
        Write-Host "================================================" -ForegroundColor Cyan
        Write-Host "Order ID: $orderId" -ForegroundColor Yellow
        Write-Host "Task: $orderName" -ForegroundColor Yellow
        Write-Host "Priority: $priority" -ForegroundColor Yellow
        Write-Host "Content: $contentKorean" -ForegroundColor White
        Write-Host "================================================" -ForegroundColor Cyan
        Write-Host ""

        # Play system sound
        [System.Media.SystemSounds]::Exclamation.Play()

        # Windows notification
        $notificationTitle = "New Order Arrived!"
        $notificationMessage = "Order ID: $orderId`nContent: $contentKorean"

        # PowerShell basic notification
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.Visible = $true
        $notify.ShowBalloonTip(10000, $notificationTitle, $notificationMessage, [System.Windows.Forms.ToolTipIcon]::Info)

        Start-Sleep -Seconds 2
        $notify.Dispose()

        # Use BurntToast if available
        if (Get-Module -ListAvailable -Name BurntToast) {
            Import-Module BurntToast
            New-BurntToastNotification -Text $notificationTitle, $notificationMessage -Sound "Default"
        }

    } catch {
        Write-Host "Failed to read notification file: $_" -ForegroundColor Red
    }
}

# Register events
Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action

Write-Host "Monitoring started. Waiting..." -ForegroundColor Green

# Infinite wait
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    # Cleanup
    $watcher.Dispose()
}
