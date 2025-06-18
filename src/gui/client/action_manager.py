"""
Central GUI action manager
Logs all user actions before execution
"""
from PyQt5.QtCore import QObject, pyqtSignal
from config import DEFAULT_MESSAGES, DISK_CONFIG


class ActionManager(QObject):
    """Manages all user actions and logs them"""
    
    # Signal for registering actions in the logger
    action_logged = pyqtSignal(str, str)  # (level, message)
    
    def __init__(self, server_service=None):
        super().__init__()
        self.server_service = server_service
        
    def log_user_action(self, action_name, details=""):
        """Log user action with INFO level"""
        message = f"User action: {action_name}"
        if details:
            message += f" - {details}"
        self.action_logged.emit("INFO", message)
    
    def log_system_event(self, event_type, details):
        """Log system event with SYSTEM level"""
        self.action_logged.emit("SYSTEM", f"{event_type}: {details}")
        
    def log_warning(self, message):
        """Log warning with WARNING level"""
        self.action_logged.emit("WARNING", message)
        
    def log_error(self, message):
        """Log error with ERROR level"""
        self.action_logged.emit("ERROR", message)
    
    # ========== DISK ACTIONS (INFO level) ==========
    def reboot_disk(self, disk_name):
        """Restart a specific disk"""
        # Validate disk is in configured list
        if disk_name not in DISK_CONFIG["disk_names"]:
            self.log_warning(f"Unknown disk selected: {disk_name}")
            return
            
        self.log_user_action("REBOOT_DISK", f"Target: {disk_name}")
        
        # TODO: Implement real server call
        # if self.server_service:
        #     self.server_service.reboot_disk(disk_name)
        
        # Simulate command sent
        self.log_system_event("REBOOT_COMMAND", f"Command sent to {disk_name}")
        
    def select_disk(self, disk_name):
        """Select a disk - not logged as user action"""
        # Log disk changes as system events, not user actions
        if disk_name in DISK_CONFIG["disk_names"]:
            self.log_system_event("DISK_SELECTION", f"Active disk: {disk_name}")
        else:
            self.log_warning(f"Invalid disk selection: {disk_name}")
        
    # ========== FILE ACTIONS (INFO level) ==========
    def upload_file(self, file_path=""):
        """Upload a file"""
        if file_path:
            self.log_user_action("UPLOAD_FILE", f"File: {file_path}")
        else:
            self.log_user_action("UPLOAD_FILE", "File dialog opened")
        
        # TODO: Implement real upload
        # if self.server_service and file_path:
        #     self.server_service.upload_file(file_path)
        
        # Simulate result
        if file_path:
            self.log_system_event("UPLOAD_STATUS", f"File '{file_path}' queued for upload")
        
    def download_file(self, filename, save_path=""):
        """Download a file"""
        self.log_user_action("DOWNLOAD_FILE", f"File: {filename}")
        
        # TODO: Implement real download
        # if self.server_service:
        #     self.server_service.download_file(filename, save_path)
        
        # Simulate result
        self.log_system_event("DOWNLOAD_STATUS", f"File '{filename}' download initiated")
        
    def delete_file(self, filename):
        """Delete a file"""
        self.log_user_action("DELETE_FILE", f"File: {filename}")
        
        # TODO: Implement real deletion
        # if self.server_service:
        #     self.server_service.delete_file(filename)
        
        # Simulate result
        self.log_system_event("DELETE_STATUS", f"File '{filename}' marked for deletion")
        
    def search_files(self, search_term):
        """Search files - not logged as user action"""
        # Search is not considered user action, only system event
        if search_term.strip():
            self.log_system_event("SEARCH_FILTER", f"Applied filter: '{search_term}'")
        else:
            self.log_system_event("SEARCH_FILTER", "Filter cleared")
        
    # ========== LOG ACTIONS (INFO level) ==========
    def clear_logs(self):
        """Clear logs"""
        self.log_user_action("CLEAR_LOGS")
        self.log_system_event("LOG_MANAGEMENT", "Logs cleared by user")
        
    # ========== STARTUP/SHUTDOWN (SYSTEM level) ==========
    def app_started(self):
        """Application started"""
        self.log_system_event("APPLICATION", DEFAULT_MESSAGES["startup"])
        
    def app_shutdown(self):
        """Application shutting down"""
        self.log_system_event("APPLICATION", DEFAULT_MESSAGES["shutdown"])
