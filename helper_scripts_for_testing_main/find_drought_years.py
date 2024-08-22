import re

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

# Beispielzeilen zum Testen
lines = [
    # 1927, 2024 valide
    "drought in 1927, 2017), 2024, 1899, 2025, -1990,"
    # 2015 valide
    "In 2015, Borneo experienced a strong El Nino-driven drought."
    # 2013 nicht valide
    "Palik. 2013. Effects of thinning on drought vulnerability"
    # 2008 nicht valide
    "drought is the main lethal factor (Boulant et al., 2008; Rodríguez"
]

print(find_single_years_with_drought(lines))
