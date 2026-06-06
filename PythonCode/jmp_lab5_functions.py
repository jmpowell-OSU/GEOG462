#####################
# Block 1:  Import the packages you'll need
# 
# 

import os, sys
import rasterio
import geopandas as gpd




##################
# Block 2: 
# set the working directory to the directory where the data are

# Change this to the directory where your data are

data_dir = r"R:\2026\Spring\GEOG562\Students\poweljer\Lab5_2025\Lab5_Data"
os.chdir(data_dir)
print(os.getcwd())


##################
# Block 3: 
#   Set up a new smart raster class using rasterio  
#    that will have a method called "calculate_ndvi"

class SmartRaster:
    def __init__(self, raster_path):
        self.raster_path = raster_path
        
        # Open the raster and extract metadata on initialization
        with rasterio.open(self.raster_path) as src:
            self.crs = src.crs                  # coordinate reference system
            self.transform = src.transform      # affine transform for pixel-to-coordinate mapping
            self.width = src.width              # number of columns
            self.height = src.height            # number of rows
            self.count = src.count              # number of bands
            self.profile = src.profile          # full metadata profile for writing output files

    def calculate_ndvi(self, nir_band=4, red_band=3):
        okay = True
        try:
            with rasterio.open(self.raster_path) as src:
                nir = src.read(nir_band).astype(float)   # read NIR band as float
                red = src.read(red_band).astype(float)   # read red band as float

            # Suppress divide-by-zero warnings where NIR+red=0
            import numpy as np
            with np.errstate(divide='ignore', invalid='ignore'):
                ndvi = np.where(         # rasterio reads bands as numpy arrays directly, so the NDVI math is done in memory rather than through ArcPy raster objects
                    (nir + red) == 0,    # avoid dividing by zero
                    0,                   # assign 0 where denominator is zero
                    (nir - red) / (nir + red)   # standard NDVI formula
                )
            return okay, ndvi

        except Exception as e:
            okay = False
            return okay, e

    def save_ndvi(self, ndvi_array, output_path):
        import numpy as np
        # Build output profile from source: single band, float32
        profile = self.profile.copy()
        profile.update(count=1, dtype='float32')

        try:
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(ndvi_array.astype('float32'), 1)   # write NDVI array to band 1
            print(f"NDVI saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving NDVI: {e}")
            return False


##################
# Block 4: 
#   Set up a new smart vector class using geopandas
#    that will have a method similar to what did in lab 4
#    to calculate the zonal statistics for a raster
#    and add them as a column to the attribute table of the vector


class SmartVectorLayer:
    def __init__(self, vector_path):
        self.vector_path = vector_path

        if not os.path.exists(self.vector_path):
            raise FileNotFoundError(f"{self.vector_path} does not exist.")
        
        self.gdf = gpd.read_file(self.vector_path)   # load shapefile into a GeoDataFrame
        print(f"Loaded {len(self.gdf)} features from {self.vector_path}")

    def zonal_stats_to_field(self, raster_path, output_field="NDVI_mean"):
        from rasterstats import zonal_stats   # open-source replacement for arcpy.sa.ZonalStatisticsAsTable

        try:
            # Reproject vector to match raster CRS if needed
            with rasterio.open(raster_path) as src:
                raster_crs = src.crs

            if self.gdf.crs != raster_crs:
                print("Reprojecting vector to match raster CRS...")
                gdf_projected = self.gdf.to_crs(raster_crs)   # reproject to match raster
            else:
                gdf_projected = self.gdf

            # Calculate mean zonal stats for each feature
            stats = zonal_stats(gdf_projected,  # shapefile
                                raster_path,    # raster
                                stats="mean",   # The statistic we want back
                                nodata=-9999)   # How to treat nodata

            # Extract the mean value from each result dict and add as a new column
            self.gdf[output_field] = [s["mean"] if s["mean"] is not None else None for s in stats]
            print(f"Zonal stats added to field '{output_field}'")
            return True

        except Exception as e:
            print(f"Error calculating zonal stats: {e}")
            return False

    def save_as(self, output_path):
        self.gdf.to_file(output_path)   # save GeoDataFrame back to a shapefile
        print(f"Saved to {output_path}")




