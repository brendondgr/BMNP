from PySide6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QTextEdit
from PySide6.QtCore import QDateTime

############################################################################
##   This widget will be used to display what is occuring in the program  ##
##     to a makeshift console that will contain timestamps and other      ##
##           information of what is occuring in the program.              ##
############################################################################
class ConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.text_edit)

    def add_message(self, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] {message}"
        self.text_edit.append(formatted_message)