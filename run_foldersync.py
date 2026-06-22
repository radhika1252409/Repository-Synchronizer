import os
import socket
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore, Style

# ---------------- Initialize colorama ----------------
init(autoreset=True)

# ---------------- Configuration ----------------
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001

CLIENT_FOLDER = os.path.join("client", "client_folder")
SERVER_FOLDER = os.path.join("server", "server_folder")
os.makedirs(SERVER_FOLDER, exist_ok=True)
os.makedirs(CLIENT_FOLDER, exist_ok=True)

sent_cache = {}  # To prevent multiple rapid sends

# ---------------- Logging ----------------
def log(source, message):
    color = {
        "SERVER": Fore.GREEN,
        "CLIENT": Fore.BLUE,
        "WATCHER": Fore.YELLOW
    }.get(source, Fore.WHITE)
    print(f"{color}[{time.strftime('%H:%M:%S')}] [{source}] {message}{Style.RESET_ALL}")

# ---------------- Server ----------------
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen()
        log("SERVER", f"Running on {SERVER_HOST}:{SERVER_PORT}")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def handle_client(conn, addr):
    try:
        # Peek first 6 bytes to check for DELETE command
        command = conn.recv(6)
        if command == b"DELETE":
            filename_len = int.from_bytes(conn.recv(4), 'big')
            filename = conn.recv(filename_len).decode()
            server_path = os.path.join(SERVER_FOLDER, filename)
            if os.path.exists(server_path):
                os.remove(server_path)
                log("SERVER", f"Deleted file: {filename}")
            conn.close()
            return
        else:
            # Normal file transfer, put back the bytes
            conn = PrependSocket(conn, command)

        # ---------------- Receive file properly ----------------
        # Receive filename
        filename_len = int.from_bytes(conn.recv(4), 'big')
        filename = conn.recv(filename_len).decode()
        # Receive filesize
        filesize = int.from_bytes(conn.recv(8), 'big')

        server_path = os.path.join(SERVER_FOLDER, filename)

        # Backup old version if exists
        if os.path.exists(server_path):
            try:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
                os.rename(server_path, os.path.join(SERVER_FOLDER, backup_name))
                log("SERVER", f"Backup created: {backup_name}")
            except PermissionError:
                log("SERVER", f"Cannot backup {filename}, file in use.")

        log("SERVER", f"Receiving file: {filename}")
        with open(server_path, "wb") as f:
            bytes_read = 0
            while bytes_read < filesize:
                chunk = conn.recv(min(4096, filesize - bytes_read))
                if not chunk:
                    break
                f.write(chunk)
                bytes_read += len(chunk)
        log("SERVER", f"File saved: {filename}")
        conn.send(b"File received successfully")
        # ---------------------------------------------------
        
    except Exception as e:
        log("SERVER", f"Error: {e}")
    finally:
        conn.close()

# ---------------- Helper to prepend initial bytes ----------------
class PrependSocket:
    def __init__(self, sock, initial_bytes):
        self.sock = sock
        self.buffer = initial_bytes
    def recv(self, n):
        if self.buffer:
            to_return = self.buffer[:n]
            self.buffer = self.buffer[n:]
            return to_return
        return self.sock.recv(n)
    def send(self, data):
        return self.sock.send(data)
    def sendall(self, data):
        return self.sock.sendall(data)
    def close(self):
        return self.sock.close()

# ---------------- Client ----------------
def send_file(filepath):
    filename = os.path.basename(filepath)
    now = time.time()
    
    # Only send if not sent in last 2 seconds
    if filename in sent_cache and now - sent_cache[filename] < 2:
        return
    sent_cache[filename] = now

    filesize = os.path.getsize(filepath)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            log("CLIENT", f"Sending file: {filename}")

            # Send filename
            s.send(len(filename.encode()).to_bytes(4, 'big'))
            s.send(filename.encode())

            # Send filesize
            s.send(filesize.to_bytes(8, 'big'))

            # Send file content
            with open(filepath, 'rb') as f:
                while chunk := f.read(4096):
                    s.sendall(chunk)

            response = s.recv(1024)
            log("CLIENT", f"Server: {response.decode()}")

    except Exception as e:
        log("CLIENT", f"Error sending file: {e}")

# ---------------- Watcher ----------------
class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            send_file(event.src_path)
            log("WATCHER", f"Created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            send_file(event.src_path)
            log("WATCHER", f"Modified: {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory:
            send_file(event.dest_path)
            log("WATCHER", f"Renamed: {event.src_path} → {event.dest_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((SERVER_HOST, SERVER_PORT))
                    s.send(b"DELETE")
                    s.send(len(filename.encode()).to_bytes(4, "big"))
                    s.send(filename.encode())
                log("WATCHER", f"Deleted: {event.src_path} → Server will delete {filename}")
            except Exception as e:
                log("WATCHER", f"Error sending delete command: {e}")

def start_watcher():
    # Send all existing files at startup
    for file in os.listdir(CLIENT_FOLDER):
        file_path = os.path.join(CLIENT_FOLDER, file)
        if os.path.isfile(file_path):
            send_file(file_path)

    # Start the observer
    observer = Observer()
    observer.schedule(Watcher(), CLIENT_FOLDER, recursive=True)
    observer.start()
    log("WATCHER", f"Watching: {CLIENT_FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# ---------------- Main ----------------
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    start_watcher()
