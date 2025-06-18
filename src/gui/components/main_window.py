from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt

from components.disk_status.DiskStatusPanel import DiskStatusPanel
from components.file_manager.FileManagerPanel import FileManagerPanel
from components.log.LogPanel import LogPanel
from systems.DiskMonitor import DiskMonitor
from systems.FileManager import FileManager
from systems.Logger import Logger
from systems.MessageRouter import MessageRouter
from client.server_service import ServerService
from client.action_manager import ActionManager
from config import GUI_CONFIG, SERVER_CONFIG, DEFAULT_MESSAGES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Window configuration usando config
        screen = QApplication.desktop().screenGeometry()
        self.setWindowTitle(GUI_CONFIG["window_title"])
        self.setGeometry(100, 100, screen.width()//2, screen.height()//2)
        self.setMinimumSize(GUI_CONFIG["min_width"], GUI_CONFIG["min_height"])
        
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
        
        # Inicializar servicios usando config
        self.server_service = ServerService(
            server_host=SERVER_CONFIG["host"], 
            server_port=SERVER_CONFIG["port"]
        )
        self.action_manager = ActionManager(self.server_service)
        
        # Conectar ActionManager a los paneles
        self.filemanager_panel.action_manager = self.action_manager
        
        # Conectar servicios con el sistema de routing
        self.server_service.data_received.connect(self.router.route_message)
        self.server_service.connection_status_changed.connect(self.on_connection_status_changed)
        self.server_service.error_occurred.connect(self.on_log_message)
        self.action_manager.action_logged.connect(self.on_log_message)
        
        # Configurar callbacks de botones
        self.setup_button_callbacks()
        
        # Iniciar monitoreo del servidor usando config
        self.server_service.start_monitoring(interval=SERVER_CONFIG["polling_interval"])
        
        # Log de inicio de la aplicación
        self.action_manager.app_started()
        
    def setup_button_callbacks(self):
        """Configura todos los callbacks de botones para usar ActionManager"""
        
        # === DISK PANEL CALLBACKS ===
        if hasattr(self.disk_panel, 'reboot_button'):
            try:
                self.disk_panel.reboot_button.clicked.disconnect()
            except:
                pass
            self.disk_panel.reboot_button.clicked.connect(self.on_reboot_disk_clicked)
            
        if hasattr(self.disk_panel, 'disk_selector'):
            try:
                self.disk_panel.disk_selector.currentTextChanged.disconnect()
            except:
                pass
            self.disk_panel.disk_selector.currentTextChanged.connect(self.on_disk_selected)
        
        # === FILE MANAGER CALLBACKS ===
        if hasattr(self.filemanager_panel, 'search_button'):
            try:
                self.filemanager_panel.search_button.clicked.disconnect()
            except:
                pass
            self.filemanager_panel.search_button.clicked.connect(self.on_search_files_clicked)
            
        if hasattr(self.filemanager_panel, 'search_input'):
            try:
                self.filemanager_panel.search_input.textChanged.disconnect()
            except:
                pass
            self.filemanager_panel.search_input.textChanged.connect(self.on_search_text_changed)
            
        # === LOG PANEL CALLBACKS ===
        if hasattr(self.log_panel, 'clear_button'):
            try:
                self.log_panel.clear_button.clicked.disconnect()
            except:
                pass
            self.log_panel.clear_button.clicked.connect(self.on_clear_logs_clicked)
             # Log que se configuraron los callbacks
        self.action_manager.log_system_event("INITIALIZATION", "All button callbacks configured")
        
    # === DISK PANEL HANDLERS ===
    def on_reboot_disk_clicked(self):
        """Maneja click del botón reboot"""
        selected_disk = self.disk_panel.disk_selector.currentText()
        self.action_manager.reboot_disk(selected_disk)
        
    def on_disk_selected(self, disk_name):
        """Maneja selección de disco"""
        self.action_manager.select_disk(disk_name)
        
    # === FILE MANAGER HANDLERS ===
    def on_search_files_clicked(self):
        """Maneja click del botón buscar"""
        search_term = self.filemanager_panel.search_input.text()
        self.action_manager.search_files(search_term)
        
    def on_search_text_changed(self, text):
        """Maneja cambio en el texto de búsqueda - NO se loggea como acción"""
        # Solo actualizar la búsqueda, sin loggear cada tecleo
        pass
            
    # === LOG PANEL HANDLERS ===
    def on_clear_logs_clicked(self):
        """Maneja click del botón limpiar logs"""
        # Log la acción de usuario
        self.action_manager.clear_logs()
        # Ejecutar la acción real en el LogPanel
        self.log_panel.clear_logs()
        
    # === SYSTEM HANDLERS ===
    def on_connection_status_changed(self, is_connected):
        """Maneja cambios en el estado de conexión"""
        status = "CONNECTED" if is_connected else "DISCONNECTED"
        title = f"{GUI_CONFIG['window_title']} - {status}"
        self.setWindowTitle(title)
        
        # El logging de conexión se maneja en server_service
        
    def on_log_message(self, level, message):
        """Maneja mensajes de log del sistema"""
        print(f"[DEBUG] MainWindow.on_log_message called with: level='{level}', message='{message}'")
        log_data = {
            "tag": "log",
            "logs": [{"level": level, "message": message}]
        }
        print(f"[DEBUG] Routing message to router: {log_data}")
        self.router.route_message(log_data)
        
    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        if hasattr(self, 'action_manager'):
            self.action_manager.app_shutdown()
        if hasattr(self, 'server_service'):
            self.server_service.stop_monitoring()
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