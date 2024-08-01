# Logging zum besseren Verständnis der Ergebnisse bzw. Ausgaben
import logging

from pdf_processing import extract_coordinates_from_pdfs_in_folder
from excel_processing import update_excel_with_extracted_data

""" 
To DO:

2. "How was drought quantified" Als suchoption hinzufügen: PET, SPI, SPEI, PDSI, precipitation usw. als Schlüsselwörter + Zeilen davor und danach - in Bearbeitung, läuft schon ist aber Ausbaufähig

3. "time period with drought (if mentioned)" und "time period analyzed" als Suchoption ergänzen (wahrscheinlich eingeschränkt als (Jahr-Jahr) such-pattern, wird nicht alles finden aber immerhin keine redundanzen durch Spezialisierung

4. Experimentell oder field study (observational) als Suche zur Extraktion hinzufügen für Charts


Eventuell:
Logik so ändern, dass nur die umliegenden 3 Zeilen von Koordinaten gespeichert und ausgegeben werden, wenn def find_study_site(lines): keinen Erfolg hatte

Generell:
Programmierschritte stichpunktartig festhalten

Entstandene Excel Tabelle komplett überprüfen und säubern (redundanzen entfernen, Koordinaten aufräumen und eventuell umwandeln
in Einheitliches Format, https://spei.csic.es/map/maps.html#months=1#month=5#year=2024 braucht Dezimalgrad (WGS84) Bsp.: 51.98622, 7.632755)

   Danach Plots und Karte wie besprochen erstellen 
   

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
"""

# Einrichten des Loggings für Informationen, hierbei wird die Zeit angegeben (asctime), sowieso um welchen Typ von logg-ausgabe es sich handelt (levelname) und natürlich die nachricht welche Ausgegeben werden soll (message)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Pfad zum Ordner mit den PDF-Dateien
folder_path = r'D:\Uni\Bachelorarbeit\Articles_PDF\add_to_table\151-169'

# Pfad zur Excel-Datei
excel_path = r'D:\Uni\Bachelorarbeit/2024Apr_Mana_Review_v2i - Kopie.xlsx'

# Extrahiere Daten aus den PDF-Dateien
extracted_data = extract_coordinates_from_pdfs_in_folder(folder_path)

# Aktualisiere die Excel-Datei mit den extrahierten Daten
update_excel_with_extracted_data(excel_path, extracted_data)

# Ausgabe der extrahierten Informationen im Terminal zur Überprüfung
for i, (pdf_basename, coordinates, lines_with_coordinates, drought_quantified, found_keywords) in enumerate(extracted_data):
    print(f"Paper: '{pdf_basename}'")
    print(f"Location coordinates: {coordinates}")
    print(f"Vorkommende Zeilen im Text: '{lines_with_coordinates}'")
    print(f"Dürre quantifiziert: '{drought_quantified}'")
    if found_keywords:
        print(f"Dürre quantifiziert: '{found_keywords}'")
    if i != len(extracted_data) - 1:
        print()
