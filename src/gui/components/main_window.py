from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt

from .disk_status.DiskStatusPanel import DiskStatusPanel
from .file_manager.FileManagerPanel import FileManagerPanel
from .log.LogPanel import LogPanel

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
        right_splitter.setSizes([400, 200])
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([266, 534])
        
        # Event connections
        main_splitter.splitterMoved.connect(self.update)
        right_splitter.splitterMoved.connect(self.update)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        
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