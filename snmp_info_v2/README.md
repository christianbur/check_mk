**Beschreibung:**  
Da mit der Check_mk Installation vorwiegend Cisco und HP Netzwerkgeräte überwacht werden, wurde der snmp_info Check um folgende Punkte erweitert:
 - Auslesen der Seriennummer
      - Sobald sich die Seriennummer ändert, geht der Check auf WARN. (so bekommt man z.B. mit wenn ein Switch oder Router getaucht wird)
 - Auslesen des Models
 - Der Check gibt einen Infotext aus, wenn er eine unbekannte Firmware-Version ohne SSH erkennt.

**Installation:**  
Manuell:  
CMK-Server: den Check aus "checks/snmp_info_v2" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  

Info:
Der orginale snmp_info Check sollte deaktiviert werden

**Screenshort:**
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/snmp_info_v2/screenshort_snmp_info_v2.png)

Seriennummer hat sich geändert
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/snmp_info_v2/screenshort_snmp_info_v2_changed.png)

Cisco Firmware ohne SSH
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/snmp_info_v2/screenshort_snmp_info_v2_keineSSHFirmware.png)
