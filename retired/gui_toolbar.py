from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar
from PySide6.QtGui import QAction, QIcon 
from PySide6.QtCore import QSize

class toolbar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)

        self.exit_action = QAction(QIcon("exit.png"), "Exit", self)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.exit_app)
        self.toolbar.addAction(self.exit_action)

    def exit_app(self):
        QApplication.quit()