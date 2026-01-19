; AutoHotkey Script - Automatically send input to Claude Code session
; This monitors for .new_order_notification and types into Claude Code

; Configuration
notificationFile := "C:\Your_Project_Path\Web_ClaudeCode_Bridge\.new_order_notification"
checkInterval := 1000  ; Check every 1 second

; Main loop
Loop {
    ; Check if notification file exists
    if FileExist(notificationFile) {
        ; Read the order data
        FileRead, orderData, %notificationFile%

        ; Parse JSON to get order info
        orderObj := JSON.Load(orderData)
        orderId := orderObj.order_id
        content := orderObj.content_korean

        ; Find Claude Code window
        ; Adjust the window title or class as needed
        WinActivate, ahk_exe claude.exe
        ; Alternative: WinActivate, Claude Code
        ; Alternative: WinActivate, ahk_class ConsoleWindowClass

        Sleep, 500  ; Wait for window to activate

        ; Type the notification message
        message := "NEW ORDER ARRIVED!`n"
        message .= "Order ID: " . orderId . "`n"
        message .= "Content: " . content . "`n"
        message .= "Please check and respond.`n"

        SendRaw, %message%
        Send, {Enter}

        ; Delete the notification file
        FileDelete, %notificationFile%

        ; Play sound
        SoundBeep, 1000, 300
    }

    Sleep, %checkInterval%
}

; JSON parsing function (basic implementation)
; For full JSON support, use JSON.ahk library
class JSON {
    static Load(jsonStr) {
        obj := {}
        ; Simple parsing - extract key values
        ; order_id
        if RegExMatch(jsonStr, "i)""order_id""\s*:\s*""([^""]+)""", match)
            obj.order_id := match1
        ; content_korean
        if RegExMatch(jsonStr, "i)""content_korean""\s*:\s*""([^""]+)""", match)
            obj.content_korean := match1
        return obj
    }
}
