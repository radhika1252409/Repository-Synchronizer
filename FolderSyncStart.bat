@echo off
title FolderSync Server & Client

:: Start Server
start "Server" cmd /k "cd /d C:\Users\radhi\OneDrive\Desktop\FolderSync\server && python server.py"

:: Start Client
start "Client" cmd /k "cd /d C:\Users\radhi\OneDrive\Desktop\FolderSync\client && python client.py"

echo FolderSync started!
pause
