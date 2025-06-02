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
        
        # Set minimum size for the main window (not panels)
        self.setMinimumSize(screen.width()//2, screen.height()//2)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal splitter (left/right)
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Right side vertical splitter (file manager top, log bottom)
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
        
        # DISK STATUS PANEL (left side, full height, 1/3 width)
        self.disk_panel = DiskStatusPanel()
        main_splitter.addWidget(self.disk_panel)
        
        # FILE MANAGER PANEL (right top)
        self.filemanager_panel = FileManagerPanel()
        right_splitter.addWidget(self.filemanager_panel)
        
        # LOG PANEL (right bottom)
        self.log_panel = LogPanel()
        right_splitter.addWidget(self.log_panel)
        
        # Set sizes for right splitter (file manager: 400, log: 200)
        right_splitter.setSizes([400, 200])
        
        # Add right splitter to main splitter
        main_splitter.addWidget(right_splitter)
        
        # Set sizes for main splitter (disk: 266 = 1/3, right side: 534 = 2/3)
        main_splitter.setSizes([266, 534])
        
        # Connect splitter signals for immediate updates
        main_splitter.splitterMoved.connect(self.update)
        right_splitter.splitterMoved.connect(self.update)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        
    def resizeEvent(self, event):
        """Handle main window resize - update all panels"""
        super().resizeEvent(event)
        self.update()
        
    def update(self):
        """MAIN UPDATE FUNCTION - Called from main loop and events"""
        # Update disk status panel
        if hasattr(self, 'disk_panel'):
            self.disk_panel.update()
            
        # Update file manager panel
        if hasattr(self, 'filemanager_panel'):
            self.filemanager_panel.update()
            
        # Update log panel
        if hasattr(self, 'log_panel'):
            self.log_panel.update()