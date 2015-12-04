**Beschreibung:**  
Das Skript convert-mk-csv.py habe ich mal geschrieben um mehren tausend Hostes in CMK zu importieren.
Es konvertiert das CMK Format in eine CSV-Datei und umgekehrt.

Möglichkeiten:  
  host.mk -> host.csv (python convert-mk-csv.py -c csv2mk -i ./input.csv -o ./output.mk)
  host.csv -> host.mk (python convert-mk-csv.py -c mk2csv -i ./input.mk  -o ./output.csv)


**Installation:**  
Einfach die CMK-Datein (unter OMD[site]:~/etc/check_mk/conf.d/wato/*/*.mk) dem Skript als Parameter übergeben
