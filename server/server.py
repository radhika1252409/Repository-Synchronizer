import socket
import threading
import os
import time
from protocol import decode, FILE_CREATE, FILE_MODIFY, FILE_DELETE

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
SERVER_FOLDER = os.path.join("server", "server_folder")
os.makedirs(SERVER_FOLDER, exist_ok=True)
BUFFER_SIZE = 4096

server_running = True
server_socket = None

def recvall(conn, n):
    """Receive exactly n bytes or return None if connection closed."""
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_client(conn, gui_logger=None):
    try:
        # ---------------- HEADER ----------------
        header_len_bytes = recvall(conn, 4)
        if not header_len_bytes:
            return
        header_len = int.from_bytes(header_len_bytes, "big")
        header_data = recvall(conn, header_len)
        if not header_data:
            return

        opcode, filename, filesize = decode(header_data)
        server_path = os.path.join(SERVER_FOLDER, filename)

        # ---------------- DELETE ----------------
        if opcode == FILE_DELETE:
            if os.path.exists(server_path):
                os.remove(server_path)
                if gui_logger:
                    gui_logger(f"[SERVER] Deleted file: {filename}", "red")
            else:
                if gui_logger:
                    gui_logger(f"[SERVER] File not found for deletion: {filename}", "red")
            conn.sendall(b"DELETE OK")
            return  # VERY IMPORTANT

        # ---------------- CREATE / MODIFY ----------------
        if gui_logger:
            gui_logger(f"[SERVER] Receiving file: {filename}", "blue")

        # Backup old file if exists
        if os.path.exists(server_path):
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            backup_name = f"{name}_{timestamp}{ext}"
            os.rename(server_path, os.path.join(SERVER_FOLDER, backup_name))
            if gui_logger:
                gui_logger(f"[SERVER] Backup created: {backup_name}", "blue")

        # Receive file content
        with open(server_path, "wb") as f:
            bytes_read = 0
            while bytes_read < filesize:
                chunk = conn.recv(min(BUFFER_SIZE, filesize - bytes_read))
                if not chunk:
                    break
                f.write(chunk)
                bytes_read += len(chunk)

        if gui_logger:
            gui_logger(f"[SERVER] File saved: {filename}", "blue")
        conn.sendall(b"FILE RECEIVED")

    except Exception as e:
        if gui_logger:
            gui_logger(f"[SERVER] Error: {e}", "red")
    finally:
        conn.close()

def start_server(gui_logger=None):
    global server_running, server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()

    server_running = True
    if gui_logger:
        gui_logger(f"[SERVER] Running on {SERVER_HOST}:{SERVER_PORT}", "blue")
    print(f"[SERVER] Running on {SERVER_HOST}:{SERVER_PORT}")

    while server_running:
        try:
            conn, addr = server_socket.accept()
        except OSError:
            break

        threading.Thread(
            target=handle_client,
            args=(conn, gui_logger),
            daemon=True
        ).start()

def stop_server(gui_logger=None):
    global server_running, server_socket
    server_running = False
    if gui_logger:
        gui_logger("[SERVER] Shutdown requested...", "red")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp:
            temp.connect((SERVER_HOST, SERVER_PORT))
    except:
        pass
    if server_socket:
        try:
            server_socket.close()
        except:
            pass
    if gui_logger:
        gui_logger("[SERVER] Successfully stopped.", "red")

if __name__ == "__main__":
    start_server()
