# Define the SSH command
$sshCommand = 'ssh u0_a827@192.168.0.102 -p 8022'

# Start the SSH command in PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", $sshCommand

# Wait for the connection to be established
Start-Sleep -Seconds 3  # Adjust as needed

# Type the command after connecting
# Note: This will type in the active PowerShell window
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("hellomusic{ENTER}")
