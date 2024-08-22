import re

# Beispielzeilen zum Testen
lines = [
    "drought in 2024, 2021-22, from 2000 to 2010, between 2022 and 2023, 2012-2019, (1945-67), (2021-27), 2001-26"
]

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

    # Gibt die Liste der gefundenen Zeiträume zurück, sortiert nach dem Anfangsjahr
    return sorted(drought_periods)

# Beispielhafte Ausgabe der Ergebnisse
print(find_periods_with_drought(lines))
