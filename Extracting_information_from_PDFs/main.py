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
folder_path = r'D:\Uni\Bachelorarbeit\Articles_PDF\add_to_table'

# Path to the Excel file where the information needs to be stored
# Docker: os.getenv('EXCEL_PATH', './data/2024Apr_Mana_Review_v2i - Kopie.xlsx')
excel_path = r'D:\Uni\Bachelorarbeit\Bachelor-thesis\Extracting_information_from_PDFs\data\2024Apr_Mana_Review_v2i - Kopie.xlsx'

# Use the process_extraction_results() function from the pdf_processing module toe extract the relevant data
extracted_data = process_extraction_results(folder_path)

# Fill in the information into the Excel file using the update_excel_with_extracted_data() function of the excel_processing module
update_excel_with_extracted_data(excel_path, extracted_data)
