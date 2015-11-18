
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

Für jeden einzelnen Contex ist folgende Einstellung möglich:
- Default:
    Man kann einen Default Werte für WARN/CRIT hinterlegen, um z.B. die Serferfarmen einer Testumgebung immer auf OK zu belassen.
    Wenn dies eingestellt ist erscheint im "Status detail" der Text "[Default-Rule, orginal return status: WARN]" oder "[Default-Rule, orginal return status: CRIT]", der CMK Status ist jedoch der eingestellt Wert.
- für jede Serverfarm
    für jede Serverfarm kann (auch abweichend vom Default Wert) einzeln festgelegt werden welcher CMK Status zurückgegeben werden soll. Wenn dies eingestellt ist erscheint im "Status detail" der Text "[Individual-Rule, orginal return status: WARN]" oder "[Individual-Rule, orginal return status: CRIT]", der CMK Status ist jedoch der eingestellt Wert.

- Normalerweise werden die IPs der Endgeräte bei den einzelnen Servern der Serverfarm nicht angezeigt, sondern nur die IP des Loadbalancers, will man jedoch die IPs der Endgeräte auf den einzelnen Servern sehen, verwendet man route-maps auf den Core-Routern.
Dies führt jedoch dazu, dann immer nur der aktive Loadbanlacer Context OK ist, der Backup Context ist immer CRIT (kann nicht geroutet werden). Daher gibt es in WATO die Funktion "Show only short status of other nodes (only ACE)", dadurch wird nur noch der verkürzte Status der andern Nodes (z.B. -- other Cluster-Nodes: Nodename -> CRIT) angezeigt und nicht mehr die kompletten "Status details" der jeweiligen Node.

Cluster:  
Meinst werden Loadbanlacer im Cluster betrieben, daher ist der Check für den Cluster Betrieb ausgelegt. Hierbei werden zwei Hosts (zwei gleiche ACE Contexte auf zwei physikalischen ACEs) zusammengefallst, der schlechtere Status wird dabei ignoiert. Eigentich wäre es besser, denn Cluster Status (Check: cisco_ace_cluster) abzufragen und immer den Status den aktiven Context zu verwenden (so habe ich es bei F5-Check gelöst), jedoch kann der Cluster-Status nur im Admin-Context abgefragt werden.

Zunächst muss ein Cluster aus den beiden Hosts des gleichen Contextes erstellt werden, danach muss dann unter "Clustered services" eine Regel mit "Farm: .*" angelegt werden. Danach wertet der Check dann die Serverfarmen beider Hosts zu einem Service aus.



**INFO:**  
Auf einem Cisco ACE Loadbalancer können unterschiedliche Contexte angelegt werden.
Die Contexte können auf zwei unterschiedliche Arten abgefragt werden:
  1. Über die IP des Admin-Contextes
      -  um die einzelnen Contexte abzufragen (Ausnahme Admin-Context), muss an die SNMP-Community der Context-Name angehängt werden (z.B. Community@Context)
      - CMK unterstützt diese Art der SNMP-Community leider nicht
  2. Über die IP des jeweiligen Contextes
      - Ich habe für jeden Context in CMK einen Host mit der jeweiligen IP-Adresse angelegt, somit ist die SNMP-Community bei allen Contexten gleich.
      - Der Check cisco_ace_serverfarm funktioniert nicht im Admin-Context.

**TODO:**   
Der Plugin ist für Version 1.2.6p5 entwickelt worden, mit Version 1.2.7 muss die Datei ace_serverfarm.py angepasst werden, dies habe ich bis jetzt noch nicht gemacht. 

**Installation:**     
Manuell:  
CMK-Server: den Check aus "checks/cisco_ace_serverfarm" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  
CMK-Server: den Check aus "checks/lb.include nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren
CMK-Server: den Check aus "web/plugins/wato/ace_serverfarm.py nach "/omd/sites/SITE/local/share/check_mk/web/plugins/wato" kopieren



**Screenshort:**  
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/1.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/2.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/4.png)
![ScreenShot](https://github.com/christianbur/check_mk/blob/master/cisco_ace_serverfarm/5.png)
