# ---------------- gui.py ----------------
import os
import socket
import threading
import time
import tkinter as tk
from tkinter import filedialog, scrolledtext, Listbox, END
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue
from protocol import encode, FILE_CREATE, FILE_MODIFY, FILE_DELETE

log_queue = queue.Queue()

# ---------------- Configuration ----------------
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 4096

CLIENT_FOLDER = os.path.join("client", "client_folder")
SERVER_FOLDER = os.path.join("server", "server_folder")
os.makedirs(CLIENT_FOLDER, exist_ok=True)
os.makedirs(SERVER_FOLDER, exist_ok=True)

# ---------------- Logging ----------------
def log(source, message, gui_logger=None):
    color_map = {
        "SERVER": "green",
        "CLIENT": "blue",
        "WATCHER": "orange",
        "SYSTEM": "purple",
    }
    text = f"[{time.strftime('%H:%M:%S')}] [{source}] {message}\n"
    if gui_logger:
        log_queue.put((source, text))
    else:
        print(text)

# ---------------- File Sender ----------------
def send_file(filepath, gui_logger=None, opcode=FILE_CREATE):
    if not os.path.exists(filepath):
        return
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            header = encode(opcode, filename, filesize)
            s.sendall(len(header).to_bytes(4, "big"))
            s.sendall(header)

            with open(filepath, "rb") as f:
                while chunk := f.read(BUFFER_SIZE):
                    s.sendall(chunk)

            resp = s.recv(1024)
            log("CLIENT", f"Server acknowledged: {resp.decode()}", gui_logger)
    except Exception as e:
        log("CLIENT", f"Error sending {filename}: {e}", gui_logger)

def send_delete_command(filename, gui_logger=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            header = encode(FILE_DELETE, filename, 0)
            s.sendall(len(header).to_bytes(4, "big"))
            s.sendall(header)
            resp = s.recv(1024)
            log("CLIENT", f"Server acknowledged delete: {resp.decode()}", gui_logger)
    except Exception as e:
        log("CLIENT", f"Error sending delete for {filename}: {e}", gui_logger)

# ---------------- Server ----------------
def start_server(gui_logger=None):
    def handle_client(conn):
        try:
            header_len_bytes = conn.recv(4)
            header_len = int.from_bytes(header_len_bytes, "big")
            header = conn.recv(header_len)

            from protocol import decode
            opcode, filename, filesize = decode(header)
            server_path = os.path.join(SERVER_FOLDER, filename)

            if opcode == FILE_DELETE:
                if os.path.exists(server_path):
                    os.remove(server_path)
                    log("SERVER", f"Deleted file: {filename}", gui_logger)
                conn.send(b"File deleted successfully")
                conn.close()
                return

            # Backup if file exists
            if os.path.exists(server_path):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
                os.rename(server_path, os.path.join(SERVER_FOLDER, backup))
                log("SERVER", f"Backup created: {backup}", gui_logger)

            log("SERVER", f"Receiving file: {filename}", gui_logger)
            bytes_read = 0
            with open(server_path, "wb") as f:
                while bytes_read < filesize:
                    chunk = conn.recv(min(BUFFER_SIZE, filesize - bytes_read))
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_read += len(chunk)

            log("SERVER", f"File saved: {filename}", gui_logger)
            conn.send(b"File received successfully")
        except Exception as e:
            log("SERVER", f"Error: {e}", gui_logger)
        finally:
            conn.close()
        try:
            app.refresh_folders()
        except Exception:
            pass

    def server_thread():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((SERVER_HOST, SERVER_PORT))
            server.listen()
            log("SERVER", f"Running on {SERVER_HOST}:{SERVER_PORT}", gui_logger)
            while True:
                conn, _ = server.accept()
                threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

    threading.Thread(target=server_thread, daemon=True).start()

# ---------------- Watcher ----------------
class Watcher(FileSystemEventHandler):
    def __init__(self, gui_logger):
        self.gui_logger = gui_logger

    def on_created(self, event):
        if not event.is_directory:
            send_file(event.src_path, self.gui_logger, FILE_CREATE)
            log("WATCHER", f"Created file: {os.path.basename(event.src_path)}", self.gui_logger)

    def on_modified(self, event):
        if not event.is_directory:
            send_file(event.src_path, self.gui_logger, FILE_MODIFY)
            log("WATCHER", f"Modified file: {os.path.basename(event.src_path)}", self.gui_logger)

    def on_deleted(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            send_delete_command(filename, self.gui_logger)
            log("WATCHER", f"Deleted file: {filename}", self.gui_logger)

    def on_moved(self, event):
        if not event.is_directory:
            old_name = os.path.basename(event.src_path)
            new_name = os.path.basename(event.dest_path)
            send_delete_command(old_name, self.gui_logger)
            send_file(event.dest_path, self.gui_logger, FILE_CREATE)
            log("WATCHER", f"Renamed: {old_name} → {new_name}", self.gui_logger)

def start_watcher(gui_logger):
    observer = Observer()
    observer.schedule(Watcher(gui_logger), CLIENT_FOLDER, recursive=False)
    observer.start()
    log("WATCHER", f"Watching: {CLIENT_FOLDER}", gui_logger)
    return observer

# ---------------- GUI ----------------
class FolderSyncGUI:
    def __init__(self, master):
        self.master = master
        master.title("Repository / Directory Synchronizer")
        master.geometry("1200x650")
        master.configure(bg="#F5F5F5")

        control_frame = tk.Frame(master, bg="#FFFFFF", bd=2, relief="groove")
        control_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        tk.Label(control_frame, text="Controls", font=("Arial", 14, "bold"), bg="#FFFFFF").pack(pady=10)

        self.browse_button = tk.Button(control_frame, text="Browse Client Folder", width=20,
                                       command=self.browse_client_folder, bg="#3498DB", fg="white")
        self.browse_button.pack(pady=5)

        self.start_button = tk.Button(control_frame, text="Start Sync", bg="green", fg="white", width=20,
                                      command=self.start_sync)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(control_frame, text="Stop Sync", bg="red", fg="white", width=20,
                                     state=tk.DISABLED, command=self.stop_sync)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(control_frame, text="Status: STOPPED", bg="#FFFFFF", fg="red",
                                     font=("Arial", 12, "bold"))
        self.status_label.pack(pady=15)

        files_frame = tk.Frame(master, bg="#F5F5F5")
        files_frame.grid(row=0, column=1, padx=10)

        tk.Label(files_frame, text="Client Folder", font=("Arial", 12, "bold")).grid(row=0, column=0)
        tk.Label(files_frame, text="Server Folder", font=("Arial", 12, "bold")).grid(row=0, column=1)

        self.client_files_box = Listbox(files_frame, width=45, height=20, font=("Consolas", 11))
        self.client_files_box.grid(row=1, column=0, padx=10, pady=10)

        self.server_files_box = Listbox(files_frame, width=45, height=20, font=("Consolas", 11))
        self.server_files_box.grid(row=1, column=1, padx=10, pady=10)

        log_frame = tk.Frame(master, bg="#F5F5F5")
        log_frame.grid(row=0, column=2, padx=10, pady=10)

        tk.Label(log_frame, text="System Logs", font=("Arial", 12, "bold")).pack()

        self.log_box = scrolledtext.ScrolledText(log_frame, width=55, height=23, font=("Consolas", 10))
        self.log_box.pack()

        self.observer = None
        self.refresh_folders()

    def browse_client_folder(self):
        global CLIENT_FOLDER
        folder = filedialog.askdirectory()
        if folder:
            CLIENT_FOLDER = folder
            self.refresh_folders()

    def start_sync(self):
        log("SYSTEM", "Starting FolderSync...", self.log_box)
        self.status_label.config(text="Status: RUNNING", fg="green")
        start_server(self.log_box)
        self.observer = start_watcher(self.log_box)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_sync(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: STOPPED", fg="red")
        log("SYSTEM", "FolderSync stopped.", self.log_box)

    def refresh_folders(self):
        try:
            self.client_files_box.delete(0, END)
            for f in os.listdir(CLIENT_FOLDER):
                self.client_files_box.insert(END, f)
        except Exception:
            pass

        try:
            self.server_files_box.delete(0, END)
            for f in os.listdir(SERVER_FOLDER):
                if "_20" in f:
                    self.server_files_box.insert(END, f + " (backup)")
                    self.server_files_box.itemconfig(END, {'fg': 'gray'})
                else:
                    self.server_files_box.insert(END, f)
                    self.server_files_box.itemconfig(END, {'fg': 'green'})
        except Exception:
            pass

        self.master.after(1000, self.refresh_folders)

# ---------------- Process queued logs ----------------
def process_logs():
    while not log_queue.empty():
        source, text = log_queue.get()
        tag_name = f"{source}_{time.time()}"
        color_map = {"SERVER": "green", "CLIENT": "blue", "WATCHER": "orange", "SYSTEM": "purple"}
        try:
            app.log_box.tag_config(tag_name, foreground=color_map.get(source, "black"))
            app.log_box.insert("end", text, tag_name)
            app.log_box.see("end")
        except Exception:
            print(text.strip())
    root.after(100, process_logs)

# ---------------- Main ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FolderSyncGUI(root)
    process_logs()
    root.mainloop()
