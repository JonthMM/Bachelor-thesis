# os zur Datenverwaltung (Einlesen von Dateien)
import os

# Regex zum Implementieren der Suchmuster (pattern)
import re

# PDFMiner zum Extrahieren der Texte aus den PDFs
from pdfminer.high_level import extract_text

# defaultdict um Zählungen durchführen
from collections import defaultdict

# Logging zum besseren Verständnis der Ergebnisse bzw. Ausgaben
# Hier wird dabei auf logging.info() und logging.error() zurückgegriffen:
# https://docs.python.org/3/library/logging.html#logging.INFO
# https://docs.python.org/3/library/logging.html#logging.error
import logging

def remove_illegal_characters(excel_data):
    """
    Entfernt Zeichen, die von Openpyxl nicht unterstützt werden und somit nicht in der Excel-Datei verwendet werden
    können aus den Informationen, welche in die Excel-Datei übernommen werden sollen
    https://www.w3schools.com/python/ref_func_ord.asp

    Args:
        excel_data (str): Der String, aus dem für openpyxl illegale Zeichen entfernt werden sollen.

    Returns:
        str: Der bereinigte String ohne für openpyxl illegale Zeichen.
    """
    
    # Entferne alle ASCII-Steuerzeichen welche von Openpyxl nicht unterstützt werden mithilfe von ord()
    return ''.join(char for char in excel_data if ord(char) in range(32, 127))


def clean_and_remove_control_characters(text):
    """
    Entfernt alle ASCII-Steuerzeichen, ersetzt '(cid:6)', '(cid:57\)' und '¢' durch "′" und andere '(cid:\d+)' mithilfe der re.sub() Funktion
    durch "°". um bereits (durch das Hilfsscript "find_special_characters") bekannte Sonderzeichen zu umgehen.
    https://www.w3schools.com/python/python_regex.asp
    https://www.w3schools.com/python/ref_func_ord.asp
    https://docs.python.org/3/library/re.html#re.sub

    Args:
        text (str): Der Text, aus dem Steuerzeichen und bestimmte andere Zeichen entfernt werden sollen.

    Returns:
        str: Der bereinigte Text.
    """

    # Ersetze "(cid:6)", "(cid:57)" und "¢" durch "′" sowie generalisiert alle anderen cid Sonderzeichen durch "°"
    text = re.sub(r'\(cid:6\)', '′', text)
    text = re.sub(r'\(cid:57\)', '′', text)
    text = re.sub(r'\(cid:5\)', '′', text)
    text = re.sub(r'\(cid:\d+\)', '°', text)
    text = text.replace('¢', '′')

    # Entferne alle anderen ASCII-Steuerzeichen mithilfe von ord()
    cleaned_text = ''.join(char for char in text if ord(char) >= 32 or ord(char) == 10)

    return cleaned_text


def find_matches(line):
    """
    Findet Koordinaten in einer gegebenen Zeile des bereinigten Textes einer PDF aus einem Ordner.
    https://www.w3schools.com/python/python_regex.asp
    https://docs.python.org/3/library/re.html#re.findall

    Args:
        line (str): Eine einzelne Textzeile, in der nach Koordinatenmustern gesucht wird.

    Returns:
        list: Eine Liste von Strings, jeder ein gefundener Koordinaten-Match.
    """

    # Alle RegEx-pattern zur Suche von verschiedenen Koordinatenformaten
    patterns = [
        # Die meisten der Pattern erlaubt es nicht, dass Koordinaten mit "." anfangen, um DOI Sucheinträge zu verhindern.
        # Himmelsrichtungen sind bei der Kategorisierung automatisch inklusive

        # ------------------- Dezimalgrad Pattern -------------------------------------------
        # Dieses Muster erkennt einfache Dezimalkoordinaten ohne Vorzeichen und ohne Himmelsrichtung
        # Beispiele: "123.456789", "32.123456"
        r'\b(?<!\.)\d{1,3}\.\d{6}\b',

        # Dieses Muster erfasst Dezimalgradangaben mit Grad-Symbol gefolgt von einer Himmelsrichtung.
        # Beispiele: "123.456° N", "32.1234°E"
        r'\b(?<!\.)(?!0\.)\d{1,3}\.\d{2,6}[°º◦]?\s*[NSEW](?!-)\b',

        # Erfasst zusammenhängende Koordinaten in Dezimalform mit möglichem negativen Vorzeichen und Himmelsrichtungen, getrennt durch Komma.
        # Beispiele: "-123.45678 N, -98.76543 E", "-23.4567 S, -45.6789 W"
        r'\b(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d+[NS],\s*(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d+[EW]\b',

        # Erfasst Koordinaten in Dezimalgrad format mit Grad-Symbol und Himmelsrichtungen, jeweils für Längen- und Breitengrad.
        # Beispiele: "123.4567°N, 89.1234°W", "45.6789°S, 23.4567°E"
        r'\b(?<!\.)(?!0\.)\d{1,3}\.\d{1,6}[°º◦][NS],\s*(?<!\.)\d{1,3}\.\d{1,6}[°º◦][EW]\b',

        # Erfasst Koordinaten innerhalb von Klammern, getrennt durch Kommas, im Dezimalformat.
        # Beispiele: "(123.456, 78.901)", "(-12.345, -67.890)", "(35.275, −111.721)"
        r'\(\s*(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d{3}\s*,\s*(?<!\.)\s*[-–−]?\s*(?!0\.)[\d−]{1,3}\.\d{3}\s*\)',

        # ------------------- NUR [°º◦] Pattern-------------------------------------------
        # Erfasst einfache Gradangaben mit einem Grad-Symbol und einer Himmelsrichtung.
        # Beispiele: "123° N", "98° W"
        r'\b(?<!\.)(?!0{1,2}\b)\d{1,3}[°º◦]\s*[NSEW]\b',

        # Erfasst Gradangaben gefolgt von einer spezifischen Null in der Zahl
        # Anmerkung: Die Nullen sind hier falsch konvertierte "°"
        # Beispiele: "123°270 N", "98°020 W"
        r'\b(?<!\.)\d{1,3}[°º◦]\d{1,3}0\s*[NSEW]\b',

        # Erfasst zwei separate Gradangaben, durch ein Trennzeichen verbunden
        # Beispiele: "123° - 45° N", "98° - 76° W"
        r'\b(?<!\.)\d{1,3}[°º◦]\s*[-–−]*\s*\d{1,3}[°º◦]\s*[NSEW]\b',

        # Erfasst Koordinaten, die dreimal wiederholte Gradangaben enthalten, gefolgt von einer Himmelsrichtung.
        # Beispiele: "123°45°67° N", "98°76°54° W"
        r'\b(?<!\.)\d{1,3}[°º◦]\d{2}[°º◦]\d{2}[°º◦]\s*[NSEW]\b',

        # ------------------- NUR [°º◦] und [ʹ′'’] Pattern-------------------------------------------
        # Erfasst Bereiche von Koordinaten in Grad und Minuten durch ein Trennzeichen verbunden, möglicherweise auch ohne spezifische Himmelsrichtungen.
        # Beispiele: "123°45' N -67°89'", "12°34' S- 56°78' E"
        r"(?<!\.)\d{1,3}[°º◦]\d{1,2}[ʹ′'’]\s*[NSEW]?\s*[-–−]\s*(?<!\.)\d{1,3}[°º◦]\d{1,2}[ʹ′'’]\s*[NSEW]?\b",

        # Erfasst Koordinaten in der Form von Grad und Minuten getrennt durch Komma mit Himmelsrichtungen.
        # Beispiele: "52° 12' N, 13°28' E", "12°34', 56 78' W"
        r"\b(?<!\.)\d{1,3}[°º◦]?\s*\d{1,3}[ʹ′'’]?\s*[NSEW],\s*\d{1,3}[°º◦]?\s*\d{1,3}[ʹ′'’]?\s*[NSEW]\b",

        # Erfasst zwei vollständige Koordinatensätze, getrennt durch ein Semikolon.
        # Beispiele: "123°045'067 N; 123°045'067 W", "12°034'056 N; 12°034'056 W"
        r'\b(?<!\.)\d{1,3}[°º◦]\s*0\d{2}\s*(?<!\.)\d{1,3}[°º◦]\s*0\d{3}\s*[NSEW];\s*(?<!\.)\d{1,3}[°º◦]\s*0\d{3}\s*(?<!\.)\d{1,3}[°º◦]\s*0\d{3}\s*[NSEW]\b',

        # Erfasst Koordinaten in vollständiger Notation mit Gradzeichen, Minuten und Sekunden, optional gefolgt von einer Himmelsrichtung.
        # Beispiele: "123°45''67' N", "98°76''54' E"
        r"\d{1,3}[º°◦]\d{1,2}[ʹ′'’][ʹ′'’]\d{1,2}[ʹ′'’]\s*[N|S|E|W]?",

        # Erfasst Koordinaten in Grad, Minuten und Sekunden, wobei die Sekunden dezimale Werte enthalten können.
        # Anmerkung: Keine Wortgrenze (\b) da Koordinaten in Tabelle
        # Beispiele: "123°45'67.89''", "98°76'54.32''"
        r"(?<!\.)\d{1,3}[°º◦]\d{1,3}[ʹ′'’]\d{1,3}\.\d{1,3}[ʹ′'’][ʹ′'’]",

        # Erfasst Koordinaten in Grad und Minuten, direkt gefolgt von einer Himmelsrichtung.
        # Beispiele: "123°456' N", "98°765' W"
        r"\b(?<!\.)(?!0\.)\d{1,3}[°º◦]\s*\d{1,3}[ʹ′'’]?\s*[NSEW]\b",

        # ------------------- [°º◦] und (?:′|\u2032|\u0027) und ″ Pattern -------------------------------------------
        # Anmerkung: Hier muss auf unicode Angaben für Symbole zurückgegriffen werden, da sonst ein konflikt mit der Pythonsyntax entsteht

        # Erfasst Koordinaten in Form von Grad, Minuten und Sekunden.
        # Beispiele: "123°45'67″ N", "12°34'56″ S"
        r'\b(?<!\.)\d{1,3}(?:[°º◦]|\u00B0)?\s*\d{1,3}(?:′|\u2032|\u0027)?\s*\d{1,3}(?:″|\u2033)?\s*[NSEW]\b',

        # Erfasst Koordinaten in Form von Grad, Minuten und Sekunden in Tabellen.
        # Anmerkung: Keine Wortgrenze (\b) da Koordinaten in Tabelle
        # Beispiele: "123°45'67"", "98°76'54"
        r'(?<!\.)\d{1,3}[°º◦]\d{2}[′’\u0027\u2032]\d{2}["”]?',

        # Erfasst zwei Koordinaten in einer Zeile, die Grad, Minuten und Sekunden in unterschiedlicher Präzision anzeigen.
        # Beispiele: "123°45'67.89″ N - 98°76'54.32″ W", "12°34'56.78″ S - 23°45'67.89″ E"
        r'\b(?<!\.)\d{1,3}(?:[°º◦]|\u00B0)?\d{1,3}(?:′|\u2032|\u0027)?(?!0\.)\d{1,3}\.\d{1,3}(?:″|\u2033)?\s*[NSEW]\s*[-–−]\s*(?<!\.)\d{1,3}(?:[°◦]|\u00B0)?\d{1,3}(?:′|\u2032|\u0027)?(?!0\.)\d{1,3}\.\d{1,3}(?:″|\u2033)?\s*[NSEW]\b',

        # Erfasst Koordinaten in Tabellen in Grad, Minuten und Sekunden, wobei die Sekunden Dezimalstellen aufweisen können.
        # Anmerkung: Keine Wortgrenze (\b) da Koordinaten in Tabelle
        # Beispiele: "123°45'67.89" N", "12°34'56.78"S"
        r'(?<!\.)\d{1,3}[°º◦]\s*\d{1,3}[′’\u0027\u2032]\d{1,3}\.\d{1,3}["”]\s*[NSEW]?',

        # ------------------- NUR [ʹ′'’] Pattern -------------------------------------------
        # Erfasst spezifische Koordinaten in Minutenangabe, auch in Tabellen.
        # Eingeführt, da "°" in PDF Text zu "0" konvertiert wurde.
        # Beispiele: "43010'", "39058'"
        r"(?<!\.)\d{1,3}0\d{1,3}[ʹ′'’]",

        # ------------------- Weitere besondere Pattern -------------------------------------------
        # Erfasst simple Angaben von Koordinatenbereichen, getrennt durch das Wort "to".
        # Beispiele: "123 to 130 N", "45 to 50 W"
        r'\b(?<!\.)\d{1,3}\s*to\s*\d{1,3}0\s*[NSEW]\b',

        # Erfasst Bereiche von Dezimalgraden, getrennt durch das Wort "to", mit abschließender Himmelsrichtung bei der jeweiligen letzteren Koordinate.
        # Beispiele: "123.456 to 789.012 N", "45.678 to 123.456 W"
        r'\b(?<!\.)\d{1,3}\.\d{1,3}\s*to\s*\d{1,3}\.\d{1,3}\s*[NSEW]\b',

        # Erfasst Bereiche von Koordinaten, getrennt durch einen Bindestrich, gefolgt von einer Himmelsrichtung.
        # Beispiele: "36–528 N", "52–988 W"
        r'\b(?<!\.)\d{1,3}[-–−]\d{1,3}\s[NSWE]\b',

        # Erfasst Koordinaten in Klammern, mit "lat" oder "long" prefix der länge 9 bis 10.
        # Anmerkung: Keine Wortgrenze (\b) da Koordinaten in Tabelle
        # Beispiele: (lat 1230230140, long 340450260)
        r'\(lat \d{9,10}, long \d{9,10}\)',

        # Erfasst sehr große Zahlwerte als Koordinaten mit nachfolgender Himmelsrichtung.
        # Anmerkung: Hier fehlen durch eine falsche konversation der PDF die Sonderzeichen wie "°" und "'"
        # Anmerkung: Keine Wortgrenze (\b) da Koordinaten in Tabelle
        # Beispiele: "123456789N", "987654321 W"
        r'(?<!\.)(?!0\.)\d{9,10}\s*[NSEW]',

        # Erfasst Koordinaten mit Himmelsrichtungen, verbunden durch ein Semikolon.
        # Anmerkung: Die Nullen sind hier falsch konvertierte "°"
        # Beispiele: "12034 56078 N; 12034 56078 E"
        r'\b(?<!\.)\d{1,3}\s*0\d{1,3}\s*\d{1,3}\s*0\d{1,3}\s*[NSEW];\s*\d{1,3}\s*0\d{1,3}\*\d{1,3}\s*0\d{1,3}\s*[NSEW]\b'
    ]

    # Alle gefundenen Koordinaten sollen in die "matches" Liste, welche hier erstellt wird
    matches = []
    # Es wird über die pattern iteriert und sobald ein pattern in einer Zeile ein Ergebnis gefunden hat, wird dieses zu "matches" hinzugefügt
    for pattern in patterns:
        matches.extend(re.findall(pattern, line))
    return matches


def find_study_site(lines):
    """
    Sucht nach den bestimmten Begriffen, welche einen relevanten Eintrag in die Spalte "Area name" der Excel Tabelle darstellen und gibt die darauffolgenden vier Zeilen zurück.
    Wichtig!: Dies wird nur ausgeführt, wenn keine Koordinaten gefunden wurden!
    https://www.w3schools.com/python/python_regex.asp
    https://docs.python.org/3/library/re.html#re.search
    https://docs.python.org/3/library/re.html#re.IGNORECASE

     Args:
        lines (list): Eine Liste von Textzeilen, in der nach Schlüsselwörtern für den Bereich einer Studie gesucht wird.

    Returns:
        str or None: Ein String, der den Kontext der gefundenen Bereiche einer Studie enthält, oder None, falls keine gefunden wurden.
    """

    # Iteriert über alle Zeilen des Textes einer PDf, falls ein Schlüsselwort gefunden wurde, wird diese Zeile
    # und die darauffolgenden 2 Zeilen gespeichert und zu den Zeilen, welche Aufschluss über das gesuchte Gebiet geben angehangen.
    for i, line in enumerate(lines):
        # Überprüfung auf alle gesuchten Schlüsselwörter, groß- und kleinschreibung wird hierbei ignoriert
        if (re.search(r'\bData Sources and Location\b', line, re.IGNORECASE)
                or re.search(r'\bstudy area\b', line, re.IGNORECASE)
                or re.search(r'\bstudy  area\b', line, re.IGNORECASE)
                or re.search(r'\bThe area of\b', line, re.IGNORECASE)
                or re.search(r'\bforest areas\b', line, re.IGNORECASE)
                or re.search(r'\bstudy site\b', line, re.IGNORECASE)
                or re.search(r'\bstudy sites\b', line, re.IGNORECASE)
                or re.search(r'\bS T U D Y S I T E\b', line, re.IGNORECASE)

                # Falls "study site" durch einen Zeilenumbruch getrennt ist
                or (line.strip().endswith("study") and (i + 1 < len(lines)) and lines[i + 1].strip().startswith(
                    "site"))

                or re.search(r'\bcompared three sites\b', line, re.IGNORECASE)
                or re.search(r'\bstudy region\b', line, re.IGNORECASE)
                or re.search(r'\bBioregional  description\b', line, re.IGNORECASE)
                or re.search(r'\bStudy landscapes\b', line, re.IGNORECASE)
                or re.search(r'\bsite description\b', line, re.IGNORECASE)
                or re.search(r'\bStudy system\b', line, re.IGNORECASE)

        ):
            # Kontextzeilen (also die Zeile, in welcher der Fund ist und die darauffolgenden 4) speichern
            context_lines = lines[i:i + 4]
            return " | ".join(context_lines).strip()
    return None


def find_forest_types(lines):
    """
    DISCLAIMER: Nicht zu 100% zuverlässig
    Sucht nach bestimmten Begriffen, die auf Waldtypen hinweisen, und gibt die relevanten Zeilen zurück.
    https://www.w3schools.com/python/python_regex.asp
    https://docs.python.org/3/library/re.html#re.search
    https://docs.python.org/3/library/re.html#re.IGNORECASE

    Args:
        lines (list): Eine Liste von Textzeilen, in der nach Schlüsselwörtern für Waldtypen gesucht wird.

    Returns:
        str or None: Ein String, der den Kontext der gefundenen Waldtypen enthält, oder None, falls keine gefunden wurden.
    """
    # Iteriert über alle Zeilen des Textes einer PDf, falls ein Schlüsselwort gefunden wurde, wird diese Zeile
    # und die darauffolgenden 3 Zeilen gespeichert und zu den Zeilen, welche Aufschluss über die untersuchte Waldart geben angehangen.
    for i, line in enumerate(lines):
        # Überprüfung auf alle gesuchten Schlüsselwörter, groß- und kleinschreibung wird hierbei ignoriert
        if (re.search(r'\bSpecies studied\b', line, re.IGNORECASE)
                or re.search(r'\bforest type\b', line, re.IGNORECASE)
                or re.search(r'\bforest types\b', line, re.IGNORECASE)
        # Weitere hinzufügen und generell verlässlicher machen
        ):
            # Kontextzeilen (also die Zeile, in welcher der Fund ist und die darauffolgenden 4) speichern
            ecosystem_context_lines = lines[i:i + 4]
            return " | ".join(ecosystem_context_lines).strip()
    return None


def find_analyzed_years(lines):
    """
    Extrahiert untersuchte Zeiträume aus den gegebenen Textzeilen.
    https://www.w3schools.com/python/python_regex.asp
    https://docs.python.org/3/library/re.html#re.search
    https://docs.python.org/3/library/re.html#re.IGNORECASE

    Args:
        lines (list of str): Zeilen von Text aus dem PDF-Dokument.

    Returns:
        str oder None: Sortierte Liste der extrahierten Zeiträume, falls gefunden, sonst None.
    """
    # Definiere reguläre Ausdrücke für die Erfassung von Zeiträumen
    time_period_patterns = [
        # Erfasst Muster wie '1980-1990' mit drei verschiedenen Bindestrichen
        r'\b(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\b',

        # Erfasst Muster wie '(1980-1990)' mit drei verschiedenen Bindestrichen
        r'\((19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\)',

        # Erfasst 'from 1980 to 1990'
        r'from (19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) to (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',

        # Erfasst 'between 1980 and 1990'
        r'between (19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) and (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',

        # Erfasst '1980s'
        r'\b(19|20)\d{2}s\b',

        # Erfasst Muster wie '1980-85'
        r'\b(19|20\d{2})\s*[-–−]\s*(\d{2})\b',

        # Erfasst 'over a 180-day period'
        r'over a (\d+)-day period'
    ]

    # Liste zum Speichern der gefundenen Zeiträume
    found_periods = []

    # Iteriere durch jede Zeile und suche nach Zeitraum-Mustern
    for line in lines:
        for pattern in time_period_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2 and len(match[1]) == 2:
                        # Jahr-Jahr-Muster wie '1980-85'
                        period = f"{match[0]}-{match[0][:2]}{match[1]}"
                    else:
                        # Standard-Zeitraum-Muster wie '1980-1990'
                        period = f"{match[0]}-{match[2]}"
                else:
                    period = match

                # Überprüfe, ob das gefundene Muster gültig ist (vermeide Einträge wie '19-1926', '19', '20')
                if re.match(r'^(19|20)\d{2}[-–−](19|20)\d{2}$', period) or re.match(r'^(19|20)\d{2}s$',
                                                                                    period) or re.match(
                        r'^over a \d+-day period$', period):
                    if period not in found_periods:
                        found_periods.append(period)

    return sorted(found_periods)


def find_years_with_drought(lines):
    """
    DISCLAIMER: Nicht zu 100% zuverlässig
    Diese Funktion extrahiert die Jahre und Zeitspannen von Dürreperioden aus den gegebenen Textzeilen.
    https://www.w3schools.com/python/ref_func_isinstance.asp
    https://docs.python.org/3/library/re.html#re.IGNORECASE
    https://docs.python.org/3/library/re.html#re.compile
    https://docs.python.org/3/library/re.html#re.findall

    Args:
        lines (list of str): Zeilen von Text aus dem PDF-Dokument.

    Returns:
        list: Sortierte Liste der extrahierten Zeiträume oder Jahre, in denen Dürre vorkam, falls gefunden, sonst eine leere Liste.
    """
    # Definiere reguläre Ausdrücke für die Erfassung von Zeiträumen
    drought_years_patterns = [
        # Erfasst Muster wie '1980-1990' mit drei verschiedenen Bindestrichen
        r'\b(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\b',

        # Erfasst Muster wie '(1980-1990)' mit drei verschiedenen Bindestrichen
        r'\((19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\)',

        # Erfasst 'from 1980 to 1990'
        r'from (19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) to (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',

        # Erfasst 'between 1980 and 1990'
        r'between (19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) and (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',

        # Erfasst '1980s'
        r'\b(19|20)\d{2}s\b',

        # Erfasst Muster wie '1980-85'
        r'\b(19|20\d{2})\s*[-–−]\s*(\d{2})\b',

        # Erfasst alle Zahlen von 1900 bis 1999
        r'\b(19\d{2})(?!\))\b'
        
        # Erfasst alle Zahlen von 1900 bis 2024
        r'\b20(0[0-9]|1[0-9]|2[0-4])(?!\))\b'

        # Erfasst 'over a 180-day period'
        r'over a (\d+)-day period'
    ]

    # Definiere ein Muster für das Schlüsselwort "drought"
    drought_pattern = re.compile(r'\bdrought\b', re.IGNORECASE)

    # Liste zum Speichern der gefundenen Zeiträume
    drought_years = []

    # Iteriere durch jede Zeile und suche nach Zeitraum-Mustern
    for line in lines:
        # Überprüfe, ob das Wort "drought" in der Zeile vorhanden ist
        if drought_pattern.search(line):
            for pattern in drought_years_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) == 2 and len(match[1]) == 2:
                            # Jahr-Jahr-Muster wie '1980-85'
                            period = f"{match[0]}-{match[0][:2]}{match[1]}"
                        else:
                            # Standard-Zeitraum-Muster wie '1980-1990'
                            period = f"{match[0]}-{match[2]}"
                    else:
                        period = match

                    # Überprüfe, ob das gefundene Muster gültig ist
                    if re.match(r'^(19|20)\d{2}[-–−](19|20)\d{2}$', period) or re.match(r'^(19|20)\d{2}s$', period) or re.match(r'^over a \d+-day period$', period):
                        if period not in drought_years:
                            drought_years.append(period)

    return sorted(drought_years)

def find_study_type(lines, pdf_file):
    """
    DISCLAIMER: Nicht zu 100% zuverlässig
    Diese Funktion durchsucht die Zeilen eines Textes nach Schlüsselwörtern,
    die auf verschiedene Studientypen hinweisen, und gibt den Studientyp zurück,
    der die höchste Häufigkeit von Stichwörtern aufweist.
    https://stackoverflow.com/questions/52862907/checking-if-a-value-in-a-python-dictionary-is-below-a-threshold-in-order-to-incr
    https://docs.python.org/3/library/re.html#re.compile
    https://docs.python.org/3/library/re.html#re.escape
    https://docs.python.org/3/library/re.html#re.IGNORECASE

    Args:
        lines (list): Eine Liste von Textzeilen, in der nach Schlüsselwörtern für den Studientyp gesucht wird.
        pdf_file (str): Der Name der PDF-Datei (zur Dokumentation).

    Returns:
        str: Der Studientyp, der den höchsten Score aufweist oder 'Unknown', wenn keiner eindeutig dominiert.
    """

    study_types = {
        'observational': ['field campaigns','field campaign', 'observational', 'observed', 'field study', 'observation', 'monitoring', 'survey', 'data collection',
                          'cohort study', 'case-control study', 'epidemiological study', 'prospective study', 'retrospective study',
                          'ecological study', 'correlational study'],
        'experimental': ['experimental', 'experimentally', 'experiment', 'treatment', 'controlled', 'variable', 'manipulation',
                         'randomized controlled trial', 'placebo-controlled', 'clinical trial', 'randomized', 'intervention',
                         'controlled study', 'experimental design', 'field experiment', 'laboratory experiment'],
        'modeling': ['model', 'modeling', 'simulation', 'algorithm', 'predictive', 'statistical model', 'computational model',
                     'modeling approach', 'scenario analysis', 'projection', 'machine learning', 'data-driven model',
                     'predictive analytics', 'Monte Carlo', 'agent-based model', 'dynamic model']
    }

    # Erstelle reguläre Ausdrücke für die Stichwörter jedes Studientyps
    study_type_pattern = {key: re.compile(r'\b(?:' + '|'.join(map(re.escape, terms)) + r')\b', re.IGNORECASE)
                          for key, terms in study_types.items()}

    # Zähle die Vorkommen der Stichwörter in den Zeilen des Textes
    scores = {key: 0 for key in study_types}
    for line in lines:
        for study_type, pattern in study_type_pattern.items():
            scores[study_type] += len(pattern.findall(line))

    # Bestimme die Kategorie mit dem höchsten Score
    best_fit_study_type = max(scores, key=scores.get)
    max_score = scores[best_fit_study_type]

    # Bestimme den zweithöchsten Score
    second_best_fit_study_type = sorted(scores, key=scores.get, reverse=True)[1]
    second_max_score = scores[second_best_fit_study_type]

    if max_score == 0 or max_score == second_max_score:
        return 'Unknown'

    return best_fit_study_type

""" Alte find_study_type Funktion mit defaultdict als Kriterium
def find_study_type(lines, pdf_file, threshold=10):
    DISCLAIMER: Alter Ansatz mit defaultdict als Gewichtung
    Diese Funktion durchsucht die Zeilen eines Textes nach Schlüsselwörtern,
    die auf verschiedene Studientypen hinweisen, und gibt eine Liste aller
    gefundenen Studientypen zurück, die eine bestimmte Häufigkeit überschreiten.
    https://stackoverflow.com/questions/52862907/checking-if-a-value-in-a-python-dictionary-is-below-a-threshold-in-order-to-incr
    https://docs.python.org/3/library/re.html#re.compile
    https://docs.python.org/3/library/re.html#re.escape
    https://docs.python.org/3/library/re.html#re.IGNORECASE

    Args:
        lines (list): Eine Liste von Textzeilen, in der nach Schlüsselwörtern für den Studientyp gesucht wird
        pdf_file (str): Der Name der PDF-Datei (zur Dokumentation).
        threshold (int): Der Schwellenwert für die Häufigkeit von Stichwörtern, um eine Kategorie zuzuordnen.

    Returns:
        list of str: Eine Liste der gefundenen Studientypen, die den angegebenen Schwellenwert überschreiten.
    

    study_types = {
        'observational': ['observational', 'observed', 'field study', 'observation', 'monitoring', 'survey', 'data collection'],
        'experimental': ['experimental', 'experimentally', 'experiment', 'treatment', 'controlled', 'variable', 'manipulation'],
        'modeling': ['model', 'modeling', 'simulation', 'algorithm', 'predictive']
    }

    # Erstelle eine Liste aller Stichwörter zum Suchen
    search_terms = [term for sublist in study_types.values() for term in sublist]
    
    # Kombiniere die Stichwörter zu einem einzigen regulären Ausdruck
    study_type_pattern = {key: re.compile(r'\b(?:' + '|'.join(map(re.escape, terms)) + r')\b', re.IGNORECASE)
                    for key, terms in study_types.items()}

    # Zähle die Vorkommen der Stichwörter in den Zeilen des Textes
    scores = defaultdict(int)
    for line in lines:
        for study_type, pattern in study_type_pattern.items():
            scores[study_type] += len(pattern.findall(line))

    # Bestimme die Kategorien, deren Scores über dem Schwellenwert liegen
    relevant_categories = [category for category, score in scores.items() if score >= threshold]

    return relevant_categories
"""
def find_drought_quantification(lines, pdf_file):
    """
    Sucht nach bestimmten Begriffen, die sich auf die Quantifizierung von Dürren beziehen, und gibt die relevanten Zeilen zurück.
    Hierbei wird in jeder PDF ein mal nach jedem Begriff gesucht und dann, wenn er ein- oder keinmal vorgekommen ist, wird der nächste Begriff gesucht usw....
    https://www.w3schools.com/python/python_regex.asp

    Args:
        lines (list): Eine Liste von Textzeilen, in der nach Schlüsselwörtern für die quantifizierung von Dürre gesucht wird
        pdf_file (str): Der Dateiname der PDF, aus der die Zeilen stammen.

    Returns:
        tuple: Ein Tupel, das entweder (str, list) enthält, wobei der String die zusammengefassten relevanten Zeilen und die Liste die gefundenen Schlüsselwörter enthält, oder (None, None), falls keine relevanten Informationen gefunden wurden.
    """

    # Die zu suchenden Begriffe werden in dieser Liste gespeichert:
    keywords = ['PET', 'SPI', 'SPEI', 'PDSI', 'low soil moisture', 'soil water content', 'VPD', 'reduced rainfall', 'low precipitation', 'plant water stress', 'drought', 'dry season', 'dry period']
    # Diese Liste soll später alle relevanten Zeilen, also diese wo ein Keyword drin steckt plus 3 Zeilen danach speichern
    drought_lines = []
    # Diese Liste speichert alle gefundenen Begriffe einer PDF aus der "keywords" Liste
    drought_quantification_keywords = []

    # Hier wird jede Zeile einer PDF nach den Begriffen in der "keywords" Liste durchsucht
    for keyword in keywords:
        for i, line in enumerate(lines):
            # re.escape um sicherzustellen, dass alle Sonderzeichen als Literale behandelt werden und keine Regex-Metazeichen
            if re.search(r'\b' + re.escape(keyword) + r'\b', line):
                # Wurde ein Begriff gefunden, wird er zu "drought_quantification_keywords" hinzugefügt
                drought_quantification_keywords.append(keyword)
                # und die Zeile, in welche der Begriff gefunden wurde und die darauffolgenden drei werden gespeichert
                context_lines = lines[max(0, i - 1):i + 3]
                drought_lines.append(" | ".join(context_lines).strip())
                break

    if drought_lines:
        # Die relevanten Zeilen werden zu einem einzigen String zusammengefügt, wobei jede Zeile durch " | " getrennt ist.
        # Dabei entfernt `.strip()` alle überflüssigen Leerzeichen
        # "drought_quantification_keywords" wird außerdem ebenfalls zurückgegeben, die alle Keywords enthält, die in der PDF gefunden wurden.
        return " | ".join(drought_lines).strip(), drought_quantification_keywords
        # Wenn keine relevante Zeile in der PDF gefunden wurde (d.h., "drought_lines" ist leer),
        # gibt die Funktion ein Tupel zurück, das zwei "None" Werte enthält.
    return None, None

def extract_coordinates_from_pdfs_in_folder(folder_path):
    """
    Diese Funktion extrahiert Koordinaten aus PDF-Dateien in einem spezifizierten Ordner.
    Duplikate und einzelne, isolierte Koordinaten werden dabei ignoriert.
    https://docs.python.org/3/library/os.html#os.listdir
    https://docs.python.org/3/library/os.path.html#module-os.path
    https://www.w3schools.com/python/python_regex.asp
    https://docs.python.org/3/library/re.html#re.split
    https://docs.python.org/3/library/re.html#re.match

    Args:
        folder_path (str): Pfad zum Ordner, der die PDF-Dateien enthält.

    Returns:
        list: Eine Liste von Tupel wobei jedes Tupel die extrahierten Informationen einer PDF-Datei enthält, einschließlich des Dateinamens, gefundenen Koordinaten, Kontextzeilen und Informationen zur Dürre-Quantifizierung.
    """

    # Initialisiere die Liste für die Ergebnisse der automatischen Koordinatenextraktion
    results = []

    # Muster, die für die Identifikation von Koordinatenformate verwendet werden, welche, wenn sie alleine auftreten ignoriert werden sollen
    decimal_pattern = r'\b(?<!\.)\d{1,3}\.\d{6}\b'
    decimal_dir_pattern = r'\b(?!0\.)\d{1,3}\.\d{2}\s*[NSEW]\b'
    number_dir_pattern = r'\b(?!0\.)\d{1,6}(?<!\d8\d{2}0)\s*[NSEW]\b'
    number_dir_pattern_range = r'\b(?!0\.)\d{3}–\d{3}[NSEW]\b'

    # Durchsuche alle Dateien im angegebenen Ordner
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_file = os.path.join(folder_path, filename)
            pdf_basename = os.path.splitext(os.path.basename(pdf_file))[0]
            try:
                # Extrahiere den Text aus der PDF-Datei mithilfe von pdfminer
                text = extract_text(pdf_file)
                # Bereinige den Text von diversen Sonderzeichen durch die Hilfsfunktion clean_and_remove_control_characters()
                cleaned_text = clean_and_remove_control_characters(text)

                # Set zur Speicherung aller gefundenen Koordinaten
                coordinates = set()
                # Liste zur Speicherung der Kontextzeilen, in denen Koordinaten gefunden wurden
                lines_with_coordinates = []
                # Teile den bereinigten Text in Zeilen auf
                lines = re.split('\n+', cleaned_text)

                # Sets zur Verwaltung gefundener einzelner Koordinaten zum Ignorieren je nach Muster
                all_found_types = {decimal_pattern: set(), decimal_dir_pattern: set(), number_dir_pattern: set(), number_dir_pattern_range: set()}
                # Liste zur Speicherung von ignorierten Koordinaten
                ignored_coordinates = []

                # Durchsuche jede Zeile des bereinigten PDF-Textes nach Koordinaten, sowohl den richtigen, als die zu ignorierenden
                for line in lines:
                    matches = find_matches(line)
                    if matches:
                        for match in matches:
                            coordinates.add(match)
                            for pattern in [decimal_pattern, decimal_dir_pattern, number_dir_pattern, number_dir_pattern_range]:
                                if re.match(pattern, match):
                                    all_found_types[pattern].add(match)

                # Überprüfen, ob gefundene Koordinaten Duplikate oder Teil von anderen Koordinaten sind
                final_coordinates = set()
                for coord in coordinates:
                    include = True
                    for other_coord in coordinates:
                        if coord != other_coord and coord in other_coord:
                            include = False
                            break
                    if include:
                        final_coordinates.add(coord)

                # Ignoriere einzelne Koordinaten der gegebenen Muster, wenn sie die einzigen ihrer Art sind
                for pattern, coord_set in all_found_types.items():
                    if len(coord_set) == 1:
                        coord_to_ignore = next(iter(coord_set))
                        if coord_to_ignore in final_coordinates:
                            final_coordinates.remove(coord_to_ignore)
                            ignored_coordinates.append(coord_to_ignore)
                            # Logging Ausgabe, wenn und welche einzelne Koordinate ignoriert wurden und in welcher PDF
                            logging.info(
                                f"Ignored single coordinate {coord_to_ignore} in '{pdf_basename}' as per pattern.")

                # Speichere Kontextzeilen nur für die gültigen Koordinaten
                for line in lines:
                    line_matches = find_matches(line)
                    valid_matches = [match for match in line_matches if match in final_coordinates]
                    if valid_matches:
                        context_lines = lines[max(0, lines.index(line) - 2):lines.index(line) + 1]
                        lines_with_coordinates.append(" | ".join(context_lines).strip())

                # Ergebnis verarbeiten und speichern
                process_extraction_results(pdf_basename, final_coordinates, lines_with_coordinates, lines, pdf_file, results)

            # Absicherungslogging, falls es einen Fehler gab, der verhindert, dass in den PDFs nach Informationen gesucht werden kann
            except Exception as e:
                logging.error(f"Failed to extract text from '{pdf_file}': {str(e)}")
                results.append((pdf_basename, 'Keine Koordinaten gefunden', '', None, None))

    return results

def logging_extraction_results(pdf_basename, coordinates, study_site_lines, study_site_context, drought_quantified, study_type, forest_type, analyzed_years, drought_years):
    """
    Diese Funktion protokolliert die Ergebnisse der Extraktion in einer sinnvollen Reihenfolge übersichtlich und loggt sie entsprechend.

    Args:
        pdf_basename (str): Der bereinigte Dateiname der PDF.
        coordinates (str): Gefundene Koordinaten oder 'Keine Koordinaten gefunden'.
        study_site_lines (str): Gefundene Studienregion basierend auf Kontextzeilen oder 'Keine Studienregion gefunden'.
        study_site_context (str): Gefundene Studienregion basierend auf dem Kontext oder 'Keine Studienregion gefunden'.
        drought_quantified (list): Eine Liste der gefundenen Schlüsselwörter zur Dürre-Quantifizierung.
        study_type (str): Der Studientyp, falls gefunden, sonst None.
        forest_type (str): Die Waldart bzw. Baumart, falls gefunden, sonst None
        analyzed_years (str): Die untersuchten Jahre, falls gefunden, sonst None
        drought_years (str): Die Jahre mit Dürre, falls gefunden, sonst None

    Returns:
        None
    """
    # Logging des Artikelnamens um sicherzugehen um welchen wissenschaftlichen Artikel es sich handelt
    logging.info(f"Processing '{pdf_basename}:'")

    # Logging ob und wenn ja welche Koordinaten gefunden wurden
    if coordinates != 'Keine Koordinaten gefunden':
        logging.info(f"Coordinates found: '{coordinates}'")
    else:
        logging.info(f"No coordinates found/given")

    # Logging von entweder den gefundenen Studienregionen basierend auf Kontextzeilen oder den durch die Funktion "find_study_site" gefunden Zeilen
    if study_site_lines != 'Keine Studienregion gefunden':
        logging.info(f"Study site found: '{study_site_lines}'")
    elif study_site_context != 'Keine Studienregion gefunden':
        logging.info(f"Study site found: '{study_site_context}'")
    else:
        logging.info(f"No study site found/given")

    # Logging ob und wie Dürre definiert wurde
    if drought_quantified:
        logging.info(f"Drought quantified via: '{', '.join(drought_quantified)}'")
    else:
        logging.info(f"No drought quantification found/given")

    # Logging ob und wenn welchen Studientypen ein Artikel hat
    if study_type:
        logging.info(f"Study type: '{study_type}'")
    else:
        logging.info(f"No study type found/given")

    # Logging ob und wenn mit welcher Waldart bzw Baumart ein Artikel sich beschäftigt
    if forest_type:
        logging.info(f"Forest type: '{forest_type}'")
    else:
        logging.info(f"No forest type found/given")

    # Logging ob und wenn mit welchen Jahren sich ein Artikel beschäftigt hat
    if analyzed_years:
        logging.info(f"Analyzed years: '{analyzed_years}'")
    else:
        logging.info(f"No Analyzed years specified")

    # Logging ob und wenn welche Jahre mit dem Zustand Dürre quantifiziert wurden
    if drought_years:
        logging.info(f"Years were drought was quantified: '{drought_years}'")
    else:
        logging.info(f"No drought years found/given")

    #Logging einer Leerzeile zur Trennung zweier PDFs für einen besseren Überblick
    logging.info("")

def process_extraction_results(pdf_basename, final_coordinates, lines_with_coordinates, lines, pdf_file, results):
    """
    Verarbeitet die extrahierten Ergebnisse und speichert sie in der Ergebnisliste.
    Erleichtert das Hinzufügen von weiteren extrahierten Informationen deutlich

    Args:
        pdf_basename (str): Basisname der PDF-Datei für "Paper".
        final_coordinates (set): Menge der endgültigen Koordinaten ohne Duplikate für "location coordinates".
        lines_with_coordinates (list): Liste der Kontextzeilen der Koordinaten für "Area Name".
        lines (list): Liste aller Zeilen im bereinigten Text zum Durchsuchen.
        pdf_file (str): Pfad zu den einzelnen PDF-Dateien.
        results (list): Liste zur Speicherung der Ergebnisse um diese mit Excel weiterzuverarbeiten.

    Returns:
        list: Aktualisierte Ergebnisliste mit den extrahierten Informationen aus der PDF-Datei.
    """
    # Ausführen der Hilfsfunktion zum Herausfinden, wie Dürre definiert wurde
    drought_quantified, drought_quantification_keywords = find_drought_quantification(lines, pdf_file)

    #TO-DO: Die 2 neuen Werte mit Hilfsfunktionen extrahieren und zu result.append hinzufügen sowie in main.py zur print überprüfung
    #years_with_drought = find_years_with_drought(lines)
    #analyzed_years = find_analyzed_years(lines)

    # Ausführen der Hilfsfunktion zum Herausfinden des Studientyps
    study_type = find_study_type(lines, pdf_file)

    # Ausführen der Hilfsfunktion zum Herausfinden der Waldtypen
    forest_type = find_forest_types(lines)

    # Ausführen der Hilfsfunktion zum Herausfinden der erforschten Jahre
    analyzed_years = find_analyzed_years(lines)

    # Ausführen der Hilfsfunktion zum Herausfinden der Jahre mit Dürre
    drought_years = find_years_with_drought(lines)

    # Überprüfen, ob Koordinaten und oder Study Areas gefunden wurden
    coordinates_found = bool(final_coordinates)
    study_site_lines_found  = bool(lines_with_coordinates)

    # Wenn gültige Koordinaten gefunden wurden, werden diese als String zusammengefügt,
    # andernfalls wird 'Keine Koordinaten gefunden' gesetzt, um fürs logging zu vergleichen.
    coordinates_str = ', '.join(final_coordinates) if coordinates_found else 'Keine Koordinaten gefunden'
    # Wenn Kontextzeilen mit Koordinaten gefunden wurden, werden diese als String zusammengefügt,
    # andernfalls wird 'Keine Studienregion gefunden' gesetzt, um fürs logging zu vergleichen.
    study_site_lines_str = '; '.join(
        lines_with_coordinates) if study_site_lines_found else 'Keine Studienregion gefunden'

    # Aufrufen der Hilfsfunktion "find_study_site(lines)" um die Study Area zu finden
    study_site_context = find_study_site(lines)
    study_site_context_str = remove_illegal_characters(
        study_site_context) if study_site_context else 'Keine Studienregion gefunden'

    # Loggt die Ergebnisse der Extraktion mithilfe der logging_extraction_results() Funktion
    logging_extraction_results(pdf_basename, coordinates_str, study_site_lines_str, study_site_context_str,
                               drought_quantification_keywords, study_type, forest_type, analyzed_years, drought_years)

    # Speichere die Ergebnisse bei gefundenen validen Koordinaten (Name des Papers, die validen Koordinaten, die Kontextzeilen von gefundenen Koordinaten und wie Dürre definiert wurde)
    if final_coordinates:
        results.append((pdf_basename, ', '.join(final_coordinates), '; '.join(lines_with_coordinates), drought_quantified, drought_quantification_keywords, study_type, forest_type, analyzed_years, drought_years))
    # Speichere die Ergebnisse, wenn keine validen Koordinaten gefunden wurden
    else:
        # Aufrufen der Hilfsfunktion "find_study_site(lines)" um die Bereiche der Studien zu finden, in welcher sie durchgeführt wurden
        study_site_context = find_study_site(lines)
        # Wenn etwas von der Hilfsfunktion "find_study_site(lines)" gefunden wurde, wird das Ergebnis
        # so bereinigt, dass es mit openpyxl weiterverarbeitet werden kann und die Ergebnisse gespeichert.
        if study_site_context:
            cleaned_lines_with_coordinates = remove_illegal_characters(study_site_context)
            results.append((pdf_basename, 'Keine Koordinaten gefunden', cleaned_lines_with_coordinates, drought_quantified, drought_quantification_keywords, study_type, forest_type, analyzed_years, drought_years))
        # Wenn nichts von der Hilfsfunktion "find_study_site(lines)" gefunden wurde, wird dies als Ergebnis festgehalten und als Logging Information ausgegeben
        else:
            results.append((pdf_basename, 'Keine Koordinaten gefunden', '', drought_quantified, drought_quantification_keywords, study_type, forest_type, analyzed_years, drought_years))