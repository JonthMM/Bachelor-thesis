# 'os' for data management (importing files)
import os

# 'Regex' for implementing the search patterns (pattern)
import re

# PDFMiner to extract the texts from the PDFs
from pdfminer.high_level import extract_text

# 'time' to make the logging overview more clear
import time

# defaultdict for weighting of values
# from collections import defaultdict

# Logging for a better understanding of the results and outputs as set up in the main module
# Logging.info() and logging.error() are used here
# https://docs.python.org/3/library/logging.html#logging.INFO
# https://docs.python.org/3/library/logging.html#logging.error
import logging


def clean_and_remove_control_characters(text):
    """
    Removes all ASCII control characters that are not supported by Openpyxl and interfere with the format,
    replaces '(cid:6)', '(cid:57\)' and '¢' with “′” and other '(cid:\d+)' with '°' using the re.sub() function,
    to bypass special characters already known (by the helper script 'find_special_characters').

    Args:
        text (str): The string from which control characters and certain other characters are to be removed.

    Returns:
        str: The cleaned text as string

    References:
        - Python RegEx in general: https://www.w3schools.com/python/python_regex.asp
        - 're.sub()': https://docs.python.org/3/library/re.html#re.sub
        - Filtering strings: https://blog.finxter.com/5-best-ways-to-filter-strings-within-ascii-range-in-python/ (Method 5)
    """

    # Replace '(cid:6)', '(cid:57)' and '¢' with "′" as well as all other special 'cid' characters with '°'
    text = re.sub(r'\(cid:6\)', '′', text)
    text = re.sub(r'\(cid:57\)', '′', text)
    text = re.sub(r'\(cid:5\)', '′', text)
    text = re.sub(r'\(cid:\d+\)', '°', text)
    text = text.replace('¢', '′')

    # Remove all unwanted ASCII control characters using ord() to get their ASCII numbers and joining the cleaned text
    cleaned_text = ''.join(char for char in text if ord(char) >= 32 or ord(char) == 10)

    return cleaned_text

def find_matches(line):
    """
    Finds coordinates which are given as regex patterns in lines of the cleaned text from a PDF file.


    Args:
        line (str): A single line of (cleaned) text in which coordinate patterns are searched for.

    Returns:
        list: A list of strings, each containing a found coordinate match.

    References:
        - Python RegEx in general: https://www.w3schools.com/python/python_regex.asp
        - 're.findall()': https://docs.python.org/3/library/re.html#re.findall

    """

    # All RegEx patterns for searching different coordinate formats
    patterns = [
        # Most of the patterns do not allow coordinates to start with “.” to prevent DOI search entries.
        # Cardinal points are automatically included in the categorization

        # ------------------- Decimal degree pattern -------------------------------------------
        # Captures simple decimal coordinates without sign and without cardinal direction
        # Examples: '123.456789', '32.123456'
        r'\b(?<!\.)\d{1,3}\.\d{6}\b',

        # Captures decimal degrees with a degree symbol followed by a cardinal point.
        # Examples: '123.456° N', '32.1234°E'
        r'\b(?<!\.)(?!0\.)\d{1,3}\.\d{2,6}[°º◦]?\s*[NSEW](?!-)\b',

        # Captures contiguous coordinates in decimal form with a possible negative sign and cardinal points, separated by commas.
        # Examples: '-123.45678 N, -98.76543 E', '-23.4567 S, -45.6789 W'
        r'\b(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d+[NS],\s*(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d+[EW]\b',

        # Captures coordinates in decimal degree format with degree symbol and cardinal points, each for longitude and latitude.
        # Examples: '123.4567°N, 89.1234°W', '45.6789°S, 23.4567°E'
        r'\b(?<!\.)(?!0\.)\d{1,3}\.\d{1,6}[°º◦][NS],\s*(?<!\.)\d{1,3}\.\d{1,6}[°º◦][EW]\b',

        # Captures coordinates within brackets, separated by commas, in decimal format.
        # Examples: '(123.456, 78.901)', ‘(-12.345, -67.890)’, '(35.275, -111.721)'
        r'\(\s*(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d{3}\s*,\s*(?<!\.)\s*[-–−]?\s*(?!0\.)[\d−]{1,3}\.\d{3}\s*\)',

        # ------------------- Only [°º◦] pattern-------------------------------------------
        # Captures simple degrees with a degree symbol and a cardinal point.
        # Examples: '123° N”, '98° W'
        r'\b(?<!\.)(?!0{1,2}\b)\d{1,3}[°º◦]\s*[NSEW]\b',

        # Captures degrees followed by a specific zero in the number
        # Note: The zeros here are incorrectly converted “°”
        # Examples: '123°270 N', '98°020 W'
        r'\b(?<!\.)\d{1,3}[°º◦]\d{1,3}0\s*[NSEW]\b',

        # Captures two separate degrees, connected by a separator
        # Examples: '123° - 45° N', '98° - 76° W', '78.5°−82.5°E', '123° - 45° N'
        # r'\b(?<!\.)\d{1,3}[°º◦]\s*[-–−]*\s*\d{1,3}[°º◦]\s*[NSEW]\b',
        r'\b(?<!\.)\d{1,3}(?:\.\d+)?[°º◦]\s*[-–−]*\s*\d{1,3}(?:\.\d+)?[°º◦]\s*[NSEW]\b',

        # Captures coordinates that contain three repeated degrees followed by a cardinal point.
        # Examples: '123°45°67° N', '98°76°54° W'
        r'\b(?<!\.)\d{1,3}[°º◦]\d{2}[°º◦]\d{2}[°º◦]\s*[NSEW]\b',

        # ------------------- Only [°º◦] and [ʹ′'’] pattern-------------------------------------------
        # Captures ranges of coordinates in degrees and minutes connected by a separator, possibly without specific cardinal points.
        # Examples: "123°45' N -67°89'", "12°34' S- 56°78' E"
        r"(?<!\.)\d{1,3}[°º◦]\d{1,2}[ʹ′'’]\s*[NSEW]?\s*[-–−]\s*(?<!\.)\d{1,3}[°º◦]\d{1,2}[ʹ′'’]\s*[NSEW]?\b",

        # Captures coordinates in the form of degrees and minutes separated by commas with cardinal points.
        # Examples: "52° 12' N, 13°28' E", "12°34', 56 78' W"
        r"\b(?<!\.)\d{1,3}[°º◦]?\s*\d{1,3}[ʹ′'’]?\s*[NSEW],\s*\d{1,3}[°º◦]?\s*\d{1,3}[ʹ′'’]?\s*[NSEW]\b",

        # Captures two complete sets of coordinates, separated by a semicolon.
        # Examples: "123°045'067 N; 123°045'067 W", "12°034'056 N; 12°034'056 W"
        r'\b(?<!\.)\d{1,3}[°º◦]\s*0\d{2}\s*(?<!\.)\d{1,3}[°º◦]\s*0\d{3}\s*[NSEW];\s*(?<!\.)\d{1,3}[°º◦]\s*0\d{3}\s*(?<!\.)\d{1,3}[°º◦]\s*0\d{3}\s*[NSEW]\b',

        # Captures coordinates in full notation with degree signs, minutes and seconds, optionally followed by a cardinal point.
        # Examples: "123°45''67' N", "98°76''54' E"
        r"\d{1,3}[º°◦]\d{1,2}[ʹ′'’][ʹ′'’]\d{1,2}[ʹ′'’]\s*[N|S|E|W]?",

        # Captures coordinates in degrees, minutes and seconds, whereby the seconds can contain decimal values.
        # Note: No word boundary (\b) as coordinates in table
        # Examples: "123°45'67.89''", "98°76'54.32''"
        r"(?<!\.)\d{1,3}[°º◦]\d{1,3}[ʹ′'’]\d{1,3}\.\d{1,3}[ʹ′'’][ʹ′'’]",

        # Captures coordinates in degrees and minutes, directly followed by a cardinal point.
        # Examples: "123°456' N", "98°765' W"
        r"\b(?<!\.)(?!0\.)\d{1,3}[°º◦]\s*\d{1,3}[ʹ′'’]?\s*[NSEW]\b",

        # ------------------- [°º◦] and (?:′|\u2032|\u0027) and ″ pattern -------------------------------------------
        # Note: Unicode specifications for symbols must be used here, otherwise there will be a conflict with the Python syntax because of quotation marks

        # Captures coordinates in the form of degrees, minutes and seconds.
        # Examples: '123°45'67″ N', '12°34'56″ S'
        #r'\b(?<!\.)\d{1,3}(?:[°º◦]|\u00B0)?\s*\d{1,3}(?:′|\u2032|\u0027)?\s*\d{1,3}(?:″|\u2033)?\s*[NSEW]\b',
        r'\b(?<!\.)\d{1,3}(?:[°º◦]|\u00B0)?\s*\d{1,3}(?:′|\u2032|\u0027)?\s*\d{1,3}(?:\.\d+)?(?:″|\u2033)?\s*[NSEW]\b',

        # Captures coordinates in the form of degrees, minutes and seconds in tables.
        # Note: No word boundary (\b) as coordinates in table
        # Examples: '123°45'67" ', '98°76'54" '
        r'(?<!\.)\d{1,3}[°º◦]\d{2}[′’\u0027\u2032]\d{2}["”]?',

        # Captures two coordinates in one line, displaying degrees, minutes and seconds with different precision.
        # Examples: '123°45'67.89″ N - 98°76'54.32″ W', '12°34'56.78″ S - 23°45'67.89″ E'
        r'\b(?<!\.)\d{1,3}(?:[°º◦]|\u00B0)?\d{1,3}(?:′|\u2032|\u0027)?(?!0\.)\d{1,3}\.\d{1,3}(?:″|\u2033)?\s*[NSEW]\s*[-–−]\s*(?<!\.)\d{1,3}(?:[°◦]|\u00B0)?\d{1,3}(?:′|\u2032|\u0027)?(?!0\.)\d{1,3}\.\d{1,3}(?:″|\u2033)?\s*[NSEW]\b',

        # Captures coordinates in tables in degrees, minutes and seconds, whereby the seconds can have decimal places.
        # Note: No word boundary (\b) as coordinates in table
        # Examples: '123°45'67.89" N', '12°34'56.78"S'
        r'(?<!\.)\d{1,3}[°º◦]\s*\d{1,3}[′’\u0027\u2032]\d{1,3}\.\d{1,3}["”]\s*[NSEW]?',

        # ------------------- Only [ʹ′'’] pattern -------------------------------------------
        # Captures specific coordinates in minutes, also in tables.
        # Introduced, because '°' was converted to '0' in some PDFs
        # Examples: "43010'", "39058'"
        r"(?<!\.)\d{1,3}0\d{1,3}[ʹ′'’]",

        # Captures specific coordinates in minutes, also in tables.
        # Introduced, because '°' was converted to 'o' in some PDFs
        # Examples: "44o26’N", "121o34’W"
        r"(?<!\.)\d{1,3}o\d{1,3}[ʹ′'’]s*[NSEW]",

        # ------------------- Other special case pattern -------------------------------------------
        # Captures simple details of coordinate ranges, separated by the word 'to'.
        # Examples: '123 to 130 N'"', '45 to 50 W'
        r'\b(?<!\.)\d{1,3}\s*to\s*\d{1,3}0\s*[NSEW]\b',

        # Captures ranges of decimal degrees, separated by the word 'to', with a final cardinal point at the latter coordinate.
        # Examples: '123.456 to 789.012 N', '45.678 to 123.456 W'
        r'\b(?<!\.)\d{1,3}\.\d{1,3}\s*to\s*\d{1,3}\.\d{1,3}\s*[NSEW]\b',

        # Captures ranges of coordinates, separated by a hyphen, followed by a cardinal point.
        # Examples: '36–528 N', '52–988 W'
        r'\b(?<!\.)\d{1,3}[-–−]\d{1,3}\s[NSWE]\b',

        # Captures coordinates in brackets, with 'lat' or 'long' prefix of length 9 to 10.
        # Note: No word boundary (\b) as coordinates in table
        # Examples: '(lat 1230230140, long 340450260)'
        r'\(lat \d{9,10}, long \d{9,10}\)',

        # Captures very large numerical values as coordinates with subsequent cardinal points.
        # Note: Due to a wrong conversation of the PDF the special characters like '°' and "'"
        # Note: No word boundary (\b) as coordinates in table
        # Examples: '123456789N', '987654321 W'
        r'(?<!\.)(?!0\.)\d{9,10}\s*[NSEW]',

        # Captures coordinates with cardinal points, connected by a semicolon.
        # Note: The zeros here are incorrectly converted '°'
        # Examples: '12034 56078 N; 12034 56078 E'
        r'\b(?<!\.)\d{1,3}\s*0\d{1,3}\s*\d{1,3}\s*0\d{1,3}\s*[NSEW];\s*\d{1,3}\s*0\d{1,3}\*\d{1,3}\s*0\d{1,3}\s*[NSEW]\b'
    ]

    # Add all found coordinates to the 'matches' list, which is created here
    matches = []
    # Iterate over the pattern and as soon as a pattern has found a result in a line, add it to “matches” using extend()
    for pattern in patterns:
        matches.extend(re.findall(pattern, line))

    return matches


def find_study_site(lines):
    """
    Searches for specific terms/keywords that represent a relevant entry in the “Area name” column of the Excel table and returns the relevant rows.
    Here, if one of these keywords is found, the search will be stopped on purpose.
    Important: This is only executed if no coordinates were found to be able to add coordinates in the manual verification step.


    Args:
        lines (list): A list of text lines in which keywords are searched for the study area.

    Returns:
        str or None: A string containing the context of the areas found in a study, or None if none were found

    References:
        - Python RegEx in general: https://www.w3schools.com/python/python_regex.asp
        - 're.search()':https://docs.python.org/3/library/re.html#re.search
        - 're.IGNORECASE': https://docs.python.org/3/library/re.html#re.IGNORECASE
    """

    # Iterates over all lines of the text of a PDf, if a keyword is found, this line
    # and the following 4 lines are saved and appended to the lines that provide information about the searched area.
    for i, line in enumerate(lines):
        # Check for all searched keywords, upper and lower case is ignored here
        if (re.search(r'\bData Sources and Location\b', line, re.IGNORECASE)
                or re.search(r'\bstudy area\b', line, re.IGNORECASE)
                or re.search(r'\bstudy  area\b', line, re.IGNORECASE)
                or re.search(r'\bThe area of\b', line, re.IGNORECASE)
                or re.search(r'\bforest areas\b', line, re.IGNORECASE)

                or re.search(r'\bstudy site\b', line, re.IGNORECASE)
                or re.search(r'\bstudy sites\b', line, re.IGNORECASE)
                or re.search(r'\bS T U D Y S I T E\b', line, re.IGNORECASE)


                #  If “study site” is separated by a line break
                or (line.strip().endswith("study") and (i + 1 < len(lines)) and lines[i + 1].strip().startswith(
                    "site"))

                or re.search(r'\bcompared three sites\b', line, re.IGNORECASE)
                or re.search(r'\bstudy region\b', line, re.IGNORECASE)
                or re.search(r'\bBioregional  description\b', line, re.IGNORECASE)
                or re.search(r'\bStudy landscapes\b', line, re.IGNORECASE)
                or re.search(r'\bsite description\b', line, re.IGNORECASE)
                or re.search(r'\bStudy system\b', line, re.IGNORECASE)
                or re.search(r'\bforest sites\b', line, re.IGNORECASE)
                or re.search(r'\bstudy was conducted at\b', line, re.IGNORECASE)
                or re.search(r'\bstudy was conducted in\b', line, re.IGNORECASE)
                or re.search(r'\bsite is located\b', line, re.IGNORECASE)
                or re.search(r'\bstudy location\b', line, re.IGNORECASE)

        ):
            # Save context lines (the line in which the keyword was found and the following 4)
            # This is done to ensure not only that the complete study site description is saved, but also that if the keywords is
            # a headline for a section of the paper, not only this is saved but also its following content
            context_lines = lines[i:i + 4]
            return " ".join(context_lines).strip()
    return None

def find_analyzed_years(lines):
    """
    Extrahiert untersuchte Zeiträume aus den gegebenen Textzeilen.
    Hierbei darf die maximale zu erfassende Zahl 2024 sein, was durch die Regex Muster so beschränkt wird (|2[0-4])
    https://www.w3schools.com/python/python_regex.asp
    https://docs.python.org/3/library/re.html#re.search
    https://docs.python.org/3/library/re.html#re.IGNORECASE
    https://docs.python.org/3/library/re.html#re.findall
    https://docs.python.org/3/library/re.html#re.match

    Args:
        lines (list of str): (Bereinigte) Zeilen aus dem PDF-Dokument.

    Returns:
        str oder None: Sortierte Liste der extrahierten Zeiträume, wenn nichts gefunden wurde eine leere Liste.
    """
    # Regex-Muster, für die Erfassung von Zeiträumen in verschiedenen Formaten
    time_period_patterns = [
        # Erfasst Zeiträume, welche durch einen Bindestrich getrennt sind.
        # Beispiele: '1980-1990', '2022-2024'
        r'\b(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\b',

        # Erfasst Zeiträume, welche in Klammern stehen und durch einen Bindestrich getrennt sind.
        # Beispiele: '(1980-1990)', '(2022-2024)'
        r'\((19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\)',

        # Erfasst Zeiträume, welche durch Bindestrich getrennt sind und wo der zweite Teil nur zwei Ziffern hat.
        # Beispiele: '1927-54', '2021-24'
        r'\b(19\d{2}|20(?:0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(\d{2})\b',

        # Erfasst Zeiträume, welche durch 'from ... to ...' angegeben werden.
        # Beispiele: 'from 1980 to 1990', 'from 1999-2011'
        r'(?:from\s*)?(19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) to (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',

        # Erfasst Zeiträume, welche durch 'between ... to ...' angegeben werden.
        # Beispiele: 'between 1980 and 1990'
        r'between (19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) and (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',

        # Erfasst Zeiträume mit Längenangabe in Tagen.
        # Beispiele: 'over a 180-day period'
        r'over a (\d+)-day period'
    ]

    # Liste zum Speichern der gefundenen Zeitspannen
    found_periods = []

    # Iteriert durch jede Zeile und sucht mit den oben definierten Zeitraummustern nach Zeitspannen
    for line in lines:
        for pattern in time_period_patterns:
            # Findet alle Vorkommen, die dem aktuellen Muster (pattern) in der Zeile entsprechen
            matches = re.findall(pattern, line)
            for match in matches:
                # Überprüft, ob der Treffer (match) ein Tupel ist, was auf verschiedene Formen von Zeiträumen hinweist
                if isinstance(match, tuple):
                    # Handhabung für Zeiträume im Format 'YYYY-YY' wie zum Beispiel '2020-21'
                    if len(match) == 2 and len(match[1]) == 2:
                        # Extrahiert das Startjahr (z.B. '2020')
                        start_year = match[0]
                        # Extrahiert die Endjahr-Suffixe (z.B. '21')
                        end_year_suffix = match[1]

                        # Wenn das Startjahr mit "20" beginnt, prüfen wir die Endjahres-Suffixe
                        if start_year.startswith("20"):
                            # Fügt die ersten zwei Ziffern des Startjahres mit den Endjahres-Suffixen zusammen, um das Endjahr zu bilden
                            end_year = int(start_year[:2] + end_year_suffix)
                            # Überprüft, ob das Endjahr kleiner oder gleich 2024 ist, um sicherzustellen, dass es ein gültiges Jahr ist
                            if end_year <= 2024:
                                # Bildet die Zeitspanne (z.B. '2020-2021')
                                period = f"{start_year}-{end_year}"
                            else:
                                # Überspringt ungültige Zeitspannen
                                continue
                        else:
                            # Wenn das Startjahr mit "19" beginnt, wird das Endjahr direkt angefügt, da alle zweistelligen Zahlen erlaubt sind
                            period = f"{start_year}-{start_year[:2]}{end_year_suffix}"
                    else:
                        # Standard-Zeitraum-Muster wie 'YYYY-YYYY' (z.B. '1980-1990')
                        period = f"{match[0]}-{match[2]}"
                else:
                    # Wenn der Treffer kein Tupel ist, handelt es sich um ein einfacheres Muster, das direkt zugewiesen werden kann
                    period = match

                # Überprüft, ob das gefundene Muster gültig ist
                # Es wird sichergestellt, dass es sich um einen vollständigen Zeitraum handelt (z.B. '1980-1990')
                # Oder ein einzelnes Jahrzehnt (z.B. '1980s')
                # Oder um einen Ausdruck wie 'over a 180-day period'
                if re.match(r'^(19|20)\d{2}[-–−](19|20)\d{2}$', period) or re.match(r'^(19|20)\d{2}s$',
                                                                                    period) or re.match(r'^over a \d+-day period$', period):
                    # Vermeidet doppelte Einträge in der Liste
                    if period not in found_periods:
                        # Fügt die validierte Zeitspanne zur Ergebnisliste (found_periods) hinzu
                        found_periods.append(period)

    return sorted(found_periods)


def find_periods_with_drought(lines):
    """
    Diese Funktion extrahiert Zeitspannen von Dürreperioden aus den gegebenen Textzeilen und validiert Zeiträume,
    bei denen das Endjahr-Suffix in bestimmten Fällen überprüft wird.
    https://docs.python.org/3/library/re.html#re.search
    https://www.w3schools.com/python/ref_func_isinstance.asp
    https://docs.python.org/3/library/re.html#re.IGNORECASE
    https://docs.python.org/3/library/re.html#re.compile
    https://docs.python.org/3/library/re.html#re.findall

    Args:
        lines (list of str): Zeilen von Text aus dem PDF-Dokument.

    Returns:
        list: Sortierte Liste der extrahierten Zeitspannen, in denen Dürre vorkam, falls gefunden, sonst eine leere Liste.
    """
    # Regex-Muster für die Erfassung von Zeiträumen in verschiedenen Formaten
    drought_periods_patterns = [
        # Erfasst Zeiträume, welche durch einen Bindestrich getrennt sind.
        r'\b(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\b',

        # Erfasst Zeiträume, welche in Klammern stehen und durch einen Bindestrich getrennt sind.
        r'\((19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\)',

        # Erfasst Zeiträume mit zweistelligem Endjahr-Suffix.
        r'\b(19\d{2}|20(?:0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(\d{2})\b',

        # Erfasst Zeitspannen mit zweistelligem Endjahr-Suffix in Klammern.
        r'\((19\d{2}|20(?:0[0-9]|1[0-9]|2[0-4]))\s*[-–−]\s*(\d{2})\)',

        # Erfasst Zeiträume, welche durch 'from ... to ...' angegeben werden.
        r'(?:from\s*)?(19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) to (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',

        # Erfasst Zeiträume, welche durch 'between ... to ...' angegeben werden.
        r'between (19\d{2}|20(0[0-9]|1[0-9]|2[0-4])) and (19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))',
    ]

    # Regex-Muster für die Schlüsselwörter "drought", "droughts" und "drier" um sicherzugehen, dass die einzelnen Jahre im zusammenhang mit Dürre stehen
    drought_pattern = re.compile(r'\bdroughts?|drier\b', re.IGNORECASE)

    # Liste zum Speichern der gefundenen Zeitspannen
    drought_periods = []

    # Iteriert durch jede Zeile und sucht nach Zeitraum-Mustern
    for line in lines:
        # # Überprüft, ob die oben festgelegten Schlüsselwörter für Dürre in der Zeile vorhanden sind und sucht nach Zeitspannen, wenn dies der Fall ist
        if drought_pattern.search(line):
            # Wenn das Schlüsselwort für Dürre gefunden wurde, wird für jedes definierte Zeitraummuster (Regex-Pattern) in der Zeile gesucht
            for pattern in drought_periods_patterns:
                # Findet alle Vorkommen, die dem aktuellen Regex-Muster entsprechen
                matches = re.findall(pattern, line)
                for match in matches:
                    # Wenn das gefundene Match ein Tuple ist (mehrere Teile, wie z.B. Start- und Endjahr):
                    if isinstance(match, tuple):
                        # Überprüft, ob das Match zwei Teile enthält und das zweite Teil zwei Ziffern hat (z.B. '1980-85')
                        if len(match) == 2 and len(match[1]) == 2:
                            # Weist den ersten Teil des Matches dem Startjahr zu
                            start_year = match[0]
                            # Weist den zweiten Teil des Matches dem Endjahres-Suffix zu (die letzten zwei Ziffern)
                            end_year_suffix = match[1]

                            # Validierung: Wenn das Startjahr mit "20" beginnt, überprüft, ob das Endjahr-Suffix nicht größer als 24 ist
                            if start_year.startswith("20") and int(end_year_suffix) > 24:
                                # Wenn das Endjahr-Suffix größer als 24 ist, wird dieser Zeitraum übersprungen (als ungültig betrachtet)
                                continue

                            # Setzt den vollständigen Zeitraum zusammen, indem das Startjahr und das vollständige Endjahr kombiniert werden
                            # z.B. '1980-85' wird zu '1980-1985'
                            period = f"{start_year}-{start_year[:2]}{end_year_suffix}"
                        else:
                            # Für Standard-Zeitraum-Muster wie '1980-1990', bei denen das Jahr vollständig angegeben ist
                            # (d.h. sowohl Start- als auch Endjahr sind vierstellig)
                            period = f"{match[0]}-{match[2]}"
                    else:
                        # Wenn das Match kein Tuple ist (d.h. nur ein einzelner Zeitraum), wird es direkt als Zeitraum übernommen
                        period = match

                    # Überprüft, ob das gefundene Muster generell gültig ist
                    if re.match(r'^(19|20)\d{2}[-–−](19|20)\d{2}$', period):
                        # Verhindert doppelte Einträge in der Liste der gefundenen Zeiträume
                        if period not in drought_periods:
                            # Fügt den gefundenen und validierten Zeitraum der Liste hinzu
                            drought_periods.append(period)

    return sorted(drought_periods)


def find_single_years_with_drought(lines):
    """
    Extrahiert einzelne Jahreszahlen aus den gegebenen Textzeilen, wenn sie im Zusammenhang mit Dürre stehen.
    Jahre, die direkt nach einem Minuszeichen '-', vor einer schließenden Klammer ')' sowie direkt nach einem Punkt und einem Leerzeichen stehen, werden ignoriert,
    damit Angaben aus den Quellen der wissenschaftlichen Veröffentlichungen nicht eingezogen werden.
    Hierbei darf die maximale zu erfassende Zahl 2024 sein, was durch die Regex Muster so beschränkt wird (|2[0-4])
    https://www.w3schools.com/python/ref_func_isinstance.asp
    https://docs.python.org/3/library/re.html#re.IGNORECASE
    https://docs.python.org/3/library/re.html#re.compile
    https://docs.python.org/3/library/re.html#re.findall

    Args:
        lines (list of str): (Bereinigte) Zeilen aus dem PDF-Dokument.

    Returns:
        list: Sortierte Liste der extrahierten Jahreszahlen, in denen Dürre vorkam, wenn nichts gefunden wurde eine leere Liste.
    """
    # Regex-Muster für die Erfassung von einzelnen Jahreszahlen mit den oben beschriebenen Restriktionen
    #single_year_pattern = r'(?<![-])(?<!\.\s)\b(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\b(?!\))'
    single_year_pattern = r'(?<![-])(?<!\.\s)\b(19\d{2}|20(0[0-9]|1[0-9]|2[0-4]))\b(?![);])'


    # Regex-Muster für die Schlüsselwörter "drought", "droughts" und "drier" um sicherzugehen, dass die einzelnen Jahre im zusammenhang mit Dürre stehen
    drought_pattern = re.compile(r'\bdroughts?|drier\b', re.IGNORECASE)

    # Liste zum Speichern der gefundenen, einzelnen Jahreszahlen
    single_drought_years = []

    # Iteriert durch jede Zeile und sucht nach einzelnen Jahreszahlen
    for line in lines:
        # Überprüft, ob die oben festgelegten Schlüsselwörter für Dürre in der Zeile vorhanden sind und sucht nach Jahreszahlen wenn dies der Fall ist
        if drought_pattern.search(line):
            # Findet alle Vorkommen, die dem definierten Muster für einzelne Jahreszahlen entsprechen
            matches = re.findall(single_year_pattern, line)
            for match in matches:
                # Verhindert, dass doppelte Einträge übernommen werden und überprüft, ob der Treffer ein Tupel ist (das bei bestimmten Mustern vorkommen kann)
                # Dann wird das Jahr entsprechend aus dem Tupel extrahiert
                if isinstance(match, tuple):
                    # Wählt das Jahr aus dem Tupel (erste oder zweite Position)
                    year = match[0] if match[0] else match[1]
                # Wenn kein Tupel, wird der Treffer direkt als Jahr verwendet
                else:
                    year = match

                # Überprüft, ob die Jahreszahl zwischen 1900 und 2024 liegt, da dies der relevante Zeitrahmen ist
                if 1900 <= int(year) <= 2024:
                    # Fügt die einzelne Jahreszahl zur Liste (single_drought_years) hinzu, falls sie nicht schon in der Liste vorhanden ist
                    if year not in single_drought_years:
                        single_drought_years.append(year)

    return sorted(single_drought_years)

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
def find_drought_definitions(lines, pdf_file):
    """
    Searches for specific terms related to the characterization of droughts and returns the relevant lines and the keywords found.
    In contrast to the search methodology in 'find_study_site(lines)', the search is not aborted as soon as a keyword is found.
    As all possible drought definitions and their relevant text lines are searched for and saved, this makes manual verification easier,
    because from the keywords and the corresponding lines in the PDF, the drought definitions used for the evaluation can be derivied.
    Because these keywords are crucial for the evaluation, the keywords are not automatically mapped, but all taken into account for manual verification.

    Args:
        lines (list): A list of text lines in which keywords are searched for the drought definitions
        pdf_file (str): The file name of the PDF from which the lines originate.

    Returns:
        tuple: A tuple containing either (str, list), where the string contains the summarized relevant lines and the list contains the keywords found,
        or (None, None) if no relevant information was found.

    References:
        - Python RegEx in general: https://www.w3schools.com/python/python_regex.asp
        - 're.search()': https://docs.python.org/3/library/re.html#re.search
        - 're.escape()': https://docs.python.org/3/library/re.html#re.escape
        - 're.INGORECASE: 'https://docs.python.org/3/library/re.html#re.IGNORECASE
        - Saving context lines: https://stackoverflow.com/a/45291736
    """

    # The drought definition terms to be searched for are saved in this list:
    keywords = ['PET',
                'SPI',
                'SPEI',
                'PDSI',
                'scPDSI',
                'index',
                'low soil moisture',
                'soil water content',
                'VPD',
                'reduced rainfall',
                'low precipitation',
                'lower precipitation',
                'soil water content',
                'dry soil conditions',
                'absence of precipitation',
                'decline in precipitation',
                'throughfall exclusion',
                'elevated temperatures',
                'water withdrawal',
                'long-term mean',
                'plant water stress',
                'low NPP',
                'drought',
                'droughts'
                'dry conditions',
                'drought conditions',
                'hot droughts',
                'big dry',
                'dry season',
                'dry period',
                'drought year',
                'El Niño',
                'Big Dry']

    # This list saves all those lines which contain a keyword plus 3 lines after it
    drought_lines = []
    # This list saves all terms found in a PDF from the 'keywords' list
    drought_quantification_keywords = []

    # Iterating each line from the PDF using enumerate() to search for the drought definitions keywords
    for keyword in keywords:
        for i, line in enumerate(lines):
            # re.escape to ensure that all special characters are treated as literals and not regex meta characters
            # re.IGNORECASE so upper and lower case is ignored here
            if re.search(r'\b' + re.escape(keyword) + r'\b', line, re.IGNORECASE):
                # If a term was found, it is added to 'drought_quantification_keywords'
                drought_quantification_keywords.append(keyword)
                # and the line in which the term was found and the following three are saved
                context_lines = lines[max(0, i - 1):i + 3]
                drought_lines.append(" ".join(context_lines).strip())
                break

    if drought_lines:
        # The relevant lines are merged into a single string, `.strip()` removes all superfluous spaces.
        # 'drought_quantification_keywords' is also returned, which contains all keywords found in the PDF.
        return " ".join(drought_lines).strip(), drought_quantification_keywords
        # If no relevant line was found in the PDF (meaning “drought_lines” is empty),
        # the function returns a tuple containing two “None” values.
    return None, None

def extract_spatial_information_from_pdfs(folder_path):
    """
    Extracts spatial information (coordinates and their context) from PDF files in the specified folder,
    ignoring duplicates coordinates and those that match certain patterns.

    Args:
        folder_path (str): The path to the folder containing PDF files to be processed.

    Returns:
        list: A list of tuples, where each tuple contains extracted spatial information for a PDF file. Each tuple includes:
              pdf_basename (str): The file name of the PDF without the file extension (.pdf).
              final_coordinates (set): The valid coordinates or 'No coordinates found/given' if there were no coordinates found or given.
              lines_with_coordinates (list): The context lines of valid coordinates as list.
              lines (list): All lines from a PDF as list.
              pdf_file (str): The full file path to a PDF file.

    References:
        - 'os.listdir': https://docs.python.org/3/library/os.html#os.listdir
        - 'os.path': https://docs.python.org/3/library/os.path.html
        - Regular expressions in Python: https://www.w3schools.com/python/python_regex.asp
        - 're.split': https://docs.python.org/3/library/re.html#re.split
        - 're.match': https://docs.python.org/3/library/re.html#re.match
        - 'items()': https://www.w3schools.com/python/ref_dictionary_items.asp
        - 'next(iter())': https://www.programiz.com/python-programming/methods/built-in/next
        - Saving context lines using max() and index: https://python-forum.io/thread-28918-post-122845.html#pid122845
    """
    # Initialize the list for the results of the automatic coordinate extraction
    spatial_data = []

    # Patterns used for the identification of coordinate formats, which should be ignored if they occur alone
    decimal_pattern = r'\b(?<!\.)\d{1,3}\.\d{6}\b'
    decimal_dir_pattern = r'\b(?!0\.)\d{1,3}\.\d{2}\s*[NSEW]\b'
    number_dir_pattern = r'\b(?!0\.)\d{1,6}(?<!\d8\d{2}0)\s*[NSEW]\b'
    number_dir_pattern_range = r'\b(?!0\.)\d{3}–\d{3}[NSEW]\b'

    # Search all files in the specified folder
    for filename in os.listdir(folder_path):
        # Make sure that only PDFs in the specified folder are used and their file extension gets removed
        if filename.endswith('.pdf'):
            pdf_file = os.path.join(folder_path, filename)
            pdf_basename = os.path.splitext(os.path.basename(pdf_file))[0]
            # Log the pure name of the PDF file which is being searched for coordinates and their context
            logging.info(f"Looking for coordinates in '{pdf_basename}'")
            logging.info("")
            try:
                # Extract the text from the PDF file using pdfminer's 'extract_text' method
                text = extract_text(pdf_file)
                # Clean the text of specific special characters using the helper function clean_and_remove_control_characters()
                cleaned_text = clean_and_remove_control_characters(text)
                # Set for saving all coordinates found
                all_coordinates = set()
                # List for saving the context lines of these where coordinates were found
                lines_with_coordinates = []
                # Divide the cleaned text into lines for a clearer search process
                lines = re.split('\n+', cleaned_text)

                # Sets for managing individual coordinates found for ignoring depending on the pattern
                all_found_types = {decimal_pattern: set(), decimal_dir_pattern: set(), number_dir_pattern: set(), number_dir_pattern_range: set()}
                # List for storing ignored coordinates
                ignored_coordinates = []

                # Create dictionary to store all matches so find_matches() has only be calles once
                line_matches_dictionary = {}

                # Search each line of the cleaned PDF text for coordinates, both the correct ones and those to be ignored
                for line in lines:
                    # Find any coordinate matches in the given lines using the helper function 'find_matches()' and store them in the corresponding dictionary
                    matches = find_matches(line)
                    line_matches_dictionary[line] = matches
                    # If a match was found, add it to the 'coordinates' set
                    if matches:
                        for match in matches:
                            all_coordinates.add(match)
                            # Check each match against the specific given patterns which require special handling
                            for pattern in [decimal_pattern, decimal_dir_pattern, number_dir_pattern, number_dir_pattern_range]:
                                # If a match fits one of the specified pattern, store it in `all_found_types`
                                if re.match(pattern, match):
                                    all_found_types[pattern].add(match)


                # Create a new set for only these coordinates, which will be used later and are validated for duplicates
                final_coordinates = set()
                # Check whether coordinates found are duplicates or part of other coordinates
                for coord in all_coordinates:
                    include_match = True
                    for other_coord in all_coordinates:
                        # Be sure that a match if not compared with itself and then check if it is included in another match
                        if coord != other_coord and coord in other_coord:
                            # If a match is part of another match, indirectly exclude it by setting include to false. 'break' stops the comparison for this match, because it is already a duplicate
                            include_match = False
                            break
                    # If include is still True, add the coordinate to the final set
                    if include_match:
                        final_coordinates.add(coord)

                # This part makes sure that single coordinates are removed and not part of the final coordinate set if they match one of the, directly in this function specified patterns
                for pattern, coord_set in all_found_types.items():
                    # Only use single coordinates for comparison and retrieve them using next(iter()
                    if len(coord_set) == 1:
                        coord_to_ignore = next(iter(coord_set))
                        # Remove a coordinate that matches the criteria to be ignored and keep track of them for logging
                        if coord_to_ignore in final_coordinates:
                            final_coordinates.remove(coord_to_ignore)
                            ignored_coordinates.append(coord_to_ignore)
                            # log, which coordinate match was ignored in which PDF
                            logging.info(f"Ignored single coordinate {coord_to_ignore} in '{pdf_basename}'.")
                            logging.info("")

                # If a match was found, and it is valid, take the line it was in and the previous 2 lines as context
                for line, line_matches in line_matches_dictionary.items():
                    valid_matches = [match for match in line_matches if match in final_coordinates]
                    if valid_matches:
                        context_lines = lines[max(0, lines.index(line) - 2):lines.index(line) + 1]
                        lines_with_coordinates.append(" ".join(context_lines).strip())

                spatial_data.append((pdf_basename, final_coordinates, lines_with_coordinates, lines, pdf_file))

            # Backup logging, if there was an error that prevents information from being searched for in the PDFs
            except Exception as e:
                logging.error(f"Failed to extract text from '{pdf_file}': {str(e)}")
                spatial_data.append((pdf_basename, 'No coordinates found/given', '', None, None))

    return spatial_data

def logging_extraction_results(pdf_basename, coordinates, coordinate_context_lines, cleaned_study_site_context, drought_characterization_keywords, study_type, analyzed_years, periods_with_drought, single_years_with_drought):
    """
    This function logs all results of the automated information extraction

    Args:
        - pdf_basename (str): The file name of the PDF without the file extension (.pdf)
        - coordinates (str): The valid coordinates or 'No coordinates found/given' if there were no coordinates found or given
        - coordinate_context_lines (str): The context lines of coordinates as string
        - cleaned_context_lines (str): The context lines of study sites as string (only if no valid coordinates were found) or a placeholder '' (if no valid coordinates and no study site were found)
        - drought_characterization_keywords (list): The found keywords how drought was characterized
        - study_type (str): The approach to study drought of a study.
        - analyzed_years (list): The general years analyzed by a study or 'No analyzed years specified'
        - periods_with_drought (list): Time periods were a study characterized drought or 'No drought periods found/given'.
        - single_years_with_drought (list): Year(s) were a study characterized drought or 'No single drought years found/given'.

    Returns:
        None, since it only logs the results to the console
    """
    # Logging of the pure study name to make sure which scientific article is being processed
    logging.info(f"Processing '{pdf_basename}:'")

    # Logging whether and if so which (valid) coordinates were found
    if coordinates != 'No coordinates found/given':
        logging.info(f"Coordinates found: '{coordinates}'")
    else:
        logging.info(f"No coordinates found/given")

    # Logging of either the study sites found based on context lines of coordinates or the lines found by the 'find_study_site()' function
    if coordinate_context_lines != 'No study sites found/given':
        logging.info(f"Study site found: '{coordinate_context_lines}'")
    elif cleaned_study_site_context != 'No study sites found/given':
        logging.info(f"Study site found: '{cleaned_study_site_context}'")
    else:
        logging.info(f"No study site found/given")

    # Logging whether and how drought was characterized
    if drought_characterization_keywords:
        logging.info(f"Drought defined via: '{', '.join(drought_characterization_keywords)}'")
    else:
        logging.info(f"No drought definition found/given")

    # Logging whether and if, which approach to study drought was used by a study
    if study_type:
        logging.info(f"Study type: '{study_type}'")
    else:
        logging.info(f"No study type found/given")

    # Logging what year was analyzed in general by a study or the information that no years were found or given
    if analyzed_years:
        logging.info(f"Analyzed years: '{analyzed_years}'")
    else:
        logging.info(f"No analyzed years found/given")

    # Logging whether and if so which time periods are characterized by a drought according to the studies
    if periods_with_drought:
        logging.info(f"Periods were drought was given: '{periods_with_drought}'")
    else:
        logging.info(f"No drought periods found/given")

    # # Logging whether and if so which year(s) are characterized by a drought according to the studies
    if single_years_with_drought:
        logging.info(f"Years were drought was given: '{single_years_with_drought}'")
    else:
        logging.info(f"No single drought years found/given")

    # Logging a blank line to separate two PDFs for a better overview
    logging.info("")

    # For a better overview we slow down the logging a little bit
    # time.sleep(1)

def process_extraction_results(folder_path):
    """
    Processes extracted results from a PDF file and appends relevant data to the results list that is used by extract_spatial_information() to give it to the main module

    This function acts as a management function for this module, as it calls all other functions except extract_spatial_information_from_pdfs(),
    converts the information to strings and then stores it in the result list. It also calls the logging function, for an information output.

    Args:
        folder_path (str): The path to the folder containing PDF files to be processed.

    Returns:
        list: A list of tuples containing extracted data for each PDF file. Each tuple represents one PDF and includes the following elements:
            - pdf_basename (str): The file name of the PDF without the file extension (.pdf)
            - coordinates_str (str): The valid coordinates or 'No coordinates found/given' if there were no coordinates found or given
            - coordinate_context_lines (str): The context lines of coordinates as string
            - cleaned_context_lines (str): The context lines of study sites as string (only if no valid coordinates were found) or a placeholder '' (if no valid coordinates and no study site were found)
            - drought_characterization (str) The context lines of the found drought keywords
            - drought_characterization_keywords (list): The found keywords how drought was characterized
            - study_type (str): The approach to study drought of a study.
            - analyzed_years (list): The general years analyzed by a study or 'No analyzed years specified'
            - periods_with_drought (list): Time periods were a study characterized drought or 'No drought periods found/given'.
            - single_years_with_drought (list): Year(s) were a study characterized drought or 'No single drought years found/given'.
    """

    # Call the extract_spatial_information_from_pdfs() function and store the given information into 'spatial_data'
    spatial_data = extract_spatial_information_from_pdfs(folder_path)

    # Create a list to store all information in, that will be given to 'extracted_data' in the main module
    results = []

    # To ensure that the PDFs are all processed in sequence and that the information always fit together, use the data from the extract_spatial_information_from_pdfs() function
    for pdf_basename, final_coordinates, lines_with_coordinates, lines, pdf_file in spatial_data:

        # Execute the helper function 'find_drought_definitions()' to find out how drought was defined in a study
        drought_characterization, drought_characterization_keywords = find_drought_definitions(lines, pdf_file)

        # Execute the helper function 'find_study_type()' to get study type of a study
        study_type = find_study_type(lines, pdf_file)

        # Execute the helper function 'find_analyzed_years()' to find out the studied years
        analyzed_years = find_analyzed_years(lines)

        # Execute the helper function 'find_periods_with_drought()' to find out the given drought period(s) of a study
        periods_with_drought = find_periods_with_drought(lines)

        # Execute the helper function find_single_years_with_drought to find out given drought year(s) of a study
        single_years_with_drought = find_single_years_with_drought(lines)

        # Check whether coordinates and/or study areas have been found
        coordinates_found = bool(final_coordinates)
        study_site_lines_found  = bool(lines_with_coordinates)

        # If valid coordinates were found, they are joined as a string,
        # otherwise 'No coordinates found/given' is set for logging output.
        coordinates_str = ', '.join(final_coordinates) if coordinates_found else 'No coordinates found/given'

        # If context lines with coordinates were found, these are joined as a string,
        # otherwise 'No study sites found/given' is set for logging.
        coordinate_context_lines = '; '.join(
            lines_with_coordinates) if study_site_lines_found else 'No study sites found/given'

        # Execute the helper function 'find_study_site()' to find out the site(s) for a study
        study_site_context = find_study_site(lines)
        cleaned_study_site_context = clean_and_remove_control_characters(
            study_site_context) if study_site_context else 'No study sites found/given'

        # Logging the results of the extractions by calling the logging_extraction_results() function
        logging_extraction_results(pdf_basename, coordinates_str, coordinate_context_lines, cleaned_study_site_context,
                                   drought_characterization_keywords, study_type, analyzed_years, periods_with_drought, single_years_with_drought)

        # Save all results for the case, that valid coordinates were found
        if final_coordinates:
            # Return tuple with all extracted information, including valid coordinates and context lines
            results.append((
                pdf_basename,
                coordinates_str,
                coordinate_context_lines,
                drought_characterization,
                drought_characterization_keywords,
                study_type,
                analyzed_years,
                periods_with_drought,
                single_years_with_drought
            ))
        # If no valid coordinates were found, get the study locations from the helper function 'find_study_site()'
        else:
            study_site_context = find_study_site(lines)
            # If a study region/site was found by the helper function 'find_study_site()',
            # the result is cleaned up so that it can be further processed with openpyxl and the results are saved.
            if study_site_context:
                cleaned_context_lines = clean_and_remove_control_characters(study_site_context)
                results.append((
                    pdf_basename,
                    'No coordinates found/given',
                    cleaned_context_lines,
                    drought_characterization,
                    drought_characterization_keywords,
                    study_type,
                    analyzed_years,
                    periods_with_drought,
                    single_years_with_drought
                ))
            # If nothing was found by the helper function 'find_study_site()', a placeholder gets added to the results ('')
            else:
                results.append((
                    pdf_basename,
                    'No coordinates found/given',
                    '',
                    drought_characterization,
                    drought_characterization_keywords,
                    study_type,
                    analyzed_years,
                    periods_with_drought,
                    single_years_with_drought
                ))

    return results