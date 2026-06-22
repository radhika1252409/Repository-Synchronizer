# FolderSync – Edge Case Testing

## Test 1: Very Large File (>10MB)
Expected:
- Transfers without corruption
- Server receives correct size

Result:

---

## Test 2: Rapid Modifications
Steps:
- Press CTRL+S 10 times quickly on same file

Expected:
- Multiple backups created
- Final version correct

Result:

---

## Test 3: Delete & Recreate
Steps:
1. Delete file
2. Immediately create new file with same name

Expected:
- Delete recognized
- New version saved cleanly

Result:

---

## Test 4: Network Failure Simulation
Steps:
1. Disconnect WiFi during transfer

Expected:
- Partial file NOT saved
- No crashes

Result:
