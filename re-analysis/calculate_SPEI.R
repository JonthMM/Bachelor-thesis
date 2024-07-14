# Environment aufräumen und libraries laden
rm(list=ls()) 

# SPEI Package zur Berechnung des SPEI (und eventuell weiterer Indexe wie PET oder SPI)
#install.packages("SPEI")
library(SPEI)

# readxl Package um mit Excel-Dateien arbeiten zu können
#install.packages("readxl")
library(readxl)

# Workingdirectory setzen
setwd("D:/Uni/Bachelorarbeit/code/re-analysis")

# Pfad zur Excel Datei setzen
file_path <- "D:/Uni/Bachelorarbeit/2024Apr_Mana_Review_v2i - Kopie.xlsx"

# Lesen der Excel Datei
spei_data <- read_excel(file_path)

# Optional: Festlegen des spezifischen Blattes der Excel Datei
#spei_data <- read_excel(file_path, sheet = "secondAppr")

# Festlegen der Zeilen und Spalten, welche verwendet und angezeigt werden sollen
spei_data <- read_excel(file_path, range = "B1:R49")

# Ausgeben der Daten, um zu testen ob wir mit den richtigen Arbeiten
print(spei_data)

# Beispiel: Extrahieren der Daten in F6
# Da wir oben in Zeile 26 unsere eigenen Grenzen für die Daten der Tabelle gesetzt haben
# müssen wir hier die Zeilen und Spalten Indexe anpassen
row_index <- 6  # Zeilen index für die 6. Reihe
col_index <- 5  # Spalten index für F

# Ausgeben der Daten in F6
value_at_F6 <- spei_data[row_index, col_index]
print(value_at_F6)

