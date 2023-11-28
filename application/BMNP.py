import os
import configparser

class BMNP:
    @staticmethod
    def getFileLocation(date):
        # Sets up the config parser
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        # Reads [settings] for rawMUR and refinedMUR
        raw_loc = f"{config['settings']['data']}{config['settings']['raw']}{config['settings']['MUR']}"
        refined_loc = f"{config['settings']['data']}{config['settings']['refined']}{config['settings']['MUR']}"
        
        # First checks to see if the file exists in the refinedMUR folder, then checks to see if it exists in the rawMUR folder.
        if BMNP.fileExists(f"{refined_loc}/{date[0:4]}/{date[4:6]}/{date}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04_subsetted.nc4"):
            return f"{refined_loc}/{date[0:4]}/{date[4:6]}/{date}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04_subsetted.nc4"
        elif BMNP.fileExists(f"{raw_loc}/{date[0:4]}/{date[4:6]}/{date}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04_subsetted.nc4"):
            return f"{raw_loc}/{date[0:4]}/{date[4:6]}/{date}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04_subsetted.nc4"
        else:
            return None
    
    @staticmethod
    def fileExists(location):
        return True if os.path.exists(location) else False
    
    @staticmethod
    def createFolders(location):
        # Splits the location into a list
        loc_split = location.split("/")
        
        # Removes entry if the specific entry contains a "."
        newlist = [i for i in loc_split if "." not in i]
        
        # Creates the folders, going down the list one by one, if they don't exist.
        combined = ""
        for i in range(0, len(newlist)):
            # Checks to see if first entry exists, if not, creates it.
            if i == 0:
                combined = newlist[i]
                if not os.path.exists(combined):
                    os.mkdir(combined)
            else:
                combined = combined + "/" + newlist[i]
                if not os.path.exists(combined):
                    os.mkdir(combined)
            
    @staticmethod
    def getDates(startdate, enddate):
        import datetime
        dates = []
        date_generated = [datetime.datetime.strptime(startdate, "%Y%m%d") + datetime.timedelta(days=x) for x in range(0, (datetime.datetime.strptime(enddate, "%Y%m%d")-datetime.datetime.strptime(startdate, "%Y%m%d")).days)]
        
        for date in date_generated:
            dates.append(date.strftime("%Y%m%d"))
        
        # Appends the last date to the list
        dates.append(enddate)
        
        return dates
    
    @staticmethod
    def refineNCData(startdate, enddate, min_lat, max_lat, min_lon, max_lon, old_loc, new_loc, delete_old):
        import netCDF4 as nc
        
        # Creates a list of dates to iterate through, format is YYYYMMDD
        dates = BMNP.getDates(startdate, enddate)
        
        for date in dates:
            # Generates the file location for this file.
            file_location = f"{old_loc}/{date[0:4]}/{date[4:6]}/{date}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04_subsetted.nc4"
            newNC_loc = f"{new_loc}/{date[0:4]}/{date[4:6]}/{date}090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04_subsetted.nc4"
            
            # Checks to see if the file exists, if it does, skips to the next file.
            if BMNP.fileExists(newNC_loc) or not BMNP.fileExists(file_location):
                continue
            
            # Loads netCDF file in this location
            nc_file = nc.Dataset(file_location)
            
            # Filters the 'lat' and 'lon variables to be within the specified range
            lat = nc_file['lat'][:]
            lon = nc_file['lon'][:]
            lat_indices = (lat >= float(min_lat)) & (lat <= float(max_lat))
            lon_indices = (lon >= float(min_lon)) & (lon <= float(max_lon))
            
            # Filters the 'sst' variable to be within the specified range, also converts to Celsius
            sst = nc_file['analysed_sst'][:, lat_indices, lon_indices] - 273.15
            
            # Creates the new netCDF file
            BMNP.createFolders(newNC_loc)
            new_nc_file = nc.Dataset(newNC_loc, "w", format="NETCDF4")
            
            # Creates the dimensions for the new netCDF file
            new_nc_file.createDimension("lat", len(lat[lat_indices]))
            new_nc_file.createDimension("lon", len(lon[lon_indices]))
            new_nc_file.createDimension("time", None)
            
            # Creates the variables for the new netCDF file
            new_lat = new_nc_file.createVariable("lat", "f4", ("lat",))
            new_lon = new_nc_file.createVariable("lon", "f4", ("lon",))
            new_sst = new_nc_file.createVariable("sst", "f4", ("time", "lat", "lon",))
            
            # Adds the attributes to the new netCDF file
            new_nc_file.description = "Subsetted MUR SST data"
            new_nc_file.source = "Subsetted from " + file_location
            new_lat.units = "degrees_north"
            new_lon.units = "degrees_east"
            new_sst.units = "Celsius"
            
            # Adds the data to the new netCDF file
            new_lat[:] = lat[lat_indices]
            new_lon[:] = lon[lon_indices]
            new_sst[:] = sst[:]
            
            # Closes the netCDF files
            nc_file.close()
            
            # Deletes the old netCDF file if specified
            if delete_old:
                os.remove(file_location)
            
            new_nc_file.close()
                     
    @staticmethod
    def refineCSVData(min_lat, max_lat, min_lon, max_lon, old_loc, new_loc, delete_old):
        # Retrieves a list of files located in old_loc
        files = os.listdir(old_loc)
        
        # Specifies possible column names for lat/lon
        lat_names = ["lat", "latitude", "Lat", "Latitude"]
        lon_names = ["lon", "longitude", "Lon", "Longitude"]
        
        # Imports Required Libaries
        import pandas as pd
        
        # Iterates through each file in the list
        for file in files:
            # Checks to see if the file is a CSV file, if not, skips to the next file.
            if BMNP.fileExists(f'{new_loc}/{file}'): continue
            
            # Loads the CSV file into a dataframe
            df = pd.read_csv(f"{old_loc}/{file}")
            
            # Initializes the lat/lon index variables
            index_lat = None
            index_lon = None
            
            # Cycles through the possible column names for lat/lon, if it finds one breaks and provides the name
            for lat_name in lat_names:
                if lat_name in df.columns:
                    index_lat = lat_name
                    break
            
            for lon_name in lon_names:
                if lon_name in df.columns:
                    index_lon = lon_name
                    break
                
            # For loop going through each row in the dataframe
            print(f'Filtering {file}...')
            for index, row in df.iterrows():
                # Checks to see if the lat/lon is within the specified range, if not, drops the row.
                if row[index_lat] < float(min_lat) or row[index_lat] > float(max_lat) or row[index_lon] < float(min_lon) or row[index_lon] > float(max_lon):
                    df.drop(index, inplace=True)
            
            # Saves files to the new location
            BMNP.createFolders(f'{new_loc}/{file}')
            
            # Saves the file to the new location
            df.to_csv(f'{new_loc}/{file}', index=False)
            
            # Deletes the old file if specified
            if delete_old:
                os.remove(f'{old_loc}/{file}')

    @staticmethod 
    def DailyAverageView(date, saveGraph, shape_loc, graph_loc):
        # Retrieves the file location for the specified date
        file_location = BMNP.getFileLocation(date)
        shape_location = f"{shape_loc}/BON_Coastline.shp"
        
        # Checks if shape_location exists
        if BMNP.fileExists(shape_location) == False:
            print(f'Error: {shape_location} does not exist.')
            return None        
        
        if file_location == None:
            print(f'Error: {date} does not exist in either Raw or Refined Capacity.')
            return None
        
        # Imports required Libraries
        import geopandas as gpd
        import seaborn as sns
        import netCDF4 as nc
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Loads in the shapefile
        
        # Loads netCDF file in this location
        print(f'Loading {file_location}...')
        nc_file = nc.Dataset(file_location)
        
        # Obtains data from the netCDF file, however, lods lat in reverse order
        lat = nc_file['lat'][:]
        lat = lat[::-1]
        lon = nc_file['lon'][:]
        sst = nc_file['sst'][:]
        
        # Obtains the bounding box for the plot
        bbox = (lon.min(), lon.max(), lat.min(), lat.max())
        
        # Remove time dimension from sst
        sst = sst[0, :, :]
        
        # Set the figure size
        fig, ax = plt.subplots(figsize=(7, 7))
        
        # Create a heatmap /w tight layout
        #im = ax.imshow(sst, extent=bbox, vmin = 25, vmax = 32, cmap='turbo', interpolating='bilinear', origin='lower', aspect='auto')
        im = ax.imshow(sst, extent=bbox, vmin = 25, vmax = 32, cmap='turbo', origin='lower', aspect='auto')
        
        # Loads the Shape Files
        shapefile = gpd.read_file(shape_location)
        shapefile.plot(ax=ax, facecolor='green', edgecolor='darkgreen', linewidth=1) 

        # Color Bar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('SST (°C)')
        
        # Set the title and show the plot
        plt.title(f"MUR Daily SST for {date[0:4]}/{date[4:6]}/{date[6:8]}"), plt.xlabel("Longitude"), plt.ylabel("Latitude")
        
        # Sets the x and y axis ticks to be every single degree in the bounding box
        ax.set_xticks(np.arange(bbox[0], bbox[1], 0.01))
        ax.set_yticks(np.arange(bbox[2], bbox[3], 0.01))
        
        # Turns on grid with opacity of 0.25
        ax.grid(alpha=0.25)
        
        # x-ticks rotated 90 degrees
        plt.xticks(rotation=90)
        
        # Saves the graph if specified
        if saveGraph:
            download_loc = f"{graph_loc}/MUR-Daily/{date}.png"
            BMNP.createFolders(download_loc)
            plt.savefig(download_loc)
        else:
            # Display the heatmap in a popup window
            plt.show()
    
    @staticmethod
    def createNC_HRCS(file_location, csv_data, variable, period, scenario):
        # Imports required Libraries
        import os
        import netCDF4 as nc
        
        # Reads in the lat/lon data from the csv file, as well as data
        lat = csv_data['latitude']
        lon = csv_data['longitude']
        if period == '1985-2019':
            data = csv_data['data']
        else:
            pass

        # Creates the new netCDF file
        new_nc_file = nc.Dataset(f'{file_location}/{period}_{variable}_{scenario}.nc', "w", format="NETCDF4")
        
        # Creates the dimensions for the new netCDF file, which are lat and lon but time is automatically created
        # Lat and lon do not expand the entire range, but rather the range of the Bonaire Region
        new_nc_file.createDimension("lat", 1)
        new_nc_file.createDimension("lon", 1)
        
        # Creates the variables for the new netCDF file
        new_lat = new_nc_file.createVariable("lat", "f4", ("lat",))
        new_lon = new_nc_file.createVariable("lon", "f4", ("lon",))
        new_var = new_nc_file.createVariable( "f4", ("time", "lat", "lon",))
    
    @staticmethod
    def VisualizeHRCSData(file_location, variable, period, scenario, shape_loc):
        # Imports required Libraries
        import pandas as pd
        import seaborn as sns
        import matplotlib.pyplot as plt
        import geopandas as gpd
        import netCDF4 as nc
        import numpy as np
        
        # Creates Basic Variables
        value = -1
        ncExists = False
        csvExists = False
        
        # Changes values if they are incorrect
        if variable == 'mmm' or variable == 'int_sst_var' or variable == 'seas_sst_var' or variable == 'trend_ann_var':
            period = '1985-2019'
            scenario = 'observed'
        elif period == '1985-2019':
            scenario = 'observed'
        
        # Checks for files based on the variable, period and scenario.
        nc_filename = f'{file_location}/{period}_{variable}_{scenario}.nc4'
            
        # Loads netCDF file in this location
        nc_file = nc.Dataset(nc_filename)
        
        # Create a graph of the data utilizing matplotlib + seaborn, plotting the data as a heatmap
        # Overlay the shapefile on top of the heatmap
        latitude = nc_file['lat'][:]
        longitude = nc_file['lon'][:]
        
        if 'dhw' in variable:
            variable = f'ensemble_mean_{variable}'
            variable = variable.replace('-', '_')
        else:
            variable = variable.replace('-', '_')
        data = nc_file[variable][:]
        
        # Repalce 0's in data with NaNs
        data[data == 0] = np.nan
        
        # Create Graph
        plt.figure(figsize=(10, 10))
        
        # Create Heatmap, using the variables
        sns.heatmap(data[:, :], vmin = 0, vmax = 1, cmap='turbo', xticklabels=longitude, yticklabels=latitude)
        
        # Loads the Shape Files
        shapefile = gpd.read_file(shape_loc)
        
        # Plots the shapefile on top of the heatmap
        shapefile.plot(ax=plt.gca(), facecolor='green', edgecolor='black', linewidth=1)
        
        # Sets the title and show the plot
        plt.title(f"HRCS {variable} for {period} {scenario}"), plt.xlabel("Longitude"), plt.ylabel("Latitude")
        
        # Shows the graph
        plt.show()
            
    @staticmethod
    def HRCS_CSV2NC(file_location):
        # Imports required Libraries
        import pandas as pd
        import netCDF4 as nc
        import numpy as np
        import warnings
        
        # Ignore all warnings.
        warnings.filterwarnings("ignore")
        
        # Creates a list for each thing
        variables = ['no_dhw_days_4', 'no_dhw_days_8', 'prob_dhw_4', 'prob_dhw_8', 'mmm', 'int_sst_var', 'seas_sst_var', 'trend_ann_sst']
        scenarios = ['ssp126', 'ssp245', 'ssp370', 'ssp585']
        
        # Where files are stored
        new_location = './data/refined/HRCS/'
        
        # Checks to see that the file_location exists
        BMNP.createFolders(new_location)
        
        # Creates a list of files located in file_location
        files = os.listdir(file_location)
        
        # Iterates through each file in the list
        for file in files:
            if 'mmm' in file:
                continue
            # or if file is "nc" folder
            elif 'nc' in file:
                continue
            
            # Two Paths:
            # 1. 1985-2019_data.csv
            # 2. 2021-2100_variable_scenario_data.csv
            
            if '1985-2019' in file:
                period = '1985-2019'
                scenario = 'observed'
                
                for variable in variables:
                    # Loads in the csv file
                    csv_data = pd.read_csv(f'{file_location}/{file}')
                    
                    # Creates list of lat/lon
                    lat = csv_data['latitude']
                    lon = csv_data['longitude']
                    
                    # Deletes repeats of lat/lon
                    lat = lat.drop_duplicates()
                    lon = lon.drop_duplicates()
                    
                    # Orders lon from smallest to biggest
                    lon = lon.sort_values()
                    
                    # Orders lat from biggest to smallest
                    lat = lat.sort_values(ascending=False)
                    
                    # Create a numpy array, width = range of lon, height = range of lat
                    # Array is filled with Nan values
                    temp_array = np.empty((len(lat)+1, len(lon)+1))
                    
                    # Adds lon to top row of array, starting at pos 1
                    temp_array[0, 1:] = lon
                    temp_array[1:, 0] = lat
                    
                    # Goes through each row in csv file and adds the data to the array
                    for index, row in csv_data.iterrows():
                        # Gets the lat/lon index
                        lat_index = np.where(lat == row['latitude'])[0][0]
                        lon_index = np.where(lon == row['longitude'])[0][0]
                        
                        # Adds the data cell to that particular position in temp_array
                        temp_array[lat_index+1, lon_index+1] = row[variable]
                        
                    # Creates the new netCDF file
                    temp_var = variable.replace('_', '-')
                    new_nc_file = nc.Dataset(f'{new_location}/{period}_{temp_var}_{scenario}.nc4', "w", format="NETCDF4")
                    
                    # Creates the dimensions for the new netCDF file, which are lat and lon but time is automatically created
                    # Lat and lon do not expand the entire range, but rather the range of the Bonaire Region
                    new_nc_file.createDimension("lat", len(lat))
                    new_nc_file.createDimension("lon", len(lon))
                    
                    # Creates the variables for the new netCDF file
                    new_lat = new_nc_file.createVariable("lat", "f4", ("lat",))
                    new_lon = new_nc_file.createVariable("lon", "f4", ("lon",))
                    new_var = new_nc_file.createVariable(variable, "f4", ("lat", "lon",))
                    
                    # Adds the attributes to the new netCDF file
                    new_nc_file.description = f"HRCS {variable} data"
                    new_nc_file.source = "Subsetted from " + file
                    new_lat.units = "degrees_north"
                    new_lon.units = "degrees_east"
                    new_var.units = "Celsius"
                    
                    # Adds the data to the new netCDF file
                    new_lat[:] = lat[0:len(lat)]
                    new_lon[:] = lon[0:len(lon)]
                    
                    # Saves temp_array to csv in current folder
                    #np.savetxt('temp_array.csv', temp_array, delimiter=',')
                    
                    # Delete the top row and left column of the array
                    temp_array = np.delete(temp_array, 0, 0)
                    temp_array = np.delete(temp_array, 0, 1)
                    
                    # Saves the data to the new netCDF file
                    new_var[:] = temp_array
                    
                    # Closes the netCDF files
                    new_nc_file.close()
                    
            else:
                name = file.split('_')
                years = ['2021-2040', '2041-2060', '2061-2080', '2081-2100']
                
                # For variable, changes "-" to "_"
                variable = name[1].replace('-', '_')
                scenario = name[2]
                
                # Removes .csv from scenario
                scenario = scenario.replace('.csv', '')
                
                # Loads file into dataframe
                csv_data = pd.read_csv(f'{file_location}/{file}')
                
                # Creates a list of lat/lon
                lat = csv_data['latitude']
                lon = csv_data['longitude']
                
                # Deletes repeats of lat/lon
                lat = lat.drop_duplicates()
                lon = lon.drop_duplicates()
                
                # Orders lon from smallest to biggest
                lon = lon.sort_values()

                # Orders lat from biggest to smallest
                lat = lat.sort_values(ascending=False)
                
                for year in years:
                    
                    # Extracts the data for a specific year, which is in the 'time_period' column.
                    data = csv_data.loc[csv_data['time_period'] == year]
                    
                    # Drop "region_name"
                    data.drop('region_name', axis=1, inplace=True)
                    
                    # Create a numpy array, width = range of lon, height = range of lat
                    # Array is filled with Nan values
                    temp_array = np.empty((len(lat)+1, len(lon)+1))
                    
                    # new variable name:
                    temp_var = variable.split('_')
                    
                    # If "days" in list, delete.
                    if 'days' in temp_var: temp_var.remove('days')
                    
                    # Recombines list into string, with - instead of _
                    temp_var = '_'.join(temp_var)
                    nowvariable = f'ensemble_mean_{temp_var}'
                    
                    # Adds lon to top row of array, starting at pos 1
                    temp_array[0, 1:] = lon
                    temp_array[1:, 0] = lat
                    
                    # Goes through each row in csv file and adds the data to the array
                    for index, row in data.iterrows():
                        # Gets the lat/lon index
                        lat_index = np.where(lat == row['latitude'])[0][0]
                        lon_index = np.where(lon == row['longitude'])[0][0]
                        
                        # Adds the data cell to that particular position in temp_array
                        temp_array[lat_index+1, lon_index+1] = row[nowvariable]
                    
                    # Creates the new netCDF file
                    newishvariable = temp_var.replace('_', '-')
                    new_nc_file = nc.Dataset(f'{new_location}/{year}_{newishvariable}_{scenario}.nc4', "w", format="NETCDF4")
                    
                    # Creates the dimensions for the new netCDF file, which are lat and lon but time is automatically created
                    # Lat and lon do not expand the entire range, but rather the range of the Bonaire Region
                    new_nc_file.createDimension("lat", len(lat))
                    new_nc_file.createDimension("lon", len(lon))
                    
                    # Creates the variables for the new netCDF file
                    new_lat = new_nc_file.createVariable("lat", "f4", ("lat",))
                    new_lon = new_nc_file.createVariable("lon", "f4", ("lon",))
                    new_var = new_nc_file.createVariable(nowvariable, "f4", ("lat", "lon",))
                    
                    # Adds the attributes to the new netCDF file
                    new_nc_file.description = f"HRCS {nowvariable} data"
                    new_nc_file.source = "Subsetted from " + file
                    new_lat.units = "degrees_north"
                    new_lon.units = "degrees_east"
                    new_var.units = "Celsius"
                    
                    # Adds the data to the new netCDF file
                    new_lat[:] = lat[0:len(lat)]
                    new_lon[:] = lon[0:len(lon)]
                    
                    # Delete the top row and left column of the array
                    temp_array = np.delete(temp_array, 0, 0)
                    temp_array = np.delete(temp_array, 0, 1)
                    
                    # Saves the data to the new netCDF file
                    new_var[:] = temp_array
                    
                    # Closes the netCDF files
                    new_nc_file.close()