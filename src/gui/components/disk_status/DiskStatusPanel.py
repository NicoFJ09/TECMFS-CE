from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
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
        disk_names = ["Disk1", "Disk2", "Disk3", "Disk4"]
        statuses = [DiskStatus.ONLINE, DiskStatus.REBUILDING, DiskStatus.BUSY, DiskStatus.FAILED]
        disk_data = [
            {"status": DiskStatus.ONLINE, "used": "45%", "files": "8", "activity": "1 minute ago"},
            {"status": DiskStatus.REBUILDING, "used": "68%", "files": "12", "activity": "3 seconds ago"},
            {"status": DiskStatus.BUSY, "used": "72%", "files": "15", "activity": "Active now"},
            {"status": DiskStatus.FAILED, "used": "0%", "files": "0", "activity": "System error"}
        ]
        
        # Cylinder visualization section
        cylinders_layout = QVBoxLayout()
        cylinders_layout.setSpacing(8)
        for i in range(4):
            cylinder = CylinderWidget()
            cylinder.set_status(statuses[i])
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
            
            info_text = f"<b>{disk_names[i]}</b><br>"
            info_text += f"Status: <b>{statuses[i].name}</b><br>"
            info_text += f"Used Space: {disk_data[i]['used']}<br>"
            info_text += f"Files: {disk_data[i]['files']}<br>"
            info_text += f"Last activity: {disk_data[i]['activity']}"
            
            info_widget.setText(info_text)
            self.info_labels.append(info_widget)
            info_layout.addWidget(info_widget)
        
        content_layout.addLayout(cylinders_layout, 1)
        content_layout.addLayout(info_layout, 1)
        main_layout.addLayout(content_layout)
        
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
        if self.width() < 50 or self.height() < 50:
            return
        
        # Title styling - only font, no custom background/colors
        title_container_width = self.width() - 20
        title_font_size = self.calculate_max_font_size("DISK ARRAY STATUS", title_container_width, 50, min_size=10, max_size=24)
        
        self.title.setFont(QFont("Arial", title_font_size, QFont.Bold))
        self.title.setStyleSheet("")  # Use native styling
        
        # Info labels styling - native appearance with font sizing
        available_height = self.height() - 120
        label_container_height = available_height // 4
        label_container_width = (self.width() // 2) - 30
        
        label_text_width = label_container_width - 20
        label_text_height = label_container_height - 20
        
        label_text_width = max(40, label_text_width)
        label_text_height = max(20, label_text_height)
        
        sample_text = "Disk1\nStatus: REBUILDING\nUsed Space: 68%\nFiles: 12\nLast activity: 3 seconds ago"
        info_font_size = self.calculate_max_font_size(sample_text, label_text_width, label_text_height, min_size=6, max_size=14)
        
        for info_label in self.info_labels:
            info_label.setFont(QFont("Arial", info_font_size))
            info_label.setStyleSheet("")  # Use native styling
            # Set frame style for visual separation while keeping native appearance
            info_label.setFrameStyle(QFrame.StyledPanel)
            
    def update_disk_status(self, disk_index, status, used_space, files_count, last_activity):
        if 0 <= disk_index < len(self.disks):
            self.disks[disk_index].set_status(status)
            
            info_text = f"<b>Disk D{disk_index + 1}</b><br>"
            info_text += f"Status: <b>{status.name}</b><br>"
            info_text += f"Used Space: {used_space}%<br>"
            info_text += f"Files: {files_count}<br>"
            info_text += f"Last activity: {last_activity}"
            
            self.info_labels[disk_index].setText(info_text)
            self.update_responsive_styling()