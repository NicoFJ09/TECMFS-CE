from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class FileManagerPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Dummy text label
        self.label = QLabel("FILE MANAGER PANEL\nResize me to see dynamic text!")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 20px;
                background-color: rgba(100, 255, 150, 50);
                border: 2px dashed #666;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(self.label)
        
    def resizeEvent(self, event):
        """Update label text based on panel size"""
        super().resizeEvent(event)
        if hasattr(self, 'label'):
            width = self.width()
            height = self.height()
            self.label.setText(f"FILE MANAGER PANEL\nSize: {width} x {height}\nResize me!")