from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QWidget, QSizePolicy, QLabel, QComboBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics

class FileManagerPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.disk_files = {}  # Store files for each disk
        self.current_disk = "DISK1"  # Track current disk
        self.setup_ui()
        
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
        
        # Disk selector
        disk_label = QLabel("Disk:")
        disk_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.disk_selector = QComboBox()
        self.disk_selector.addItems(["DISK1", "DISK2", "DISK3", "DISK4"])
        self.disk_selector.setCurrentIndex(0)
        self.disk_selector.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # Connect disk change to load different files
        self.disk_selector.currentTextChanged.connect(self.on_disk_changed)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nombre de archivo...")
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # Connect Enter key to search
        self.search_input.returnPressed.connect(self.search_files)
        
        # Search button
        self.search_button = QPushButton("Buscar")
        self.search_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.search_button.clicked.connect(self.search_files)
        
        controls_layout.addWidget(disk_label, 0)
        controls_layout.addWidget(self.disk_selector, 0)
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
        
        # File table with OS native styling
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
        header.resizeSection(2, 240) # Set Actions column width to 220px
        
        # Set fixed row height for all rows
        self.file_table.verticalHeader().setDefaultSectionSize(65)
        self.file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        # Enable scrolling
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.file_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Initialize sample data for all disks
        self.populate_disk_data()
        
        # Load initial disk data
        self.load_disk_files()
        
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
        
        # Reboot disk button
        self.reboot_button = QPushButton("Reboot Disk")
        self.reboot_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.reboot_button.setMinimumHeight(35)
        self.reboot_button.clicked.connect(self.reboot_disk)
        
        bottom_buttons_layout.addWidget(self.upload_button)
        bottom_buttons_layout.addWidget(self.reboot_button)
        
        main_layout.addWidget(bottom_buttons_container)
        
        self.update()
        
    def populate_disk_data(self):
        """Initialize sample files for each disk"""
        self.disk_files = {
            "DISK1": [
                ("system_config.ini", "2 KB"),
                ("boot.img", "128 MB"),
                ("kernel.bin", "45 MB"),
                ("drivers.sys", "15 MB"),
                ("startup.exe", "3.2 MB")
            ],
            "DISK2": [
                ("document.pdf", "2.1 MB"),
                ("presentation.pptx", "12.5 MB"),
                ("spreadsheet.xlsx", "3.7 MB"),
                ("report.docx", "1.8 MB"),
                ("notes.txt", "25 KB"),
                ("manual.pdf", "8.9 MB")
            ],
            "DISK3": [
                ("vacation_2023.jpg", "4.2 MB"),
                ("family_photo.png", "2.8 MB"),
                ("sunset.raw", "45 MB"),
                ("wedding_video.mp4", "1.2 GB"),
                ("music_collection.zip", "89 MB"),
                ("birthday.mov", "567 MB")
            ],
            "DISK4": [
                ("backup_db.sql", "234 MB"),
                ("server_logs.txt", "15 KB"),
                ("config.json", "3 KB"),
                ("application.jar", "67 MB"),
                ("source_code.zip", "12 MB"),
                ("database.backup", "456 MB"),
                ("scripts.tar.gz", "8.5 MB")
            ]
        }
    
    def on_disk_changed(self, disk_name):
        """Handle disk selection change"""
        self.current_disk = disk_name
        self.search_input.clear()  # Clear search when changing disks
        self.load_disk_files()
        print(f"Switched to {disk_name}")
    
    def load_disk_files(self):
        """Load files for the current disk"""
        current_files = self.disk_files.get(self.current_disk, [])
        self.display_files(current_files)
    
    def get_current_disk_files(self):
        """Get files for the current disk"""
        return self.disk_files.get(self.current_disk, [])
    
    def display_files(self, files_to_display):
        """Display the given list of files in the table"""
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
            delete_btn.setFixedSize(80, 34)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_file(r))
            
            download_btn = QPushButton("Download")
            download_btn.setFixedSize(90, 34)
            download_btn.clicked.connect(lambda checked, r=row: self.download_file(r))
            
            actions_layout.addWidget(delete_btn)
            actions_layout.addWidget(download_btn)
            
            self.file_table.setCellWidget(row, 2, actions_widget)
    
    def search_files(self):
        """Search for files matching the search term in the current disk"""
        search_term = self.search_input.text().strip().lower()
        current_files = self.get_current_disk_files()
        
        if not search_term:
            # If search is empty, show all files from current disk
            self.display_files(current_files)
            return
        
        # Filter files that contain the search term in their name
        matching_files = []
        for filename, size in current_files:
            if search_term in filename.lower():
                matching_files.append((filename, size))
        
        # Display the filtered results
        self.display_files(matching_files)
        
        # Show feedback in console
        if matching_files:
            print(f"Found {len(matching_files)} file(s) matching '{search_term}' in {self.current_disk}")
        else:
            print(f"No files found matching '{search_term}' in {self.current_disk}")
    
    def delete_file(self, row):
        """Handle file deletion from current disk"""
        if row < self.file_table.rowCount():
            filename = self.file_table.item(row, 0).text()
            print(f"Deleting file: {filename} from {self.current_disk}")
            
            # Remove from current disk's file list
            current_files = self.disk_files.get(self.current_disk, [])
            self.disk_files[self.current_disk] = [(f, s) for f, s in current_files if f != filename]
            
            # Refresh the current view (re-apply search if active)
            self.search_files()
        
    def download_file(self, row):
        """Handle file download"""
        if row < self.file_table.rowCount():
            filename = self.file_table.item(row, 0).text()
            print(f"Downloading file: {filename} from {self.current_disk}")
    
    def upload_file(self):
        """Handle file upload - opens file dialog and prints absolute path"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select file to upload",
            "",
            "All Files (*)"
        )
        
        if file_path:
            print(f"Selected file for upload: {file_path}")
            # Here you would normally handle the file upload to the current disk
            # For now, we just print the absolute path
    
    def reboot_disk(self):
        """Handle disk reboot"""
        print(f"Rebooting {self.current_disk}...")
        # Here you would normally handle the actual disk reboot functionality
        
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
            
        # Title styling - keep only font sizing, remove custom colors/backgrounds
        title_container_width = self.width() - 20
        title_font_size = self.calculate_max_font_size("FILE MANAGER", title_container_width, 50, min_size=10, max_size=24)
        
        self.title.setFont(QFont("Arial", title_font_size, QFont.Bold))
        self.title.setStyleSheet("")  # Remove custom styling, use native
        
        # Controls - use native styling, only set dimensions
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
        
        # Font sizes only
        label_font_size = self.calculate_max_font_size("Disk:", label_width, controls_height - 8, min_size=8, max_size=12)
        dropdown_font_size = self.calculate_max_font_size("DISK1", dropdown_width, controls_height - 8, min_size=8, max_size=12)
        input_font_size = self.calculate_max_font_size("Aa", search_width, controls_height - 8, min_size=8, max_size=14)
        button_font_size = self.calculate_max_font_size("Buscar", button_width, controls_height - 8, min_size=8, max_size=12)
        
        # Apply only font styling, keep native appearance
        disk_label = self.findChildren(QLabel)[1]
        if disk_label and disk_label.text() == "Disk:":
            disk_label.setFont(QFont("Arial", label_font_size, QFont.Bold))
            disk_label.setStyleSheet("")  # Native styling
        
        # Set dimensions but keep native styling
        self.disk_selector.setFixedWidth(dropdown_width)
        self.disk_selector.setFont(QFont("Arial", dropdown_font_size))
        self.disk_selector.setStyleSheet("")  # Native styling
        
        self.search_input.setMinimumWidth(search_width)
        self.search_input.setMaximumWidth(search_width)
        self.search_input.setFont(QFont("Arial", input_font_size))
        self.search_input.setStyleSheet("QLineEdit { padding: 4px; }") 
        
        self.search_button.setMinimumWidth(button_width)
        self.search_button.setMaximumWidth(button_width)
        self.search_button.setFont(QFont("Arial", button_font_size))
        self.search_button.setStyleSheet("")  # Native styling
        
        # Bottom buttons - native styling with font sizing
        bottom_button_font_size = self.calculate_max_font_size("Upload File", self.width()//2 - 40, 35, min_size=10, max_size=16)
        
        self.upload_button.setFont(QFont("Arial", bottom_button_font_size))
        self.upload_button.setStyleSheet("")  # Native styling
        
        self.reboot_button.setFont(QFont("Arial", bottom_button_font_size))
        self.reboot_button.setStyleSheet("")  # Native styling
        
        # File table - completely native styling
        self.file_table.setStyleSheet("")  # Remove all custom styling
        
        # Separators - native styling
        for child in self.findChildren(QFrame):
            if child.frameShape() == QFrame.HLine:
                child.setStyleSheet("")  # Native styling
        
    def get_selected_disk(self):
        return self.disk_selector.currentText()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()