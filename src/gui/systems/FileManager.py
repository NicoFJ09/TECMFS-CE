# file_manager.py

class FileManager:
    def __init__(self, panel):
        self.panel = panel

    def update_from_json(self, data):
        files = data.get("files", [])
        # files: list of dicts with 'name' and 'size'
        self.panel.set_files([(f["name"], f["size"]) for f in files])
