# Tasks
- [x] Implement `parseResetTimeToSeconds` and `formatSecondsToResetTime` helpers in frontend (`index.html`)
- [x] Update frontend response parsing to store `timestamp: Date.now()` instead of `toLocaleTimeString()`
- [x] Update `updateRateLimitsUI()` to dynamically compute remaining reset time based on elapsed seconds
- [x] Add real-time reset timer countdowns for client-tracked fallbacks (RPM and TPM)
- [x] Set up a `setInterval` in frontend to call `updateRateLimitsUI()` once per second when usage container is open
