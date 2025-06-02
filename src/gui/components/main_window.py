from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt

from .disk_status.disk_status_panel import DiskStatusPanel
from .file_manager.file_manager_panel import FileManagerPanel
from .log.log_panel import LogPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Window setup
        screen = QApplication.desktop().screenGeometry()
        self.setWindowTitle("TECMFS-CE")
        self.setGeometry(100, 100, screen.width()//2, screen.height()//2)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_splitter = QSplitter(Qt.Vertical)
        top_splitter = QSplitter(Qt.Horizontal)
        
        splitter_style = """
            QSplitter::handle {
                background-color: rgba(128, 128, 128, 30);
            }
            QSplitter::handle:hover {
                background-color: rgba(128, 128, 128, 80);
            }
        """
        main_splitter.setStyleSheet(splitter_style)
        top_splitter.setStyleSheet(splitter_style)
        
        # DISK STATUS PANEL
        self.disk_panel = DiskStatusPanel()
        top_splitter.addWidget(self.disk_panel)
        
        # FILE MANAGER PANEL
        self.filemanager_panel = FileManagerPanel()
        top_splitter.addWidget(self.filemanager_panel)
        
        top_splitter.setSizes([266, 534])
        main_splitter.addWidget(top_splitter)
        
        # LOG PANEL
        self.log_panel = LogPanel()
        main_splitter.addWidget(self.log_panel)
        
        main_splitter.setSizes([400, 200])
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)