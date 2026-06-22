# Backup Logic Documentation

## 1. Purpose
To prevent accidental data loss, FolderSync keeps old versions of files.
Each time a file is overwritten, the old version is renamed with a timestamp.

## 2. Example
Original:
report.txt
Modified file arrives → Server renames:

    report_20251121_222643.txt
    
## 3. Benefits
- Can recover old versions
- Helps debug sync behavior
- Prevents data overwrites

## 4. Format
The timestamp format is:
YYYYMMDD_HHMMSS
## 5. Triggers
Backup occurs when:
- A file with same name already exists on server
