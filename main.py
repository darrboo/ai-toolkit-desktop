import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QSystemTrayIcon,
    QMenu
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

# --- Import your services ---
from detector_service import DetectorService
from validator_service import ValidatorService
from installer_service import InstallerService
from gpu_provisioner import GPUProvisioner
from service_manager import ServiceManager
from config_manager import ConfigManager


class AppController:
    def __init__(self):
        self.detector = DetectorService()
        self.validator = ValidatorService()
        self.installer = InstallerService()
        self.gpu = GPUProvisioner()
        self.service_manager = ServiceManager()
        self.config = ConfigManager()

        self.system_info = None

    def initialize(self):
        print("Detecting system...")
        self.system_info = self.detector.detect()
        print("System detected.")
        print(self.system_info)


class MainWindow(QMainWindow):
    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("AI Toolkit")
        self.resize(600, 400)

        layout = QVBoxLayout()
        label = QLabel("AI Toolkit is running.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class TrayManager:
    def __init__(self, window: MainWindow, controller: AppController):
        self.window = window
        self.controller = controller

        self.tray = QSystemTrayIcon(QIcon())
        self.tray.setToolTip("AI Toolkit")

        menu = QMenu()

        open_action = QAction("Open")
        open_action.triggered.connect(self.window.show)

        stop_action = QAction("Stop Services")
        stop_action.triggered.connect(self.stop_services)

        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit_app)

        menu.addAction(open_action)
        menu.addAction(stop_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def stop_services(self):
        print("Stopping services...")
        self.controller.service_manager.stop_all()

    def quit_app(self):
        print("Shutting down...")
        self.controller.service_manager.stop_all()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)

    controller = AppController()
    controller.initialize()

    window = MainWindow(controller)
    window.show()

    tray = TrayManager(window, controller)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()