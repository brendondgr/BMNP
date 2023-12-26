#################################################################
# This file is just a test file to ensure accuracy of the code. #
#################################################################
from BMNP import BMNP as bmnp

import configparser

# Imports the Config Parser Object
config = configparser.ConfigParser()

# Reads config.ini
config.read('config.ini')

'''def run_refineData(startdate, enddate):
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
    #bmnp.refineNCData(startdate, enddate, min_lat, max_lat, min_lon, max_lon, raw_loc, refined_loc, False)'''

'''def run_dailyAverageView(date, del_old):
    shape_loc = f"{config['settings']['shapeFiles']}"
    graph_loc = f"{config['settings']['graphs']}"
    bmnp.DailyAverageView(date, del_old, shape_loc, graph_loc)'''
    
'''def run_MultiDailyAverageView(startdate, enddates, del_old):
    dateList = bmnp.getDates(startdate, enddates)
    shape_loc = f"{config['settings']['shapeFiles']}"
    graph_loc = f"{config['settings']['graphs']}"
    
    for date in dateList:
        bmnp.DailyAverageView(date, del_old, shape_loc, graph_loc)'''

def run_HRCSData():
    file_location = f"{config['settings']['data']}{config['settings']['refined']}{config['settings']['HRCS']}"
    shape_loc = f"{config['settings']['shapeFiles']}"
    
    play = 3
    
    if play == 1:
        variable = 'mmm'
        period = '1985-2019'
        scenario = 'observed'
    elif play == 2:
        variable = 'no-dhw-4'
        period = '2021-2040'
        scenario = 'ssp370'
    elif play == 3:
        variable = 'prob-dhw-8'
        period = '2041-2060'
        scenario = 'ssp370'
    
    bmnp.VisualizeHRCSData(file_location, variable, period, scenario, shape_loc)

if __name__ == "__main__":
    # run_refineData("20200101", "20230101")
    # run_dailyAverageView("20221001", False)
    # run_MultiDailyAverageView("20221101", "20221130", True)
    import xarray as xr
    import s3fs

    # Create an S3FileSystem object
    s3 = s3fs.S3FileSystem(anon=True)

    # Define the S3 bucket and prefix
    bucket = 'mur-sst'
    prefix = 'zarr-v1'

    # Create a mapper for the Zarr store
    store = s3fs.S3Map(root=f'{bucket}/{prefix}', s3=s3)

    # Open the dataset using xarray
    ds = xr.open_zarr(store)

    # Access the data
    print(ds)
