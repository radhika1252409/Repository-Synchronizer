# FolderSync / Repository Synchronizer

A Python-based client-server file synchronization system that keeps folders in sync across machines using a custom protocol and real-time communication.

---

## 🚀 Features

- Client–Server architecture
- Real-time file synchronization
- Automatic detection of file changes
- File transfer between client and server
- Custom communication protocol
- GUI interface for user interaction
- Modular design (client, server, protocol separated)
- Test cases for reliability

---

## 🧠 Architecture

This project follows a **client-server architecture**:

- **Client** monitors local folder changes and sends updates
- **Server** receives updates and syncs files
- **Protocol layer** defines communication rules between client and server
- **GUI** provides a simple interface for user interaction

All detailed architecture explanations are available in the `/docs` folder.

---

## 📁 Project Structure
│
├── client/ # Client-side logic
├── server/ # Server-side logic
├── docs/ # Architecture and design documentation
├── tests/ # Test cases
├── gui.py # Graphical user interface
├── protocol.py # Communication protocol logic
├── run_foldersync.py # Main entry point
├── requirements.txt # Dependencies

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
2. Start the server
python server/server.py
3. Run the application
python run_foldersync.py
## Tech Stack
Python
Socket Programming
File System APIs
Multithreading
GUI (Tkinter / PyQt)

Demo


##Future Improvements
Cloud-based synchronization
Web dashboard interface
File encryption during transfer
Multi-user support
Conflict resolution system

-->>>Author

Radhika P
