# Meet Timesheet

Chrome Manifest V3 extension that records Google Meet sessions in local extension storage and syncs the records to the shared Convex `backups` table.

## Install

1. Open `chrome://extensions` and enable Developer mode.
2. Choose **Load unpacked** and select this `GoogleMeet` folder.
3. Join a Google Meet. The extension detects the active call, records its name and start time, then saves the end time and duration when the call ends or its tab closes.

The meeting name is taken from the visible page heading/title when available, otherwise it falls back to the Meet code.

## Convex sync

`background.js` uses the existing `functions:save` and `functions:get` HTTP API and extension key `google_meet_timesheet`. It is configured with the Convex URL used by the sibling extensions. The stored Convex value is `{ meetings: [...] }`; sync replaces that extension's saved dataset, following the shared integration guide. Use **Sync now** to send local records or **Restore** to load the Convex dataset.

The shared Convex API stores one value per extension, so this extension keeps up to 5,000 meeting records in its dataset. No package install or build step is required.
