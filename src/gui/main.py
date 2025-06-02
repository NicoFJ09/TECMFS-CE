import sys
from PyQt5.QtWidgets import QApplication
from components.main_window import MainWindow

def main():
    # Create app
    app = QApplication(sys.argv)
    
    # Show main window
    window = MainWindow()
    window.show()
    
    # Main event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()