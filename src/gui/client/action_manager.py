"""
Manejador central de acciones de la GUI
Registra todas las acciones en el logger antes de ejecutarlas
"""
from PyQt5.QtCore import QObject, pyqtSignal
from config import DEFAULT_MESSAGES, DISK_CONFIG


class ActionManager(QObject):
    """Maneja todas las acciones de usuario y las registra"""
    
    # Señal para registrar acciones en el logger
    action_logged = pyqtSignal(str, str)  # (level, message)
    
    def __init__(self, server_service=None):
        super().__init__()
        self.server_service = server_service
        
    def log_user_action(self, action_name, details=""):
        """Registra una acción de usuario con nivel INFO"""
        message = f"User action: {action_name}"
        if details:
            message += f" - {details}"
        print(f"[DEBUG] Emitting signal: action_logged('INFO', '{message}')")
        self.action_logged.emit("INFO", message)
    
    def log_system_event(self, event_type, details):
        """Registra un evento del sistema con nivel SYSTEM"""
        self.action_logged.emit("SYSTEM", f"{event_type}: {details}")
        
    def log_warning(self, message):
        """Registra una advertencia con nivel WARNING"""
        self.action_logged.emit("WARNING", message)
        
    def log_error(self, message):
        """Registra un error con nivel ERROR"""
        self.action_logged.emit("ERROR", message)
    
    # ========== ACCIONES DE DISCOS (INFO level) ==========
    def reboot_disk(self, disk_name):
        """Reiniciar un disco específico"""
        # Validar que el disco esté en la lista configurada
        if disk_name not in DISK_CONFIG["disk_names"]:
            self.log_warning(f"Unknown disk selected: {disk_name}")
            return
            
        self.log_user_action("REBOOT_DISK", f"Target: {disk_name}")
        
        # TODO: Implementar llamada real al servidor
        # if self.server_service:
        #     self.server_service.reboot_disk(disk_name)
        
        # Por ahora, simular que se envió el comando
        self.log_system_event("REBOOT_COMMAND", f"Command sent to {disk_name}")
        
    def select_disk(self, disk_name):
        """Seleccionar un disco - NO se loggea como acción de usuario"""
        # Solo loggear cambios de disco, no como acción de usuario
        if disk_name in DISK_CONFIG["disk_names"]:
            self.log_system_event("DISK_SELECTION", f"Active disk: {disk_name}")
        else:
            self.log_warning(f"Invalid disk selection: {disk_name}")
        
    # ========== ACCIONES DE ARCHIVOS (INFO level) ==========
    def upload_file(self, file_path=""):
        """Subir un archivo"""
        if file_path:
            self.log_user_action("UPLOAD_FILE", f"File: {file_path}")
        else:
            self.log_user_action("UPLOAD_FILE", "File dialog opened")
        
        # TODO: Implementar subida real
        # if self.server_service and file_path:
        #     self.server_service.upload_file(file_path)
        
        # Por ahora, simular resultado
        if file_path:
            self.log_system_event("UPLOAD_STATUS", f"File '{file_path}' queued for upload")
        
    def download_file(self, filename, save_path=""):
        """Descargar un archivo"""
        print(f"[DEBUG] ActionManager.download_file called with: {filename}")
        self.log_user_action("DOWNLOAD_FILE", f"File: {filename}")
        
        # TODO: Implementar descarga real
        # if self.server_service:
        #     self.server_service.download_file(filename, save_path)
        
        # Por ahora, simular resultado
        self.log_system_event("DOWNLOAD_STATUS", f"File '{filename}' download initiated")
        print(f"[DEBUG] ActionManager.download_file completed for: {filename}")
        
    def delete_file(self, filename):
        """Eliminar un archivo"""
        print(f"[DEBUG] ActionManager.delete_file called with: {filename}")
        self.log_user_action("DELETE_FILE", f"File: {filename}")
        
        # TODO: Implementar eliminación real
        # if self.server_service:
        #     self.server_service.delete_file(filename)
        
        # Por ahora, simular resultado
        self.log_system_event("DELETE_STATUS", f"File '{filename}' marked for deletion")
        print(f"[DEBUG] ActionManager.delete_file completed for: {filename}")
        
    def search_files(self, search_term):
        """Buscar archivos - NO se loggea como acción de usuario"""
        # Search no se considera acción de usuario, solo evento del sistema
        if search_term.strip():
            self.log_system_event("SEARCH_FILTER", f"Applied filter: '{search_term}'")
        else:
            self.log_system_event("SEARCH_FILTER", "Filter cleared")
        
    # ========== ACCIONES DE LOGS (INFO level) ==========
    def clear_logs(self):
        """Limpiar logs"""
        self.log_user_action("CLEAR_LOGS")
        self.log_system_event("LOG_MANAGEMENT", "Logs cleared by user")
        
    def export_logs(self, file_path=""):
        """Exportar logs"""
        if file_path:
            self.log_user_action("EXPORT_LOGS", f"To: {file_path}")
            self.log_system_event("LOG_MANAGEMENT", f"Logs exported to {file_path}")
        else:
            self.log_user_action("EXPORT_LOGS", "Export dialog opened")
        
    # ========== ACCIONES DE SISTEMA (INFO level) ==========
    def refresh_data(self):
        """Refrescar datos manualmente"""
        self.log_user_action("REFRESH_DATA")
        
        if self.server_service:
            success = self.server_service.ping_server()
            if success:
                self.log_system_event("DATA_REFRESH", "Manual refresh completed successfully")
            else:
                self.log_error("Manual refresh failed - server not responding")
        else:
            self.log_warning("Manual refresh requested but no server service available")
            
    def test_connection(self):
        """Probar conexión al servidor"""
        self.log_user_action("TEST_CONNECTION")
        
        if self.server_service:
            success = self.server_service.ping_server()
            if success:
                self.log_system_event("CONNECTION_TEST", "Server connection successful")
            else:
                self.log_error("Connection test failed - server unreachable")
        else:
            self.log_error("No server service available for connection test")
            
    # ========== EVENTOS DE UI (SYSTEM level) ==========
    def window_resized(self, new_size):
        """Ventana redimensionada"""
        self.log_system_event("UI_EVENT", f"Window resized to {new_size.width()}x{new_size.height()}")
        
    def panel_moved(self, panel_name):
        """Panel movido/redimensionado"""
        self.log_system_event("UI_EVENT", f"Panel '{panel_name}' layout changed")
        
    def button_clicked(self, button_name, context=""):
        """Botón genérico clickeado - Solo para debugging"""
        details = f"Button: {button_name}"
        if context:
            details += f" - {context}"
        self.log_system_event("UI_DEBUG", details)
        
    def menu_selected(self, menu_item):
        """Elemento de menú seleccionado"""
        self.log_system_event("UI_EVENT", f"Menu item selected: {menu_item}")
        
    # ========== EVENTOS DE ENTRADA (NO se loggean como acciones) ==========
    def text_input_changed(self, input_type, value):
        """Entrada de texto genérica - NO se loggea como acción"""
        # Solo loggear si es relevante para debugging
        if len(value) > 10:  # Solo texto largo
            self.log_system_event("INPUT_DEBUG", f"{input_type}: '{value[:20]}...'")
            
    # ========== EVENTOS DE CONEXIÓN (WARNING/ERROR levels) ==========
    def connection_lost(self):
        """Conexión perdida"""
        self.log_warning(DEFAULT_MESSAGES["connection_lost"])
        
    def connection_restored(self):
        """Conexión restaurada"""
        self.log_system_event("CONNECTION", DEFAULT_MESSAGES["connection_restored"])
        
    def server_error(self, error_message):
        """Error del servidor"""
        self.log_error(f"Server error: {error_message}")
        
    def network_timeout(self, endpoint):
        """Timeout de red"""
        self.log_error(f"Network timeout accessing {endpoint}")
        
    # ========== STARTUP/SHUTDOWN (SYSTEM level) ==========
    def app_started(self):
        """Aplicación iniciada"""
        self.log_system_event("APPLICATION", DEFAULT_MESSAGES["startup"])
        
    def app_shutdown(self):
        """Aplicación cerrándose"""
        self.log_system_event("APPLICATION", DEFAULT_MESSAGES["shutdown"])
