import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from components.main_window import MainWindow
from config import GUI_CONFIG, DEFAULT_MESSAGES

def main():
    # Create app
    app = QApplication(sys.argv)
    
    # Show main window
    window = MainWindow()
    window.show()
    
    # Log de inicio usando config - Solo console, el log interno se maneja en MainWindow
    print(f"[STARTUP] {DEFAULT_MESSAGES['startup']}")
    
    # Create update timer for responsive updates usando config
    update_timer = QTimer()
    update_timer.timeout.connect(window.update)  # Call window's update method
    update_timer.start(GUI_CONFIG["update_interval"])  # Update interval desde config
    
    # Main event loop
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print(f"[SHUTDOWN] {DEFAULT_MESSAGES['shutdown']}")
        window.close()

if __name__ == "__main__":
    main()