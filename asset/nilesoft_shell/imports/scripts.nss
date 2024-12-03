menu(where=sel.count>0 type='file|dir|drive|namespace|back' mode="multiple" title='Script List' image=\uE218)
{
item(title='Restart File Explorer' image=\uE013 cmd-powershell="Stop-Process -Name explorer -Force; Start-Process explorer")


	menu(separator="after" title="Rclone" image=\uE09C)
	{
	item(title='sync.ps1' image=\uE218 cmd-pwsh="C:\\ms1\\sync.ps1")
	item(title='msBackups' image=\uE218 cmd-pwsh='rclone sync C:\\msBackups\\ o0:\\msBackups\\ -P --check-first --transfers=1 --track-renames --fast-list')
	}

	menu(separator="after" title="FFmpeg" image=\uE09C)
	{
    item(title='Open Image Dimension Script' image=\uE21C cmd-powershell="Start-Process powershell.exe -ArgumentList '-ExecutionPolicy Bypass -File \"C:\\ms1\\scripts\\ffmpeg\\img_dim.ps1\"'")
	}

	menu(separator="after" title="New File" image=\uE09C)
	{
    item(title='Python Script' image=\uE22D cmd-powershell="New-Item -Path . -Name 'new_script.py' -ItemType 'file' -Force")
	item(title='Ahk Script' image=\uE22D cmd-powershell="New-Item -Path . -Name 'new_script.ahk' -ItemType 'file' -Force")
	item(title='Batch Script' image=\uE22D cmd-powershell="New-Item -Path . -Name 'new_script.bat' -ItemType 'file' -Force")
	item(title='PWSH Script' image=\uE22D cmd-powershell="New-Item -Path . -Name 'new_script.ps1' -ItemType 'file' -Force")
	}

}