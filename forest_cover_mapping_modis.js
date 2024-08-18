// Laden des Modis Land Cover Datasets via https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#description
var landCover = ee.ImageCollection("MODIS/061/MCD12Q1")
                .filter(ee.Filter.date('2020-01-01', '2020-12-31'))
                .first()
                .select('LC_Type1');

// Auswahl von nur den fünf Waldklassen und diesen, die 60+% tree cover haben
var classesToDisplay = [1, 2, 3, 4, 5, 6, 8];

// Maske welche nur die sieben ausgewählten Klassen enthält
var maskedLandCover = landCover.updateMask(landCover.eq(1)
                            .or(landCover.eq(2))
                            .or(landCover.eq(3))
                            .or(landCover.eq(4))
                            .or(landCover.eq(5))
                            .or(landCover.eq(6))
                            .or(landCover.eq(8))
                            );

// Anzeigen der Ergebnisse auf der Karte mit den entsprechenden Farben
Map.centerObject(maskedLandCover, 2.5); // Zoom auf Welt
Map.addLayer(maskedLandCover, {
  min: 1,
  max: 8,
  palette: ['05450a', '086a10', '54a708', '78d203', '009900', 'c6b044', 'dade48'] // Farben von https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands
}, 'All mayor Forest Classes');


// Exportieren des GeoTiffs nach Drive zum benutzen als Karte
Export.image.toDrive({
  image: maskedLandCover,
  description: 'woody_and_forest_cover_export_world',  // Name der Datei
  folder: 'GEE_Exports',  // Name des Ordners in Google Drive (optional)
  scale: 500,  // Auflösung in Metern pro Pixel
  maxPixels: 10000000000000,  // Maximal zulässige Anzahl an Pixeln
  crs: 'EPSG:4326',  // Koordinatensystem (WGS84)
  fileFormat: 'GeoTIFF'  // Dateiformat
});

// Erstellen einer Legende
function createLegend() {
  var legend = ui.Panel({
    style: {
      position: 'bottom-left',
      padding: '8px 15px'
    }
  });

  // Tite der Legende 
  var legendTitle = ui.Label({
    value: 'Forest Cover Legend',
    style: {
      fontWeight: 'bold',
      fontSize: '18px',
      margin: '0 0 6px 0',
      padding: '0'
    }
  });

  legend.add(legendTitle);

  // Farben und Labels der Attribute der Legende
  var palette = ['#05450a', '#086a10', '#54a708', '#78d203', '#009900', '#c6b044', '#dade48'];
  var names = ['Evergreen Needleleaf Forests', 
               'Evergreen Broadleaf Forests', 
               'Deciduous Needleleaf Forests', 
               'Deciduous Broadleaf Forests', 
               'Mixed Forests',
               'Closed Shrublands',
               'Woody Savannas'];
  
  // Größen und Farbenspezifikation für die Legende selbst
  for (var i = 0; i < palette.length; i++) {
    var colorBox = ui.Label({
      style: {
        backgroundColor: palette[i],
        padding: '8px',
        margin: '0 0 4px 0'
      }
    });

    var description = ui.Label({
      value: names[i],
      style: {
        margin: '0 0 4px 6px'
      }
    });

    var panel = ui.Panel({
      widgets: [colorBox, description],
      layout: ui.Panel.Layout.Flow('horizontal')
    });

    legend.add(panel);
  }
  
  Map.add(legend);
}

// Legende erstellen
createLegend();

