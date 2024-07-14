# Regex zum Implementieren der Suchmuster (pattern)
import re

# Beispielkoordinaten welche gefunden werden sollen als String
example_coordinates = "39  to  430  S"

# Textausgabe zur Überprüfung
print(example_coordinates)

# Alle regex pattern zur Suche von bestimmten Koordinatenformaten
# Source: https://www.w3schools.com/python/python_regex.asp
patterns = [
        # Die meisten der Pattern erlaubt es nicht, dass Koordinaten mit "." anfangen, um DOI Sucheinträge zu verhindern.
        # Himmelsrichtungen sind bei der Kategorisierung automatisch inklusive


        # ------------------- Dezimalgrad Pattern -------------------------------------------
        # Erfasst einfache Dezimalkoordinaten ohne Vorzeichen und ohne Himmelsrichtung
        # Beispiele: "123.456789", "32.123456"
        r'\b(?<!\.)\d{1,3}\.\d{6}\b',

        # Erfasst Dezimalgradangaben mit Grad-Symbol gefolgt von einer Himmelsrichtung.
        # Beispiele: "123.456° N", "32.1234°E"
        r'\b(?<!\.)(?!0\.)\d{1,3}\.\d{2,6}[°º◦]?\s*[NSEW](?!-)\b',

        # Erfasst zusammenhängende Koordinaten in Dezimalform mit möglichem negativen Vorzeichen und Himmelsrichtungen, getrennt durch Komma.
        # Beispiele: "-123.45678 N, -98.76543 E", "-23.4567 S, -45.6789 W"
        r'\b(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d+[NS],\s*(?<!\.)[-–−]?(?!0\.)\d{1,3}\.\d+[EW]\b',

        # Erfasst Koordinaten in Dezimalgradformat mit Grad-Symbol und Himmelsrichtungen, jeweils für Längen- und Breitengrad.
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
        # Anmerkung: Die Nullen vor der Himmelsrichtung sind hier falsch konvertierte "°"
        # Beispiele: "123°270 N", "98°020 W"
        r'\b(?<!\.)\d{1,3}[°º◦]\d{1,3}0\s*[NSEW]\b',

        # Erfasst zwei separate Gradangaben, durch ein Trennzeichen verbunden
        # Beispiele: "123° - 45° N", "98° - 76° W"
        r'\b(?<!\.)\d{1,3}[°º◦]\s*[-–−]*\s*\d{1,3}[°º◦]\s*[NSEW]\b',

        # Erfasst Koordinaten, die dreimal wiederholte Gradangaben enthalten, gefolgt von einer Himmelsrichtung.
        # Beispiele: "123°45°67° N", "98°76°54°W"
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
        # Anmerkung: Hier muss auf unicode Angaben für Symbole zurückgegriffen werden, da sonst ein konflikt mit dem Python-Syntax entsteht

        # Erfasst Koordinaten in Form von Grad, Minuten und Sekunden.
        # Beispiele: "123°45'67″ N", "12°34'56″ S"
        r'\b(?<!\.)\d{1,3}(?:[°º◦]|\u00B0)?\s*\d{1,3}(?:′|\u2032|\u0027)?\s*\d{1,3}(?:″|\u2033)?\s*[NSEW]\b',

        # Erfasst Koordinaten in Form von Grad, Minuten und Sekunden in Tabellen
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
        # Erfasst spezifische Koordinaten in Minutenangabe, auch in Tabellen
        # Eingeführt, da "°" in PDF Text zu "0" konvertiert wurde.
        # Beispiele: "43010'", "39058'"
        r"(?<!\.)\d{1,3}0\d{1,3}[ʹ′'’]",


        # ------------------- Weitere besondere Pattern -------------------------------------------
        # Erfasst simple Angaben von Koordinatenbereichen, getrennt durch das Wort "to"
        # Beispiele: "123 to 130 N", "45 to 50 W"
        r'\b(?<!\.)\d{1,3}\s*to\s*\d{1,3}0\s*[NSEW]\b',

        # Erfasst Bereiche von Dezimalgraden, getrennt durch das Wort "to", mit abschließender Himmelsrichtung bei der jeweiligen letzteren Koordinate.
        # Beispiele: "123.456 to 789.012 N", "45.678 to 123.456 W"
        r'\b(?<!\.)\d{1,3}\.\d{1,3}\s*to\s*\d{1,3}\.\d{1,3}\s*[NSEW]\b',

        # Erfasst Bereiche von Koordinaten, getrennt durch einen Bindestrich, gefolgt von einer Himmelsrichtung.
        # Beispiele: "36–528 N", "52–988 W"
        r'\b(?<!\.)\d{1,3}[-–−]\d{1,3}\s[NSWE]\b',

        # Erfasst Koordinaten in Klammern, mit "lat" oder "long" prefix der länge 9 bis 10
        # Anmerkung: Keine Wortgrenze (\b) da Koordinaten in Tabelle
        # Beispiele: (lat 1230230140, long 340450260)
        r'\(lat \d{9,10}, long \d{9,10}\)',

        # Erfasst sehr große Zahlwerte als Koordinaten mit nachfolgender Himmelsrichtung
        # Anmerkung: Hier fehlen durch eine falsche konversation der PDF die Sonderzeichen wie "°" und "'"
        # Anmerkung: Keine Wortgrenze (\b) da Koordinaten in Tabelle
        # Beispiele: "123456789N", "987654321 W"
        r'(?<!\.)(?!0\.)\d{9,10}\s*[NSEW]',

        # Erfasst Koordinaten mit Himmelsrichtungen, verbunden durch ein Semikolon.
        # Anmerkung: Die Nullen sind hier falsch konvertierte "°"
        # Beispiele: "12034 56078 N; 12034 56078 E"
        r'\b(?<!\.)\d{1,3}\s*0\d{1,3}\s*\d{1,3}\s*0\d{1,3}\s*[NSEW];\s*\d{1,3}\s*0\d{1,3}\*\d{1,3}\s*0\d{1,3}\s*[NSEW]\b'
    ]

# Leere Liste erstellen, in welche die gefundenen Koordinaten gespeichert werden
matches = []

# Alle Pattern durchgehen und mit der regex "re.findall" Funktion aufrufen, die gefundenen Koordinaten werden dann an die Liste angehangen
for pattern in patterns:
    matches.extend(re.findall(pattern, example_coordinates))

# Ausgabe der gefundenen Koordinaten
print(f"Matches: {matches}")