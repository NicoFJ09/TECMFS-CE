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
    def refresh_disk(self):
        """Refresca el estado de todos los discos llamando al server_service"""
        self.log_user_action("REFRESH_DISKS", "Refreshing all disks")

        if self.server_service:
            success, msg = self.server_service.refresh_disk()
            if success:
                self.log_system_event("REFRESH_COMMAND", f"Refresh request sent: {msg}")
                self.action_logged.emit("INFO", f"Server response: {msg}")
            else:
                self.log_error(f"Refresh failed: {msg}")
        else:
            self.log_error("No server service available for refresh")
        
    # ========== FILE ACTIONS (INFO level) ==========
    def upload_file(self, file_path=""):
        """Upload a file"""
        if file_path:
            self.log_user_action("UPLOAD_FILE", f"File: {file_path}")
            
            # Real upload implementation
            if self.server_service:
                success = self.server_service.upload_file(file_path)
                if success:
                    self.log_system_event("UPLOAD_STATUS", f"File '{file_path}' uploaded successfully")
                else:
                    self.log_error(f"Upload failed for '{file_path}'")
            else:
                self.log_error("No server service available for upload")
        else:
            self.log_user_action("UPLOAD_FILE", "File dialog opened")
        
    def download_file(self, filename, save_path=""):
        """Download a file"""
        self.log_user_action("DOWNLOAD_FILE", f"File: {filename}")
        
        # Real download implementation
        if self.server_service:
            success = self.server_service.download_file(filename, save_path)
            if success:
                self.log_system_event("DOWNLOAD_STATUS", f"File '{filename}' downloaded successfully")
            else:
                self.log_error(f"Download failed for '{filename}'")
        else:
            self.log_error("No server service available for download")
        
    def delete_file(self, filename):
        """Delete a file"""
        self.log_user_action("DELETE_FILE", f"File: {filename}")
        
        # Real deletion implementation
        if self.server_service:
            success = self.server_service.delete_file(filename)
            if success:
                self.log_system_event("DELETE_STATUS", f"File '{filename}' deleted successfully")
            else:
                self.log_error(f"Delete failed for '{filename}'")
        else:
            self.log_error("No server service available for deletion")
        
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
