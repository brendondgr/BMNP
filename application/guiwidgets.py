import configparser
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QTextEdit, QComboBox, QTabWidget, QGridLayout, QCheckBox, QPushButton, QLineEdit, QRadioButton, QLabel, QApplication, QMenu, QMenuBar
from PySide6.QtCore import QDateTime, Qt, Signal
from PySide6.QtGui import QAction


#####################################################################################################################
###                                              MATPLOTLIB WIDGET                                                ###
#####################################################################################################################
class MatplotlibWidget(QWidget):
    def __init__(self, bmnp, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        bmnp.NewGraph.connect(self.update_graph)
        #self.setMinimumHeight(400)
        
    def update_graph(self, new_fig):
        # Clear the layout and remove the current canvas
        for i in reversed(range(self.layout.count())): 
            widgetToRemove = self.layout.itemAt(i).widget()
            self.layout.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)
        
        # Update the figure and canvas with the new figure
        self.figure = new_fig
        self.canvas = FigureCanvas(self.figure)
        
        # Add the new canvas to the layout
        self.layout.addWidget(self.canvas)
        
        # Redraw the canvas
        self.canvas.draw()
        
        # Show the widget
        self.show()


#####################################################################################################################
###                                                CONSOLE WIDGET                                                 ###
#####################################################################################################################
class ConsoleWidget(QWidget):
    def __init__(self, bmnp):
        super().__init__()
        self.init_ui()
        self.bmnp = bmnp

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
class TabWidget(QTabWidget):
    GraphCreated = Signal(str)
    
    def __init__(self, console_widget, bmnp):
        super().__init__()
        self.number = 0
        self.console_widget = console_widget
        self.bmnp = bmnp
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
        from BMNP_Logic import checkDates
        
        # Checks to see if the Daily Data Radio Button is selected
        if self.viewDataTab.layout().itemAtPosition(0, 0).widget().isChecked():
            if checkDates().checkSingleDate(self.viewDataTab.layout().itemAtPosition(2, 1).widget().text(),
                                            self.console_widget, location_source=self.viewDataTab.layout().itemAtPosition(1, 1).widget().currentText()):
                
                # Retrieves the date from the Text Boxes
                date = str(self.viewDataTab.layout().itemAtPosition(2, 1).widget().text())
                updatedate = f'{date[0:4]}-{date[4:6]}-{date[6:8]}'
                saveGraphs = self.viewDataTab.layout().itemAtPosition(3, 1).widget().isChecked()
                datatype = self.viewDataTab.layout().itemAtPosition(1, 1).widget().currentText()
                colorbar = self.viewDataTab.layout().itemAtPosition(3, 2).widget().isChecked()
                
                # Sends message
                self.console_widget.add_message(f"Creating graph for {updatedate}, please wait...")
                
                if datatype == "MUR Data":
                    self.bmnp.viewMUR2020(updatedate, saveGraphs, colorbar, self.console_widget, self.bmnp)
                
            else:
                self.console_widget.add_message("Date is not valid")
                
        elif self.viewDataTab.layout().itemAtPosition(4, 0).widget().isChecked():
            #self.console_widget.add_message("HRCS Data")
            pass
            
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
        DailyData_Label05 = QLabel("SST Source:")
        DailyData_Label05.setAlignment(Qt.AlignRight)
        DailyData_Label05.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)  # Set the size policy
        DailyData_Label05.setVisible(False)
        DailyData_Dropdown1 = QComboBox()
        sst_location = f"{self.config['settings']['schemas']}/sst_source.json"
        with open(sst_location) as json_file:
            sst_details = json.load(json_file)
            for source in sst_details['sources']:
                DailyData_Dropdown1.addItem(source)
        DailyData_Dropdown1.setVisible(False)
        DailyData_Label1 = QLabel("Date:")
        DailyData_Label1.setVisible(False)
        DailyData_Label1.setAlignment(Qt.AlignRight)
        DailyData_Label1.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)  # Set the size policy
        DailyData_TextBox1 = QLineEdit()
        DailyData_TextBox1.setPlaceholderText("YYYYMMDD")
        DailyData_TextBox1.setVisible(False)
        DailyData_Check1 = QCheckBox("Save Graph")
        DailyData_Check1.setVisible(False)
        DailyData_Check2 = QCheckBox("Stationary Colorbar")
        DailyData_Check2.setVisible(False)

        # Sets Positions for Daily Data #
        layout.addWidget(RadioDailyData, viewDataRow, 0)
        viewDataRow += 1
        layout.addWidget(DailyData_Label05, viewDataRow, 0)
        layout.addWidget(DailyData_Dropdown1, viewDataRow, 1, 1, 2)
        viewDataRow += 1
        layout.addWidget(DailyData_Label1, viewDataRow, 0)
        layout.addWidget(DailyData_TextBox1, viewDataRow, 1, 1, 2)
        viewDataRow += 1
        layout.addWidget(DailyData_Check1, viewDataRow, 1)
        layout.addWidget(DailyData_Check2, viewDataRow, 2)
        viewDataRow += 1

        # Add pixel gap on the left side
        layout.setColumnStretch(0, 1)
        
        RadioDailyData.toggled.connect(lambda: self.TV_DailyData(DailyData_Label1, DailyData_TextBox1,
                                                                 DailyData_Check1, DailyData_Label05,
                                                                 DailyData_Dropdown1, DailyData_Check2))
        
        
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
        # -            SUBMIT BUTTON           - #
        # -------------------------------------- #
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.ButtonClicked)
        layout.addWidget(submit_button, viewDataRow, 0, 1, 3)
        viewDataRow += 1
        
        # Set Alignment to Top
        layout.setAlignment(Qt.AlignTop)
            
        return layout
    
    ## // --------- // View Daily Data // --------- // ##
    def TV_DailyData(self, label1, text1, check1, label05, dropdown1, check2):
        label1.setVisible(not label1.isVisible())
        text1.setVisible(not text1.isVisible())
        check1.setVisible(not check1.isVisible())
        label05.setVisible(not label05.isVisible())
        dropdown1.setVisible(not dropdown1.isVisible())
        check2.setVisible(not check2.isVisible())
        
    
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