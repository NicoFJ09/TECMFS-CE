class Logger:
    def __init__(self, panel):
        self.panel = panel

    def update_from_json(self, data):
        logs = data.get("logs", [])
        for log in logs:
            self.panel.add_log_message(log.get("level", "INFO"), log.get("message", ""))
