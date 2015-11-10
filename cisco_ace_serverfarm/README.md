
**Beschreibung:**  
Der cisco_ace_serverfarm Check überwacht die einzelnen Serverfarmen eines Cisco ACE Loadbalancers (ACE 4710).

Als "Status details" werden folgende Werte angezeigt (siehe Screenshort 1.png und 2.png):
  - rServer: Anzahl der konfigurierten Server in der Serverfarm
  - inService: Anzahl der aktiven Server in der Serverfarm
  - OutOfOrder: deaktivierte Server
  - Error: Server mit einem Fehler
  - Error_detail: genauere Fehlermeldung

Perfdata:
   - TotalConns:   Anzahl der Verbindungen seit Neustart des Loadbalancers
   - FailedConns:  Anzahl der fehlerhaften Verbindungen seit Neustart des Loadbalancers
   - CurrentConns: Anzahl der aktuellen Verbindungen des rServers


Konfiguration der Serverfarmen:
 Der Check lässt sich sehr variabel über WATO konfigurieren.
 Man findet die Einstellungen unter "Host & Service Parameters -> ACE_F5_Serverfarm".

Für jeden einzelnen Contex ist folgende Einstellungen möglich
- Default:
    ich kann einen Default Werte für WARN/CRIT hinterlegen, um z.B. die Serferfarmen für eine Testumgebung immer auf OK zu belassen.
    Wenn dies eingestellt ist erschein im "Status detail" der Text "[Default-Rule, orginal return status: WARN]" oder "[Default-Rule, orginal return status: CRIT]"
- für jede Serverfarm
    für jede Serverfarm kann (auch abweichend vom Default Wert) einzeln festgelegt werden ob eine Alarmierung erfolgen soll.

- Bei einem ACE Loadbanlacer kann man auch noch "Error_detail" aus "Status details" entfernen.

Cluster:
Meinst werden Loadbanlacer im Cluster betrieben, daher kann der Check auch im Cluster verwendet werden.
Dafür muss zunächst ein Cluster aus den beiden Hosts des gleichen Contextes erstellt werden, danach muss dann unter "Clustered services" eine Regel mit "Farm: .*" angelegt werden. Danach wertet der Check dann die Serverfarmen beider Hosts zu einem Service aus.



**INFO:**
Auf einem Cisco ACE Loadbalancer können unterschiedliche Contexte angelegt werden.
Die Contexte können auf zwei unterschiedliche Arten abgefragt werden:
  1. Über die IP des Admin-Contextes
      -  um die einzelnen Contexte abzufragen (Ausnahme Admin-Context), muss an die SNMP-Community der Context-Name angehängt werden (z.B. Community@Context)
      - CMK unterstützt diese Art der SNMP-Community leider nicht
  2. Über die IP des jeweiligen Contextes
      - Ich habe für jeden Context in CMK einen Host mit der jeweiligen IP-Adresse angelegt, somit ist die SNMP-Community bei allen Contexten gleich.
      - Der Check cisco_ace_serverfarm funktioniert nicht im Admin-Context.


**Installation:**  
Manuell:  
CMK-Server: den Check aus "checks/cisco_ace_serverfarm" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  
CMK-Server: den Check aus "checks/lb.include nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren
CMK-Server: den Check aus "web/plugins/ace_serverfarm.py nach "/omd/sites/SITE/local/share/check_mk/web/plugins/" kopieren



**Screenshort:**  
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/1.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/2.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/4.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/5.png)
