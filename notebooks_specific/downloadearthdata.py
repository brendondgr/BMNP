import pandas as pd
import numpy as np
import netCDF4 as nc
import subprocess
import os
import datetime

min_lon = -68.447
max_lon = -68.178
min_lat = 11.996
max_lat = 12.332

dataset = 'MUR-JPL-L4-GLOB-v4.1'
directory = './data/'
new_directory = "./corrected_data/"
start_date = '2002-06-01'
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

dates = (pd.date_range(start_date, end_date, freq='D')).strftime('%Y-%m-%d').tolist()

def FixData(date):    
    # Check the directory and delete items that have ".txt" extensions
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            os.remove(f'{directory}{filename}')
    
    # Open the only other item which is an .nc file
    filename = os.listdir(directory)[0]
    file = nc.Dataset(directory + filename, 'r')
    
    # Filter the data to the area of interest.
    lons = file.variables['lon'][:]
    lats = file.variables['lat'][:]
    time = file.variables['time'][:]
    temp = file.variables['analysed_sst'][:]
    
    lon_idx = np.where((lons >= min_lon) & (lons <= max_lon))[0]
    lat_idx = np.where((lats >= min_lat) & (lats <= max_lat))[0]
    
    lons = lons[lon_idx]
    lats = lats[lat_idx]
    temp = temp[:, lat_idx, :][:, :, lon_idx]
    
    # Create a new netCDF file with the filtered data
    new_file = nc.Dataset(new_directory + date, 'w')
    
    # Create dimensions
    new_file.createDimension('lon', len(lons))
    new_file.createDimension('lat', len(lats))
    new_file.createDimension('time', None)
    
    #  Create variables
    new_lons = new_file.createVariable('lon', 'f4', ('lon',))
    new_lats = new_file.createVariable('lat', 'f4', ('lat',))
    new_time = new_file.createVariable('time', 'f4', ('time',))
    new_temp = new_file.createVariable('analysed_sst', 'f4', ('time', 'lat', 'lon'))
    
    # Add attributes
    new_lons.units = 'degrees_east'
    new_lats.units = 'degrees_north'
    new_time.units = 'days since 1981-01-01 00:00:00'
    new_temp.units = 'kelvin'
    
    # Add data
    new_lons[:] = lons
    new_lats[:] = lats
    new_time[:] = time
    new_temp[:] = temp
    
    # Close the files
    file.close()
    new_file.close()
    
    # Remove the old file
    os.remove(directory + filename)
    
    #  Save the new file

# Cycle through the dates
for date in dates:
    # First check to see if "date" is already in new directory, if so, go to next date
    if date in os.listdir(new_directory):
        # Get current time in HH:MM:SS format
        now = datetime.datetime.now()
        
        # Reformat the time to HH:MM:SS...
        now = now.strftime('%H:%M:%S')
        print(f'[{now}] The date {date} has already been downloaded and fixed.')
        continue
    
    # Create command for "date"
    command = [
        'podaac-data-downloader',
        '-c', dataset,
        '-d', directory,
        '--start-date', f'{date}T20:00:00Z',
        '--end-date', f'{date}T20:00:00Z'
    ]
    
    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Run the fix data
    FixData(date)
    
    # Get current time in HH:MM:SS format
    now = datetime.datetime.now()
    
    # Reformat the time to HH:MM:SS...
    now = now.strftime('%H:%M:%S')
    
    print(f'[{now}] The date {date} has been downloaded and fixed.')