# FolderSync – Manual Test Cases

## Test 1: File Creation Sync
Steps:
1. Create a new .txt file in client_folder.
2. Wait 1–2 seconds.
3. Check server_folder.

Expected:
- Newly created file appears on server.
- Log shows WATCHER → CLIENT → SERVER pipeline.

Result: PASSED / FAILED

---

## Test 2: File Modification Sync
Steps:
1. Edit a file in client_folder.
2. Save it.
3. Check server_folder.

Expected:
- Old file backed up with timestamp.
- New file saved.
- Logs show modification event.

Result: PASSED / FAILED

---

## Test 3: File Deletion Sync
Steps:
1. Delete a file in client_folder.
2. Check server_folder.

Expected:
- File removed from server.
- Delete command acknowledged.

Result: PASSED / FAILED

---

## Test 4: Rename Sync
Steps:
1. Rename a file in client_folder.
2. Check server_folder.

Expected:
- Old file backed up or removed.
- New file uploaded again.

Result: PASSED / FAILED

---

## Test 5: GUI Logging
Steps:
1. Perform create/modify/delete.
2. Look at color-coded logs in GUI.

Expected:
- Color-coded logs appear correctly.
