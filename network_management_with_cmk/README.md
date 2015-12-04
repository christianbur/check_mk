**Beschreibung:**  
Die Python-Klasse device_cisco_hp.py gehört zu meinen ersten Python Projekten.
Ziel dieser Bibliothek war es mittels Python auf ca. 3000 Switchen zuzugreifen und automatisiert Änderungen in der Config vorzunehmen.

Jetzt werden die meisten wahrscheinlich denken, das gibts es doch alles schon, ich hatte jedoch spezielle Anforderungen.
Da alle Switche unterschiedlich konfiguriert waren, musste das Skript selbst entscheiden wie es sich verbindet (SSH/Telet) und wie es sich anmeldet.

Unterstützte Geräte:
  - Cisco IOS
  - Cisco Nexus
  - Cisco ASA
  - HP Procurve

Automatische Wahl des Protokolls:
  - SSH
  - Telnet

Automatische Wahl der Anmeldung:
  - Benutzername, Passwort
  - Benutzername, Passwort, enable, Passwort
  - Benutzername, Passwort, enable, enable-Passwort
  - Passwort, enable, Passwort
  - Benutzername, local-Passwort, enable, enable-Passwort
  - usw.

***Beispiel:***  
device = Device_cisco_hp("192.168.1.1")
device.connect('user','pass',"enable_pass")
config = device.command("show running-config")
print config
device.disconnect()


In der Datei get_config.py ist ein einfaches Beispiel welches mittels Livestatus die Daten der Hosts abfragt und dann
mittels der hier vorgestellten Bibliothek die Config abruft.

In der Datei firmwreupdate.py ist ein Beisiel für ein Firmwareupdate gezeigt.

Mit dem Skript backup_switch.py (etwas gekürzt) sicher ich selbst ca. 2500 Geräte zweimal in der Woche.

***Beispiel Log:***
```python
#----------------------------------------------------------------------------------
--- try ip: 1.1.1.x
--- start connection: 2015-11-08 20:57:15.659776
--- Hostname: Switch1
--- Anmeldedaten: TACACS only
--- connect to ip: 1.1.1.x, port: 22
--- SSH Login
--- Found: user prompt, sent -enable- command
--- Found: password prompt, enter -TACACS PASSWORD-
--- Found: priv prompt (Exit Loop)
--- login sequence: CONNECT_SSH-SSHLOGIN-USERPROMPT_ENABLE-TPASSWORD-PRIVPROMPT
--- switchname: Switch1
--- set prompt: Switch1[+A-Za-z0-9_-]{0,15}>, priv: Switch1[+A-Za-z0-9_-]{0,15}#, config: Switch1[+A-Za-z0-9_-]{0,15}\(config[+A-Za-z0-9_-]{0,15}\)#
--- SSH connection established to: 1.1.1.x
--- execute command (Prompt: PRIVE ): show running-config
--- execute command (Prompt: PRIVE ): write memory
--- end connection: 2015-11-08 20:57:31.912027 (processing time: 0:00:16.252223)
--- disconnect - ip: 1.1.1.x
--- Backupfile: /daten/backup/backup_config/2015-11-08_2.2.2.2/10.5.10.11_2015-11-08_18-00-04.config


#----------------------------------------------------------------------------------
--- try ip: 1.1.1.x
--- start connection: 2015-11-08 18:11:54.076576
--- Hostname: Switch2
--- Anmeldedaten: TACACS only
--- connect to ip: 1.1.1.x, port: 23
--- Found: username prompt, enter -backup_cmk-
--- Found: password prompt, enter -TACACS PASSWORD-
--- Found: user prompt, sent -enable- command
--- Found: password prompt, enter -TACACS PASSWORD-
--- Found: priv prompt (Exit Loop)
--- login sequence: CONNECT_TELNET-TUSERNAME-TPASSWORD-USERPROMPT_ENABLE-TPASSWORD-PRIVPROMPT
--- switchname: Switch2
--- set prompt: Switch2[+A-Za-z0-9_-]{0,15}>, priv: Switch2[+A-Za-z0-9_-]{0,15}#, config: Switch2[+A-Za-z0-9_-]{0,15}\(config[+A-Za-z0-9_-]{0,15}\)#
--- Telnet connection established to: 1.1.1.x
--- execute command (Prompt: PRIVE ): show running-config
--- execute command (Prompt: PRIVE ): write memory
--- end connection: 2015-11-08 18:12:21.851208 (processing time: 0:00:27.774603)
--- disconnect - ip: 1.1.1.x
--- Backupfile: /daten/backup/backup_config/2015-11-08_2.2.2.2/1.1.1.x_2015-11-08_18-00-04.config
```

***dynamische Anpassung der Config:***   

Mit dem nachfolgenden Skript kann man z.B. dynamisch während der Laufzeit entscheiden, ob man eine Config ändert muss.
Muss man z.B. auf allen Geräten die SNMP-Community ändern, kann man dies wie folgt tun.
Zunächst speichert man in old_snmp die akutellen "snmp-server community" Config-Zeilen.
In new_snmp definiert man die gewünschte neue SNMP-Community.

Das Skripte setzt nun die neue Community und entfernt alle andern Zeilen.
Bei einem erneuten Aufrufe wird nichts mehr geändert, da bereits alles wie gewünscht gesetzt ist. 



```python
device = Device_cisco_hp("192.168.1.1")
device.connect('user','pass',"enable_pass")
config = device.command("show running-config")


regex = re.compile("snmp-server community .*")
old_snmp = [s.strip() for s in regex.findall(config)]

new_snmp = ["snmp-server community testcommunity RO 88"]

for i in old_snmp:
        if i not in new_snmp:
                device.command("no " + i)

for i in new_snmp:
        if i not in old_snmp:
                device.command(i)


device.disconnect()

```

***API:***  

```python
def __init__(self, ip, log_file=None):
    Das Skript benötigt nur eine IP-Adresse, das Skript entscheidet dann selbst ob es sich mit  Telnet (23) oder SSH (22) verbindet.
    Es kann optinal noch ein Log-Datei mitgegeben werden

def get_ip(self):
    Liefert die IP-Adresse des Gerätes.

def get_command_counter(self):
    Gbit die Anzahl der bereits ausgeführten Befehle zurück

def set_debug_mode(self,mode):
    für Debug

def set_demo_config_mode(self,mode):
    Befehle in "config"-Modus werden nicht ausgeführten
    mode -> True/False

def get_demo_config_mode(self):
    Abfrage ob man sich im demo Modus befindet

def set_prefer_ssh(self):
    SSH Verbindung wird bevorzugt, wenn das Geräte Telnet und SSH kann

def set_prefer_telnet(self):
    Telnet Verbindung wird bevorzugt, wenn das Geräte Telnet und SSH kann

def get_tacacs_username(self):
    gibt den gesetzen Usernamen zurück

def get_tacacs_password(self):
    gibt das gesetze Passwort zurück

def get_local_password(self):
    gibt das gesetzte local Passwort zruück

def get_enable_password(self):
    gibt das gesetzte enable Passwort zruück

def use_local_password(self):
    Sagt dem Skript, dass es das local_password nutzen soll und nicht das tacacs_password.
    Habe ich nur für eine Ausnahme benötigt

def use_enable_password(self):
   Sagt dem Skript, dass es das enable_password nutzen soll und nicht das tacacs_password.
   Habe ich nur für eine Ausnahme benötigt

def set_force_enable_password(self):
    Keine Ahnung wofür ich das benötigt habe

def get_loginsequence(self):
    Da das Skript selbst entscheidet wie es sich anmeldet kann man über diese Funktion die Loginsequence abfragen
    z.B. CONNECT_SSH-SSHLOGIN-USERPROMPT_ENABLE-TPASSWORD-PRIVPROMPT, CONNECT_TELNET-TUSERNAME-TPASSWORD-USERPROMPT_ENABLE-TPASSWORD-PRIVPROMPT

def logging(self,text):
    Über die Methode kann man beliebingen Text in die übergebene Log-Datei schreiben

def get_port(self):
    Gbit den Port zurück, entweder 23 (Telnet) oder 22 (SSH)

def get_switchname(self):
    Gibt den ermittelten Switchname zurück

def is_alive(self):
    wenn das Skript einen offenen Port (22 oder 23) gefunden hat, wird True zurückgegeben

def connect(self,tacacs_username, tacacs_password, local_password = None, enable_password = None):
    Über diese Methode werden dem Geräte-Objekt die Anmeledaten mitgeteilt.
    Wenn die einzelnen Werte für die Anmeldung nicht benötigt werden, werden die Werte jeweils ignoriert.

def command(self,cmd,timeout_prompt=300):
    Mit dieser Funktion werden dem Geräte einzelne Befehler übergeben.
    z.B. device.command("show running-config")
    Da die Ausgabe einer Config manchmal etwas länger dauert kann hier optional noch der timeout angegeben werden.

def command_sequence(self,cmd_list,time_between=2,timeout_prompt=300):
    Normalerweise erscheint nach der Eingabe eines Befehls der Prompt wieder, es gibt jedoch Cisco-Befehl bei denen denen ganze Sequenzen eingegeben werden müssen.
    z.B. der beim Update der Fimware
    device.command_sequence(["copy tftp://10.3.2.1/IOS/" + new_firmware_file + " flash:", ""])

    Das letze '""' geht für Enter

def disconnect(self):
    Meldet sich wieder vom Gerät ab


```
