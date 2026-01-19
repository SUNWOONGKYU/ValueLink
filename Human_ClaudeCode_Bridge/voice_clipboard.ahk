; AutoHotkey v2 Script - Voice Input via Clipboard
; Win+H alternative for terminals
;
; HOW IT WORKS:
; 1. Press Win+Shift+H to start
; 2. Hidden notepad opens with Windows Voice Typing
; 3. Speak your command
; 4. Press Enter to send to Claude Code
;
; REQUIREMENTS: AutoHotkey v2

#Requires AutoHotkey v2.0
#SingleInstance Force

; Global variables
global voiceWindow := 0
global originalClipboard := ""

; Win+Shift+H - Start voice input
#+h::
{
    global voiceWindow, originalClipboard

    ; Save current clipboard
    originalClipboard := A_Clipboard

    ; Create a small input window
    voiceWindow := Gui("+AlwaysOnTop +ToolWindow", "Voice Input")
    voiceWindow.SetFont("s12")
    voiceWindow.Add("Text", "w300", "Speak now... (Press Enter when done)")
    voiceWindow.Add("Edit", "w300 h100 vVoiceText")
    voiceWindow.Add("Button", "w100", "Send").OnEvent("Click", SendVoiceText)
    voiceWindow.Add("Button", "x+10 w100", "Cancel").OnEvent("Click", CancelVoice)
    voiceWindow.OnEvent("Escape", CancelVoice)
    voiceWindow.Show()

    ; Focus the edit field
    voiceWindow["VoiceText"].Focus()

    ; Trigger Windows Voice Typing (Win+H)
    Sleep(200)
    Send("#h")
}

SendVoiceText(*)
{
    global voiceWindow, originalClipboard

    ; Get the text
    text := voiceWindow["VoiceText"].Value

    ; Close voice window
    voiceWindow.Destroy()

    if (text != "") {
        ; Copy to clipboard
        A_Clipboard := text

        ; Small delay then paste
        Sleep(300)
        Send("^v")

        ; Restore original clipboard after a delay
        SetTimer(RestoreClipboard, -1000)
    }
}

CancelVoice(*)
{
    global voiceWindow
    voiceWindow.Destroy()
}

RestoreClipboard()
{
    global originalClipboard
    A_Clipboard := originalClipboard
}

; Show tooltip on start
ToolTip("Voice Input Ready!`nPress Win+Shift+H to start", 100, 100)
SetTimer(() => ToolTip(), -3000)
