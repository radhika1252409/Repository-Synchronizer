# FolderSync File Transfer Protocol

## 1. Purpose
Defines how the client and server communicate while transferring files
or sending delete requests.

## 2. Operations
### A. File Create / Modify
Sent when a file is created or modified.

Structure:
1. 4 bytes → filename length
2. filename bytes
3. 8 bytes → file size
4. file content

### B. File Delete
The client sends:

DELETE + [filenameLength] + [filename]

## 3. Why This Protocol?
- Simple and lightweight
- Easy to debug
- Works over plain TCP sockets
- Eliminates partial/incorrect file reading
