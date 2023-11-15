from PySide6.QtWidgets import *
from PySide6.QtCore import *

from gui_laborers import CreateWorker
from logicGates import checkDates as cd

############################################################################
##  Purpose of this code is to create a tab widget for each of the main   ##
##    Uses of this application. This will allow for the user to switch    ##
## across different uses. Main Tabs are: "Download", "Download & Convert" ##
##                        "View Data", and "TBD"                          ##
############################################################################
class tabWidget(QTabWidget):
    def __init__(self, console_widget):
        super().__init__()
        self.console_widget = console_widget
        
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
        self.viewDataTab.setLayout(self.viewDataLayout(QGridLayout()))
        self.downloadTab.setLayout(self.downloadLayout(QVBoxLayout()))
        self.downloadConvertTab.setLayout(self.downloadLayout(QVBoxLayout()))
        self.tbdTab.setLayout(self.downloadLayout(QVBoxLayout()))
        
        # Set Tab Tooltips
        self.downloadTab.setToolTip("Download data from the server.")
        self.downloadConvertTab.setToolTip("Download and convert data from the server.")
        self.viewDataTab.setToolTip("View data from the server.")
        self.tbdTab.setToolTip("To be determined.")
        
        # Display Tabs
        self.show()
         
    @Slot(str)
    def print_information(self, message):
        self.console_widget.add_message(message)
        return
    
    def downloadLayout(self, layout):
        # Layout SetupW
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)
        
        # Start Date Field
        start_date_field = QLineEdit()
        start_date_field.setPlaceholderText("Start Date (YYYYMMDD)")
        layout.addWidget(start_date_field)
        
        # End Date Field
        end_date_field = QLineEdit()
        end_date_field.setPlaceholderText("End Date (YYYYMMDD)")
        layout.addWidget(end_date_field)
        
        # Download Checkbox
        download_checkbox = QCheckBox("Download")
        layout.addWidget(download_checkbox)
        
        # Convert Checkbox (nc)
        convertnc_checkbox = QCheckBox("Convert to .nc")
        layout.addWidget(convertnc_checkbox)
        
        # Convert Checkbox (csv)
        convertcsv_checkbox = QCheckBox("Convert to .csv")
        layout.addWidget(convertcsv_checkbox)
        
        # Delete Files Checkbox
        delete_checkbox = QCheckBox("Delete Files When Done")
        layout.addWidget(delete_checkbox)
                    
        # Run Button
        run_button = QPushButton("Run")
        layout.addWidget(run_button)
        
        # Adds the functionality to the button
        run_button.clicked.connect(lambda: self.console_widget.add_message("Run Button Clicked"))

        return layout
   
    def viewDataLayout(self, layout):
        # Pushes everything to the top
        layout.setAlignment(Qt.AlignTop)
        
        ##############################
        ### RADIO 1: DAILY AVERAGE ###
        ##############################
        radio1 = QRadioButton("Daily Average")
        radio1_sub = QWidget()
        radio1_sub_layout = QGridLayout()
        radio1_sub_layout.addWidget(QLabel("Date (YYYYMMDD):"), 0, 0)
        radio1_sub_layout.addWidget(QLineEdit(), 0, 1)
        radio1_sub.setLayout(radio1_sub_layout)
        radio1_sub.hide()
        
        # Creates Sub-Sections for each radio button
        radio2 = QRadioButton("Monthly Average")
        radio2_sub = QWidget()
        
        radio3 = QRadioButton("Logger Monthly Min/Max/Mean")
        radio3_sub = QWidget()
        
        # Sets up position of these fields
        layout.addWidget(radio1, 0, 0)
        layout.addWidget(radio1_sub, 1, 0)
        layout.addWidget(radio2, 2, 0)
        layout.addWidget(radio3, 4, 0)

        # Function to show/hide the section based on the state of the radio button
        def toggle_daily(state):
            if state:
                radio1_sub.show()
            else:
                radio1_sub.hide()

        def toggle_monthly(state):
            if state:
                pass
            else:
                pass
            
        def toggle_logger(state):
            if state:
                pass
            else:
                pass
        
        # Connect the function to the radio button
        radio1.toggled.connect(toggle_daily)
        radio2.toggled.connect(toggle_monthly)
        radio3.toggled.connect(toggle_logger)

        # Adds the functionality to the button
        run_view = QPushButton("Run")
        
        # Adds the functionality to the button
        run_view.clicked.connect(lambda: self.view_checkRun())
    
        layout.addWidget(run_view, 6, 0)

        return layout
    
    def view_checkRun(self):
        # Checks to see which radio button is selected
        if self.viewDataTab.layout().itemAt(0).widget().isChecked():
            self.console_widget.add_message("Daily Average Selected")
            date = self.viewDataTab.layout().itemAt(1).widget().layout().itemAt(1).widget().text()
            if cd.checkSingleDate(date, self.console_widget):
                CreateWorker(self.console_widget).createWorker("daily", date, self)  # Pass self as the tabWidget reference
            else:
                self.console_widget.add_message("Please enter a valid date")
            
        elif self.viewDataTab.layout().itemAt(2).widget().isChecked():
            self.console_widget.add_message("Monthly Average Selected")
            
        elif self.viewDataTab.layout().itemAt(4).widget().isChecked():
            self.console_widget.add_message("Logger Monthly Min/Max/Mean Selected")
            
        else:
            self.console_widget.add_message("No Radio Button Selected")
        return