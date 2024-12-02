Import-Module BurntToast
$eventtype = $env:sonarr_eventtype
$series_title = $env:sonarr_series_title
$rel_episodenumber = $env:sonarr_release_episodenumbers
$rel_seasonnumber = $env:sonarr_release_seasonnumber
$epfile_episodenumber = $env:sonarr_episodefile_episodenumbers
$epfile_seasonnumber = $env:sonarr_episodefile_seasonnumber
$releasename = $env:sonarr_episodefile_scenename
$releasetitle = $env:sonarr_release_title
$isupgrade = $env:sonarr_isupgrade
$iconPath = "C:\msBackups\icon\sonarr.png" # Path to Sonarr icon file

if ($eventtype -eq "Test") {
    New-BurntToastNotification -AppLogo $iconPath -Text $eventtype, "Sonarr test notification."
}
elseif ($eventtype -eq "Grab") {
    New-BurntToastNotification -AppLogo $iconPath -Text "Grabbed: $series_title Season $rel_seasonnumber Episode $rel_episodenumber", $releasetitle
}
elseif ($eventtype -eq "Download" -and $isupgrade -eq "False") {
    New-BurntToastNotification -AppLogo $iconPath -Text "Downloaded: $series_title Season $epfile_seasonnumber Episode $epfile_episodenumber", $releasename
}
elseif ($eventtype -eq "Download" -and $isupgrade -eq "True") {
    New-BurntToastNotification -AppLogo $iconPath -Text "Upgraded: $series_title Season $epfile_seasonnumber Episode $epfile_episodenumber", $releasename
}
else {
    # Additional handling for other cases if needed
}
