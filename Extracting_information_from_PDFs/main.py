"""
main.py

This script is the main module of my automated information retrieval program and serves the purpose to manage and call the other two modules.

Author:
    Jonathan Mattis Wisser
    jmader@uni-muenster.de

Version:
    1.0
Datum:
    2024-11-12
"""

__author__ = "Jonathan Mattis Wisser"
__version__ = "1.0"
__date__ = "2024-11-12"

# ------------------------------------------------- IMPORTS ---------------------------------------------------------- #
# 'os' for data management (importing and saving files)
import os

# To show the extracted data, the logging library is imported here
import logging

# Loading the other modules for extracting information and storing them in the Excel file
from pdf_processing import process_extraction_results
from excel_processing import update_excel_with_extracted_data

# ------------------------------------------------- SET-UPS ---------------------------------------------------------- #
# Setting up logging for information, specifying the time (asctime), the type of log output (levelname) and of course the message to be output (message).
# https://docs.python.org/3/library/logging.config.html
# https://docs.python.org/3/library/logging.html#logging.INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the PDFs
# Docker: os.getenv('FOLDER_PATH', './data/Articles_PDF')
FOLDER_PATH = os.getenv('FOLDER_PATH', './data/Example_studies') #r'D:\Uni\Bachelorarbeit\Bachelor-thesis\Extracting_information_from_PDFs\data\Example_studies'

# Path to the Excel file where the information needs to be stored
# Docker: os.getenv('EXCEL_PATH', './data/Example.xlsx')
EXCEL_PATH =  os.getenv('EXCEL_PATH', './data/Example.xlsx') #r'D:\Uni\Bachelorarbeit\Bachelor-thesis\Extracting_information_from_PDFs\data\Example.xlsx'

# ------------------------------------------------- EXECUTION -------------------------------------------------------- #
# Looking up if there are PDF files in the given folder 'folder_path'
pdf_files = [filename for filename in os.listdir(FOLDER_PATH) if filename.endswith('.pdf')]

# For the case that no PDF files found in 'folder_path', this gets logged and the process will not continue!
if not pdf_files:
    logging.error(f" 'No searchable PDFs found in: {FOLDER_PATH}'")

# When there is at least one PDF, continue normally with the execution
else:
    # Use the process_extraction_results() function from the pdf_processing module toe extract the relevant data
    extracted_data = process_extraction_results(FOLDER_PATH)

    # Fill in the information into the Excel file using the update_excel_with_extracted_data() function of the excel_processing module
    update_excel_with_extracted_data(EXCEL_PATH, extracted_data)
