***Beschreibung:***  
Mit livestatus_host.py kann man sich sehr einfach eine Host-Datei (/etc/hosts) aus allen CMK-Hosts erstellen.

Die Hosts werden jeweils pro CMK-Folder ausgegeben mit IP-Adresse, Hostname und Alias.

***Beispiel:***  


#/dummy
127.0.0.1            http_test                            		#http_test
80.69.98.110         dns_test                                 #dns_test


#
192.123.20.1        fw0                                       #test
192.123.20.30       test                                      #test


#/linux_server
127.0.0.1            tes                                     #test
