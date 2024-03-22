menu(where=sel.count>0 type='file|dir|drive|namespace|back' mode="multiple" title='Script List' image=\uE218)
{
item(title='Restart File Explorer' image=\uE013 cmd-powershell="Stop-Process -Name explorer -Force; Start-Process explorer")


	menu(separator="after" title="Rclone" image=\uE09C)
	{
	item(title='Sync' image=\uE218 cmd-pwsh="C:\\ms1\\sync.ps1")
	}

}
