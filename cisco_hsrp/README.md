**Beschreibung:**  
Ich habe den cisco_hsrp Check etwas angepasst (siehe Screenshorts) um sie im produktiven Betieb besser benutzen zu können.
So werden z.B. auch falsch konfigurierte HSRP-Interface gemeldet. 

**Installation:**  
Manuell:  
CMK-Server: den Check aus "checks/cisco_hsrp" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  



**Screenshort:**  
Active HSRP-Router
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_hsrp/2.png)

Standby HSRP-Router
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_hsrp/1.png)

Fehelr in HSRP Config
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_hsrp/3.png)

Failover
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_hsrp/4.png)
