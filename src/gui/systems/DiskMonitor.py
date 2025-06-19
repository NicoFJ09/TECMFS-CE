from components.disk_status.CylinderWidget import DiskStatus

class DiskMonitor:
    def __init__(self, panel):
        self.panel = panel
        # Map of strings to enums
        self.status_mapping = {
            "ONLINE": DiskStatus.ONLINE,
            "REBUILDING": DiskStatus.REBUILDING,
            "BUSY": DiskStatus.BUSY,
            "FAILED": DiskStatus.FAILED
        }

    def update_from_json(self, data):
        """
        Aquí es donde los datos del servidor se registran en el DiskStatusPanel.
        """
        if hasattr(self.panel, "update_disk_status"):
            self.panel.update_disk_status(data)
