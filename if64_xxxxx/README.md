***Beschreibung:***  
Die beiden Checks if64_trunk und if64_neighbor erweitern den if64 Check von CheckMK. 

Auf HP und Cisco Switchen kann man pro Port eine Beschreibung hinterlegen, um so z.B. manuell den Nachbar-Switche zu hinterlegen.
Dies hat jedoch den Nachteil, dass die Informationen nicht immer aktuell sind, das haben auch die Hersteller erkannt und die Protokolle CDP und LLDP entwickelt.
Mit diesen Protokollen kann man die Nachbar-Switche (müssen das Protokoll ebenfalls unterstützen) erkennen. 
Man erhält z.B. folgende Informationen zum Nachbar-Switche:
	- Switch-Namen
	- Switch-Port
	- Switch-Typ
	- Switch-IP

Diese Möglichkeit nutze ich in den beiden Checks und zeige den Switch-Namen und Port des Nachbar-Switche in den Status-details an.
Diese Informationen werden beim Inventory als Parameter hinterleget, sobald sich der Switch-Namen/Port des Nachbar-Switche ändert geht der Service auf WARN.
Sollet der Switch-Port einmal down gehen, wird der zuletzt erkannte Nachbar-Switche und Port mit angezeigt, so ist die Fehlerbehebung einfacher.

Bei über 3000 Switchen ist es jedoch nicht sinnvoll alle Ports eines Switches mit dem if64 bzw. if64_neighbor zu überwachen.
Mit dem if64_trunk Check ist es daher möglich nur die relevanten Ports im Inventory zu finden.
Zu den relevanten Ports zähle ich folgendes:
	- Cisco/HP Trunk Ports (Uplinks zu andern Switchen)      -> Item-Name: If_Trunk x
		- Cisco: alles Ports die als Trunk  konfiguriert sind
		- HP: alle Ports mit mehreren Vlans  (Access-Ports mit VoiceVlan werden nicht gefunden)
	- Cisco PortChannel									     -> Item-Name: If_Po x
	- Ports an denen HP oder Cisco Geräte angeschlossen sind -> Item-Name: If_CDP/LLDP x
		- Im Check ist eingestellt, das alle Strings mit ["cisco", "ProCurve"] im CDP/LLDP-Typ gefunden werden (Ausnahme ["Phone", "ATA"]).
			- So finde ich z.B. Cisco AcesssPoints oder andere Switche an Access-Ports (z.B. Loops).
			- Einige Server z.B. VMWare ESX Server unterstützen auch CDP, diese werden jedoch vom Check ignoriert. 
	
Bei normalen Access-Switchen gibt es in der Regel nur 1 bis 2 Uplinks zu andern Switchen, der if64_trunk Check findet daher auch nur diese Uplink Ports.
Sobald ein neuer relevanter Ports auf einem Switch konfiguriert wird, wird er durch das "Check_MK inventory" automatisch erkannt. 


	
***Host Discovery:***
CheckMK bietet mit "Check_MK inventory" eine Möglichkeit neue Services auf dem Host zu finden, es bietet jedoch keine Möglichkeit neue Hosts zu finden.
Bei der Entwicklung der beiden Checks ist mir daher die Idee gekommen dies zu realisieren. 

Das Skript check_host ruft alle Services von if64_trunk, if64_neighbor und snmp_info_v2 mittels Livestatus von den CMK-Servern ab. 
Vereinfacht baue ich mir intern zwei Listen auf, einmal von allen gefunden SNMP-Namen (Check: snmp_info_v2) und einmal alle gefunden CDP/LLDP-Nachbarn (Check: if64_trunk, if64_neighbor).
Danach überprüfe ich ob für alle CDP/LLDP-Nachbarn auch ein SNMP-Name gefunden wurde, wenn nicht wird dieser Nachbar noch nicht durch CMK überwacht.
Zusätlich überprüft das Skript ob der SNMP-Name mit dem CMK-Namen übereinstimmt. 
In der Praxis müssen natürlich noch ein paar Anpassungen und Ausnahmen definiert werden, dies realisiere ich über folgende Config-Datein:
- domains.txt: die Domains von Switchen (z.b. Switch1.example.org -> example.org), da ich die Domain intern vom Switchnamen entferne
- firmware_remove_domain.txt: Bei einigen Cisco Firmware-Versionen wird die Domain nur in SNMP-Namen angezeit jedoch nicht im CDP-Namen. Um dies zu intern korrigieren, müssen die entsprechende Firmware-Versionen hier eingetragen werden.
  (INFO: ich bin mir gerade nicht sicher ob dies wirklich notwendig ist)
- hostname_wrong_ignore_startwith.txt: Manchmal ist es gewollt, dass der SNMP-Name und der CMK-Namen unterschiedlich sind
- neighbor_ignore_find.txt: Hier können Nachbar-Switche eingetragen werden die ignoriert werden sollen (Suche mit find, nützlich für ganze Domains z.B. alle QSC-Router)
- neighbor_ignore_startswith.txt: Hier können Nachbar-Switche eingetragen werden die ignoriert werden sollen (Suche mit startswith, nützlich für einzelne SNMP-Namen )

Durch dieses Host Discovery werden in unserm Netzwerk nun (fast) alle neuen Switche gefunden. 
Die Information über neue Switche wird in einer Text-Datei protkolliert, diese kann mit mk_logwatch überwacht werden. 
Ich befürchte aber, dass dieses Skript für jede Umgebung angepasst werden muss. 

**Installation:**   
Manuell:   
CMK-Server: den Check aus "checks/CMK-VERSION/if64_neighbor" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren   
CMK-Server: den Check aus "checks/CMK-VERSION/if64_trunk" nach "/omd/sites/SITE/local/share/check_mk/checks/" kopieren  

CMK-Server: den Check aus "web/plugins/perfometer/if64_trunk_perfometer.py" nach "/omd/sites/SITE/local/share/check_mk/web/plugins/perfometer" kopieren  

***Info:***
Da die Checks if64_trunk und if64_neighbor ersetzen muss der if64 deaktiviert werden.
Ich habe das über Tags wie folgt gelöst:
	Tag erstellen:
		Name : if64-Check	
			- if64_trunk -> Trunks und Portchannel (if64_trunk)
			- if64_neighbor -> Alle Interfaces mit CDP und LLDP (if64_neighbor)
			- if64_original	-> Original if64
			- LEER -> Deaktiviert
	Host & Service Parameters -> Disabled checks
		"if64-Check" isnot 	"Trunks und Portchannel (if64_trunk)"
			Check if64_trunk deaktivieren
		"if64-Check" isnot 	"Alle Interfaces mit CDP und LLDP (if64_neighbor)"
			Check if64_neighbor deaktivieren
		"if64-Check" isnot 	"Original if64"
			Check if64 deaktivieren
			
Mit diesen Tags kann man dann pro Host/Folder einstellen welchen if64 Check man verwenden will.
		
			

***Screenshort:***
![ScreenShot](httpsgithub.comchristianburcheck_mkblobmastersnmp_info_v2screenshort_snmp_info_v2.png)

Seriennummer hat sich geändert
![ScreenShot](httpsgithub.comchristianburcheck_mkblobmastersnmp_info_v2screenshort_snmp_info_v2_changed.png)

Cisco Firmware ohne SSH
![ScreenShot](httpsgithub.comchristianburcheck_mkblobmastersnmp_info_v2screenshort_snmp_info_v2_keineSSHFirmware.png)

