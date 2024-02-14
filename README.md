```diff
+ Nahid-NA6970 +
```





<table>
  <tr>
    <td><a href="https://nahid6970.github.io/ms2/1">HomePage❤️</a></td>
    <td><a href="https://nahid6970.github.io/ms2/2">ExtraPage💓</a></td>
  </tr>
<tr>
<!--ReadME🎯--><td><a href="/README.md">ReadME🎯</a></td>
<!--Formats--><td><a href="/asset/formats.md">Formats</a></td>
<!--GitHub⭐--><td><a href="https://github.com/nahid6970?tab=stars">GitHub⭐</a></td>
</tr>
<tr>
<!--GKeep--><td><a href="https://keep.google.com">GKeep</a></td>
<!--OneNote--><td><a href="https://www.onenote.com/">OneNote</a></td>
<!--Discord--><td><a href="https://discord.com/channels/@me">Discord</a></td>
</tr>
</table>

## Apps
<table>
<tr>
<!--PC-Apps--><td><a href="/asset/pcapps.md"><img src="https://cdn-icons-png.flaticon.com/512/1865/1865273.png" width="50" height="50"></a></td>
<!--Android-Apps--><td><a href="/asset/linked/androidapps.md"><img src="https://www.computerhope.com/jargon/a/android.png" width="50" height="50"></a></td>
<!--VScode--><td><a href="https://vscode.dev/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Visual_Studio_Code_1.35_icon.svg/2048px-Visual_Studio_Code_1.35_icon.svg.png" width="50" height="50"></a></td>
<!--Excel--><td><a href="https://1drv.ms/x/s!AhXBwvpMC1Pagc4mbx4e1Y0tWrci5A?e=iVa0YV"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Microsoft_Excel_2013-2019_logo.svg/1200px-Microsoft_Excel_2013-2019_logo.svg.png" width="50" height="50"></a></td>
</tr>
</table>


--------------------------------------------------------------------------------------------------------------------------------------------------------------
# ⏩Useful Commands & Locations
<details><summary>PWSH</summary>

- Set-ExecutionPo1icy -ExecutionPo1icy Bypass -Scope Process
- pwsh.exe -command "command" /or/ pwsh.exe -c command
- pwsh -c pause | command  [not to close window ]
- Copy-Item -Path "path" -Destination "path" -Force
- powershell.exe -ExecutionPolicy Unrestricted -NoLogo -File "$(FULL_CURRENT_PATH)"  -NoExit
- Measure-Command {pwsh-command} #(time takes to run command)
- Get-Process
  - Get-Process | Where-Object { $_.Name -like "*$partialName*" }
  - Get-Process [[-Name] <string[]>] [-Module] [-FileVersionInfo] [<CommonParameters>]
  - Get-Process [[-Name] <string[]>] -IncludeUserName [<CommonParameters>]
  - Get-Process -Id <int[]> [-Module] [-FileVersionInfo] [<CommonParameters>]
  - Get-Process -Id <int[]> -IncludeUserName [<CommonParameters>]
  - Get-Process -InputObject <Process[]> [-Module] [-FileVersionInfo] [<CommonParameters>]
  - Get-Process -InputObject <Process[]> -IncludeUserName [<CommonParameters>]
- Start-Process
  - Start-Process pwsh -Verb runAs
  - Start-Process appname -Verb runAs
  - Start-Process [-FilePath] <string> [[-ArgumentList] <string[]>] [-Credential <pscredential>] [-WorkingDirectory <string>] [-LoadUserProfile] [-NoNewWindow] [-PassThru] [-RedirectStandardError <string>] [-RedirectStandardInput <string>] [-RedirectStandardOutput <string>] [-WindowStyle <ProcessWindowStyle>] [-Wait] [-UseNewEnvironment] [-WhatIf] [-Confirm] [<CommonParameters>]
  - Start-Process [-FilePath] <string> [[-ArgumentList] <string[]>] [-WorkingDirectory <string>] [-PassThru] [-Verb <string>] [-WindowStyle <ProcessWindowStyle>] [-Wait] [-WhatIf] [-Confirm] [<CommonParameters>]
- Stop-Process
  - Stop-Process -Name AutoHotkeyU64
  - Stop-Process [-Id] <int[]> [-PassThru] [-Force] [-WhatIf] [-Confirm] [<CommonParameters>]
  - Stop-Process -Name <string[]> [-PassThru] [-Force] [-WhatIf] [-Confirm] [<CommonParameters>]
  - Stop-Process [-InputObject] <Process[]> [-PassThru] [-Force] [-WhatIf] [-Confirm] [<CommonParameters>]
- mklink
  - mklink "fake" "main" #[cmd]
  - New-Item -ItemType HardLink -Path "fake" -Target "main" #[pwsh]
  - New-Item -ItemType SymbolicLink -Path "fake" -Target "main" -Force #[pwsh]
  
  </details>
<details><summary>Others</summary>

- rclone config paths
- Location-Related
- C:\Users\nahid\AppData\Roaming\Microsoft\Windows\SendTo
- Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
</details>

--------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------
# ⏩Create Powershell Proflie
- if (!(Test-Path -Path $PROFILE )) { New-Item -Type File -Path $PROFILE -Force }  
- notepad $profile

|         Profile Type         |                 Profile Path                 |
| ---------------------------- | -------------------------------------------- |
| Current user, PowerShell ISE | $PROFILE.CurrentUserCurrentHost, or $PROFILE |
| All users, PowerShell ISE    | $PROFILE.AllUsersCurrentHost                 |
| Current user, All hosts      | $PROFILE.CurrentUserAllHosts                 |
| All users, All hosts         | $PROFILE.AllUsersAllHosts                    |

---
## ⏩Install Chocolatey
- Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

---
