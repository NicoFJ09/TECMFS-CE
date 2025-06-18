# disk_monitor.py
from components.disk_status.CylinderWidget import DiskStatus

class DiskMonitor:
    def __init__(self, panel):
        self.panel = panel
        # Mapeo de strings a enums
        self.status_mapping = {
            "ONLINE": DiskStatus.ONLINE,
            "REBUILDING": DiskStatus.REBUILDING,
            "BUSY": DiskStatus.BUSY,
            "FAILED": DiskStatus.FAILED
        }

    def update_from_json(self, data):
        """Aquí es donde los datos del servidor se registran en el DiskStatusPanel"""
        disks = data.get("disks", [])
        for i, disk in enumerate(disks):
            if i < len(self.panel.disks):
                # Convertir string status a enum
                status_str = disk.get("status", "FAILED")
                status_enum = self.status_mapping.get(status_str, DiskStatus.FAILED)
                
                # ← AQUÍ se actualiza el componente visual
                self.panel.update_disk_status(
                    i,
                    status_enum,
                    disk.get("used", "0%"),
                    disk.get("activity", "No activity")
                )
