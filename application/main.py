import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QSplitter
from PySide6.QtCore import Qt
from guiwidgets import ConsoleWidget, TabWidget, FileMenu, ToolBar, MatplotlibWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        ##########################################################
        ##                   Application Setup                  ##
        ##########################################################
        # Window Sizes
        self.setWindowTitle("Lenfest Project Application")
        
        # Create an instace of BMNP
        from BMNP import BMNP
        self.bmnp = BMNP()
        
        self.setMinimumWidth(900)
        
        # Adds menu to Main Window
        self.console_widget = ConsoleWidget(self.bmnp)
        self.console_widget.setMinimumWidth(450)
        self.setMenuBar(FileMenu(self.console_widget)) # Console Widget is passed to File Menu
        self.setSideBar(False) # Set to True to add sidebar
        
        ##########################################################
        ##                    Loads the Body                    ##
        ##########################################################
        # Puts "TabWidget" on the left side.
        self.first_widget = TabWidget(self.console_widget, self.bmnp)
        self.first_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.first_widget.setMinimumWidth(350)
        self.second_widget = MatplotlibWidget(self.bmnp)
        self.second_widget.setMinimumHeight(450)
        self.second_widget.hide()

        # Create the top splitter and add the first two widgets
        topSplitter = QSplitter(Qt.Horizontal)
        topSplitter.addWidget(self.first_widget)
        topSplitter.addWidget(self.console_widget)

        # Create the main splitter and add the top splitter and the third widget
        mainSplitter = QSplitter(Qt.Vertical)
        mainSplitter.addWidget(topSplitter)
        mainSplitter.addWidget(self.second_widget)

        # Creates Colors for Layouts
        full_layout = QWidget()
        full_layout.setLayout(QGridLayout())
        full_layout.layout().addWidget(mainSplitter)
        self.setCentralWidget(full_layout)
        
        self.console_widget.add_message("Please allow initial actions some time to load.")
        
        self.show()
        
    def toggle_graph(self):
        if self.second_widget.isVisible():
            self.second_widget.hide()
        else:
            self.second_widget.show()    
    
    def setSideBar(self, enabled):
        if enabled:
            self.setMinimumWidth(200)
            self.setMinimumHeight(200)
        else:
            self.setMinimumWidth(550)
            self.setMinimumHeight(350)

# Adds toolbar to Main Window
app = QApplication(sys.argv)
window = MainWindow()
app.exec()
