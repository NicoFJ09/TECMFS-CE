from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                             QPushButton, QCheckBox, QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontMetrics
import datetime

class LogPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.log_messages = []
        self.setup_ui()
        self.start_demo_timer()
        
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
        
        # Initialize with some sample logs
        self.add_sample_logs()
        
        self.update()
        
    def add_sample_logs(self):
        """Add some initial sample log messages"""
        sample_logs = [
            ("INFO", "System initialized successfully"),
            ("INFO", "File system mounted on /dev/disk1"),
            ("WARNING", "Disk D2 showing high usage (68%)"),
            ("INFO", "User uploaded file: document.pdf"),
            ("ERROR", "Disk D4 connection failed"),
            ("INFO", "Auto-rebuild started for Disk D2"),
            ("SUCCESS", "File transfer completed"),
        ]
        
        for level, message in sample_logs:
            self.add_log_message(level, message)
    
    def add_log_message(self, level, message):
        """Add a new log message with timestamp and level"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Create formatted message with separators
        formatted_message = f"[{timestamp}] {level}: {message}"
        self.log_messages.append(formatted_message)
        
        # Update display
        self.update_log_display()
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_checkbox.isChecked():
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
        print("Logs cleared")
    
    def start_demo_timer(self):
        """Start a timer to add demo log messages periodically"""
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.add_demo_log)
        self.demo_timer.start(3000)  # Add new log every 3 seconds
        
        self.demo_messages = [
            ("INFO", "Periodic system check completed"),
            ("INFO", "Disk synchronization in progress"),
            ("WARNING", "High CPU usage detected"),
            ("INFO", "Backup process started"),
            ("SUCCESS", "All systems operating normally"),
            ("INFO", "User session activity detected"),
            ("INFO", "Cache cleanup completed"),
        ]
        self.demo_index = 0
    
    def add_demo_log(self):
        """Add a demo log message for demonstration"""
        if self.demo_messages:
            level, message = self.demo_messages[self.demo_index]
            self.add_log_message(level, message)
            self.demo_index = (self.demo_index + 1) % len(self.demo_messages)
    
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