menu(where=sel.count>0 type='file|dir|drive|namespace|back' mode="multiple" title='Script List' image=\uE218)
{
item(title='Restart File Explorer' image=\uE013 cmd-powershell="Stop-Process -Name explorer -Force; Start-Process explorer")


	menu(title="Rclone" image=\uE09C)
	{
	item(title='sync.ps1' image=\uE218 cmd-pwsh="C:\\ms1\\scripts\\sync.ps1")
	item(title='msBackups' image=\uE218 cmd-pwsh='rclone sync C:\\msBackups\\ o0:\\msBackups\\ -P --check-first --transfers=1 --track-renames --fast-list')
	}

	menu(title="FFmpeg" image=\uE154)
	{
    item(title='Image Dimension' image=\uE150 cmd-powershell="Start-Process powershell.exe -ArgumentList '-ExecutionPolicy Bypass -File \"C:\\ms1\\scripts\\ffmpeg\\img_dim.ps1\"'")
	}

	menu(title="New File" image=\uE16D)
	{
    item(title='Python Script' image=\uE0A9 cmd-powershell="New-Item -Path . -Name 'new_script.py' -ItemType 'file' -Force")
	item(title='Ahk Script' image=\uE0A9 cmd-powershell="New-Item -Path . -Name 'new_script.ahk' -ItemType 'file' -Force")
	item(title='Batch Script' image=\uE0A9 cmd-powershell="New-Item -Path . -Name 'new_script.bat' -ItemType 'file' -Force")
	item(title='PWSH Script' image=\uE0A9 cmd-powershell="New-Item -Path . -Name 'new_script.ps1' -ItemType 'file' -Force")
	}

}
