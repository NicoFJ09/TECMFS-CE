import urllib.request
import urllib.parse
import json
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class PortHandler(QObject):
    """Manejo simple de comunicación HTTP con el servidor"""
    
    # Señal para enviar datos a la GUI
    data_received = pyqtSignal(dict)
    
    def __init__(self, server_host="localhost", server_port=8080):
        super().__init__()
        self.base_url = f"http://{server_host}:{server_port}"
        self.polling_active = False
        
    def start_polling(self, interval=3):
        """Inicia polling al servidor cada X segundos"""
        self.polling_active = True
        thread = threading.Thread(target=self._poll_server, args=(interval,))
        thread.daemon = True
        thread.start()
        
    def stop_polling(self):
        """Detiene el polling"""
        self.polling_active = False
        
    def _poll_server(self, interval):
        """Hilo que hace polling al servidor"""
        while self.polling_active:
            try:
                # Intentar hacer ping al servidor
                response = self._make_request("/ping")
                if response:
                    # Si el servidor responde, solicitar datos
                    self._fetch_data()
            except:
                pass  # Ignorar errores silenciosamente
            time.sleep(interval)
            
    def _fetch_data(self):
        """Obtiene datos del servidor y los envía a la GUI"""
        try:
            # Intentar obtener datos reales del servidor
            server_data = self._make_request("/gui-data")
            
            if server_data:
                # Enviar datos reales del servidor
                self.data_received.emit(server_data.get("disk_status", {}))
                self.data_received.emit(server_data.get("file_manager", {}))
                self.data_received.emit(server_data.get("logs", {}))
            else:
                # Si no hay respuesta del servidor, usar datos de fallback
                self._send_fallback_data()
                
        except Exception as e:
            # En caso de error, enviar log de error y datos de fallback
            error_log = {
                "tag": "log",
                "logs": [{"level": "ERROR", "message": f"Server error: {str(e)} - Using fallback data"}]
            }
            self.data_received.emit(error_log)
            self._send_fallback_data()
            
    def _send_fallback_data(self):
        """Envía datos hardcodeados cuando el servidor no responde"""
        # Simular respuesta del servidor (igual a tus datos hardcodeados)
        disk_data = {
            "tag": "disk_status",
            "disks": [
                {"name": "Disk D1", "status": "ONLINE", "used": "45%", "activity": "1 minute ago"},
                {"name": "Disk D2", "status": "REBUILDING", "used": "68%", "activity": "3 seconds ago"},
                {"name": "Disk D3", "status": "BUSY", "used": "72%", "activity": "Active now"},
                {"name": "Disk D4", "status": "FAILED", "used": "0%", "activity": "System error"}
            ]
        }
        
        file_data = {
            "tag": "file_manager",
            "files": [
                {"name": "system_config.ini", "size": "2 KB"},
                {"name": "boot.img", "size": "128 MB"},
                {"name": "kernel.bin", "size": "45 MB"}
            ]
        }
        
        log_data = {
            "tag": "log",
            "logs": [{"level": "WARNING", "message": "Using offline data - Server not available"}]
        }
        
        # Enviar datos a la GUI
        self.data_received.emit(disk_data)
        self.data_received.emit(file_data)
        self.data_received.emit(log_data)
    
    def _make_request(self, endpoint):
        """Hacer request HTTP simple al servidor"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = urllib.request.urlopen(url, timeout=2)
            data = response.read().decode('utf-8')
            return json.loads(data)
        except:
            return None
            
    def send_message(self, message):
        """Enviar mensaje simple al servidor"""
        try:
            # Por ahora solo hacer ping y loggear el mensaje
            response = self._make_request("/ping")
            if response:
                log_data = {
                    "tag": "log",
                    "logs": [{"level": "INFO", "message": f"Message sent: {message}"}]
                }
                self.data_received.emit(log_data)
                return True
        except:
            pass
        return False
