# Lab 5 scripts
import sys
sys.path.append(r'R:\2026\Spring\GEOG562\Students\poweljer\Lab5_2025\PythonCode')

import jmp_lab5_functions as l5
import importlib
importlib.reload(l5)

#  Part 1:

#  Assign a variable to the Landsat file 

landsat_Benton = "Landsat_image_corv.tif"  


# Pass this to your new smart raster class

r = l5.SmartRaster(landsat_Benton)

# Calculate NDVI and save to and output file

okay, ndvi = r.calculate_ndvi()

# save to output file
if okay:
    r.save_ndvi(ndvi, "NDVI_Benton.tif")
    print("NDVI calculated and saved successfully.")
else:
    print(f"NDVI calculation failed: {ndvi}")


# Part 2:
# Assign a variable to the parcels data shapefile path

Benton_parcels = "Benton_County_TaxLots.shp"  # update to match your actual filename in Lab5_Data


#  Pass this to your new smart vector class

sv = l5.SmartVectorLayer(Benton_parcels)

#  Calculate zonal statistics and add to the attribute table of the parcels shapefile

sv.zonal_stats_to_field("NDVI_Benton.tif", output_field="NDVI_mean")

# Save
sv.save_as("Benton_parcels_NDVI.shp")





#  Part 3: Optional
#  Use matplotlib to make a map of your census tracts with the average NDVI values


import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 1, figsize=(10, 10))

sv.gdf.plot(
    column="NDVI_mean",        # color by NDVI value
    cmap="RdYlGn",             # red=low NDVI, green=high NDVI
    legend=True,               
    legend_kwds={"label": "Mean NDVI"},
    missing_kwds={"color": "black"},  # color parcels with no NDVI data
    vmin=-0,               # minimum scale
    vmax=1,                # max scale
    ax=ax
)

ax.set_title("Mean NDVI by Parcel - Benton County", fontsize=14)
ax.set_axis_off()

plt.tight_layout()
plt.savefig("census_NDVI_map.png", dpi=300)
plt.show()
print("Map saved to census_NDVI_map.png")