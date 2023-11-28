from PySide6.QtCore import QRunnable, QThreadPool, Slot, QObject, Signal
from PySide6 import QtCore

####### IMPORTS THE FUNCTIONS & CLASSES #######

###########################################################
##          GENERAL SECTION FOR WORKER CREATION          ##
###########################################################
class WorkerSignals(QObject):
    finished = Signal()
    
    def __init__(self, console):
        super().__init__()
        self.console = console
        return
    
    def add_message(self, message):
        self.console.add_message(message)
        return

class CreateWorker():
    def __init__(self, console):
        self.console = console
        return

    def createWorker(self, type, date, tabWidget):  # Add tabWidget as a parameter
        if type == "daily":
            worker = viewDailyWorker(self.console, date, tabWidget)  # Pass tabWidget to the worker
            QThreadPool.globalInstance().start(worker)
            worker.signals.finished.connect(self.console.add_message("Task Finished Successfully"))
        return


###########################################################
##            VIEW DATA SECTION FOR WORKERS              ##
###########################################################
class DailyDataWorker(QRunnable):
    def __init__(self, console, date, tabWidget):  # Add tabWidget as a parameter
        super().__init__()
        self.console = console
        self.date = date
        self.tabWidget = tabWidget  # Store tabWidget as an instance variable
        self.signals = WorkerSignals(console)
        return


    @Slot()
    def run(self):
        pass