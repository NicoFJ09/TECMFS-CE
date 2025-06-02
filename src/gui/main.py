import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import QTimer
from components.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Use native system style
    if sys.platform == "darwin":  # macOS
        app.setStyle('macintosh')
    elif sys.platform.startswith('win'):  # Windows
        app.setStyle('windowsvista')
    else:  # Linux
        app.setStyle('fusion')
    
    window = MainWindow()
    window.show()
    
    update_timer = QTimer()
    update_timer.timeout.connect(window.update)
    update_timer.start(100)
    
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()