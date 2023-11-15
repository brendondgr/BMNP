import datetime

class checkDates:
    def __init__(self):
        return
    
    @staticmethod
    def checkSingleDate(date, console):
        # Checks if date is numerical
        if not date.isnumeric():
            console.add_message("Date must be numerical")
            return False
        
        # Checks if date is 8 digits long
        if len(date) != 8:
            console.add_message("Date must be 8 digits long")
            return False
        
        # Checks to see date is not in future.
        if datetime.datetime.strptime(date, "%Y%m%d") > datetime.datetime.now():
            console.add_message("Date cannot be in the future")
            return False
        
        return True