# disk_monitor.py

class DiskMonitor:
    def __init__(self, panel):
        self.panel = panel

    def update_from_json(self, data):
        disks = data.get("disks", [])
        for i, disk in enumerate(disks):
            # status as string, used as string, activity as string
            status = getattr(self.panel.disks[i], 'status', None)
            if hasattr(self.panel.disks[i], 'set_status'):
                self.panel.disks[i].set_status(getattr(self.panel.disks[i], 'status', None))
            self.panel.update_disk_status(
                i,
                getattr(self.panel.disks[i], 'status', None),
                disk.get("used", "0%"),
                disk.get("activity", "")
            )
