import subprocess
import threading
import time
from typing import Dict, List
import psutil

proc = psutil.Process(service.process.pid)
cpu = proc.cpu_percent()
mem = proc.memory_info().rss

class ServiceManager:

    def __init__(self):
        self.services: Dict[str, ManagedService] = {}
        self.monitor_thread = None
        self.running = False

class ManagedService:
    def __init__(self, name, command, cwd=None, env=None):
        self.name = name
        self.command = command
        self.cwd = cwd
        self.env = env
        self.process = None
        self.status = "stopped"
        self.logs = []

def register_service(self, service: ManagedService):
    self.services[service.name] = service

def start_all(self):
    order = ["llama", "memu", "zeroclaw"]

    for name in order:
        self.start_service(name)

    self.running = True
    self._start_monitor()

def start_service(self, name):

    service = self.services.get(name)
    if not service:
        return

    if service.process:
        return

    service.process = subprocess.Popen(
        service.command,
        cwd=service.cwd,
        env=service.env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    service.status = "running"

    threading.Thread(
        target=self._capture_logs,
        args=(service,),
        daemon=True
    ).start()

 def _capture_logs(self, service: ManagedService):

    for line in service.process.stdout:
        service.logs.append(line)

        # emit signal to GUI here if using Qt signals

def _start_monitor(self):
    self.monitor_thread = threading.Thread(
        target=self._monitor_loop,
        daemon=True
    )
    self.monitor_thread.start()

 def _monitor_loop(self):

    while self.running:
        for service in self.services.values():

            if service.process and service.process.poll() is not None:
                # Process exited
                exit_code = service.process.returncode
                service.status = "stopped"

                if exit_code != 0:
                    self._restart_service(service)

        time.sleep(2)

 def _restart_service(self, service):

    service.logs.append("Service crashed. Restarting...")
    service.process = None
    self.start_service(service.name)

 def stop_all(self):
    order = ["zeroclaw", "memu", "llama"]

    for name in order:
        self.stop_service(name)

    self.running = False

    def stop_service(self, name):

    service = self.services.get(name)
    if not service or not service.process:
        return

    service.process.terminate()
    service.process.wait(timeout=10)

    service.process = None
    service.status = "stopped"

 from PyQt6.QtCore import QObject, pyqtSignal

class QtServiceBridge(QObject):

    service_status_changed = pyqtSignal(str, str)
    log_received = pyqtSignal(str, str)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

