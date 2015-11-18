
**Beschreibung:**  
Der snmp_uptimeCheck überwacht die Uptime von Geräten.
Ich musste den Check anpassen, da der abgefrage Uptime Werte nur ein 32-Bit Counter ist und dieser daher nach 496 Tagen auf 0 zurückgesetzt wird (https://tools.cisco.com/quickview/bug/CSCeh49492).
Auf Cisco Geräten wird daher, wenn vorhanden, die OID snmpEngineTime verwendet.



**Installation:**     
Manuell:  
CMK-Server: den Check aus "checks/snmp_uptime" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  




