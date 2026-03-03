class AppController:

    def __init__(self):
        self.detector = DetectorService()
        self.validator = ValidatorService()
        self.installer = InstallerService()
        self.gpu = GPUProvisioner()
        self.service_manager = ServiceManager()

        self.system_info = None
        self.runtime_config = None

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt6.QtGui import QIcon

def setup_tray(self):

    self.tray = QSystemTrayIcon(QIcon("icon.png"))

    menu = QMenu()

    open_action = QAction("Open AI Toolkit")
    open_action.triggered.connect(self.show_main_window)

    stop_action = QAction("Stop Services")
    stop_action.triggered.connect(self.stop_services)

    quit_action = QAction("Quit")
    quit_action.triggered.connect(self.full_exit)

    menu.addAction(open_action)
    menu.addAction(stop_action)
    menu.addSeparator()
    menu.addAction(quit_action)

    self.tray.setContextMenu(menu)
    self.tray.show()

def closeEvent(self, event):
    event.ignore()
    self.hide()

class AppState(Enum):
    FIRST_RUN
    READY
    INSTALLING
    RUNNING
    ERROR      

