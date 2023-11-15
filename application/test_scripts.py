#################################################################
# This file is just a test file to ensure accuracy of the code. #
#################################################################
from BMNP import BMNP as bmnp

import configparser

# Imports the Config Parser Object
config = configparser.ConfigParser()

# Reads config.ini
config.read('config.ini')

def run_refineData(startdate, enddate):
    # Loads the lat/lon data from config.ini
    min_lat = config['latlon_data']['min_lat']
    max_lat = config['latlon_data']['max_lat']
    min_lon = config['latlon_data']['min_lon']
    max_lon = config['latlon_data']['max_lon']
    
    value_from = 'HRCS'
    value_to = 'HRCS1'
    
    raw_loc = f"{config['settings']['data']}{config['settings']['raw']}{config['settings'][f'{value_from}']}"
    refined_loc = f"{config['settings']['data']}{config['settings']['refined']}{config['settings'][f'{value_to}']}"
    
    bmnp.refineCSVData(min_lat, max_lat, min_lon, max_lon, raw_loc, refined_loc, False)
    #bmnp.refineNCData(startdate, enddate, min_lat, max_lat, min_lon, max_lon, raw_loc, refined_loc, False)

def run_dailyAverageView(date, del_old):
    shape_loc = f"{config['settings']['shapeFiles']}"
    graph_loc = f"{config['settings']['graphs']}"
    bmnp.DailyAverageView(date, del_old, shape_loc, graph_loc)
    
def run_MultiDailyAverageView(startdate, enddates, del_old):
    dateList = bmnp.getDates(startdate, enddates)
    shape_loc = f"{config['settings']['shapeFiles']}"
    graph_loc = f"{config['settings']['graphs']}"
    
    for date in dateList:
        bmnp.DailyAverageView(date, del_old, shape_loc, graph_loc)

if __name__ == "__main__":
    #run_refineData("20200101", "20230101")
    run_dailyAverageView("20221001", False)
    #run_MultiDailyAverageView("20221101", "20221130", True)