function gemini-notify {
    # Run the original gemini command passing all arguments
    # We use invoking by name which should find it in PATH
    & gemini $args

    # Check exit code if needed, but usually we notify regardless
    
    # 1. Audible Beep (Frequency 1000Hz, Duration 500ms)
    [System.Console]::Beep(1000, 500)

    # 2. Visual Notification (Popup that closes automatically after 5 seconds if not clicked)
    # The '0' is seconds to wait (0 = wait forever), but let's make it non-blocking or just a simple distinct message?
    # Actually, a simple popup is good.
    $wshell = New-Object -ComObject Wscript.Shell
    # 0 = waits forever. Let's set it to 0 so it stays until acknowledged, or just rely on the beep.
    # Common request is just a notification. 
    # Let's try to use a tray balloon if possible, but Popup is standard.
    # We will use a non-blocking timeout of 5 seconds so it doesn't hang the terminal if they are away.
    $wshell.Popup("Gemini text generation finished.", 5, "Gemini CLI", 64)
}

Write-Host "Function 'gemini-notify' has been loaded." -ForegroundColor Green
Write-Host "Try it: gemini-notify -p 'Tell me a joke'" -ForegroundColor Gray
