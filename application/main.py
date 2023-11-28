import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy
from gui_widgets import ConsoleWidget, TabWidget, FileMenu, ToolBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        ##########################################################
        ##                   Application Setup                  ##
        ##########################################################
        # Window Sizes
        self.setWindowTitle("Lenfest Project Application")
        
        # Adds menu to Main Window
        console_widget = ConsoleWidget()
        self.setMenuBar(FileMenu(console_widget)) # Console Widget is passed to File Menu
        self.setSideBar(False) # Set to True to add sidebar
        
        ##########################################################
        ##                    Loads the Body                    ##
        ##########################################################
        # Adds Large Layout to Main Window
        structured_layout = QGridLayout()
        
        # Puts "TabWidget" on the left side.
        first_widget = TabWidget(console_widget)
        first_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        first_widget.setMinimumWidth(388)
        structured_layout.addWidget(first_widget, 0, 0)
        structured_layout.addWidget(console_widget, 0, 1)
        
        # Creates Colors for Layouts
        full_layout = QWidget()
        full_layout.setLayout(structured_layout)
        self.setCentralWidget(full_layout)
        
        self.show()
        
    def setSideBar(self, enabled):
        if enabled:
            self.setMinimumWidth(200)
            self.setMinimumHeight(200)
        else:
            self.setMinimumWidth(200)
            self.setMinimumHeight(200)

# Adds toolbar to Main Window
app = QApplication(sys.argv)
window = MainWindow()
app.exec()