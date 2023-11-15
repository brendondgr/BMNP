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