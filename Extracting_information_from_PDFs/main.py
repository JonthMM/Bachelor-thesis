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
folder_path = r'D:\Uni\Bachelorarbeit\Bachelor-thesis\Extracting_information_from_PDFs\data\Example studies'  #os.getenv('FOLDER_PATH', './data/Articles_PDF')

# Path to the Excel file where the information needs to be stored
# Docker: os.getenv('EXCEL_PATH', './data/Example.xlsx')
excel_path =  r'D:\Uni\Bachelorarbeit\Bachelor-thesis\Extracting_information_from_PDFs\data\Example.xlsx' #os.getenv('EXCEL_PATH', './data/Example.xlsx')

# Looking up if there are PDF files in the given folder 'folder_path'
pdf_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.pdf')]

# For the case that no PDF files found in 'folder_path', this gets logged and the process will not continue!
if not pdf_files:
    logging.error(f" 'No searchable PDFs found in: {folder_path}'")

# When there is at least one PDF, continue normally with the execution
else:
    # Use the process_extraction_results() function from the pdf_processing module toe extract the relevant data
    extracted_data = process_extraction_results(folder_path)

    # Fill in the information into the Excel file using the update_excel_with_extracted_data() function of the excel_processing module
    update_excel_with_extracted_data(excel_path, extracted_data)
