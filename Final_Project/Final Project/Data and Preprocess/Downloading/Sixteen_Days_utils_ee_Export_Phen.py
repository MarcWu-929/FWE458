# # Using the satellite images and export the data to drive in 16-day intervals
# import ee
# import time

# # Initialize Earth Engine
# ee.Authenticate()
# ee.Initialize(project='ee-mwu336')

# # Calculate EVI2
# def addevi(image):
#     evi = image.expression(
#         '2.5 * float(nir - red)*0.0001 / float(nir*0.0001 + 2.4 * red*0.0001 + 1)',
#         {
#             'red': image.select('Nadir_Reflectance_Band1'),
#             'nir': image.select('Nadir_Reflectance_Band2')
#         })
#     return image.addBands(evi.rename(['EVI2']))

# # Generate 16-day intervals
# def generate_16day_intervals(start_date, end_date):
#     start_date = ee.Date(start_date)
#     end_date = ee.Date(end_date)
#     intervals = []
    
#     current_date = start_date
#     while current_date.advance(16, 'day').millis().getInfo() <= end_date.millis().getInfo():
#         next_date = current_date.advance(16, 'day')
#         intervals.append((current_date, next_date))
#         current_date = next_date

#     return intervals

# # Drop geometry for easier export
# def drop_geometry(feature):
#     return feature.setGeometry(None)

# # Main function
# def main(Satellite, countyCol, SoyMap, Country, year, varName, reducer):
#     print(f"Starting processing for year {year} and variable {varName} with reducer {reducer}")

#     # Mask the satellite images by soybean map
#     def soybeans_map(img):
#         return img.updateMask(SoyMap.gte(0.50))

#     Satellite = Satellite.map(soybeans_map).select(varName)

#     # Generate 16-day intervals for the year
#     start_date = ee.Date(f"{year}-01-01")
#     end_date = ee.Date(f"{year}-12-31")
#     intervals = generate_16day_intervals(start_date, end_date)

#     # **Step 1: Select Only Required Columns from `countyCol`**
#     selected_columns = ['GEOID', 'NAME', 'mean']  # Modify as needed
#     countyCol = countyCol.select(selected_columns)

#     # Initialize an empty feature collection with `GEOID`
#     merged_fc = countyCol.map(lambda f: f.set('GEOID', f.get('GEOID')))

#     # Process each 16-day interval
#     for i, (interval_start, interval_end) in enumerate(intervals):
#         # print(f"Processing interval: {interval_start.format('YYYY-MM-dd').getInfo()} to {interval_end.format('YYYY-MM-dd').getInfo()}")

#         # Filter the satellite collection by the current 16-day interval
#         filteredSatellite = Satellite.filterDate(interval_start, interval_end)

#         # Reduce the collection to one image based on the reducer
#         if reducer == 'sum':
#             reducedImg = filteredSatellite.sum()
#         elif reducer == 'min':
#             reducedImg = filteredSatellite.min()
#         elif reducer == 'max':
#             reducedImg = filteredSatellite.max()
#         elif reducer == 'mean':
#             reducedImg = filteredSatellite.mean()
#         else:
#             print("Reducer is not defined")
#             return

#         # Reduce ImageCollection to FeatureCollection
#         fc = reducedImg.reduceRegions(
#             collection=countyCol,
#             reducer=ee.Reducer.mean(),
#             scale=500,
#             crs='SR-ORG:6974'
#         ).map(drop_geometry)

#         # **Step 2: Select Only `GEOID` and `mean` Columns**
#         fc = fc.select(['GEOID', 'mean'])

#         # Convert interval start date to DOY
#         doy = interval_start.difference(ee.Date(f"{year}-01-01"), 'day').int()
#         doy_column_name = doy.format()

#         # Append the mean value column to the right
#         def append_mean_value(feature):
#             matching_feature = fc.filter(ee.Filter.eq('GEOID', feature.get('GEOID'))).first()
#             return feature.set(doy_column_name, matching_feature.get('mean') if matching_feature else None)

#         merged_fc = merged_fc.map(append_mean_value)
        
#     merged_fc = merged_fc.sort('GEOID') # don't remove
    
#     # # **Step: Select Columns in the Desired Order**
#     # column_names = ['GEOID', 'NAME']  # Start with GEOID and NAME
#     # # Add DOY columns dynamically
#     # doy_column_names = sorted([col for col in merged_fc.first().propertyNames().getInfo() if col.isdigit()], key=lambda x: int(x))
#     # column_names.extend(doy_column_names)
    
#     # # Select columns in sorted order
#     # merged_fc = merged_fc.select(column_names)
#     # merged_fc = merged_fc.sort('GEOID')
    
#     # # Step: Select Columns in the Desired Order
#     # column_names = ['GEOID', 'NAME']
    
#     # # Select only the numeric DOY columns dynamically, avoiding .getInfo()
#     # def extract_numeric_columns(fc):
#     #     return ee.List(fc.first().propertyNames()).filter(ee.Filter.stringContains("item", 'DOY')).sort()
    
#     # # Get DOY columns in sorted order
#     # doy_column_names = extract_numeric_columns(merged_fc)
    
#     # # Combine column lists
#     # column_names = ee.List(['GEOID', 'NAME']).cat(doy_column_names)
    
#     # # # Select columns in sorted order and sort by GEOID
#     # merged_fc = merged_fc.select(column_names).sort('GEOID')
    
#     # Print column names before exporting
#     column_names_merge = merged_fc.first().propertyNames().getInfo()
#     print("Final column names before export:", column_names_merge)
#     # column_names = ['system:index', 'GEOID', 'NAME', '0', '16', '32', '48', '64', '80', '96', '112', '128', '144', '160', '176', '192', '208', '224', '240', '256', '272', '288', '304', '320', '336']
#     # merged_fc = merged_fc.select(column_names).sort('GEOID')
#     # column_names_merge = merged_fc.first().propertyNames().getInfo()
#     # print("Final column names before export:", column_names_merge)

#     # Export the final merged FeatureCollection as a single CSV
#     sample_fc = merged_fc.limit(10)  # Export only 10 rows for testing

#     task = ee.batch.Export.table.toDrive(
#         collection=sample_fc,
#         description=f"{varName}_{reducer}_{year}",
#         folder=f"GEE_exports_{Country}_{reducer}",
#         fileFormat='CSV'
#     )
    
#     task.start()
#     print(f"CSV Export task started for {Country}_Regions_{year}")

# #############################################################################


# Using the satellite images and export the data to drive in 16-day intervals
import ee
import time

# Initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-mwu336')

# Calculate EVI2
def addevi(image):
    evi = image.expression(
        '2.5 * float(nir - red)*0.0001 / float(nir*0.0001 + 2.4 * red*0.0001 + 1)',
        {
            'red': image.select('Nadir_Reflectance_Band1'),
            'nir': image.select('Nadir_Reflectance_Band2')
        })
    return image.addBands(evi.rename(['EVI2']))

# Generate 16-day intervals
def generate_16day_intervals(start_date, end_date):
    start_date = ee.Date(start_date)
    end_date = ee.Date(end_date)
    intervals = []
    
    current_date = start_date
    while current_date.advance(16, 'day').millis().getInfo() <= end_date.millis().getInfo():
        next_date = current_date.advance(16, 'day')
        intervals.append((current_date, next_date))
        current_date = next_date

    print(f"Generated {len(intervals)} intervals for the year")
    return intervals

# Drop geometry for easier export
def drop_geometry(feature):
    return feature.setGeometry(None)

# Main function
def main(Satellite, countyCol, SoyMap, Country, year, varName, reducer):
    print(f"Starting processing for year {year} and variable {varName} with reducer {reducer}")

    # Mask the satellite images by soybean map
    def soybeans_map(img):
        return img.updateMask(SoyMap.gte(0.50))

    Satellite = Satellite.map(soybeans_map).select(varName)
    print(f"Number of images in Satellite after masking: {Satellite.size().getInfo()}")

    # Generate 16-day intervals for the year
    start_date = ee.Date(f"{year}-01-01")
    end_date = ee.Date(f"{year}-12-31")
    intervals = generate_16day_intervals(start_date, end_date)

    # Select necessary columns
    selected_columns = ['GEOID', 'NAME', 'mean']  # Modify as needed
    countyCol = countyCol.select(selected_columns)
    print("Selected columns in countyCol:", countyCol.first().propertyNames().getInfo())

    merged_fc = countyCol.map(lambda f: f.set('GEOID', f.get('GEOID')))

    for i, (interval_start, interval_end) in enumerate(intervals):
        print(f"Processing interval {i+1}: {interval_start.format('YYYY-MM-dd').getInfo()} to {interval_end.format('YYYY-MM-dd').getInfo()}")

        filteredSatellite = Satellite.filterDate(interval_start, interval_end)
        print(f"Number of images in filteredSatellite: {filteredSatellite.size().getInfo()}")

        if filteredSatellite.size().getInfo() == 0:
            print(f"Skipping interval {i+1} as no images are available.")
            continue

        if reducer == 'sum':
            reducedImg = filteredSatellite.sum()
        elif reducer == 'min':
            reducedImg = filteredSatellite.min()
        elif reducer == 'max':
            reducedImg = filteredSatellite.max()
        elif reducer == 'mean':
            reducedImg = filteredSatellite.mean()
        else:
            print("Reducer is not defined")
            return

        fc = reducedImg.reduceRegions(
            collection=countyCol,
            reducer=ee.Reducer.mean(),
            scale=500,
            crs='SR-ORG:6974'
        ).map(drop_geometry)
        print(f"Feature count in reduced FC for interval {i+1}: {fc.size().getInfo()}")

        fc = fc.select(['GEOID', 'mean'])

        doy = interval_start.difference(ee.Date(f"{year}-01-01"), 'day').int()
        doy_column_name = doy.format()
        print(f"DOY column name for interval {i+1}: {doy_column_name.getInfo()}")

        def append_mean_value(feature):
            matching_feature = fc.filter(ee.Filter.eq('GEOID', feature.get('GEOID'))).first()
            return feature.set(doy_column_name, matching_feature.get('mean') if matching_feature else None)

        merged_fc = merged_fc.map(append_mean_value)
    
    merged_fc = merged_fc.sort('GEOID')
    column_names_merge = merged_fc.first().propertyNames().getInfo()
    print("Final column names before export:", column_names_merge)
    print("Final feature count before export:", merged_fc.size().getInfo())
    
    # sample_fc = merged_fc.limit(100)  # Export only 10 rows for testing
    # print("Sample feature count before export:", sample_fc.size().getInfo())

    task = ee.batch.Export.table.toDrive(
        collection=merged_fc,
        # collection=sample_fc,
        description=f"{varName}_{reducer}_{year}",
        folder=f"GEE_exports_{Country}_{reducer}",
        fileFormat='CSV'
    )
    
    task.start()
    print(f"CSV Export task started for {Country}_Regions_{year}")
