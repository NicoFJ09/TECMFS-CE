from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                             QPushButton, QCheckBox, QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontMetrics
import datetime
from config import LOG_CONFIG

class LogPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.log_messages = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        self.title = QLabel("SYSTEM LOGS")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addWidget(self.title)
        
        # Log display area - scrollable text edit
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_display.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.log_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(self.log_display, 1)
        
        # Separator before controls
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Controls container
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(10, 5, 10, 10)
        controls_layout.setSpacing(15)
        
        # Auto-scroll checkbox
        self.auto_scroll_checkbox = QCheckBox("Auto-scroll")
        self.auto_scroll_checkbox.setChecked(True)
        self.auto_scroll_checkbox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        # Clear button
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.clear_button.clicked.connect(self.clear_logs)
        
        controls_layout.addWidget(self.auto_scroll_checkbox)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.clear_button)
        
        main_layout.addWidget(controls_container)
        
        self.update()
        
    def add_log_message(self, level, message):
        """Add a new log message with timestamp and level usando config"""
        timestamp = datetime.datetime.now().strftime(LOG_CONFIG["timestamp_format"])
        
        # Create formatted message with separators
        formatted_message = f"[{timestamp}] {level}: {message}"
        self.log_messages.append(formatted_message)
        
        # Mantener solo el máximo configurado de logs
        if len(self.log_messages) > LOG_CONFIG["max_logs"]:
            self.log_messages = self.log_messages[-LOG_CONFIG["max_logs"]:]
        
        # Update display
        self.update_log_display()
        
        # Auto-scroll to bottom if enabled usando config
        if LOG_CONFIG.get("auto_scroll", True) and self.auto_scroll_checkbox.isChecked():
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def update_log_display(self):
        """Update the log display with all messages"""
        log_text = ""
        for i, message in enumerate(self.log_messages):
            log_text += message
            if i < len(self.log_messages) - 1:
                log_text += "\n" + "-" * 50 + "\n"  # Separator line between messages
        
        self.log_display.setPlainText(log_text)
    
    def clear_logs(self):
        """Clear all log messages"""
        self.log_messages.clear()
        self.log_display.clear()
        # NO print a consola - la acción se loggea via ActionManager

    def update(self):
        self.update_responsive_styling()
        
    def calculate_max_font_size(self, text, max_width, max_height, min_size=4, max_size=32):
        for size in range(max_size, min_size - 1, -1):
            font = QFont("Arial", size)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(0, 0, max_width, max_height, Qt.AlignCenter | Qt.TextWordWrap, text)
            
            if rect.width() <= max_width and rect.height() <= max_height:
                return size
        return min_size
        
    def update_responsive_styling(self):
        if self.width() < 50 or self.height() < 50:
            return
            
        TITLE_PADDING = 10
        
        # Title styling - same as FileManagerPanel
        title_container_width = self.width() - 20
        title_text_width = title_container_width - (TITLE_PADDING * 2)
        title_text_height = 50 - (TITLE_PADDING * 2)
        
        title_font_size = self.calculate_max_font_size("SYSTEM LOGS", title_text_width, title_text_height, min_size=6, max_size=32)
        
        self.title.setFont(QFont("Arial", title_font_size, QFont.Bold))
        self.title.setStyleSheet(f"""
            QLabel {{
                color: #2C3E50; 
                background-color: rgba(200, 220, 240, 255);
                border-radius: {TITLE_PADDING//2}px;
                border: 1px solid rgba(150, 170, 190, 255);
                margin-bottom: {TITLE_PADDING}px;
            }}
        """)
        
        # Log display - native styling with font sizing
        log_font_size = self.calculate_max_font_size("Sample log text", self.width() - 40, 30, min_size=8, max_size=12)
        
        self.log_display.setFont(QFont("Menlo", log_font_size))
        self.log_display.setStyleSheet("")  # Native styling
        
        # Controls - native styling with font sizing
        controls_font_size = self.calculate_max_font_size("Clear Logs", 100, 30, min_size=8, max_size=12)
        
        self.clear_button.setFont(QFont("Arial", controls_font_size))
        self.clear_button.setStyleSheet("")  # Native styling
        
        self.auto_scroll_checkbox.setFont(QFont("Arial", controls_font_size))
        self.auto_scroll_checkbox.setStyleSheet("")  # Native styling
        
        # Separators - native styling
        for child in self.findChildren(QFrame):
            if child.frameShape() == QFrame.HLine:
                child.setStyleSheet("")  # Native styling
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()