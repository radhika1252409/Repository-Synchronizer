import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_sender import send_file

CLIENT_FOLDER = os.path.join("client", "client_folder")
os.makedirs(CLIENT_FOLDER, exist_ok=True)

class WatcherHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            send_file(event.src_path)
            print(f"[WATCHER] Created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            send_file(event.src_path)
            print(f"[WATCHER] Modified: {event.src_path}")

def start_watcher():
    # Send all existing files first
    for f in os.listdir(CLIENT_FOLDER):
        file_path = os.path.join(CLIENT_FOLDER, f)
        if os.path.isfile(file_path):
            send_file(file_path)

    observer = Observer()
    observer.schedule(WatcherHandler(), CLIENT_FOLDER, recursive=False)
    observer.start()
    print(f"[WATCHER] Watching: {CLIENT_FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
