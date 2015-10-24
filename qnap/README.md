**Beschreibung:**  
Mit dem "qnap" CMK-Plugin können NAS-Geräte von Qnap überwacht werden.
Der Check wurde in der Version 1.1 von Andre Eckstein geschrieben, um den Check jedoch auf mein CMK-Instanz mit der Version 1.2.7 laufen zu lassen, musste ich einige kleinere Verändeurngen vornehmen.

**TODO:**  
- die statische Inventory Funktion des "qnap_fans" Checks müsste überarbeitet werden, mein Qnap liefert jedoch keine Lüfterdaten im SNMP. 
- Komischerweise wird bei neimen Qnap der snmp_info Check nicht ausgeführt, obwohl die OID 1.3.6.1.2.1.1.1.0 ok ist.
  SNMPv2-MIB::sysDescr.0 = STRING: Linux TS-219 4.2.0

  
**Installation:**  
Mit MPK:  
check_mk -P install qnap-1.2.mkp
    
Manuell:  
checksqnap_*                  nach /omd/sites/SITE/local/share/check_mk/checks/        kopieren    
checkman/qnap_*               nach /omd/sites/SITE/local/share/check_mk/checkman/      kopieren  
pnp-templates/check_mk-qnap_* nach /omd/sites/SITE/local/share/check_mk/pnp-templates/ kopieren  
  
**Screenshort:**
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/qnap/screenshort_qnap.png)

 
