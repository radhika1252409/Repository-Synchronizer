# GUI Flow Documentation

## 1. Overview
The GUI allows the user to:
- Start syncing
- Stop syncing
- Watch server & client folders in real time
- View logs with color-coded events

## 2. Workflow
When user clicks **Start Sync**:
1. Server thread starts listening
2. Watchdog observer starts monitoring client folder
3. Logs start appearing in the log window
4. File events trigger sync functionality

## 3. Log Colors
- SERVER → Green
- CLIENT → Blue
- WATCHER → Orange
- SYSTEM → Purple

## 4. Live Folder View
The GUI refreshes every second:
- New files appear automatically
- Backups are shown in gray
- Current server files appear in green
