# Result Notifier - Shows completed order results in Claude Code session
# Watches Outbox for *_final.json files and displays results

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Speech

$outboxPath = "C:\Your_Project_Path\Web_ClaudeCode_Bridge\Outbox"
$processedFile = "C:\Your_Project_Path\Web_ClaudeCode_Bridge\.processed_orders.txt"

# Track processed orders
if (-not (Test-Path $processedFile)) {
    New-Item $processedFile -ItemType File | Out-Null
}

$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speech.Rate = 2

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   ORDER RESULT NOTIFIER RUNNING" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Watching for completed orders in Outbox..." -ForegroundColor Yellow
Write-Host "Will automatically notify Claude Code session." -ForegroundColor White
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

# File watcher for Outbox
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $outboxPath
$watcher.Filter = "*_final.json"
$watcher.EnableRaisingEvents = $true
$watcher.IncludeSubdirectories = $false

$action = {
    $filePath = $Event.SourceEventArgs.FullPath
    $fileName = $Event.SourceEventArgs.Name

    Start-Sleep -Milliseconds 500  # Wait for file write completion

    try {
        # Check if already processed
        $processedOrders = Get-Content $using:processedFile -ErrorAction SilentlyContinue
        if ($processedOrders -contains $fileName) {
            return  # Already notified
        }

        # Read the result
        $result = Get-Content $filePath -Raw -Encoding UTF8 | ConvertFrom-Json

        $orderId = $result.order_id
        $status = $result.status
        $response = $result.response
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

        Write-Host "[$timestamp] ORDER COMPLETED!" -ForegroundColor Green
        Write-Host "Order ID: $orderId" -ForegroundColor Yellow
        Write-Host "Status: $status" -ForegroundColor Cyan
        Write-Host "Response length: $($response.Length) characters" -ForegroundColor White
        Write-Host ""

        # Find Claude Code window
        $claudeProcess = Get-Process | Where-Object {
            $_.MainWindowTitle -like "*Claude*" -or
            $_.ProcessName -eq "claude" -or
            $_.MainWindowTitle -like "*MINGW64*" -or
            $_.MainWindowTitle -like "*bash*"
        } | Select-Object -First 1

        if ($claudeProcess) {
            Write-Host "Sending notification to Claude Code..." -ForegroundColor Cyan

            # Activate window
            $wshell = New-Object -ComObject wscript.shell
            $null = $wshell.AppActivate($claudeProcess.Id)
            Start-Sleep -Milliseconds 800

            # Prepare message with response preview
            $responsePreview = if ($response.Length -gt 200) {
                $response.Substring(0, 200) + "..."
            } else {
                $response
            }

            $message = @"

================================================================================
ORDER COMPLETED!
================================================================================
Order ID: $orderId
Status: $status
Completed: $($result.completed_at)

RESPONSE PREVIEW:
$responsePreview

Full response saved to: $fileName
================================================================================

"@

            # Type the message
            [System.Windows.Forms.SendKeys]::SendWait($message)

            # Audio notification
            $speech.SpeakAsync("Order $orderId completed") | Out-Null
            [console]::beep(1500, 500)

            Write-Host "Notification sent successfully!" -ForegroundColor Green
            Write-Host ""

        } else {
            Write-Host "WARNING: Could not find Claude Code window" -ForegroundColor Red
            Write-Host "Windows notification will be shown instead." -ForegroundColor Yellow

            # Fallback: Windows toast notification
            $notify = New-Object System.Windows.Forms.NotifyIcon
            $notify.Icon = [System.Drawing.SystemIcons]::Information
            $notify.Visible = $true
            $notify.ShowBalloonTip(
                10000,
                "Order Completed!",
                "Order $orderId has been processed. Check Claude Code for results.",
                [System.Windows.Forms.ToolTipIcon]::Info
            )
            Start-Sleep -Seconds 3
            $notify.Dispose()
        }

        # Mark as processed
        Add-Content $using:processedFile $fileName

    } catch {
        Write-Host "ERROR: $_" -ForegroundColor Red
        Write-Host ""
    }
}

# Register events
Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action

Write-Host "Monitoring started. Waiting for completed orders..." -ForegroundColor Green
Write-Host ""

# Keep running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    $watcher.Dispose()
}
