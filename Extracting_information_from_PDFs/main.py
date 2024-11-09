# To show the extracted data, the logging library is imported here
import logging

# 'os' for data management (importing files)
import os

# Loading the other modules for extracting information and storing them in the Excel file
from pdf_processing import process_extraction_results
from excel_processing import update_excel_with_extracted_data

# Setting up logging for information, specifying the time (asctime), the type of log output (levelname) and of course the message to be output (message).
# https://docs.python.org/3/library/logging.config.html
# https://docs.python.org/3/library/logging.html#logging.INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Path to the PDFs
# Docker: os.getenv('FOLDER_PATH', './data/Articles_PDF')
folder_path = r'D:\Uni\Bachelorarbeit\Articles_PDF\add_to_table\50-75'

# Path to the Excel file where the information needs to be stored
# Docker: os.getenv('EXCEL_PATH', './data/2024Apr_Mana_Review_v2i - Kopie.xlsx')
excel_path = r'D:\Uni\Bachelorarbeit\2024Apr_Mana_Review_v2i - Kopie.xlsx'

extracted_data = process_extraction_results(folder_path)

# Fill in the information into the Excel file using the update_excel_with_extracted_data
update_excel_with_extracted_data(excel_path, extracted_data)

"""
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
"""