class MessageRouter:
    def __init__(self, disk_monitor, file_manager, logger):
        self.disk_monitor = disk_monitor
        self.file_manager = file_manager
        self.logger = logger

    def route_message(self, json_data):
        tag = json_data.get("tag")
        if tag == "disk_status":
            self.disk_monitor.update_from_json(json_data)
        elif tag == "file_manager":
            self.file_manager.update_from_json(json_data)
        elif tag == "log":
            self.logger.update_from_json(json_data)
