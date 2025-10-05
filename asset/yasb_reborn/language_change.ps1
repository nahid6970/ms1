$l = Get-WinUserLanguageList; if ($l[0].LanguageTag -eq 'en-US') { $l.RemoveAt(0); $l.Add('en-US') } else { $l.RemoveAt(0); $l.Add('bn-IN') }; Set-WinUserLanguageList $l -Force
