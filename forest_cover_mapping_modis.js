// Load the MODIS Land Cover Dataset, filter it for all 2020 data and only load the first image of it with .first() 
// (this is extremely important, because eq(x) filtering for classes is not availably without it)
// Source: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#code-editor-javascript
// Source: https://developers.google.com/earth-engine/guides/ic_filtering
// Source: https://developers.google.com/earth-engine/apidocs/ee-imagecollection-first
var dataset = ee.ImageCollection('MODIS/061/MCD12Q1').filter(ee.Filter.date('2020-01-01', '2020-12-31'))
                .first();

// Load the 'LC_Type1' Band (Land Cover Type 1: Annual International Geosphere-Biosphere Programme (IGBP) classification)
// Source: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#code-editor-javascript
// Source: select()
var igbpLandCover = dataset.select('LC_Type1');

// Only choose those forest classes from all land cover classes that have 60%+ tree cover by creating a list with only the needed classes numbers
var relevantforestclasses = [1, 2, 3, 4, 5, 6, 8];

// Create a mask that only contains the relevant forest land cover classes by filtering by metadata, in this case the class numbers with eq()
// Source: https://courses.spatialthoughts.com/end-to-end-gee.html#filtering-image-collections
// Source: https://gis.stackexchange.com/questions/358718/filter-featurecollection-with-multiple-values
// Source: https://stackoverflow.com/questions/50219547/using-masking-in-google-earth-engine
var maskedforestcover = igbpLandCover.updateMask(igbpLandCover.eq(1)
                            .or(igbpLandCover.eq(2))
                            .or(igbpLandCover.eq(3))
                            .or(igbpLandCover.eq(4))
                            .or(igbpLandCover.eq(5))
                            .or(igbpLandCover.eq(6))
                            .or(igbpLandCover.eq(8))
                            );

// Create the variable to store the information in which classes to display and with what colors
// Source: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#code-editor-javascript
var igbpLandCoverVis = {
  min: 1.0,
  max: 8.0,
  palette: [
    '05450a', '086a10', '54a708', '78d203', '009900', 'c6b044', 'dade48'
  ],
}; 

// Set a map canter for the visualisation of the map after running the code
// Source: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#code-editor-javascript
Map.setCenter(6.746, 46.529, 2.5);

// Add the variable with the information what should be displayed and how ('igbpLandCover') to the Map and give it a Name
// Source: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#code-editor-javascript
Map.addLayer(maskedforestcover, igbpLandCoverVis, 'All relevant forest classes');

// Export the forest cover overlay as a GeoTiff to use it later as backgroundmap in QGIS and get the relevant MODIS classes for all paper locations
// Source: https://developers.google.com/earth-engine/apidocs/export-image-todrive
Export.image.toDrive({
  image: maskedforestcover,
  description: 'MODIS_forest_cover_export',  // Name of the GeoTiff
  folder: 'GEE_Exports',  // Name of the folder to save the GeoTiff to in Google Drive
  scale: 500,  // Maximal resolution per pixel for this product
  maxPixels: 10000000000000,  // Maximal count of pixels in general
  crs: 'EPSG:4326',  
  fileFormat: 'GeoTIFF'  
});


