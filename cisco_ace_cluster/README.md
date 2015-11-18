**Beschreibung:**  
Der cisco_ace_cluster Check überwacht die "fault tolerance groups" eines Cisco ACE Loadbalancers (ACE 4710).
Sobald sich der Zustand ändert, meldet der Check einen Alarm.

**INFO:**
Auf einem Cisco ACE Loadbalancer können unterschiedliche Contexte angelegt werden.
Die Contexte können auf zwei unterschiedliche Arten abgefragt werden:
  1. Über die IP des Admin-Contextes
      -  um die einzelnen Contexte abzufragen (Ausnahme Admin-Context), muss an die SNMP-Community der Context-Name angehängt werden (z.B. Community@Context)
      - CMK unterstützt diese Art der SNMP-Community leider nicht
  2. Über die IP des jeweiligen Contextes
      - Ich habe für jeden Context in CMK einen Host mit der jeweiligen IP-Adresse angelegt, somit ist die SNMP-Community bei allen Contexten gleich.
      - Der Check cisco_ace_cluster funktioniert nur im Admin-Context.


**Installation:**    
Manuell:  
CMK-Server: den Check aus "checks/cisco_ace_cluster" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  



**Screenshort:**  
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_cluster/1.png)
