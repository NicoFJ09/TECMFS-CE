from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt

from components.disk_status.DiskStatusPanel import DiskStatusPanel
from components.file_manager.FileManagerPanel import FileManagerPanel
from components.log.LogPanel import LogPanel
from systems.DiskMonitor import DiskMonitor
from systems.FileManager import FileManager
from systems.Logger import Logger
from systems.MessageRouter import MessageRouter
from client.port_handler import PortHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Window configuration
        screen = QApplication.desktop().screenGeometry()
        self.setWindowTitle("TECMFS-CE")
        self.setGeometry(100, 100, screen.width()//2, screen.height()//2)
        self.setMinimumSize(screen.width()//2, screen.height()//2)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Splitter setup
        main_splitter = QSplitter(Qt.Horizontal)
        right_splitter = QSplitter(Qt.Vertical)
        
        splitter_style = """
            QSplitter::handle {
                background-color: rgba(128, 128, 128, 30);
            }
            QSplitter::handle:hover {
                background-color: rgba(128, 128, 128, 80);
            }
        """
        main_splitter.setStyleSheet(splitter_style)
        right_splitter.setStyleSheet(splitter_style)
        
        # Panel initialization
        self.disk_panel = DiskStatusPanel()
        main_splitter.addWidget(self.disk_panel)
        
        self.filemanager_panel = FileManagerPanel()
        right_splitter.addWidget(self.filemanager_panel)
        
        self.log_panel = LogPanel()
        right_splitter.addWidget(self.log_panel)
        
        # Layout configuration
        main_splitter.addWidget(right_splitter)
        
        # Event connections
        main_splitter.splitterMoved.connect(self.update)
        right_splitter.splitterMoved.connect(self.update)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        
        self.disk_monitor = DiskMonitor(self.disk_panel)
        self.file_manager = FileManager(self.filemanager_panel)
        self.logger = Logger(self.log_panel)
        self.router = MessageRouter(self.disk_monitor, self.file_manager, self.logger)
        
        # Inicializar comunicación con servidor
        self.port_handler = PortHandler()
        self.port_handler.data_received.connect(self.router.route_message)
        
        # Set button callbacks for debug actions
        self.disk_panel.set_button_callbacks()
        self.filemanager_panel.set_button_callbacks()
        self.log_panel.set_button_callbacks()

        # Iniciar comunicación con servidor
        self.port_handler.start_polling(interval=5)  # Cada 5 segundos
        disk_status_data = {
            "tag": "disk_status",
            "disks": [
                {"name": "Disk D1", "status": "ONLINE", "used": "45%", "activity": "1 minute ago"},
                {"name": "Disk D2", "status": "REBUILDING", "used": "68%", "activity": "3 seconds ago"},
                {"name": "Disk D3", "status": "BUSY", "used": "72%", "activity": "Active now"},
                {"name": "Disk D4", "status": "FAILED", "used": "0%", "activity": "System error"}
            ]
        }
        file_manager_data = {
            "tag": "file_manager",
            "files": [
                {"name": "system_config.ini", "size": "2 KB"},
                {"name": "boot.img", "size": "128 MB"},
                {"name": "kernel.bin", "size": "45 MB"}
            ]
        }
        log_data = {
            "tag": "log",
            "logs": [
                {"level": "INFO", "message": "System initialized successfully"},
                {"level": "WARNING", "message": "Disk D2 showing high usage (68%)"}
            ]
        }
        # Iniciar comunicación con servidor
        self.port_handler.start_polling(interval=5)  # Cada 5 segundos
        
        # Conectar botón de test (opcional)
        if hasattr(self.disk_panel, 'reboot_button'):
            self.disk_panel.reboot_button.clicked.disconnect()
            self.disk_panel.reboot_button.clicked.connect(self.test_server_communication)
        
    def test_server_communication(self):
        """Método de prueba para enviar mensaje al servidor"""
        selected_disk = self.disk_panel.disk_selector.currentText()
        message = f"Test message from GUI: Reboot {selected_disk}"
        self.port_handler.send_message(message)
        
    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        if hasattr(self, 'port_handler'):
            self.port_handler.stop_polling()
        event.accept()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()
        
    def update(self):
        if hasattr(self, 'disk_panel'):
            self.disk_panel.update()
            
        if hasattr(self, 'filemanager_panel'):
            self.filemanager_panel.update()
            
        if hasattr(self, 'log_panel'):
            self.log_panel.update()