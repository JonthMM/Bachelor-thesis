# os zur Datenverwaltung (Einlesen von Dateien)
import os

# Regex zum Ersetzen von gefundenen Sonderzeichen
import re

# PDFMiner zum Extrahieren der Texte aus den PDFs
from pdfminer.high_level import extract_text

# Angeben des Pfades der zu durchsuchenden Datei
pdf_path = r'D:\Uni\Bachelorarbeit\Articles_PDF\add_to_table\151-169\Influences of large-scale climatic variability on episodic tree mortality in northern Patagonia.pdf'


def clean_and_remove_control_characters(text):
    """
    Entfernt alle ASCII-Steuerzeichen, ersetzt '(cid:6)', '(cid:57\)' und '¢' durch "′" und andere '(cid:\d+)' mithilfe der re.sub() Funktion
    durch "°". um bereits (durch das Hilfscript "find_special_characters" bekannte Sonderzeichen zu umgehen.
    https://www.w3schools.com/python/python_regex.asp
    https://www.w3schools.com/python/ref_func_ord.asp

    Args:
        text (str): Der Text, aus dem Steuerzeichen und bestimmte andere Zeichen entfernt werden sollen.

    Returns:
        str: Der bereinigte Text.
    """

    # Ersetze "(cid:6)", "(cid:57)" und "¢" durch "′" sowie generalisiert alle anderen cid Sonderzeichen durch "°"
    text = re.sub(r'\(cid:6\)', '′', text)
    cleaned_text = re.sub(r'\(cid:57\)', '′', text)
    cleaned_text = re.sub(r'\(cid:\d+\)', '°', cleaned_text)
    cleaned_text = text.replace('¢', '′')


    # Entferne alle anderen ASCII-Steuerzeichen
    cleaned_text = ''.join(char for char in text if ord(char) >= 32 or ord(char) == 10)

    return cleaned_text

def search_pdf_to_find_special_characters(pdf_path):
    """
    Nimmt einen Pfad zu einer PDF Datei entgegen und prüft, ob diese existiert. Wenn ja, wird der Text extrahiert und
    von Sonderzeichen bereinigt durch die Funktion "clean_text_and_remove_special_characters". Danach wird der Text in Zeilen
    aufgeteilt und der gesuchte String, welcher ein potenzielles Sonderzeichen enthält wird in jeder Zeile gesucht.
    Wenn dieser String gefunden wurde, wird die Zeile, in welcher er ist und die darauffolgenden 3 Zeilen zur Überprüfung ausgegeben

    Args:
        pdf_path (str): Der Pfad zu einer bestimmten PDF-Datei, welche überpüft werden soll

    Returns:
        None: Die Funktion gibt die Ergebnisse direkt im Terminal aus und hat keinen Rückgabewert.
    """

    # Überprüfen, ob die Datei existiert
    if not os.path.isfile(pdf_path):
        print(f"Die Datei {pdf_path} existiert nicht.")
        return

    # Text mit pdfminer Funktion "extract_text()" aus der PDF-Datei extrahieren
    extracted_text = extract_text(pdf_path)

    # Den erhaltenen Text bereinigen mit Hilfsfunktion "clean_text_and_remove_special_characters"
    extracted_text = clean_and_remove_control_characters(extracted_text)

    # Den extrahierten Text in Zeilen aufteilen und dann jede Zeile durchsuchen und ausgeben, falls sie den angegebenen String enthält
    lines = extracted_text.split('\n')
    for i, line in enumerate(lines):
        # String, nach dem gesucht werden soll und Zeile in welcher er gefunden wurde ausgeben
        if "39  to  430  S" in line:
            print(line)
            # Überprüfen, ob es nächste Zeilen gibt und wenn ja die nächsten 3 ausgeben
            if i + 1 < len(lines):
                print(lines[i+3])


# Aufrufen der hauptfunktion, welche den aufgeräumten Text nach dem gesuchten Schlüsselwort durchsucht
search_pdf_to_find_special_characters(pdf_path)
