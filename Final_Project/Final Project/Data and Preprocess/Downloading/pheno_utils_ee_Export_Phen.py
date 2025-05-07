# # # using the phenology dataset to mask the satellite images and export the data to drive
# import ee
# import time

# #calculate evi2
# def addevi(image):
#     evi = image.expression(
#         '2.5 * float(nir - red)*0.0001 / float(nir*0.0001 + 2.4 * red*0.0001 + 1)',
#         {
#             'red': image.select('Nadir_Reflectance_Band1'),    # 620-670nm, RED
#             'nir': image.select('Nadir_Reflectance_Band2'),    # 841-876nm, NIR
#             #blue: image.select('Nadir_Reflectance_Band3')    # 459-479nm, BLUE
#         });
#     return image.addBands(evi.rename(['EVI2']))

# #masking images by the phenology stages
# def GetPeriodCol(TimeSeries, phen_dataset):
#     # TimeSeries is the complete time series
#     # phen_dataset is a two-band image, band 1 is the start of the phenological period, band 2 is the end

#     ClassDate = ee.Date('1970-1-01')

#     def filterPeriod(CurrentImage):
#         # Extract the date from the current image
#         Date = ee.Date(CurrentImage.get('system:time_start'))
        
#         # Calculate the difference in days between the current date and the reference date
#         Date_Differ = Date.difference(ClassDate, 'day')
        
#         # Calculate the difference between the current date difference and the start and end of the phenological period
#         T1 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([0])).toFloat()
#         T2 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([1])).toFloat()

#         # Create a mask where the current date falls within the phenological period
#         PeriodTag = T1.multiply(T2).lte(0)

#         # Apply the mask to the current image and return the masked image
#         # return CurrentImage.updateMask(PeriodTag).selfMask().set('system:time_start', Date)
#         return CurrentImage.updateMask(PeriodTag).set('system:time_start', Date)

#     # Map the filter function over the time series and return the result
#     return TimeSeries.map(filterPeriod)

# # export to drive

# def export_to_drive(collection, description, folder, year, phen_start, phen_end, varName):
#     task = ee.batch.Export.table.toDrive(
#         collection=collection,
#         description=description+'_'+year+'_'+phen_start+'_'+phen_end+'_'+varName,
#         folder=folder,
#         fileFormat='GeoJSON'
#     )

#     task.start()
# #original code
# def main(Satellite, countyCol, SoyMap, Country, year, varName, reducer):

#     #map the variable
#     def soybeans_map(img):
#         return img.updateMask(SoyMap.gte(0.50))

#     Satellite = Satellite.map(soybeans_map).select(varName)

#     #select the phenology dataset
#     phen_list=['Greenup_1','MidGreenup_1','Maturity_1','Peak_1','Senescence_1','MidGreendown_1','Dormancy_1']
#     for i in range(len(phen_list)-1):
#         phen_start=phen_list[i]
#         phen_end=phen_list[i+1]

#         phen_dataset= ee.ImageCollection('MODIS/061/MCD12Q2')\
#                         .filter(ee.Filter.date(year+'-1-1',year+'-12-31')).select([phen_start,phen_end]).first()

#         #masking by the phenology stages

#         filteredSatellite = GetPeriodCol(Satellite,phen_dataset)
#         # filteredSatellite = Satellite

#         # mean reduce collection to one image
#         ## added min and max
#         if reducer=='sum':
#             reducedImg = filteredSatellite.sum()
#         if reducer=='min':
#             reducedImg = filteredSatellite.min()
#         if reducer=='max':
#             reducedImg = filteredSatellite.max()
#         if reducer=='mean':
#             reducedImg = filteredSatellite.mean()
#         else:
#             print("reducer is not defined")

#         # Convert ImageCollection to FeatureCollection
#         fc = reducedImg.reduceRegions(
#                 collection=countyCol,
#                 reducer=ee.Reducer.percentile([99, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1]),
#                 scale=500,
#                 crs='SR-ORG:6974'
#             )

#         def drop_geometry(feature):
#             return feature.setGeometry(None)

#         fc = fc.map(drop_geometry)

#         while True:
#             try:
#                 # Export the data
#                 export_to_drive(
#                     collection=fc,
#                     description=Country+'_Regions',
#                     folder='GEE_exports_'+Country+"_"+reducer,
#                     year=year,
#                     phen_start=phen_start,
#                     phen_end=phen_end,
#                     varName=varName)
#             except:
#                 print('Error, waiting 60 seconds to try again...')
#                 time.sleep(60)
#                 continue
#             break

#################################################################################################
# one csv

# # Using the phenology dataset to mask the satellite images and export the data to drive
# import ee
# import time

# # Calculate EVI2
# def addevi(image):
#     evi = image.expression(
#         '2.5 * float(nir - red)*0.0001 / float(nir*0.0001 + 2.4 * red*0.0001 + 1)',
#         {
#             'red': image.select('Nadir_Reflectance_Band1'),  # 620-670nm, RED
#             'nir': image.select('Nadir_Reflectance_Band2'),  # 841-876nm, NIR
#         })
#     return image.addBands(evi.rename(['EVI2']))

# # Masking images by the phenology stages
# def GetPeriodCol(TimeSeries, phen_dataset):
#     ClassDate = ee.Date('1970-1-01')

#     def filterPeriod(CurrentImage):
#         Date = ee.Date(CurrentImage.get('system:time_start'))
#         Date_Differ = Date.difference(ClassDate, 'day')

#         T1 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([0])).toFloat()
#         T2 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([1])).toFloat()

#         PeriodTag = T1.multiply(T2).lte(0)

#         return CurrentImage.updateMask(PeriodTag).set('system:time_start', Date)

#     return TimeSeries.map(filterPeriod)

# # Export to Drive (Modified to CSV)
# ###
# # Export to Drive (Modified to CSV)
# def export_to_drive(collection, description, folder, year, phen_start, phen_end, varName, reducer):
#     # Columns to keep
#     selected_columns = ['GEOID', 'NAME', 'p99', 'p90', 'p80', 'p70', 'p60', 'p50', 'p40', 'p30', 'p20', 'p10', 'p1']
    
#     # Print selected columns before exporting
#     first_feature = collection.first()
#     properties = first_feature.propertyNames().getInfo()
#     print(f"Exporting columns: {selected_columns}")

#     # Filter out unneeded columns
#     collection = collection.map(lambda feature: feature.select(selected_columns))

#     # # Rename columns using .set() for each feature
#     # def rename_columns(feature):
#     #     renaming_dict = {
#     #         'GEOID': f"GEOID",
#     #         'NAME': f"NAME",
#     #         'p99': f"{phen_start}_{varName}_{reducer}_p99",
#     #         'p90': f"{phen_start}_{varName}_{reducer}_p90",
#     #         'p80': f"{phen_start}_{varName}_{reducer}_p80",
#     #         'p70': f"{phen_start}_{varName}_{reducer}_p70",
#     #         'p60': f"{phen_start}_{varName}_{reducer}_p60",
#     #         'p50': f"{phen_start}_{varName}_{reducer}_p50",
#     #         'p40': f"{phen_start}_{varName}_{reducer}_p40",
#     #         'p30': f"{phen_start}_{varName}_{reducer}_p30",
#     #         'p20': f"{phen_start}_{varName}_{reducer}_p20",
#     #         'p10': f"{phen_start}_{varName}_{reducer}_p10",
#     #         'p1': f"{phen_start}_{varName}_{reducer}_p1",
#     #     }
        
#     #     # Apply renaming to each property
#     #     for old_name, new_name in renaming_dict.items():
#     #         feature = feature.set(new_name, feature.get(old_name))
        
#     #     # Remove the old properties
#     #     feature = feature.select([new_name for old_name, new_name in renaming_dict.items()])
        
#         # return feature

#     collection = collection.map(rename_columns)
    
#     print(f"Starting export: {varName}_{reducer}_{phen_start}_{phen_end}_{year}...")
#     task = ee.batch.Export.table.toDrive(
#         collection=collection,
#         description=f"{varName}_{reducer}_{phen_start}_{phen_end}_{year}",
#         folder=folder,
#         fileFormat='CSV'  # Changed from GeoJSON to CSV
#     )
#     task.start()
#     print("Export task started.")
# ###

# # def export_to_drive(collection, description, folder, year, phen_start, phen_end, varName):
# #     task = ee.batch.Export.table.toDrive(
# #         collection=collection,
# #         description=f"{description}_{year}_{phen_start}_{phen_end}_{varName}",
# #         folder=folder,
# #         fileFormat='CSV'  # Changed from GeoJSON to CSV
# #     )
# #     task.start()

# # Main function
# def main(Satellite, countyCol, SoyMap, Country, year, varName, reducer):
    
#     # Sort countyCol by GEOID at the beginning
#     countyCol = countyCol.sort('GEOID')

#     # Mask the variable
#     def soybeans_map(img):
#         return img.updateMask(SoyMap.gte(0.50))

#     Satellite = Satellite.map(soybeans_map).select(varName)

#     phen_list = ['Greenup_1', 'MidGreenup_1', 'Maturity_1', 'Peak_1', 'Senescence_1', 'MidGreendown_1', 'Dormancy_1']
#     for i in range(len(phen_list) - 1):
#         phen_start = phen_list[i]
#         phen_end = phen_list[i + 1]

#         phen_dataset = ee.ImageCollection('MODIS/061/MCD12Q2') \
#             .filter(ee.Filter.date(year + '-1-1', year + '-12-31')).select([phen_start, phen_end]).first()

#         filteredSatellite = GetPeriodCol(Satellite, phen_dataset)

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
#             continue

#         fc = reducedImg.reduceRegions(
#             collection=countyCol,  # Already sorted by GEOID
#             reducer=ee.Reducer.percentile([99, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1]),
#             scale=500,
#             crs='SR-ORG:6974'
#         )

#         def drop_geometry(feature):
#             return feature.setGeometry(None)

#         fc = fc.map(drop_geometry)

#         while True:
#             try:
#                 export_to_drive(
#                     collection=fc,
#                     description=f"{Country}_Regions",
#                     folder=f"GEE_exports_{Country}_{reducer}",
#                     year=year,
#                     phen_start=phen_start,
#                     phen_end=phen_end,
#                     varName=varName
#                 )
#             except:
#                 print('Error, waiting 60 seconds to try again...')
#                 time.sleep(60)
#                 continue
#             break

####################################################################################
# # # select columns
# # Using the phenology dataset to mask the satellite images and export the data to drive
# import ee
# import time

# # Calculate EVI2
# def addevi(image):
#     # print("Calculating EVI2 for an image...")
#     evi = image.expression(
#         '2.5 * float(nir - red)*0.0001 / float(nir*0.0001 + 2.4 * red*0.0001 + 1)',
#         {
#             'red': image.select('Nadir_Reflectance_Band1'),  # 620-670nm, RED
#             'nir': image.select('Nadir_Reflectance_Band2'),  # 841-876nm, NIR
#         })
#     return image.addBands(evi.rename(['EVI2']))

# # Masking images by the phenology stages
# def GetPeriodCol(TimeSeries, phen_dataset):
#     # print("Filtering images based on phenology stages...")
#     ClassDate = ee.Date('1970-1-01')

#     def filterPeriod(CurrentImage):
#         Date = ee.Date(CurrentImage.get('system:time_start'))
#         Date_Differ = Date.difference(ClassDate, 'day')

#         T1 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([0])).toFloat()
#         T2 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([1])).toFloat()

#         PeriodTag = T1.multiply(T2).lte(0)

#         return CurrentImage.updateMask(PeriodTag).set('system:time_start', Date)

#     return TimeSeries.map(filterPeriod)

# # Export to Drive (Modified to CSV)
# def export_to_drive(collection, description, folder, year, phen_start, phen_end, varName, reducer):
#     # Columns to keep
#     selected_columns = ['GEOID', 'NAME', 'p99', 'p90', 'p80', 'p70', 'p60', 'p50', 'p40', 'p30', 'p20', 'p10', 'p1']
    
#     # # Print selected columns before exporting
#     # first_feature = collection.first()
#     # properties = first_feature.propertyNames().getInfo()
#     # print(f"Exporting columns: {selected_columns}")

#     # Filter out unneeded columns
#     collection = collection.map(lambda feature: feature.select(selected_columns))

#     # Rename columns using .set() for each feature
#     def rename_columns(feature):
#         renaming_dict = {
#             'GEOID': f"GEOID",
#             'NAME': f"NAME",
#             'p99': f"{phen_start}_{varName}_{reducer}_p99",
#             'p90': f"{phen_start}_{varName}_{reducer}_p90",
#             'p80': f"{phen_start}_{varName}_{reducer}_p80",
#             'p70': f"{phen_start}_{varName}_{reducer}_p70",
#             'p60': f"{phen_start}_{varName}_{reducer}_p60",
#             'p50': f"{phen_start}_{varName}_{reducer}_p50",
#             'p40': f"{phen_start}_{varName}_{reducer}_p40",
#             'p30': f"{phen_start}_{varName}_{reducer}_p30",
#             'p20': f"{phen_start}_{varName}_{reducer}_p20",
#             'p10': f"{phen_start}_{varName}_{reducer}_p10",
#             'p1': f"{phen_start}_{varName}_{reducer}_p1",
#         }
        
#         # Apply renaming to each property
#         for old_name, new_name in renaming_dict.items():
#             feature = feature.set(new_name, feature.get(old_name))
        
#         # Remove the old properties
#         feature = feature.select([new_name for old_name, new_name in renaming_dict.items()])
        
#         return feature

#     collection = collection.map(rename_columns)
    
#     # print(f"Starting export: {varName}_{reducer}_{phen_start}_{phen_end}_{year}...")
#     task = ee.batch.Export.table.toDrive(
#         collection=collection,
#         description=f"{varName}_{reducer}_{phen_start}_{phen_end}_{year}",
#         folder=folder,
#         fileFormat='CSV'  # Changed from GeoJSON to CSV
#     )
#     task.start()
#     # print("Export task started.")

# # Main function
# def main(Satellite, countyCol, SoyMap, Country, year, varName, reducer, scale, crs, sort):
#     # print("Processing started...")

#     # Sort countyCol by GEOID at the beginning
#     countyCol = countyCol.sort(sort) # ALAND GEOID COUNTYNS

#     # Mask the variable
#     def soybeans_map(img):
#         return img.updateMask(SoyMap.gte(0.50))

#     Satellite = Satellite.map(soybeans_map).select(varName)
    
#     # print("Satellite images filtered for soybeans.")

#     phen_list = ['Greenup_1', 'MidGreenup_1', 'Maturity_1', 'Peak_1', 'Senescence_1', 'MidGreendown_1', 'Dormancy_1']
#     for i in range(len(phen_list) - 1):
#         phen_start = phen_list[i]
#         phen_end = phen_list[i + 1]

#         # print(f"Processing phenology period: {phen_start} to {phen_end}...")

#         phen_dataset = ee.ImageCollection('MODIS/061/MCD12Q2') \
#             .filter(ee.Filter.date(year + '-1-1', year + '-12-31')).select([phen_start, phen_end]).first()

#         filteredSatellite = GetPeriodCol(Satellite, phen_dataset)

#         if reducer == 'sum':
#             reducedImg = filteredSatellite.sum()
#         elif reducer == 'min':
#             reducedImg = filteredSatellite.min()
#         elif reducer == 'max':
#             reducedImg = filteredSatellite.max()
#         elif reducer == 'mean':
#             reducedImg = filteredSatellite.mean()
#         else:
#             print("Reducer is not defined, skipping...")
#             continue
        
#         # # Reproject and resample image
#         # reducedImg = reducedImg.resample('bilinear').reproject(crs=crs, scale=scale)

#         # print(f"Applying reducer: {reducer}")

#         fc = reducedImg.reduceRegions(
#             collection=countyCol,  # Already sorted by GEOID
#             reducer=ee.Reducer.percentile([99, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1]),
#             scale=scale, #500, 27830 for GLDAS
#             crs=crs  # EPSG:4326'SR-ORG:6974'
#         )

#         def drop_geometry(feature):
#             return feature.setGeometry(None)

#         fc = fc.map(drop_geometry)
#         # print(fc.limit(1).getInfo()) 

#         while True:
#             try:
#                 export_to_drive(
#                     collection=fc,
#                     description=f"{Country}",
#                     folder=f"GEE_exports_{Country}_{reducer}",
#                     year=year,
#                     phen_start=phen_start,
#                     phen_end=phen_end,
#                     varName=varName,
#                     reducer=reducer
#                 )
#                 print(f"Export initiated for {phen_start} to {phen_end}.")
#             except Exception as e:
#                 print(f"Error: {e}. Waiting 60 seconds before retrying...")
#                 time.sleep(60)
#                 continue
#             break

#     # print("Processing completed.")

#############################################################
# # no select columns, efficiency
# Using the phenology dataset to mask the satellite images and export the data to drive
import ee
import time

# Calculate EVI2
def addevi(image):
    # print("Calculating EVI2 for an image...")
    evi = image.expression(
        '2.5 * float(nir - red)*0.0001 / float(nir*0.0001 + 2.4 * red*0.0001 + 1)',
        {
            'red': image.select('Nadir_Reflectance_Band1'),  # 620-670nm, RED
            'nir': image.select('Nadir_Reflectance_Band2'),  # 841-876nm, NIR
        })
    return image.addBands(evi.rename(['EVI2']))

# Masking images by the phenology stages
def GetPeriodCol(TimeSeries, phen_dataset):
    # print("Filtering images based on phenology stages...")
    ClassDate = ee.Date('1970-1-01')

    def filterPeriod(CurrentImage):
        Date = ee.Date(CurrentImage.get('system:time_start'))
        Date_Differ = Date.difference(ClassDate, 'day')

        T1 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([0])).toFloat()
        T2 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([1])).toFloat()

        PeriodTag = T1.multiply(T2).lte(0)

        return CurrentImage.updateMask(PeriodTag).set('system:time_start', Date)

    return TimeSeries.map(filterPeriod)

# Export to Drive (Modified to CSV)
def export_to_drive(collection, description, folder, year, phen_start, phen_end, varName, reducer):
    # Columns to keep
    selected_columns = ['GEOID', 'NAME', 'p99', 'p90', 'p80', 'p70', 'p60', 'p50', 'p40', 'p30', 'p20', 'p10', 'p1']
    
    # # Print selected columns before exporting
    # first_feature = collection.first()
    # properties = first_feature.propertyNames().getInfo()
    # print(f"Exporting columns: {selected_columns}")

    # Filter out unneeded columns
    collection = collection.map(lambda feature: feature.select(selected_columns))

    # Rename columns using .set() for each feature
    def rename_columns(feature):
        renaming_dict = {
            'GEOID': f"GEOID",
            'NAME': f"NAME",
            'p99': f"{phen_start}_{varName}_{reducer}_p99",
            'p90': f"{phen_start}_{varName}_{reducer}_p90",
            'p80': f"{phen_start}_{varName}_{reducer}_p80",
            'p70': f"{phen_start}_{varName}_{reducer}_p70",
            'p60': f"{phen_start}_{varName}_{reducer}_p60",
            'p50': f"{phen_start}_{varName}_{reducer}_p50",
            'p40': f"{phen_start}_{varName}_{reducer}_p40",
            'p30': f"{phen_start}_{varName}_{reducer}_p30",
            'p20': f"{phen_start}_{varName}_{reducer}_p20",
            'p10': f"{phen_start}_{varName}_{reducer}_p10",
            'p1': f"{phen_start}_{varName}_{reducer}_p1",
        }
        
        # Apply renaming to each property
        for old_name, new_name in renaming_dict.items():
            feature = feature.set(new_name, feature.get(old_name))
        
        # Remove the old properties
        feature = feature.select([new_name for old_name, new_name in renaming_dict.items()])
        
        return feature

    collection = collection.map(rename_columns)
    
    # print(f"Starting export: {varName}_{reducer}_{phen_start}_{phen_end}_{year}...")
    task = ee.batch.Export.table.toDrive(
        collection=collection,
        description=f"{varName}_{reducer}_{phen_start}_{phen_end}_{year}",
        folder=folder,
        fileFormat='CSV'  # Changed from GeoJSON to CSV
    )
    task.start()
    # print("Export task started.")

# Main function
def main(Satellite, countyCol, SoyMap, Country, year, varName, reducer, scale, crs, sort):
    # print("Processing started...")

    # Sort countyCol by GEOID at the beginning
    countyCol = countyCol.sort(sort) # ALAND GEOID COUNTYNS

    # Mask the variable
    def soybeans_map(img):
        return img.updateMask(SoyMap.gte(0.50))

    Satellite = Satellite.map(soybeans_map).select(varName)
    
    # print("Satellite images filtered for soybeans.")

    phen_list = ['Greenup_1', 'MidGreenup_1', 'Maturity_1', 'Peak_1', 'Senescence_1', 'MidGreendown_1', 'Dormancy_1']
    for i in range(len(phen_list) - 1):
        phen_start = phen_list[i]
        phen_end = phen_list[i + 1]

        # print(f"Processing phenology period: {phen_start} to {phen_end}...")

        phen_dataset = ee.ImageCollection('MODIS/061/MCD12Q2') \
            .filter(ee.Filter.date(year + '-1-1', year + '-12-31')).select([phen_start, phen_end]).first()

        filteredSatellite = GetPeriodCol(Satellite, phen_dataset)

        if reducer == 'sum':
            reducedImg = filteredSatellite.sum()
        elif reducer == 'min':
            reducedImg = filteredSatellite.min()
        elif reducer == 'max':
            reducedImg = filteredSatellite.max()
        elif reducer == 'mean':
            reducedImg = filteredSatellite.mean()
        else:
            print("Reducer is not defined, skipping...")
            continue
        
        # # Reproject and resample image
        # reducedImg = reducedImg.resample('bilinear').reproject(crs=crs, scale=scale)

        # print(f"Applying reducer: {reducer}")

        fc = reducedImg.reduceRegions(
            collection=countyCol,  # Already sorted by GEOID
            reducer=ee.Reducer.percentile([99, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1]),
            scale=scale, #500, 27830 for GLDAS
            crs=crs  # EPSG:4326'SR-ORG:6974'
        )

        def drop_geometry(feature):
            return feature.setGeometry(None)

        fc = fc.map(drop_geometry)
        # print(fc.limit(1).getInfo()) 

        while True:
            try:
                export_to_drive(
                    collection=fc,
                    description=f"{Country}",
                    folder=f"GEE_exports_{Country}_{reducer}",
                    year=year,
                    phen_start=phen_start,
                    phen_end=phen_end,
                    varName=varName,
                    reducer=reducer
                )
                print(f"Export initiated for {phen_start} to {phen_end}.")
            except Exception as e:
                print(f"Error: {e}. Waiting 60 seconds before retrying...")
                time.sleep(60)
                continue
            break

    # print("Processing completed.")
########################################################################################
# # optimize for efficiency

# # Using the phenology dataset to mask the satellite images and export the data to drive
# import ee
# import time

# # Calculate EVI2
# def addevi(image):
#     print("Calculating EVI2 for an image...")
#     evi = image.expression(
#         '2.5 * float(nir - red)*0.0001 / float(nir*0.0001 + 2.4 * red*0.0001 + 1)',
#         {
#             'red': image.select('Nadir_Reflectance_Band1'),  # 620-670nm, RED
#             'nir': image.select('Nadir_Reflectance_Band2'),  # 841-876nm, NIR
#         })
#     return image.addBands(evi.rename(['EVI2']))

# # Masking images by the phenology stages
# def GetPeriodCol(TimeSeries, phen_dataset):
#     print("Filtering images based on phenology stages...")
#     ClassDate = ee.Date('1970-1-01')

#     def filterPeriod(CurrentImage):
#         Date = ee.Date(CurrentImage.get('system:time_start'))
#         Date_Differ = Date.difference(ClassDate, 'day')

#         T1 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([0])).toFloat()
#         T2 = ee.Image.constant(Date_Differ).subtract(phen_dataset.select([1])).toFloat()

#         PeriodTag = T1.multiply(T2).lte(0)

#         return CurrentImage.updateMask(PeriodTag).set('system:time_start', Date)

#     return TimeSeries.map(filterPeriod)

# # Main function
# def main(Satellite, countyCol, SoyMap, Country, year, varName, reducer):
#     print("Processing started...")

#     # Sort countyCol by GEOID at the beginning
#     countyCol = countyCol.sort('GEOID')

#     # Mask the variable
#     def soybeans_map(img):
#         return img.updateMask(SoyMap.gte(0.50))

#     Satellite = Satellite.map(soybeans_map).select(varName)
    
#     print("Satellite images filtered for soybeans.")

#     phen_list = ['Greenup_1', 'MidGreenup_1', 'Maturity_1', 'Peak_1', 'Senescence_1', 'MidGreendown_1', 'Dormancy_1']
    
#     # Initialize a feature collection that will accumulate all results
#     merged_fc = None
    
#     for i in range(len(phen_list) - 1):
#         phen_start = phen_list[i]
#         phen_end = phen_list[i + 1]

#         print(f"Processing phenology period: {phen_start} to {phen_end}...")

#         phen_dataset = ee.ImageCollection('MODIS/061/MCD12Q2') \
#             .filter(ee.Filter.date(year + '-1-1', year + '-12-31')).select([phen_start, phen_end]).first()

#         filteredSatellite = GetPeriodCol(Satellite, phen_dataset)

#         if reducer == 'sum':
#             reducedImg = filteredSatellite.sum()
#         elif reducer == 'min':
#             reducedImg = filteredSatellite.min()
#         elif reducer == 'max':
#             reducedImg = filteredSatellite.max()
#         elif reducer == 'mean':
#             reducedImg = filteredSatellite.mean()
#         else:
#             print("Reducer is not defined, skipping...")
#             continue

#         print(f"Applying reducer: {reducer}")

#         fc = reducedImg.reduceRegions(
#             collection=countyCol,  # Already sorted by GEOID
#             reducer=ee.Reducer.percentile([99, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1]),
#             scale=500,
#             crs='SR-ORG:6974'
#         )

#         def drop_geometry(feature):
#             return feature.setGeometry(None)

#         fc = fc.map(drop_geometry)
        
#         # Rename columns for this phenology period
#         def rename_columns(feature):
#             renaming_dict = {
#                 'p99': f"{phen_start}_{varName}_p99",
#                 'p90': f"{phen_start}_{varName}_p90",
#                 'p80': f"{phen_start}_{varName}_p80",
#                 'p70': f"{phen_start}_{varName}_p70",
#                 'p60': f"{phen_start}_{varName}_p60",
#                 'p50': f"{phen_start}_{varName}_p50",
#                 'p40': f"{phen_start}_{varName}_p40",
#                 'p30': f"{phen_start}_{varName}_p30",
#                 'p20': f"{phen_start}_{varName}_p20",
#                 'p10': f"{phen_start}_{varName}_p10",
#                 'p1': f"{phen_start}_{varName}_p1",
#             }
            
#             # Apply renaming to each property
#             for old_name, new_name in renaming_dict.items():
#                 feature = feature.set(new_name, feature.get(old_name))
            
#             # Remove the old properties (except GEOID and NAME)
#             properties_to_keep = ['GEOID', 'NAME'] + [new_name for old_name, new_name in renaming_dict.items()]
#             feature = feature.select(properties_to_keep)
            
#             return feature

#         fc = fc.map(rename_columns)
        
#         # fc = fc.filter(ee.Filter.notNull(['p99'])) #new

        
#         # Merge with the accumulated feature collection
#         if merged_fc is None:
#             merged_fc = fc
#         else:
#             # # Join the new data to the existing collection
#             # merged_fc = merged_fc.map(lambda feature: 
#             #     ee.Feature(
#             #         feature.geometry(), 
#             #         feature.toDictionary().combine(
#             #             fc.filter(ee.Filter.eq('GEOID', feature.get('GEOID'))).first().toDictionary()
#             #         )
#             #     )
#             # )
            
#             join_filter = ee.Filter.equals(leftField='GEOID', rightField='GEOID')
#             merged_fc = ee.Join.inner().apply(merged_fc, fc, join_filter)


#     # Export the merged feature collection
#     def export_merged_to_drive(collection, description, folder, year, varName):
#         print(f"Starting export of merged data: {description}_{year}_{varName}...")
        
#         limited_collection = collection.limit(5)
        
#         task = ee.batch.Export.table.toDrive(
#             collection=collection,
#             description=f"{description}_{year}_{varName}_MERGED",
#             folder=folder,
#             fileFormat='CSV'
#         )
#         task.start()
#         print("Merged export task started.")

#     if merged_fc is not None:
#         while True:
#             try:
#                 export_merged_to_drive(
#                     collection=merged_fc,
#                     description=f"{Country}_Regions",
#                     folder=f"GEE_exports_{Country}_{reducer}",
#                     year=year,
#                     varName=varName
#                 )
#                 print("Merged export initiated.")
#             except Exception as e:
#                 print(f"Error: {e}. Waiting 60 seconds before retrying...")
#                 time.sleep(60)
#                 continue
#             break

#     print("Processing completed.")