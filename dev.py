import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ReiniciarHandler(FileSystemEventHandler):
    def __init__(self):
        self.processo = None
        self.iniciar()

    def iniciar(self):
        if self.processo:
            self.processo.kill()
        self.processo = subprocess.Popen([sys.executable, "main.py"])

    def on_modified(self, event):
        if event.src_path.endswith(".py") or event.src_path.endswith(".qss"):
            print(f"Alteração detectada: {event.src_path}")
            self.iniciar()


if __name__ == "__main__":
    handler = ReiniciarHandler()
    observer = Observer()
    observer.schedule(handler, path="app", recursive=True)
    observer.start()
    print("Modo desenvolvimento ativo — salvou, reiniciou automaticamente.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.processo:
            handler.processo.kill()
    observer.join()