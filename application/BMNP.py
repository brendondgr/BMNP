import os
import configparser

from PySide6.QtCore import Signal, QObject
from matplotlib.figure import Figure

class BMNP(QObject):
    NewGraph = Signal(Figure)

    def __init__(self, parent=None):
        super().__init__(parent)
        return
    
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
    def AWSMUR():
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
        
        data = ds.sel(lat=slice(12.0, 13.0), lon=slice(-68.0, -67.0))
        
    @staticmethod
    def viewMUR2020(date, save, colorbar, console, bmnp, signals = None):
        # Importing Plotting Libraries
        import matplotlib.pyplot as plt
        import geopandas as gpd
        import xarray as xr
        import numpy as np
        from configparser import ConfigParser
        
        # Sets up the config parser
        config = ConfigParser()
        config.read('config.ini')
        
        # Reads in location for MUR
        data_location = f"{config['settings']['MUR_pre2020']}"
        
        # Push signal to say data was loaded in.
        # signals.add_message(f'Loading {data_location}...')

        # Loads the data
        nc = xr.open_dataset(f'{data_location}')

        # Slices to show only data from 2010-05-05
        nc = nc.sel(time=date)

        # Create plot with multiple subplots
        fig, ax = plt.subplots(1,1, figsize=(15,10))

        # Loads Shape File
        shape = gpd.read_file('./shapeFiles/BON_Coastline.shp')

        # Sets Label Ranges
        x_range = np.arange(-68.48, -68.17, 0.01).round(2)
        y_range = np.arange(12.0, 12.35, 0.01).round(2)[::-1]

        # Sets Limits
        ax.set_xlim(x_range.min(), x_range.max())
        ax.set_ylim(y_range.min(), y_range.max())

        # Sets the Title
        ax.set_title(f'MUR SST for: {date}')

        # Sets Axis
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # Plots the Shape File
        shape.plot(ax=ax, color='lime', edgecolor='black', zorder=3)

        # Generate the heatmap
        

        # Add colorbar
        if colorbar:
            img = plt.imshow(nc.analysed_sst[0,:,:]-273.14, extent=[x_range.min(), x_range.max(), y_range.min(), y_range.max()], 
                alpha=1, zorder=2, cmap='jet', vmin=25, vmax=35)
            
            cbar = plt.colorbar(img)
            cbar.set_label('Temperature (C)')
        else:
            plt.imshow(nc.analysed_sst[0,:,:]-273.14, extent=[x_range.min(), x_range.max(), y_range.min(), y_range.max()], 
                alpha=1, zorder=2, cmap='jet')
            
            cbar = plt.colorbar()
            cbar.set_label('Temperature (C)')
        
        # Saves the graph if specified
        if save:
            colorbar = '_ColorBarAdjusted' if colorbar else ''
            name = f'MUR_{date}{colorbar}'
            download_loc = f"{config['settings']['graphs']}/MUR-Daily/{name}.png"
            
            # First checks to see if the file exists in the refinedMUR folder, then checks to see if it exists in the rawMUR folder.
            if BMNP.fileExists(download_loc):
                console.add_message(f'Error: {name} already exists. It was not saved.')
            else:
                BMNP.createFolders(download_loc)
                plt.savefig(download_loc)
                console.add_message(f'{name} was saved.')
                
        # Push signal of the plot
        bmnp.NewGraph.emit(fig)

    @staticmethod
    def sortDFCol(df):
        # Imports required Libraries
        import pandas as pd
        
        ## Passed in df is only a single column
        # Removes duplicates from column
        df = df.drop_duplicates()
        
        # Orders the items in column in ascending order
        df = df.sort_values(ascending=True)
        
        # Returns the sorted column
        return df

    @staticmethod
    def addValues(datalat, datalon, datacol, lat, lon, data):
        pass

    @staticmethod
    def HRCS_CSV2NC(file_location):
        # Imports required Libraries
        import pandas as pd
        import netCDF4 as nc
        import numpy as np
        import warnings
        
        # Ignore all warnings.
        warnings.filterwarnings("ignore")
        
        # Creates a list for each possibility
        variables = ['no_dhw_days_4', 'no_dhw_days_8', 'prob_dhw_4', 'prob_dhw_8', 'mmm', 'int_sst_var', 'seas_sst_var', 'trend_ann_sst']
        scenarios = ['ssp126', 'ssp245', 'ssp370', 'ssp585']
        years = ['2021-2040', '2041-2060', '2061-2080', '2081-2100']
        
        # Where files are stored
        new_location = './data/refined/HRCS_nc/'
        
        # Checks to see that the file_location exists
        BMNP.createFolders(new_location)
        
        # Iterates through new_location, creates a list of files
        deletefiles = True
        if deletefiles:
            files = os.listdir(new_location)
            for file in files:
                os.remove(f'{new_location}/{file}')
                
        
        # Creates a list of files located in file_location
        files = os.listdir(file_location)
        
        # Iterates through each file in the list
        for file in files:
            # Read in the file to a dataframe
            df = pd.read_csv(f"{file_location}/{file}")
            
            # Check to see if contains 1985-2019
            if '1985-2019' in file:
                period = '1985-2019'
                scenario = 'observed'
                
                # Retrieve latitude and longitude
                latitude = df['latitude']
                longitude = df['longitude']
                
                del df['latitude']
                del df['longitude']
                del df['time_period']
                del df['region_name']
                del df['p_value']     
                
                for column in df.columns:
                    # Extract variable name    
                    variable = str(column).replace('_', '-')
                    
                    # Checks to see if exists, if it does, continues
                    if BMNP.fileExists(f'{new_location}/{period}_{variable}_{scenario}.nc'): continue
                    
                    # Extract data from the column.
                    prev_data = df[column]
                    
                    # Sorts lat and lon
                    lat = (BMNP.sortDFCol(latitude))[::-1]
                    lon = BMNP.sortDFCol(longitude)
                    
                    # Create a 2D array of np.nan, in size of lon vs lat
                    new_data = np.full((len(lat), len(lon)), np.nan)
                    
                    # Convert data to a dataframe
                    data = pd.DataFrame(new_data, index=lat, columns=lon)
                    #print(data)
                    
                    # Cycle through values found in prev_data
                    # Look at the respective rows in lat and lon
                    # Find the respective column / row in data
                    # Add this value to this location
                    for i in range(0, len(prev_data)):
                        # Extract the lat and lon from the dataframe
                        lati = latitude[i]
                        long = longitude[i]
                        
                        # Extract the data from the dataframe
                        data_value = prev_data[i]
                        
                        # Add the data to the correct location
                        data[long][lati] = data_value
                        '''if lat in data.index and lon in data.columns:
                            data[lon][lat] = data_value'''                    
                            
                    # Create the netCDF file for new_data
                    BMNP.createFolders(f'{new_location}/{period}_{variable}_{scenario}.nc')
                    
                    # Create the netCDF file
                    nc_file = nc.Dataset(f'{new_location}/{period}_{variable}_{scenario}.nc', "w", format="NETCDF4")
                    
                    # Create the dimensions for the new netCDF file
                    nc_file.createDimension("lat", len(lat))
                    nc_file.createDimension("lon", len(lon))
                    
                    # Create the variables for the new netCDF file
                    lat_nc = nc_file.createVariable("lat", "f4", ("lat",))
                    lon_nc = nc_file.createVariable("lon", "f4", ("lon",))
                    variable_nc = nc_file.createVariable("variable", "f4", ("lat", "lon",))
                    
                    # Add the attributes to the new netCDF file
                    nc_file.description = "Subsetted HRCS Data"
                    nc_file.source = "Subsetted from " + file
                    lat_nc.units = "degrees_north"
                    lon_nc.units = "degrees_east"
                    
                    # Add the data to the new netCDF file
                    lat_nc[:] = lat
                    lon_nc[:] = lon
                    variable_nc[:] = new_data
                    
                    # Close the netCDF file
                    nc_file.close()
                    
            elif '2021-2100' in file:
                # Extract names
                period, variable, scenario = str(file).split('_')
                #variable = variable.replace('-', '_')
                scenario = scenario.replace('.csv', '')
                
                # Checks to see if 'dhw' is in variable name
                if 'dhw' in variable:
                    # Change variable to the 'ensemble_mean_{variable}' while also removing '_days' from the variable name
                    variablelabel = f'ensemble_mean_{variable.replace("-", "_")}'
                    variablelabel = variablelabel.replace('_days', '')
                    
                    df = pd.read_csv(f"{file_location}/{file}")
                    
                    for time in years:
                        # Create new dataframe, filtering by the specified 'time' in 'time_period' column.
                        df2 = df[df['time_period'] == time]
                        
                        # Extract the latitude and longitude from the dataframe
                        latitude = df2['latitude']
                        longitude = df2['longitude']
                        
                        # Sorts lat and lon
                        lat = (BMNP.sortDFCol(latitude))[::-1]
                        lon = BMNP.sortDFCol(longitude)
                        
                        # Convert latitude and longitude to a list
                        latitude = latitude.tolist()
                        longitude = longitude.tolist()
                        
                        # Extracts Variable Data from the dataframe
                        prev_data = df2[f'{variablelabel}']
                        prev_data = prev_data.tolist()
                
                        # Checks to see if nc file already exists, if it does, skips to the next file.
                        if BMNP.fileExists(f'{new_location}/{time}_{variable}_{scenario}.nc'): continue
                        
                        # Create numpy array
                        new_data = np.full((len(lat), len(lon)), np.nan)
                        
                        # Convert data to a dataframe
                        data = pd.DataFrame(new_data, index=lat, columns=lon)
                        
                        # Cycle through values found in prev_data
                        # Look at the respective rows in lat and lon
                        # Find the respective column / row in data
                        # Add this value to this location
                        for i in range(0, len(prev_data)):
                            # Extract the lat and lon from the dataframe
                            lati = latitude[i]
                            long = longitude[i]
                            
                            # Extract the data from the dataframe
                            data_value = prev_data[i]
                            
                            # Add the data to the correct location
                            data[long][lati] = data_value
                            
                        # Create the netCDF file for new_data
                        BMNP.createFolders(f'{new_location}/{time}_{variable}_{scenario}.nc')
                        
                        # Create the netCDF file
                        nc_file = nc.Dataset(f'{new_location}/{time}_{variable}_{scenario}.nc', "w", format="NETCDF4")
                        
                        # Create the dimensions for the new netCDF file
                        nc_file.createDimension("lat", len(lat))
                        nc_file.createDimension("lon", len(lon))
                        
                        # Create the variables for the new netCDF file
                        lat_nc = nc_file.createVariable("lat", "f4", ("lat",))
                        lon_nc = nc_file.createVariable("lon", "f4", ("lon",))
                        variable_nc = nc_file.createVariable("variable", "f4", ("lat", "lon",))
                        
                        # Add the attributes to the new netCDF file
                        nc_file.description = "Subsetted HRCS Data"
                        nc_file.source = "Subsetted from " + file
                        lat_nc.units = "degrees_north"
                        lon_nc.units = "degrees_east"
                        
                        # Add the data to the new netCDF file
                        lat_nc[:] = lat
                        lon_nc[:] = lon
                        variable_nc[:] = new_data
                        
                        # Close the netCDF file
                        nc_file.close()
                        
                elif 'mmm' in variable:
                    period = '1985-2019'
                    variablename = variable.replace('-', '_')
                    
                    # Checks to see if nc file already exists, if it does, skips to the next file.
                    if BMNP.fileExists(f'{new_location}/{period}_{variable}_{scenario}.nc'): continue
                    
                    # Load file into dataframe
                    df = pd.read_csv(f"{file_location}/{file}")
                    
                    # Extract the latitude and longitude from the dataframe
                    latitude = df['latitude']
                    longitude = df['longitude']
                    
                    # Sorts lat and lon
                    lat = (BMNP.sortDFCol(latitude))[::-1]
                    lon = BMNP.sortDFCol(longitude)
                    
                    # Delete columns that are not needed
                    del df['latitude']
                    del df['longitude']
                    del df['region_name']
                    
                    # Take each row, find the mean of the row, create a column called "data" and add the mean to the column
                    df['data'] = df.mean(axis=1)
                    
                    # Extract the data from the dataframe
                    prev_data = df['data']
                    
                    # Create numpy array
                    new_data = np.full((len(lat), len(lon)), np.nan)
                    
                    # Convert data to a dataframe
                    data = pd.DataFrame(new_data, index=lat, columns=lon)
                    
                    # Cycle through values found in prev_data
                    # Look at the respective rows in lat and lon
                    # Find the respective column / row in data
                    # Add this value to this location
                    for i in range(0, len(prev_data)):
                        # Extract the lat and lon from the dataframe
                        lati = latitude[i]
                        long = longitude[i]
                        
                        # Extract the data from the dataframe
                        data_value = prev_data[i]
                        
                        # Add the data to the correct location
                        data[long][lati] = data_value
                        
                    # Create the netCDF file for new_data
                    BMNP.createFolders(f'{new_location}/{period}_{variable}_{scenario}.nc')
                    
                    # Create the netCDF file
                    nc_file = nc.Dataset(f'{new_location}/{period}_{variable}_{scenario}.nc', "w", format="NETCDF4")
                    
                    # Create the dimensions for the new netCDF file
                    nc_file.createDimension("lat", len(lat))
                    nc_file.createDimension("lon", len(lon))
                    
                    # Create the variables for the new netCDF file
                    lat_nc = nc_file.createVariable("lat", "f4", ("lat",))
                    lon_nc = nc_file.createVariable("lon", "f4", ("lon",))
                    variable_nc = nc_file.createVariable("variable", "f4", ("lat", "lon",))
                    
                    # Add the attributes to the new netCDF file
                    nc_file.description = "Subsetted HRCS Data"
                    nc_file.source = "Subsetted from " + file
                    lat_nc.units = "degrees_north"
                    lon_nc.units = "degrees_east"
                    
                    # Add the data to the new netCDF file
                    lat_nc[:] = lat
                    lon_nc[:] = lon
                    variable_nc[:] = new_data
                    
                    # Close the netCDF file
                    nc_file.close()
                    
    @staticmethod
    def viewHRCSData(variable, period, scenario):
        if period == '1985`-2019' or scenario == 'observed' or variable == 'mmm' or variable == 'int-sst-var' or variable == 'seas-sst-var' or variable == 'trend-ann-var':
            period = '1985-2019'
            scenario = 'observed'
        
        # Load Config Parser
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        # File location
        file_location = f"{config['settings']['data']}{config['settings']['refined']}{config['settings']['HRCSnc']}"
        file_location = f'{file_location}/{period}_{variable}_{scenario}.nc'
        
        # Checks to see if file exists
        if BMNP.fileExists(file_location):
            # Load in the file location
            import xarray as xr
            import numpy as np
            import geopandas as gpd
            import matplotlib.pyplot as plt
            
            nc = xr.open_dataset(f'{file_location}')
            
            # Create plot with multiple subplots
            fig, ax = plt.subplots(1,1, figsize=(15,10))

            # Loads Shape File
            shape = gpd.read_file('./shapeFiles/BON_Coastline.shp')

            # Sets Label Ranges
            x_range = np.arange(-68.48, -68.17, 0.01).round(2)
            y_range = np.arange(12.0, 12.35, 0.01).round(2)[::-1]
            
            # Sets Limits
            ax.set_xlim(x_range.min(), x_range.max())
            ax.set_ylim(y_range.min(), y_range.max())
            
            # Set the title
            ax.set_title(f'HRCS Data for {period}: {scenario} {variable}')
            
            # Sets Axis
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            
            # Plots the Shape File
            shape.plot(ax=ax, color='lime', edgecolor='black', zorder=3)
            
            # Add the colorbar based on multiple factors
            if 'prob' in variable:
                img = plt.imshow(nc.variable[:,:], extent=[x_range.min(), x_range.max(), y_range.min(), y_range.max()], 
                    alpha=1, zorder=2, cmap='jet', vmin=0, vmax=1)
                
                # Add in colorbar
                cbar = plt.colorbar(img)
            else:
                img = plt.imshow(nc.variable[:,:], extent=[x_range.min(), x_range.max(), y_range.min(), y_range.max()], alpha=1, zorder=2, cmap='jet')
                
                # Add in colorbar
                cbar = plt.colorbar(img)
                cbar.set_label('Probability')
            
            plt.show()
            
            #bmnp.NewGraph.emit(fig)
if __name__ == "__main__":
    # Clear Linux Console first
    os.system('clear')
    #BMNP.HRCS_CSV2NC('./data/refined/HRCS_csv2/')
    
    variable = 'prob-dhw-4'
    period = '2041-2060'
    scenario = 'ssp126'
    
    BMNP.viewHRCSData(variable, period, scenario)