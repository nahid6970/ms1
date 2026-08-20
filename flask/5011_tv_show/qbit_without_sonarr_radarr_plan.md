# qBittorrent Workflow Without Sonarr/Radarr

This is a rough plan for adding movie and TV update scanning directly into the app, without depending on Sonarr or Radarr.

## Goal

Build a smaller internal system that can:

- Scan the local movie and TV library.
- Track which episodes or movies are missing.
- Check metadata sources for new episodes and release dates.
- Match available releases from user-provided RSS feeds.
- Send selected torrents or magnet links to qBittorrent.
- Update the app after downloads finish.

The safest first version should use manual approval before downloading anything.

## Main Pieces

### 1. Local Library Scanner

The app scans the configured TV and movie folders and detects existing files.

For TV episodes, it should parse common patterns like:

```text
Show Name - S02E05 - Episode Title.mkv
Show.Name.S02E05.1080p.mkv
```

For movies, it should parse patterns like:

```text
Movie Name (2025).mkv
Movie.Name.2025.1080p.mkv
```

Detected files should be saved in the database with title, type, season, episode, year, quality, path, and downloaded status.

### 2. Metadata Updates

Use metadata APIs to keep the app aware of new episodes and movie releases.

Good options:

- TVmaze for TV episode schedules.
- TMDb for movie and TV metadata.
- Trakt later, if watchlists or calendars are useful.

Basic flow:

```text
Tracked shows -> check metadata API -> find new aired episodes -> mark missing/wanted
Tracked movies -> check release dates -> mark wanted when available
```

### 3. Wanted List

The app should have a wanted list for missing content.

Each wanted item can include:

- title
- movie or TV
- season and episode, if TV
- year
- desired quality
- status: wanted, found, downloading, downloaded, ignored

This should reuse the existing card styling where possible.

### 4. RSS Release Scanner

Instead of hardcoding torrent sites, the app should let the user add RSS feeds they are allowed to use.

The RSS scanner checks feed entries and tries to match them against wanted items.

Matching should look at:

- normalized title
- year for movies
- season and episode for TV
- quality tags like 720p, 1080p, 2160p
- source tags, if useful

Suggested first behavior:

```text
RSS match found -> show candidate card -> user clicks Download
```

Auto-download can be added later as a per-show or per-movie option.

### 5. qBittorrent Integration

Use qBittorrent Web API to add downloads.

Settings needed:

- qBittorrent URL
- username
- password
- TV save path
- movie save path
- category names, such as tv and movies

The app can then:

- log in to qBittorrent
- add magnet links or torrent URLs
- assign category
- set save path
- monitor progress
- detect completion
- rescan the local folder

### 6. Post-download Scan

After qBittorrent reports a completed download, the app should rescan the matching folder.

If the expected file is found:

- mark the wanted item as downloaded
- save the final file path
- remove it from missing/wanted lists

If no match is found:

- keep it as downloading or needs review
- show a small warning in the app

## Suggested Build Order

1. Add qBittorrent settings and connection test.
2. Add manual "send magnet/torrent to qBit" action.
3. Add local folder scanner for existing movies and TV episodes.
4. Add metadata updates for tracked shows.
5. Add wanted/missing list from metadata and local scan.
6. Add RSS feed management.
7. Add release matching.
8. Add manual download approval.
9. Add optional auto-download rules.

## First Version UI

Keep it compact and utility-focused:

- Existing poster/card style for shows and movies.
- Small toolbar button for qBittorrent/download queue.
- Compact two-panel settings layout.
- Manual approval cards for found releases.
- Clear status labels: Wanted, Found, Downloading, Downloaded, Needs Review.

## Important Notes

- The app should only use RSS feeds and sources the user is authorized to access.
- Matching should start conservative to avoid downloading the wrong file.
- Manual approval should be the default.
- Auto-download should be opt-in and limited by quality and title matching rules.

