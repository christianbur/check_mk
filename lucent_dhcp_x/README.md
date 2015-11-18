**Beschreibung:**  
Die drei Checks lucent_dhcp_failover, lucent_dhcp_pool und lucent_dhcp_status dienen dazu einen Lucent-QIP-DHCP-Server (nur Linux-Appliance) mittels SNMP zu überwachen.
Der Check erfüllt zwar seinen Zweck, ich bin jedoch noch nicht zufriden mit der Abfrage.
Aufgrund der MIB-Struktur muss ich für 1000 Subnetze über 100.000 OIDs abfragen und dies ist nicht performant.
Besser wäre es wohl die internen  Text-Datein (dhcpd.conf, dhcp.db) auszuwerten. 

**Installation:**  
Manuell:  
CMK-Server: den Check aus "checks/lucent_dhcp_failover" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  
CMK-Server: den Check aus "checks/lucent_dhcp_pool" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  
CMK-Server: den Check aus "checks/lucent_dhcp_status" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  


**Screenshort:**
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/lucent_dhcp_x/1.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/lucent_dhcp_x/3.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/lucent_dhcp_x/2.png)