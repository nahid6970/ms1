# System Cleanup Assistant

## Description
Scan common Windows temporary files, user %TEMP%, C:\Windows\Temp, and recycle bin, report findings, and request permission before cleaning up.

## Goal
Scan for temporary files, cache, and trash on the system, report findings with item count and estimated disk space, and ask for explicit permission before deleting anything.

## Instructions
1. **Scan Temp Locations:** Use `run_powershell` to check total size and item count in common temporary directories:
   - User Temp (`$env:TEMP`)
   - Windows Temp (`C:\Windows\Temp`)
   - Recycle Bin (`Get-ChildItem -Path 'C:\$Recycle.Bin' -Recurse -ErrorAction SilentlyContinue`)
2. **Report Findings:** Display a concise summary of the locations, number of items, and estimated disk space occupied.
3. **Ask Permission:** Always ask the user for explicit confirmation before running any deletion commands.
4. **Execute Cleanup:** Only after receiving explicit confirmation from the user, run safe removal commands and report the total reclaimed disk space.
