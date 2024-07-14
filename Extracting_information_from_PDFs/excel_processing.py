# openpyxl zum Arbeiten mit Excel Dateien
import openpyxl

# Benötigt, um Zeichen zu entfernen, welche nicht von openpyxl verarbeitet werden können
from openpyxl.utils.exceptions import IllegalCharacterError

def remove_illegal_characters(excel_data):
    """
    Entfernt Zeichen, die von Openpyxl nicht unterstützt werden und somit nicht in der Excel-Datei verwendet werden
    können aus den Informationen, welche in die Excel-Datei übernommen werden sollen.

    Args:
        excel_data (str): Der String, aus dem für openpyxl illegale Zeichen entfernt werden sollen.

    Returns:
        str: Der bereinigte String ohne für openpyxl illegale Zeichen.
    """
    return ''.join(char for char in excel_data if ord(char) in range(32, 127))

def find_first_empty_row(sheet, columns):
    """
    Findet die erste leere Zeile in angegebenen Spalten eines Excel-Arbeitsblatts zur Festlegung eines Startpunktes
    zum Einfügen der relevanten Informationen.
    Dies ist nötig, um so flexibel wie möglich mit jeder möglichen Excel-Tabelle arbeiten zu können

    Args:
        sheet (openpyxl.worksheet.worksheet.Worksheet): Das Arbeitsblatt, in dem gesucht wird.
        columns (list): Eine Liste von Spaltennummern, in denen nach der ersten leeren Zeile gesucht wird.

    Returns:
        int: Die Nummer der ersten leeren Zeile, die gefunden wurde.
    """
    for row in range(1, sheet.max_row + 1):
        if all(sheet.cell(row=row, column=col).value is None for col in columns):
            return row
    return sheet.max_row + 1

def update_excel_with_extracted_data(excel_path, extracted_data):
    """
    Aktualisiert die Excel-Datei mit den vorher durch das Modul "pdf_processing" extrahierten Daten aus den PDFs.

    Args:
        excel_path (str): Pfad zur Excel-Datei.
        extracted_data (list): Liste von Tupeln mit den extrahierten Informationen.

    Returns:
        workbook: Das aktualisierte Workbook-Objekt.
    """

    # Öffnen dem angegebenen Arbeitsblatt (sheet) der angegebenen Excel-Datei mithilfe von openpyxl
    workbook = openpyxl.load_workbook(excel_path)
    worksheet = workbook['secondAppr']

    # Finde die erste leere Zeile in den Spalten B (Paper), F (location coordinates) und J (Area name)
    start_row = find_first_empty_row(worksheet, [2, 6, 10])

    # Trage die aus den PDFs extrahierten Informationen in die Excel-Datei ein
    for i, (pdf_basename, coordinates, lines_with_coordinates, drought_quantified, found_keywords) in enumerate(extracted_data):
        worksheet.cell(row=start_row + i, column=2, value=pdf_basename)

        # Kopiere, falls vorhanden, die Koordinaten immer in Spalte F (location coordinates)
        if coordinates != 'Keine Koordinaten gefunden' and len(coordinates.split(', ')) > 1:
            unique_coordinates = ', '.join(sorted(set(coordinates.split(', '))))
            worksheet.cell(row=start_row + i, column=6, value=unique_coordinates)

            # Kopiere, falls vorhanden, die Kontextzeilen der gefundenen Koordinaten immer in Spalte J (Area name)
            cleaned_lines_with_coordinates = remove_illegal_characters(lines_with_coordinates)
            worksheet.cell(row=start_row + i, column=10, value=cleaned_lines_with_coordinates)

        # Kopiere, falls keine Koordinaten gefunden wurden die Information darüber immer in Spalte F (location coordinates)
        else:
            worksheet.cell(row=start_row + i, column=6, value=coordinates)
            # Kopiere, falls keine Koordinaten gefunden, die Kontextzeilen den gefundenen Bereich der Studie immer in Spalte J (Area name)
            worksheet.cell(row=start_row + i, column=10, value=remove_illegal_characters(lines_with_coordinates))

        # Kopiere, falls ein Schlüsselwort zur Definition von Dürre gefunden wurden die Information darüber wie, immer in Spalte R (how was drought quantified)
        if drought_quantified:
            worksheet.cell(row=start_row + i, column=18, value=remove_illegal_characters(drought_quantified))

    # Speichere die durchgeführten Änderungen in der Excel-Datei
    workbook.save(excel_path)
