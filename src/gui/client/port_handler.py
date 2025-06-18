import urllib.request
import urllib.parse
import json
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class PortHandler(QObject):
    """Simple HTTP communication handler with the server"""
    
    # Signal to send data to the GUI
    data_received = pyqtSignal(dict)
    
    def __init__(self, server_host="localhost", server_port=8080):
        super().__init__()
        self.base_url = f"http://{server_host}:{server_port}"
        self.polling_active = False
        
    def start_polling(self, interval=3):
        """Start polling the server every X seconds"""
        self.polling_active = True
        thread = threading.Thread(target=self._poll_server, args=(interval,))
        thread.daemon = True
        thread.start()
        
    def stop_polling(self):
        """Stop polling"""
        self.polling_active = False
        
    def _poll_server(self, interval):
        """Thread that polls the server"""
        while self.polling_active:
            try:
                # Try to ping the server
                response = self._make_request("/ping")
                if response:
                    # If the server responds, request data
                    self._fetch_data()
            except:
                pass  # Silently ignore errors
            time.sleep(interval)
            
    def _fetch_data(self):
        """Fetch data from the server and send it to the GUI"""
        try:
            # Try to get actual data from the server
            server_data = self._make_request("/gui-data")
            
            if server_data:
                # Send actual server data
                self.data_received.emit(server_data.get("disk_status", {}))
                self.data_received.emit(server_data.get("file_manager", {}))
                self.data_received.emit(server_data.get("logs", {}))
            else:
                # If no response, use fallback data
                self._send_fallback_data()
                
        except Exception as e:
            # On error, send error log and fallback data
            error_log = {
                "tag": "log",
                "logs": [{"level": "ERROR", "message": f"Server error: {str(e)} - Using fallback data"}]
            }
            self.data_received.emit(error_log)
            self._send_fallback_data()
            
    def _send_fallback_data(self):
        """Send hardcoded data when the server is unavailable"""
        # Simulate server response (same as your hardcoded data)
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
        
        # Send data to the GUI
        self.data_received.emit(disk_data)
        self.data_received.emit(file_data)
        self.data_received.emit(log_data)
    
    def _make_request(self, endpoint):
        """Perform a simple HTTP request to the server"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = urllib.request.urlopen(url, timeout=2)
            data = response.read().decode('utf-8')
            return json.loads(data)
        except:
            return None
            
    def send_message(self, message):
        """Send a simple message to the server"""
        try:
            # For now, just ping and log the message
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
