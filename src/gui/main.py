import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from components.main_window import MainWindow

def main():
    # Create app
    app = QApplication(sys.argv)
    
    # Show main window
    window = MainWindow()
    window.show()
    
    # Create update timer for responsive updates
    update_timer = QTimer()
    update_timer.timeout.connect(window.update)  # Call window's update method
    update_timer.start(100)  # Update every 100ms
    
    # Main event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()