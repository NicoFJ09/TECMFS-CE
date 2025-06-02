from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from enum import Enum

class DiskStatus(Enum):
    ONLINE = "online"
    BUSY = "busy"
    FAILED = "failed"
    REBUILDING = "rebuilding"

class CylinderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.status = DiskStatus.ONLINE  # Default status
        
    def set_status(self, status):
        """Update disk status"""
        if isinstance(status, DiskStatus):
            self.status = status
        else:
            # Allow string as well
            status_map = {
                "online": DiskStatus.ONLINE,
                "busy": DiskStatus.BUSY,
                "failed": DiskStatus.FAILED,
                "rebuilding": DiskStatus.REBUILDING
            }
            self.status = status_map.get(status.lower(), DiskStatus.ONLINE)
        
        self.update()  # Redraw the widget
        
    def get_colors_for_status(self):
        """Get colors based on status"""
        if self.status == DiskStatus.ONLINE:
            return {
                'top': QColor(100, 255, 100),      # Light green
                'side': QColor(80, 200, 80),       # Medium green
                'bottom': QColor(60, 150, 60)      # Dark green
            }
        elif self.status == DiskStatus.BUSY:
            return {
                'top': QColor(255, 255, 100),      # Light yellow
                'side': QColor(200, 200, 80),      # Medium yellow
                'bottom': QColor(150, 150, 60)     # Dark yellow
            }
        elif self.status == DiskStatus.FAILED:
            return {
                'top': QColor(255, 100, 100),      # Light red
                'side': QColor(200, 80, 80),       # Medium red
                'bottom': QColor(150, 60, 60)      # Dark red
            }
        elif self.status == DiskStatus.REBUILDING:
            return {
                'top': QColor(255, 180, 100),      # Light orange
                'side': QColor(200, 140, 80),      # Medium orange
                'bottom': QColor(150, 100, 60)     # Dark orange
            }
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Configure center and dimensions
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 4
        height = int(radius * 1.5)  # Convert to integer
        
        # Draw cylinder
        self.draw_cylinder(painter, center_x, center_y, radius, height)
        
    def draw_cylinder(self, painter, cx, cy, radius, height):
        # Get colors based on status
        colors = self.get_colors_for_status()
        top_color = colors['top']
        side_color = colors['side']
        bottom_color = colors['bottom']
        
        # Border color (darker)
        border_color = QColor(40, 40, 40)
        
        # Draw bottom part (dark ellipse)
        painter.setBrush(QBrush(bottom_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(cx - radius, cy + height//2 - 10, radius * 2, 20)
        
        # Draw cylinder body (rectangle)
        painter.setBrush(QBrush(side_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawRect(cx - radius, cy - height//2, radius * 2, height)
        
        # Draw top part (light ellipse)
        painter.setBrush(QBrush(top_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(cx - radius, cy - height//2 - 10, radius * 2, 20)