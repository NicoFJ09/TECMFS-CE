from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QWidget, QSizePolicy, QLabel, QComboBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics, QPalette
import platform
import importlib
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from client.action_manager import ActionManager

class FileManagerPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.files = []  # Single file list
        self.action_manager: Optional['ActionManager'] = None  # Will be set by MainWindow
        self.setup_ui()
        
    def is_dark_mode(self):
        """Detect if the system is in dark mode"""
        try:
            if platform.system() == "Darwin":  # macOS
                import subprocess
                result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                      capture_output=True, text=True)
                return result.stdout.strip() == 'Dark'
            elif platform.system() == "Windows":  # Windows
                try:
                    winreg = importlib.import_module('winreg')
                    key = getattr(winreg, 'OpenKey')(getattr(winreg, 'HKEY_CURRENT_USER'),
                        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = getattr(winreg, 'QueryValueEx')(key, "AppsUseLightTheme")
                    getattr(winreg, 'CloseKey')(key)
                    return value == 0  # 0 = dark mode, 1 = light mode
                except Exception:
                    pass
            
            # Fallback: check QPalette for all systems
            palette = self.palette()
            window_color = palette.color(QPalette.Window)
            text_color = palette.color(QPalette.WindowText)
            return window_color.lightness() < text_color.lightness()
            
        except Exception as e:
            print(f"Dark mode detection failed: {e}")
            # Ultimate fallback
            palette = self.palette()
            return palette.color(QPalette.Window).lightness() < 128
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        self.title = QLabel("FILE MANAGER")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addWidget(self.title)
        
        # Controls bar container with centered content
        controls_outer_container = QWidget()
        controls_outer_layout = QHBoxLayout(controls_outer_container)
        controls_outer_layout.setContentsMargins(0, 0, 0, 0)
        controls_outer_layout.addStretch(1)
        
        # Inner controls container
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("File name...")
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # Connect Enter key to search
        self.search_input.returnPressed.connect(self.search_files)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.search_button.clicked.connect(self.search_files)
        
        controls_layout.addWidget(self.search_input, 1)
        controls_layout.addWidget(self.search_button, 0)
        
        controls_outer_layout.addWidget(controls_container, 0)
        controls_outer_layout.addStretch(1)
        
        main_layout.addWidget(controls_outer_container)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # File table
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["File Name", "Size", "Actions"])
        self.file_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setShowGrid(True)
        self.file_table.setAlternatingRowColors(True)
        
        # Configure table headers
        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Fixed width for Actions column
        header.resizeSection(2, 220)  # Set Actions column width to 220px
        
        # Set fixed row height for all rows
        self.file_table.verticalHeader().setDefaultSectionSize(65)
        self.file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        # Enable scrolling
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.file_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        main_layout.addWidget(self.file_table, 1)
        
        # Separator before bottom buttons
        bottom_separator = QFrame()
        bottom_separator.setFrameShape(QFrame.HLine)
        bottom_separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(bottom_separator)
        
        # Bottom buttons container
        bottom_buttons_container = QWidget()
        bottom_buttons_layout = QHBoxLayout(bottom_buttons_container)
        bottom_buttons_layout.setContentsMargins(10, 1, 10, 10)
        bottom_buttons_layout.setSpacing(20)
        
        # Upload file button
        self.upload_button = QPushButton("Upload File")
        self.upload_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.upload_button.setMinimumHeight(35)
        self.upload_button.clicked.connect(self.upload_file)
        bottom_buttons_layout.addWidget(self.upload_button)
        
        main_layout.addWidget(bottom_buttons_container)
        
        self.update()
        
    def display_files(self, files_to_display):
        self.file_table.setRowCount(len(files_to_display))
        for row, (filename, size) in enumerate(files_to_display):
            # File name
            name_item = QTableWidgetItem(filename)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.file_table.setItem(row, 0, name_item)
            
            # Size
            size_item = QTableWidgetItem(size)
            size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)
            size_item.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 1, size_item)
            
            # Actions - centered widget in cell
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(10, 8, 10, 8)  # More padding for centering
            actions_layout.setSpacing(8)
            actions_layout.setAlignment(Qt.AlignCenter)  # Center the layout
            
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(70, 34)  # Bigger buttons to fit better in 50px rows
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_file(r))
            
            download_btn = QPushButton("Download")
            download_btn.setFixedSize(80, 34)
            download_btn.clicked.connect(lambda checked, r=row: self.download_file(r))
            
            actions_layout.addWidget(delete_btn)
            actions_layout.addWidget(download_btn)
            
            self.file_table.setCellWidget(row, 2, actions_widget)

    def search_files(self):
        """Search for files matching the search term in the current disk"""
        search_term = self.search_input.text().strip().lower()
        
        if not search_term:
            # If search is empty, show all files from current disk
            self.display_files(self.files)
            return
        
        # Filter files that contain the search term in their name
        matching_files = [(f, s) for f, s in self.files if search_term in f.lower()]
        
        # Display the filtered results
        self.display_files(matching_files)
        
        # Optional: Log search results via ActionManager (but not as user action)
        if search_term.strip() and self.action_manager and len(matching_files) > 0:
            self.action_manager.log_system_event("SEARCH_RESULT", f"Found {len(matching_files)} files matching '{search_term}'")

    def delete_file(self, row):
        """Handle file deletion from current disk"""
        if row < self.file_table.rowCount():
            filename = self.file_table.item(row, 0).text()
            
            # DEBUG: Check if action_manager is available
            print(f"[DEBUG] delete_file called for: {filename}")
            print(f"[DEBUG] action_manager is: {self.action_manager}")
            
            if self.action_manager:
                print(f"[DEBUG] Calling action_manager.delete_file({filename})")
                self.action_manager.delete_file(filename)
            else:
                print(f"[DEBUG] action_manager is None!")
            
            # Remove from current disk's file list
            self.files = [(f, s) for f, s in self.files if f != filename]
            
            # Refresh the current view (re-apply search if active)
            self.search_files()

    def download_file(self, row):
        """Handle file download"""
        if row < self.file_table.rowCount():
            filename = self.file_table.item(row, 0).text()
            
            # DEBUG: Check if action_manager is available
            print(f"[DEBUG] download_file called for: {filename}")
            print(f"[DEBUG] action_manager is: {self.action_manager}")
            
            if self.action_manager:
                print(f"[DEBUG] Calling action_manager.download_file({filename})")
                self.action_manager.download_file(filename)
            else:
                print(f"[DEBUG] action_manager is None!")

    def upload_file(self):
        """Handle file upload"""
        if self.action_manager:
            self.action_manager.upload_file()
            
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select file to upload",
            "",
            "All Files (*)"
        )
        
        if file_path and self.action_manager:
            # Log the actual file selected
            self.action_manager.upload_file(file_path)
    
    def reboot_disk(self):
        """Handle disk reboot"""
        if self.action_manager:
            self.action_manager.log_system_event("DEPRECATED", "reboot_disk called from FileManagerPanel")
        
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
            
        # Determine text color based on dark mode detection
        is_dark = self.is_dark_mode()
        table_text_color = "white" if is_dark else "black"
        header_text_color = "white" if is_dark else "black"
        button_text_color = "white" if is_dark else "black"
            
        TITLE_PADDING = 10
        
        # Title styling
        title_container_width = self.width() - 20
        title_text_width = title_container_width - (TITLE_PADDING * 2)
        title_text_height = 50 - (TITLE_PADDING * 2)
        
        title_font_size = self.calculate_max_font_size("FILE MANAGER", title_text_width, title_text_height, min_size=6, max_size=32)
        
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
        
        # Controls bar styling
        controls_height = 35
        
        label_width = 40
        dropdown_width = 80
        button_width = 80
        search_width = 200
        
        total_controls_width = label_width + dropdown_width + search_width + button_width + (8 * 3)
        
        available_width = self.width() - 40
        if total_controls_width > available_width:
            scale_factor = available_width / total_controls_width
            search_width = int(search_width * scale_factor)
            button_width = int(button_width * scale_factor)
            dropdown_width = int(dropdown_width * scale_factor)
        
        # Font sizes
        input_font_size = self.calculate_max_font_size("Aa", 200, 27, min_size=8, max_size=14)
        button_font_size = self.calculate_max_font_size("Search", 80, 27, min_size=6, max_size=12)
        
        # Apply styling to controls
        self.search_input.setMinimumWidth(search_width)
        self.search_input.setMaximumWidth(search_width)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid #ccc;
                border-radius: 4px;
                font-size: {input_font_size}px;
                background-color: white;
                color: black;
                font-family: Arial;
                min-height: {controls_height - 8}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """)
        
        self.search_button.setMinimumWidth(button_width)
        self.search_button.setMaximumWidth(button_width)
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: {button_font_size}px;
                font-weight: bold;
                font-family: Arial;
                min-height: {controls_height - 4}px;
            }}
            QPushButton:hover {{
                background-color: #005a9e;
            }}
            QPushButton:pressed {{
                background-color: #004080;
            }}
        """)
        
        # Bottom buttons styling
        bottom_button_font_size = self.calculate_max_font_size("Upload File", self.width()//2 - 40, 40, min_size=10, max_size=16)
        
        self.upload_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {bottom_button_font_size}px;
                font-weight: bold;
                font-family: Arial;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
            QPushButton:pressed {{
                background-color: #1e7e34;
            }}
        """)
        
        # File table with smart dark mode detection
        self.file_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: palette(mid);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
                alternate-background-color: palette(alternate-base);
                background-color: palette(base);
                color: {table_text_color};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid palette(mid);
                color: {table_text_color};
            }}
            QHeaderView::section {{
                background-color: palette(button);
                color: {header_text_color};
                padding: 10px;
                border: 1px solid palette(mid);
                font-weight: bold;
                height: 30px;
            }}
            QPushButton {{
                background-color: palette(button);
                color: {button_text_color};
                border: 1px solid palette(mid);
                border-radius: 3px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: palette(light);
                color: {button_text_color};
            }}
            QPushButton:pressed {{
                background-color: palette(dark);
                color: {button_text_color};
            }}
        """)
        
        # Separator styling
        for child in self.findChildren(QFrame):
            if child.frameShape() == QFrame.HLine:
                child.setStyleSheet("QFrame { color: #666; }")
        
    def get_selected_disk(self):
        return self.disk_selector.currentText()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()
        
    def set_files(self, files):
        self.files = files
        self.display_files(self.files)