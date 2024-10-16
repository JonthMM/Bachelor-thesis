# Logging zum besseren Verständnis der Ergebnisse bzw. Ausgaben
import logging

from pdf_processing import extract_coordinates_from_pdfs_in_folder
from excel_processing import update_excel_with_extracted_data

""" 
To DO: FÜR JAHRESZAHLEN NOCH MAL TESTEN OB ES GEHT DAS NACH DEM WORT "REFERENCES" DIE SUCHE ABGEBROCHEN WIRD UM CITATIONS ZU VERMEIDEN!
FÜR JAHRESZAHLEN CHECKEN DASS WENN 20XX-YY IST, YY GRÖßER SEIN MUSS ALS XX

1. "Study Type" als Suche ergänzen: "Experimental", "Observational" oder "modeling" - fertig muss nur noch optimiert werden in Zukunft

2. "How was drought quantified" Als suchoption hinzufügen: PET, SPI, SPEI, PDSI, precipitation usw. als Schlüsselwörter + Zeilen davor und danach - fertig muss nur noch optimiert werden in Zukunft

3. "time period with drought (if mentioned)" und "time period analyzed" als Suchoption ergänzen (wahrscheinlich eingeschränkt als (Jahr-Jahr) such-pattern, wird nicht alles finden aber immerhin keine redundanzen durch Spezialisierung

4. Forest type für "ecosystem type" als Suche ergänzen - fertig, muss nur noch optimiert werden in Zukunft

5. Insgesamt muss die fertige Excel Tabelle am Ende so nahe wie möglich an das Muster von mir rankommen

6. Eventuell noch umwandlung von Koordinaten in Dezimalgrad einbauen, könnte bei den vielen verschiedenen Koordinaten-Formaten aber sehr schwierig werden

7. Docker wenn noch Zeit (nur für Main script, nicht für helfer Funktionen oder die Plot creation


Eventuell:
Logik so ändern, dass nur die umliegenden 3 Zeilen von Koordinaten gespeichert und ausgegeben werden, wenn def find_study_site(lines): keinen Erfolg hatte
Beispiel dafür: Climatic and human influences on fire regimes of the southern San Juan Mountains, Colorado, USA zum Überprüfen

Generell:
Programmierschritte stichpunktartig festhalten
   

Done:

1. Logging so ergänzen, dass wenn eine single coordinate ignoriert wurde, aber trotzdem valide coordinates gefunden wurden, dies auch ausgegeben wird

2. Einzelne, redundante Koordinaten Ignorieren

3. Alle PDFs ebenfalls manuell nach Koordinaten durchsucht um weitere regex Suchpattern hinzuzufügen

4. Ersetzen von cid und anderen Sonderzeichen durch das entsprechende richtige Symbol

5. Entfernen von Zeichen in PDFs, welche von Openpyxl nicht unterstützt werden mit https://www.w3schools.com/python/ref_func_ord.asp

6. Suche nach Koordinaten mithilfe von regex pattern

7. Suche nach Study sites in Textformm:
   7.1. Entweder, wenn Koordinaten gefunden wurden 2 Zeilen davor und die wo die Koordinaten waren
   7.2 Oder mit Schlüsselwortsuche wie z.B. "study site" oder "study area" etc.

8. Kopieren von gefundenen Informationen, in die Excel Tabelle

9. Doppel-Koordinaten werden, nicht in die Tabelle übernommen

10. Pattern so gut wie es geht, ohne redundanzen zu erzeugen zusammenfassen, um doppelte zu vermeiden

11. Alle regex Suchpattern kommentieren
    11.1 Beispiele ergänzen

12. Alle PDFs ohne study site aus dem Word Dokument nach verschiedenen study site schreibweisen checken
    12.1 Schlüsselwortsuche wie z.B. "study site" oder "study area" etc. erweitern

13. Alles gut verständlich auskommentieren
    13.1. Args und Returns bei jeder Funktion hinzufügen
    
14. Entstandene Excel Tabelle komplett überprüfen und säubern (redundanzen entfernen, Koordinaten aufräumen und eventuell umwandeln
in Einheitliches Format, https://spei.csic.es/map/maps.html#months=1#month=5#year=2024 braucht Dezimalgrad (WGS84) Bsp.: 51.98622, 7.632755)
"""

# Einrichten des Loggings für Informationen, hierbei wird die Zeit angegeben (asctime), sowieso um welchen Typ von logg-ausgabe es sich handelt (levelname) und natürlich die nachricht welche Ausgegeben werden soll (message)
# https://docs.python.org/3/library/logging.config.html
# https://docs.python.org/3/library/logging.html#logging.INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Pfad zum Ordner mit den PDF-Dateien
folder_path = r'D:\Uni\Bachelorarbeit\Articles_PDF\add_to_table\50-75'

# Pfad zur zu befüllenden Excel-Datei
excel_path = r'D:\Uni\Bachelorarbeit/2024Apr_Mana_Review_v2i - Kopie.xlsx'

# Path to the shapefile containing the information we need for the plot(s)
shapefile_path = r'D:\Uni\Bachelorarbeit\complete_paper_points\re-analysed paper points with forest\re-analysed_paper_points_with_forest.shp'

# Extrahiere Daten aus den PDF-Dateien
extracted_data = extract_coordinates_from_pdfs_in_folder(folder_path)

# Aktualisiere die Excel-Datei mit den extrahierten Daten
update_excel_with_extracted_data(excel_path, extracted_data)

# Ausgabe der extrahierten Informationen im Terminal zur Überprüfung
for i, (pdf_basename, coordinates, lines_with_coordinates, drought_quantified, found_keywords, study_type, forest_type, analyzed_years, periods_with_drought, single_years_with_drought) in enumerate(extracted_data):
    print(f"Paper: '{pdf_basename}'")
    print(f"Location coordinates: {coordinates}")
    print(f"Vorkommende Zeilen im Text: '{lines_with_coordinates}'")
    print(f"Dürre quantifiziert: '{drought_quantified}'")
    if found_keywords:
        print(f"Dürre quantifiziert: '{found_keywords}'")
    print(f"Studientyp: '{study_type}'")
    print(f"Waldtyp: '{forest_type}'")
    print(f"Untersuchte Jahre: '{analyzed_years}'")
    print(f"Jahre mit Dürre: '{periods_with_drought}', {single_years_with_drought}")
    if i != len(extracted_data) - 1:
        print()