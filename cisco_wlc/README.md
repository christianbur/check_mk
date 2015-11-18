**Beschreibung:**  
Der cisco_wlc Check dient zur Überwachung von Wireless LAN Controllern und ist einer Erweiterung des CMK-Checks.
Ich verwende den Check im Cluster, da wir zwei Controller verwenden. 

Der Check gibt folgende Informationen aus.
  - IP
  - AP enabled/disabled
  - AP-Group
  - WL-Controller
      - überprüft den primary und secondary Controller und gibt eine Warnung bei einer Änderung
  - Warnung wenn AP nicht mehr gefunden wird

**Installation:**  
Manuell:  
CMK-Server: den Check aus "checks/cisco_wlc" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  



**Screenshort:**
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_wlc/1.png)
