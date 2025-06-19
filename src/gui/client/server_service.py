"""
Communication service with TECMFS-CE server
Handles domain-specific business logic
"""
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal
from .http_client import HTTPClient
from config import SERVER_CONFIG, DISK_CONFIG, DEFAULT_MESSAGES
from urllib.parse import quote

class ServerService(QObject):
    """Service that handles specific communication with TECMFS-CE"""
    
    # Signals for GUI communication
    data_received = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str, str)  # (level, message)
    
    def __init__(self, server_host=None, server_port=None):
        super().__init__()
        # Use config if no parameters specified
        host = server_host or SERVER_CONFIG["host"]
        port = server_port or SERVER_CONFIG["port"]
        timeout = SERVER_CONFIG["timeout"]
        
        self.http_client = HTTPClient(f"http://{host}:{port}", timeout)
        self.polling_active = False
        self.is_connected = False
        self.fallback_data_sent = False  # Flag to avoid fallback data spam
        
    def start_monitoring(self, interval=None):
        """Start automatic server monitoring"""
        if self.polling_active:
            return
        
        # Use config interval if not specified
        monitoring_interval = interval or SERVER_CONFIG["polling_interval"]
            
        self.polling_active = True
        thread = threading.Thread(target=self._monitor_server, args=(monitoring_interval,))
        thread.daemon = True
        thread.start()
        
        self.error_occurred.emit("SYSTEM", "Server monitoring started")
        
    def stop_monitoring(self):
        """Stop server monitoring"""
        self.polling_active = False
        self.error_occurred.emit("SYSTEM", "Server monitoring stopped")
        
    def _monitor_server(self, interval):
        """Server monitoring thread"""
        while self.polling_active:
            try:
                # Check connection
                ping_response = self.http_client.get("/ping")
                
                if ping_response:
                    if not self.is_connected:
                        self.is_connected = True
                        self.connection_status_changed.emit(True)
                        self.error_occurred.emit("SYSTEM", DEFAULT_MESSAGES["connection_restored"])
                        self.fallback_data_sent = False  # Reset flag when connected
                    
                    # Get server data
                    self._fetch_server_data()
                else:
                    if self.is_connected:
                        self.is_connected = False
                        self.connection_status_changed.emit(False)
                        self.error_occurred.emit("WARNING", DEFAULT_MESSAGES["connection_lost"])
                        
                    # Send fallback data ONLY ONCE
                    if not self.fallback_data_sent:
                        self._send_fallback_data()
                        self.fallback_data_sent = True
                        
            except Exception as e:
                self.error_occurred.emit("ERROR", f"Server monitoring error: {str(e)}")
                
            time.sleep(interval)
    
    def _fetch_server_data(self):
        """Get real server data"""
        try:
            # Get disk status from dedicated endpoint (hardcoded)
            disk_data = self.http_client.get("/disk-status")
            if disk_data and "disk_status" in disk_data:
                self.data_received.emit(disk_data["disk_status"])
            
            # Get real file data from individual endpoints
            self._fetch_individual_data()
                
        except Exception as e:
            self.error_occurred.emit("ERROR", f"Failed to fetch server data: {str(e)}")
            self._send_fallback_data()
    
    def _fetch_individual_data(self):
        """Build data from individual endpoints"""
        try:
            # Disk status from /raid-status
            raid_status = self.http_client.get("/raid-status", {"max": 10})
            if raid_status:
                disk_data = self._convert_raid_to_gui_format(raid_status)
                self.data_received.emit(disk_data)
            
            # File list from /list
            file_list = self.http_client.get("/list")
            if file_list:
                # Check if we get the new format with file info or old format with just names
                if file_list and isinstance(file_list, list):
                    if len(file_list) > 0 and isinstance(file_list[0], dict):
                        # New format: list of objects with name, size, etc.
                        files = []
                        for file_info in file_list:
                            files.append({
                                "name": file_info.get("name", "Unknown"),
                                "size": file_info.get("size", "Unknown"),
                                "blocks": file_info.get("blocks", 0),
                                "stripes": file_info.get("stripes", 0)
                            })
                    else:
                        # Old format: list of strings (just filenames)
                        files = [{"name": filename, "size": "Unknown"} for filename in file_list]
                    
                    file_data = {
                        "tag": "file_manager",
                        "files": files
                    }
                    self.data_received.emit(file_data)
                
        except Exception as e:
            self.error_occurred.emit("ERROR", f"Failed to fetch individual data: {str(e)}")
            
    def ping_server(self):
        """Manual server ping"""
        try:
            response = self.http_client.get("/ping")
            if response:
                self.error_occurred.emit("SYSTEM", f"Server ping successful: {response}")
                return True
            else:
                self.error_occurred.emit("ERROR", "Server ping failed - no response")
                return False
        except Exception as e:
            self.error_occurred.emit("ERROR", f"Ping error: {str(e)}")
            return False
    
    def _convert_raid_to_gui_format(self, raid_status):
        """Convert RAID status to GUI format using config"""
        disks = []
        for disk_id, blocks in raid_status.items():
            disk_num = int(disk_id)
            
            # Validate disk is within configured range
            if disk_num > DISK_CONFIG["disk_count"]:
                continue
                
            total_blocks = len(blocks) if isinstance(blocks, list) else 100
            ok_blocks = sum(1 for b in blocks if b == "OK") if isinstance(blocks, list) else total_blocks
            
            # Determine status based on available blocks using config
            status_types = DISK_CONFIG["status_types"]
            if ok_blocks == total_blocks:
                status = status_types[0]  # "ONLINE"
            elif ok_blocks > total_blocks * 0.8:
                status = status_types[1]  # "REBUILDING"
            elif ok_blocks > total_blocks * 0.5:
                status = status_types[2]  # "BUSY"
            else:
                status = status_types[3]  # "FAILED"
            
            # Use disk names from config
            disk_name = DISK_CONFIG["disk_names"][disk_num - 1] if disk_num <= len(DISK_CONFIG["disk_names"]) else f"Disk D{disk_num}"
            
            disks.append({
                "name": disk_name,
                "status": status,
                "activity": f"Checked {ok_blocks}/{total_blocks} blocks"
            })
        
        return {"tag": "disk_status", "disks": disks}
    
    def _send_fallback_data(self):
        """Send fallback data when no server using config - ONLY ONCE"""
        # Generate disk data using config
        fallback_disks = []
        for i, disk_name in enumerate(DISK_CONFIG["disk_names"]):
            # Simulate different states for demo
            if i == 0:
                status, activity = "ONLINE", "1 minute ago"
            elif i == 1:
                status, activity = "REBUILDING", "3 seconds ago"
            elif i == 2:
                status, activity = "BUSY", "Active now"
            else:
                status, activity = "FAILED", "System error"
                
            fallback_disks.append({
                "name": disk_name,
                "status": status,
                "activity": activity
            })
        
        fallback_disk_data = {
            "tag": "disk_status",
            "disks": fallback_disks
        }
        
        fallback_file_data = {
            "tag": "file_manager", 
            "files": [
                {"name": "system_config.ini", "size": "2 KB"},
                {"name": "boot.img", "size": "128 MB"},
                {"name": "kernel.bin", "size": "45 MB"}
            ]
        }
        
        self.data_received.emit(fallback_disk_data)
        self.data_received.emit(fallback_file_data)
        
        # Initial fallback log (only once)
        fallback_log = {
            "tag": "log",
            "logs": [
                {"level": "SYSTEM", "message": "TECMFS-CE GUI initialized with offline data"},
                {"level": "WARNING", "message": "Server not available - using demo data"}
            ]
        }
        self.data_received.emit(fallback_log)
    
    # ========== FILE OPERATIONS ==========

    def fetch_file_list(self):
        """Fetch the current file list from the server and emit it"""
        try:
            file_list = self.http_client.get("/list")
            if file_list and isinstance(file_list, list):
                # Maneja ambos formatos (nuevo y antiguo)
                if len(file_list) > 0 and isinstance(file_list[0], dict):
                    files = []
                    for file_info in file_list:
                        files.append({
                            "name": file_info.get("name", "Unknown"),
                            "size": file_info.get("size", "Unknown"),
                            "blocks": file_info.get("blocks", 0),
                            "stripes": file_info.get("stripes", 0)
                        })
                else:
                    files = [{"name": filename, "size": "Unknown"} for filename in file_list]
                file_data = {
                    "tag": "file_manager",
                    "files": files
                }
                self.data_received.emit(file_data)
        except Exception as e:
            self.error_occurred.emit("ERROR", f"Failed to fetch file list: {str(e)}")
            
    def upload_file(self, file_path, filename=None):
        """Upload a file to the server"""
        try:
            import os
            if not os.path.exists(file_path):
                self.error_occurred.emit("ERROR", f"File not found: {file_path}")
                return False
                
            # Use filename from path if not specified
            if not filename:
                filename = os.path.basename(file_path)
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload using HTTPClient
            response = self.http_client.post_binary(
                f"/upload?name={filename}", 
                file_content, 
                "application/octet-stream"
            )
            
            if response and response.get("status") == "OK":
                self.error_occurred.emit("INFO", f"File '{filename}' uploaded successfully")
                self.fetch_file_list()
                return True
            else:
                self.error_occurred.emit("ERROR", f"Upload failed: {response or 'No response'}")
                return False
                
        except Exception as e:
            self.error_occurred.emit("ERROR", f"Upload error: {str(e)}")
            return False
    
    def download_file(self, filename, save_path=None):
        """Download a file from the server"""
        try:
            import os
            
            # Use default path if not specified
            if not save_path:
                save_path = f"downloads/{filename}"
                
            # Create downloads directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else "downloads", exist_ok=True)
            
            # Download using HTTPClient
            binary_data = self.http_client.get_binary(f"/download?name={filename}")
            
            if binary_data:
                with open(save_path, 'wb') as f:
                    f.write(binary_data)
                
                self.error_occurred.emit("INFO", f"File '{filename}' downloaded to '{save_path}'")
                return True
            else:
                self.error_occurred.emit("ERROR", f"Download failed: File '{filename}' not found or server error")
                return False
                
        except Exception as e:
            self.error_occurred.emit("ERROR", f"Download error: {str(e)}")
            return False
    
    def delete_file(self, filename):
        """Delete a file from the server"""
        try:
            response = self.http_client.delete(f"/delete?name={filename}")
                    
            if response and response.get("status") == "deleted":
                self.error_occurred.emit("INFO", f"File '{filename}' deleted successfully")
                self.fetch_file_list()
                return True
            elif response and "error" in response:
                self.error_occurred.emit("ERROR", f"Delete failed: {response['error']}")
                return False
            else:
                self.error_occurred.emit("ERROR", f"Delete failed: No response from server")
                return False
                
        except Exception as e:
            self.error_occurred.emit("ERROR", f"Delete error: {str(e)}")
            return False
    
    def reboot_disk(self, disk_name):
        """Reboot a specific disk (placeholder)"""
        try:
            encoded_disk = quote(disk_name)
            response = self.http_client.post(f"/reboot?disk={encoded_disk}")

            print("DEBUG reboot response:", response)  # Para depuración

            if response and response.get("status") == "accepted":
                msg = response.get("message", "")
                self.error_occurred.emit("INFO", f"Reboot request sent for {disk_name}: {msg}")
                return True, msg
            else:
                msg = response.get("message", "") if response else "No response"
                self.error_occurred.emit("ERROR", f"Reboot failed for {disk_name}: {msg}")
                return False, msg

        except Exception as e:
            self.error_occurred.emit("ERROR", f"Reboot error for {disk_name}: {str(e)}")
            return False, str(e)