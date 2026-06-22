# FolderSync – System Architecture Documentation

## 1. Overview
FolderSync is a real-time client–server folder synchronization application.
Whenever a file is created, modified, renamed, or deleted in the client
folder, the change is immediately sent to the server, along with a backup
system for version history.

## 2. Components
1. **Client**
   - Watches a local folder using `watchdog`
   - Detects file events (create, modify, delete)
   - Sends file updates to server

2. **Server**
   - Listens for client connections
   - Receives files or delete commands
   - Maintains backup history

3. **GUI**
   - Built using Tkinter
   - Shows real-time logs
   - Displays server & client folder contents

## 3. Data Flow
Client Folder → Watcher → File Sender → Socket Transmission → Server → Server Folder + Backup
## 4. Backup Logic
Whenever a file already exists on the server, FolderSync renames the
existing file with a timestamp before saving the new version.

Example:
New Text Document.txt
New Text Document_20251122_103242.txt (backup)
## 5. Communication
TCP sockets are used for reliable file transfer. Every transfer follows:

[FilenameLength][Filename][FileSize][Content]

## 6. Limitations
- Folder creation is not synced
- Large files may transfer slowly
- No encryption (plain TCP)

## 7. Future Enhancements
- Add secure file transfer (TLS)
- Add folder sync (not only files)
- Add conflict resolution rules
