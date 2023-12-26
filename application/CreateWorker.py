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
    def __init__(self, console, date, save, datatype):
        self.console = console
        self.date = date
        self.save = save
        self.datatype = datatype
        self.signals = WorkerSignals(console)
        return

    def createWorker(self):  # Add tabWidget as a parameter
        print(self.datatype)
        if self.datatype == "MUR Data":
            print("MUR Data")
            worker = MURPre2020_DataWorker(self.console, self.date)  # Pass tabWidget to the worker
            
            # Execute
            worker.signals.finished.connect(self.signals.finished)
            worker.signals.finished.connect(worker.deleteLater)
            worker.signals.finished.connect(self.deleteLater)
            worker.signals.add_message.connect(worker.signals.add_message)
            QThreadPool.globalInstance().start(worker)
        return


###########################################################
##            VIEW DATA SECTION FOR WORKERS              ##
###########################################################
class MURPre2020_DataWorker(QRunnable):
    def __init__(self, console, date, save, datatype):
        super().__init__()
        self.console = console
        self.date = date
        self.save = save
        self.datatype = datatype
        self.signals = WorkerSignals(console)
        return

    @Slot()
    def run(self):
        from BMNP import BMNP
        self.signals.add_message("Running Daily Data Worker")
        BMNP.viewMUR2020(self.date, self.save, self.console, self.signals)
        self.signals.finished.emit()
        return