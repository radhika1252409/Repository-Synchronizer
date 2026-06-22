import socket
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from protocol import encode, FILE_CREATE, FILE_MODIFY, FILE_DELETE

WATCH_FOLDER = r"C:\Users\radhi\OneDrive\Desktop\FolderSync\client\client_folder"
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001
BUFFER_SIZE = 4096

class Watcher(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory: return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        print(f"[WATCHER] Created: {filepath}")
        send_file(filepath, filename, FILE_CREATE)

    def on_modified(self, event):
        if event.is_directory: return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        print(f"[WATCHER] Modified: {filepath}")
        send_file(filepath, filename, FILE_MODIFY)

    def on_deleted(self, event):
        if event.is_directory: return
        filename = os.path.basename(event.src_path)
        print(f"[WATCHER] Deleted: {filename}")
        send_delete(filename)

    def on_moved(self, event):
        if event.is_directory: return
        old_name = os.path.basename(event.src_path)
        new_name = os.path.basename(event.dest_path)
        print(f"[WATCHER] Renamed: {old_name} → {new_name}")
        send_delete(old_name)
        send_file(event.dest_path, new_name, FILE_CREATE)

def send_file(filepath, filename, opcode):
    try:
        filesize = os.path.getsize(filepath)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            print(f"[CLIENT] Sending file: {filename}")
            header = encode(opcode, filename, filesize)
            s.sendall(len(header).to_bytes(4,'big'))
            s.sendall(header)
            with open(filepath, 'rb') as f:
                while chunk := f.read(BUFFER_SIZE):
                    s.sendall(chunk)
            resp = s.recv(1024).decode()
            print(f"[CLIENT] Server acknowledged: {resp}")
    except Exception as e:
        print(f"[CLIENT] Error sending file {filename}: {e}")

def send_delete(filename):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            header = encode(FILE_DELETE, filename, 0)
            s.sendall(len(header).to_bytes(4,'big'))
            s.sendall(header)
            resp = s.recv(1024).decode()
            print(f"[CLIENT] Server acknowledged delete: {resp}")
    except Exception as e:
        print(f"[CLIENT] Error deleting file {filename}: {e}")

if __name__ == "__main__":
    os.makedirs(WATCH_FOLDER, exist_ok=True)
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=True)
    observer.start()
    print(f"[WATCHER] Watching: {WATCH_FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
