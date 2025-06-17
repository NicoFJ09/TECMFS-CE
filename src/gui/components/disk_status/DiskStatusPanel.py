from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QWidget, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from .CylinderWidget import CylinderWidget, DiskStatus

class DiskStatusPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title section
        self.title = QLabel("DISK ARRAY STATUS")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addWidget(self.title)
        
        # Content layout: cylinders left, info right
        content_layout = QHBoxLayout()
        
        # Initialize disk data
        self.disks = []
        self.info_labels = []
        disk_names = ["Disk D1", "Disk D2", "Disk D3", "Disk D4"]
        statuses = [DiskStatus.ONLINE, DiskStatus.REBUILDING, DiskStatus.BUSY, DiskStatus.FAILED]
        
        # Cylinder visualization section
        cylinders_layout = QVBoxLayout()
        cylinders_layout.setSpacing(8)
        for i in range(4):
            cylinder = CylinderWidget()
            cylinder.set_status(statuses[i])  # Default status, can be updated by system
            cylinder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.disks.append(cylinder)
            cylinders_layout.addWidget(cylinder)
        
        # Info labels section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        for i in range(4):
            info_widget = QLabel()
            info_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            info_widget.setAlignment(Qt.AlignCenter)
            info_widget.setWordWrap(True)
            info_widget.setAutoFillBackground(True)
            
            # Set empty/default info, will be updated by system
            info_text = f"<b>{disk_names[i]}</b><br>"
            info_text += f"Status: <b>{statuses[i].name}</b><br>"
            info_text += f"Used Space: -<br>"
            info_text += f"Last activity: -"
            
            info_widget.setText(info_text)
            self.info_labels.append(info_widget)
            info_layout.addWidget(info_widget)
        content_layout.addLayout(cylinders_layout, 1)
        content_layout.addLayout(info_layout, 1)
        main_layout.addLayout(content_layout)
        # Disk controls (dropdown + reboot)
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(40, 10, 40, 10)
        controls_layout.setSpacing(20)
        self.disk_selector = QComboBox()
        self.disk_selector.addItems(["Disk D1", "Disk D2", "Disk D3", "Disk D4"])
        self.disk_selector.setCurrentIndex(0)
        self.disk_selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.reboot_button = QPushButton("Reboot Disk")
        self.reboot_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.reboot_button.setMinimumHeight(35)
        controls_layout.addWidget(self.disk_selector)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(self.reboot_button)
        main_layout.addWidget(controls_container)
        self.update()
        
    def update(self):
        self.update_responsive_styling()
        for disk in self.disks:
            if hasattr(disk, 'update'):
                disk.update()

    def calculate_max_font_size(self, text, max_width, max_height, min_size=4, max_size=32):
        for size in range(max_size, min_size - 1, -1):
            font = QFont("Arial", size)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(0, 0, max_width, max_height, Qt.AlignCenter | Qt.TextWordWrap, text)
            
            if rect.width() <= max_width and rect.height() <= max_height:
                return size
        return min_size
        
    def update_responsive_styling(self):
        # Only update info labels and button size, not dropdown or layout
        TITLE_PADDING = 10
        INFO_PADDING = 10
        title_container_width = self.width() - 20
        title_text_width = title_container_width - (TITLE_PADDING * 2)
        title_text_height = 50 - (TITLE_PADDING * 2)
        title_font_size = self.calculate_max_font_size("DISK ARRAY STATUS", title_text_width, title_text_height, min_size=6, max_size=32)
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
        available_height = self.height() - 120
        label_container_height = available_height // 4
        label_container_width = (self.width() // 2) - 30
        label_text_width = label_container_width - (INFO_PADDING * 2)
        label_text_height = label_container_height - (INFO_PADDING * 2)
        label_text_width = max(40, label_text_width)
        label_text_height = max(20, label_text_height)
        sample_text = "Disk D1\nStatus: REBUILDING\nUsed Space: 68%\nLast activity: 3 seconds ago"
        info_font_size = self.calculate_max_font_size(sample_text, label_text_width, label_text_height, min_size=4, max_size=16)
        for info_label in self.info_labels:
            info_label.setFont(QFont("Arial", info_font_size))
            info_label.setStyleSheet(f"""
                QLabel {{
                    color: #000000;
                    background-color: rgba(240, 240, 240, 255);
                    border-radius: {INFO_PADDING//2}px;
                    border: 1px solid rgba(200, 200, 200, 255);
                    margin: {INFO_PADDING//2}px;
                }}
            """)
        # Restore reboot button style (visual only, not size)
        if hasattr(self, 'reboot_button'):
            self.reboot_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: Arial;
                    min-height: 35px;
                }}
                QPushButton:hover {{
                    background-color: #c82333;
                }}
                QPushButton:pressed {{
                    background-color: #bd2130;
                }}
            """)

    def update_disk_status(self, disk_index, status, used_space, last_activity):
        if 0 <= disk_index < len(self.disks):
            self.disks[disk_index].set_status(status)
            
            info_text = f"<b>Disk D{disk_index + 1}</b><br>"
            info_text += f"Status: <b>{status.name}</b><br>"
            info_text += f"Used Space: {used_space}<br>"
            info_text += f"Last activity: {last_activity}"
            
            self.info_labels[disk_index].setText(info_text)
            self.update_responsive_styling()

    def set_button_callbacks(self):
        self.reboot_button.clicked.connect(lambda: print(f"[ACTION] Would send reboot command for: {self.disk_selector.currentText()}"))