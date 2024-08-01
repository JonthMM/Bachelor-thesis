# os zur Datenverwaltung (Einlesen von Dateien)
import os

# Regex zum Ersetzen von gefundenen Sonderzeichen
import re

# PDFMiner zum Extrahieren der Texte aus den PDFs
from pdfminer.high_level import extract_text

# Angeben des Pfades der zu durchsuchenden PDF
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

def printing_lines_and_searching_separated_keywords(pdf_path):
    """
    Nimmt einen Pfad zu einer PDF Datei entgegen und prüft, ob diese existiert. Wenn ja, wird der Text extrahiert und
    von Sonderzeichen bereinigt durch die Funktion "clean_text_and_remove_special_characters". Danach wird der Text in Zeilen
    aufgeteilt und es werden alle Zeilen mit Nummerierung zur Überprüfung ausgegeben. Außerdem wird dann geprüft, ob das gesuchte
    Keywords am Ende, beziehungsweise Anfang einer Zeile ist und somit durch einen Zeilenumbruch getrennt ist

    Args:
        pdf_path (str): Der Pfad zu einer bestimmten PDF-Datei, welche überprüft werden soll

    Returns:
        None: Die Funktion gibt die Ergebnisse direkt im Terminal aus und hat keinen Rückgabewert.
    """

    # Überprüfen, ob die Datei existiert
    if not os.path.isfile(pdf_path):
        print(f"Die Datei {pdf_path} existiert nicht.")
        return

    # Text mit pdfminer Funktion "extract_text()" aus der PDF-Datei extrahieren
    text = extract_text(pdf_path)

    # Den erhaltenen Text bereinigen mit Hilfsfunktion "clean_text_and_remove_special_characters"
    text = clean_and_remove_control_characters(text)

    # Den Text in Zeilen aufteilen, jede Zeile durchsuchen und prüfen, ob (hier) "study" am Ende und "site" am Anfang der nächsten Zeile vorkommt
    # (Dabei handelt es sich um ein Anwendungsbeispiel, welches durch andere Keywords ersetzt werden kann)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Ausgabe welche alle Zeilen mit Nummerierung ausgibt
        print(f"Zeile {i}: {line}")

        # Suche nach "study" am Ende der Zeile und "site" am Anfang der darauffolgenden Zeile
        if line.strip().endswith("Study") and (i + 1 < len(lines)) and lines[i + 1].strip().startswith("Site"):
            # Ausgabe, welche bestätigt, ob das Keyword entsprechend gefunden wurde und die entsprechende Zeile ausgibt
            print(f"Gefunden: {line}")
            # Ausgabe, welche die darauffolgende Zeile ebenfalls ausgibt
            print(lines[i + 1])



# Aufrufen der Funktion, welche den aufgeräumten Text nach dem gesuchten Schlüsselwort durchsucht
printing_lines_and_searching_separated_keywords(pdf_path)
