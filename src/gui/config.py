"""
Central configuration for the TECMFS-CE GUI application
"""

# Server configuration
SERVER_CONFIG = {
    "host": "localhost",
    "port": 8080,
    "timeout": 5,
    "polling_interval": 5,  # seconds
}

# GUI configuration
GUI_CONFIG = {
    "window_title": "TECMFS-CE",
    "min_width": 800,
    "min_height": 600,
    "update_interval": 100,  # ms for UI updates
}

# Logging configuration
LOG_CONFIG = {
    "max_logs": 100,
    "log_levels": ["INFO", "WARNING", "ERROR", "SYSTEM"],
    "timestamp_format": "%H:%M:%S",
    "auto_scroll": True,
    "clear_on_startup": False,
}

# Disk configuration
DISK_CONFIG = {
    "disk_count": 4,
    "disk_names": ["Disk D1", "Disk D2", "Disk D3", "Disk D4"],
    "status_types": ["ONLINE", "REBUILDING", "BUSY", "FAILED"],
    "status_colors": {
        "ONLINE": "#4CAF50",      # Green
        "REBUILDING": "#FF9800",  # Orange
        "BUSY": "#2196F3",        # Blue
        "FAILED": "#F44336"       # Red
    }
}

# Default messages
DEFAULT_MESSAGES = {
    "connection_lost": "Server connection lost - switching to offline mode",
    "connection_restored": "Server connection restored successfully",
    "startup": "TECMFS-CE GUI initialized successfully",
    "shutdown": "TECMFS-CE GUI shutting down gracefully",
}
