import BMNP
import configparser
import json

#####################################################################################################################
###                                                CONSOLE WIDGET                                                 ###
#####################################################################################################################
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QTextEdit
from PySide6.QtCore import QDateTime

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
        
#####################################################################################################################
###                                                  TAB WIDGET                                                   ###
#####################################################################################################################
from PySide6.QtWidgets import QComboBox, QTabWidget, QWidget, QGridLayout, QVBoxLayout, QCheckBox, QPushButton, QLineEdit, QRadioButton, QLabel
from PySide6.QtCore import QRunnable, QThreadPool, Slot, QObject, Signal, Qt
from CreateWorker import CreateWorker

class TabWidget(QTabWidget):
    def __init__(self, console_widget):
        super().__init__()
        self.console_widget = console_widget
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        # Create the Widgets for the tabs
        self.viewDataTab = QWidget()
        self.downloadTab = QWidget()
        self.downloadConvertTab = QWidget()
        self.tbdTab = QWidget()
        
        # Add the tabs to the layout with names
        self.addTab(self.viewDataTab, "View Data")
        self.addTab(self.downloadTab, "Download")
        self.addTab(self.downloadConvertTab, "Convert")
        self.addTab(self.tbdTab, "TBD")
        
        # Sets the internal layout of the tabs
        self.viewDataTab.setLayout(self.viewDataLayout())
        self.downloadTab.setLayout(self.tempLayout())
        self.downloadConvertTab.setLayout(self.tempLayout())
        self.tbdTab.setLayout(self.tempLayout())
        
        # Set Tab Tooltips
        self.downloadTab.setToolTip("Download data from the server.")
        self.downloadConvertTab.setToolTip("Download and convert data from the server.")
        self.viewDataTab.setToolTip("View data from the server.")
        self.tbdTab.setToolTip("To be determined.")
        
        # Display Tabs
        self.show()
    
    #--------------------------------------------------------------------------------------------------#
    #                                            VIEW DATA                                             #
    #--------------------------------------------------------------------------------------------------#
    def ButtonClicked(self):
        # Checks to see if the Daily Data Radio Button is selected
        if self.viewDataTab.layout().itemAtPosition(0, 0).widget().isChecked():
            # Retrieves the date from the Text Boxes
            date = str(self.viewDataTab.layout().itemAtPosition(1, 1).widget().text())
            saveGraphs = self.viewDataTab.layout().itemAtPosition(2, 1).widget().isChecked()
            shape_locations = self.config['settings']['shapeFiles']
            graph_locations = self.config['settings']['graphs']
            
            # Creates a Worker
                
    def viewDataLayout(self):                          
        # Creates Layout
        layout = QGridLayout()
        viewDataRow = 0

        # -------------------------------------- #
        # -             DAILY DATA             - #
        # -------------------------------------- #
        # Category for Daily Data #
        RadioDailyData = QRadioButton("View Daily Data")
        
        # Items for Daily Data #
        DailyData_Label1 = QLabel("Date:")
        DailyData_Label1.setVisible(False)
        DailyData_Label1.setAlignment(Qt.AlignRight)
        DailyData_Label1.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)  # Set the size policy
        DailyData_TextBox1 = QLineEdit()
        DailyData_TextBox1.setPlaceholderText("YYYYMMDD")
        DailyData_TextBox1.setVisible(False)
        DailyData_Check1 = QCheckBox("Save the Graph")
        DailyData_Check1.setVisible(False)

        # Sets Positions for Daily Data #
        layout.addWidget(RadioDailyData, viewDataRow, 0)
        viewDataRow += 1
        layout.addWidget(DailyData_Label1, viewDataRow, 0)
        layout.addWidget(DailyData_TextBox1, viewDataRow, 1)
        viewDataRow += 1
        layout.addWidget(DailyData_Check1, viewDataRow, 1)
        viewDataRow += 1

        # Add pixel gap on the left side
        layout.setColumnStretch(0, 1)
        
        RadioDailyData.toggled.connect(lambda: self.TV_DailyData(DailyData_Label1, DailyData_TextBox1,
                                                                 DailyData_Check1))
        
        # -------------------------------------- #
        # -             DAILY DATA             - #
        # -              MULTIPLE              - #
        # -------------------------------------- #
        # Category for Multiple Daily Data #
        RadioMultiDailyData = QRadioButton("Multiple Daily Data")
        
        layout.addWidget(RadioMultiDailyData, viewDataRow, 0)
        viewDataRow += 1
        
        # -------------------------------------- #
        # -            LOGGER DATA             - #
        # -------------------------------------- #
        # Category for Logger Data #
        RadioLoggerData = QRadioButton("Logger Data")
        layout.addWidget(RadioLoggerData, viewDataRow, 0)
        viewDataRow += 1
        
        
        
        # -------------------------------------- #
        # -             HRCS DATA              - #
        # -------------------------------------- #
        # Category for HRCS Data #
        RadioHRCSData = QRadioButton("HRCS Data")
        
        layout.addWidget(RadioHRCSData, viewDataRow, 0)
        viewDataRow += 1
        
        # Create a drop down menu
        variable_dropdown = QComboBox()
        label_variable = QLabel("Variable:")
        variable_dropdown.setVisible(False)
        label_variable.setVisible(False)
        hrcs_location = f"{self.config['settings']['schemas']}/hrcs_details.json"
        with open(hrcs_location) as json_file:
            hrcs_details = json.load(json_file)
            for variable in hrcs_details['variable']:
                variable_dropdown.addItem(variable)
        
        # Adds to next row  
        layout.addWidget(label_variable, viewDataRow, 0)
        layout.addWidget(variable_dropdown, viewDataRow, 1)
        viewDataRow += 1
        
        # Creates a second drop down menu
        period_dropdown = QComboBox()
        label_period = QLabel("Period:")
        period_dropdown.setVisible(False)
        label_period.setVisible(False)     
        with open(hrcs_location) as json_file:
            hrcs_details = json.load(json_file)
            for period in hrcs_details['period']:
                period_dropdown.addItem(period)
        
        # Adds to next row
        layout.addWidget(label_period, viewDataRow, 0)
        layout.addWidget(period_dropdown, viewDataRow, 1)
        
        RadioHRCSData.toggled.connect(lambda: self.TV_HRCSData(variable_dropdown, label_variable,
                                                               period_dropdown, label_period))
        
        viewDataRow += 1
        
        # -------------------------------------- #
        # -            SUBMIT BUTTON           - #
        # -------------------------------------- #
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.ButtonClicked)
        layout.addWidget(submit_button, viewDataRow, 0)
        viewDataRow += 1
        
        # Set Alignment to Top
        layout.setAlignment(Qt.AlignTop)
            
        return layout
    
    ## // --------- // View Daily Data // --------- // ##
    def TV_DailyData(self, label1, text1, check1):
        label1.setVisible(not label1.isVisible())
        text1.setVisible(not text1.isVisible())
        check1.setVisible(not check1.isVisible())
    
    def TV_HRCSData(self, variable_dropdown, label_variable, period_dropdown, label_period):
        variable_dropdown.setVisible(not variable_dropdown.isVisible())
        label_variable.setVisible(not label_variable.isVisible())
        period_dropdown.setVisible(not period_dropdown.isVisible())
        label_period.setVisible(not label_period.isVisible())
        
    def ViewDailyData(self):
        pass
    
    def tempLayout(self):
        # Create a Single Centered Field that says "To Be Determined"
        layout = QVBoxLayout()
        label = QLabel("To Be Determined")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return layout


        

    
#####################################################################################################################
###                                                  File Menu                                                    ###
#####################################################################################################################
from PySide6.QtWidgets import QApplication, QMenu, QMenuBar
from PySide6.QtGui import QAction

class FileMenu(QMenuBar):
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

#####################################################################################################################
###                                                  Tool Bar                                                     ###
#####################################################################################################################
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize

class ToolBar(QMainWindow):
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