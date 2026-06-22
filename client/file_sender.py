import socket
import os

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 4096

# Send a file to the server
def send_file(filepath, gui_logger=None):
    if not os.path.exists(filepath):
        return
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))

            if gui_logger:
                gui_logger(f"[CLIENT] Sending file: {filename}", "green")

            # Send filename length + filename
            s.send(len(filename.encode()).to_bytes(4, 'big'))
            s.send(filename.encode())

            # Send filesize + file content
            s.send(filesize.to_bytes(8, 'big'))
            with open(filepath, 'rb') as f:
                while chunk := f.read(BUFFER_SIZE):
                    s.sendall(chunk)

            # Server response
            resp = s.recv(1024)
            if gui_logger:
                gui_logger(f"[CLIENT] Server: {resp.decode()}", "green")

    except Exception as e:
        if gui_logger:
            gui_logger(f"[CLIENT] Error sending {filename}: {e}", "red")

# Send delete command to server
def send_delete_command(filename, gui_logger=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.send(b"DELETE")
            s.send(len(filename.encode()).to_bytes(4, "big"))
            s.send(filename.encode())
            if gui_logger:
                gui_logger(f"[CLIENT] Delete command sent for {filename}", "red")
    except Exception as e:
        if gui_logger:
            gui_logger(f"[CLIENT] Error sending delete for {filename}: {e}", "red")
