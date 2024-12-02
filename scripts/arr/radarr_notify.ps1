Import-Module BurntToast

$eventtype = $env:radarr_eventtype
$movie_title = $env:radarr_movie_title
$releasedyear = $env:radarr_movie_year
$movie_quality = $env:radarr_release_quality
$iconPath = "C:\msBackups\icon\radarr.png" # Path to Radarr icon file

switch ($eventtype) {
    Grab {
        $toastinfo = @{
            applogo = $iconPath
            text = " Grabbed: $movie_title", $releasedyear, $movie_quality
        }
    }
    download {
        if ($isupgrade -eq $False){
            $toastinfo = @{
                applogo = $iconPath
                text = " Downloaded: $movie_title", $releasedyear, $movie_quality
            }
        } else {
            $toastinfo = @{
                applogo = $iconPath
                text = " Upgraded: $movie_title", $releasedyear, $movie_quality
            }
        }
    }
    Default {
        New-BurntToastNotification -AppLogo $iconPath -Text $eventtype, "Radarr test notification."
    }
}

New-BurntToastNotification @toastinfo
