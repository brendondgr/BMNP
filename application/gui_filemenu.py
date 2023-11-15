from PySide6.QtWidgets import QApplication, QMenu, QMenuBar
from PySide6.QtGui import QAction

class fileMenu(QMenuBar):
    def __init__(self, console_widget):
        super().__init__()

        # Create the "File" menu
        file_menu = QMenu("&File", self)
        self.addMenu(file_menu)
        
        # Create and "Edit" menu
        edit_menu = QMenu("&Edit", self)
        self.addMenu(edit_menu)

        # Create the "Exit" action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(lambda: QApplication.quit())

        # Add the "Exit" action to the "File" menu
        file_menu.addAction(exit_action)
        
        # Creates a "Preferences" action
        preferences_action = QAction("Change Default Values", self)
        preferences_action.setShortcut("Ctrl+D")
        preferences_action.triggered.connect(lambda: console_widget.add_message("Preferences Tab Opened"))
        edit_menu.addAction(preferences_action)
        
        # Shows the menu bar
        self.show()
    
    def menuSize(self):
        pass