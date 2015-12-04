#!/usr/bin/python
#
import socket
from device_cisco_hp import Device_cisco_hp
#from device_f5 import Device_f5
#from device_wlc import Device_wlc
import time
import sys
import re
import os


def recv_timeout(the_socket,timeout=2):
    #make socket non blocking
    the_socket.setblocking(0)

    #total data partwise in an array
    total_data=[];
    data='';

    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break

        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break

        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass

    #join all parts to make final string
    return ''.join(total_data)





def list_startswith(item, list):
	found = False
	for i in list:
		if item.startswith(i):
			found = True
			break

	return found

def list_find(item, list):
        found = False
        for i in list:
                if item.find(i) != -1:
                        found = True
                        break

        return found






def get_backuphosts(lql_answer_python):

        backuphosts = []
        backuphosts_ignored = []

	# alle Geraete die mit folgenden SNMP-Info Strings beginnen, werden gebackupt
        snmpinfo_cisco_hp = [ "sysDescr: Cisco IOS Software",
                        "sysDescr: Cisco Internetwork Operating System Software",
                        "sysDescr: Cisco NX-OS",
                        "sysDescr: HP J",
                        "sysDescr: ProCurve J",
			"sysDescr: Cisco Adaptive Security Appliance",
			"sysDescr: Content Switch",
			"sysDescr: ACE 4710 Application Control Engine Appliance"]

	#snmpinfo_f5 = ["sysDescr: Linux F5"]

	#snmpinfo_wlc = ["sysDescr: Cisco Controller"]

	#snmpinfo_all = snmpinfo_cisco_hp + snmpinfo_f5 + snmpinfo_wlc
	snmpinfo_all = snmpinfo_cisco_hp

	# Diese Hosts werden ignoritert
        ips_ignore = {  "10.1.1.1":"LB_01",
                        "10.2.2.2":"LB_02",
		     }


	# Entscheiden ob Hosten in der Tabelle gebackupt werden soll oder nicht.
        for host in lql_answer_python:
		(host_name, host_alias, host_address, plugin_output, host_filename) = host

                if list_find(plugin_output, snmpinfo_all) and not host_address.startswith("10.127.") and not host_address in ips_ignore.keys():
                        backuphosts.append(host)
                else:

                        backuphosts_ignored.append(host)

	# Listen sortieren
	backuphosts.sort(key=lambda tup: tup[0])
	backuphosts_ignored.sort(key=lambda tup: tup[0])

        return (backuphosts,backuphosts_ignored, snmpinfo_cisco_hp, snmpinfo_f5, snmpinfo_wlc)


# Holte die Config vom Host
def get_config_cisco_hp(host, log_file):

	(host_name, host_alias, host_address, plugin_output, host_filename) = host

        device = Device_cisco_hp(host_address.strip(),log_file)

	# Telnet fuer CSS Loadbalancer
	if plugin_output.find("sysDescr: Content Switch") != -1:
		device.set_prefer_telnet()

	device.logging("--- Hostname: " + host_name)
        #device.set_debug_mode(True)
        #device.set_demo_config_mode(True)



        tacacs_username = 'test'
        tacacs_tpasswort = 'test1'


	ips_dsl     = ["192.168.121.1", "192.168.121.2"]

	if list_startswith(host_address, ips_dsl  ):
		device.logging("--- Anmeldedaten: DSL-Switche")
		device.connect(tacacs_username, tacacs_tpasswort, 'test')
	else:
		device.logging("--- Anmeldedaten: TACACS only")
		device.connect(tacacs_username, tacacs_tpasswort)


        config = device.command("show running-config")

        write_memory_config(device, host)

        device.disconnect()

        return config


def write_memory_config(device, host):
        (host_name, host_alias, host_address, plugin_output, host_filename) = host


        snmpinfo_nexus = ["sysDescr: Cisco NX-OS"]
        snmpinfo_ace   = ["sysDescr: ACE 4710 Application Control Engine Appliance"]
        snmpinfo_css   = ["sysDescr: Content Switch"]
        snmpinfo_hp   = ["sysDescr: HP J", "sysDescr: ProCurve J"]

        if list_find(plugin_output, snmpinfo_nexus):
                save_output = device.command("copy running-config startup-config")

                if save_output.find("Copy complete") != -1:
                        device.logging("--- INFO: -copy running-config startup-config- erfolgreich ausgefuehrt")
                else:
                        device.logging("ERROR: -copy running-config startup-config- konnte NICHT erfolgreich ausgefuehrt werden!")
                        device.logging(save_output)

        elif list_find(plugin_output, snmpinfo_ace):
                save_output = device.command("write memory")

                if save_output.find("Sync Done") != -1:
                        device.logging("--- INFO: -write memory- erfolgreich ausgefuehrt")
                else:
                        device.logging("ERROR: -write memory- konnte NICHT erfolgreich ausgefuehrt werden!")
                        device.logging(save_output)

        elif list_find(plugin_output, snmpinfo_css):
                save_output = device.command("write memory")

                if save_output.find("Working..") != -1:
                        device.logging("--- INFO: -write memory- EVENTUELL erfolgreich ausgefuehrt")
                else:
                        device.logging("ERROR: -write memory- konnte NICHT erfolgreich ausgefuehrt werden!")
                        device.logging(save_output)

        elif list_find(plugin_output, snmpinfo_hp):
                save_output = device.command("write memory")
		if len(save_output) == 1 or len(save_output) == 2:
                        device.logging("--- INFO: -write memory- erfolgreich ausgefuehrt")
                #else:
                 #       device.logging("ERROR: -write memory- konnte NICHT erfolgreich ausgefuehrt werden!")
                  #      device.logging(save_output)

        else:
                save_output = device.command("write memory")

                if save_output.find("[OK]") != -1:
                        device.logging("--- INFO: -write memory- erfolgreich ausgefuehrt")
                else:
                        device.logging("ERROR: -write memory- konnte NICHT erfolgreich ausgefuehrt werden!")
                        device.logging(save_output)

#def get_config_f5(host, log_file, path):
#def get_config_wlc(host, log_file, date):



# Speichert eine Textdatei ab
def save_output(address, config, extension, path, date):
        #date = time.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = str(address) + "_" + str(date) + "." + extension
	config_file_path = path + file_name
        fh = open(config_file_path,"w")
        fh.writelines(config)
        fh.close()

	return config_file_path

def logging(log_file, msg):
	log_file.writelines(msg)
	print msg

def backup_devices(backuphosts, backuphosts_ignored, server, livestatus_log, snmpinfo_cisco_hp, snmpinfo_f5, snmpinfo_wlc):
        base_path = "/daten/backup/backup_config/"
	lastbackup_path = base_path + "lastbackup/"

        date = time.strftime("%Y-%m-%d")
        date_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = base_path + date + "_" + server[0] + "/"

        if not os.path.exists(path):
                os.mkdir(path)

	if not os.path.exists(lastbackup_path):
                os.mkdir(lastbackup_path)


	log_file_path = path + "DEVICELOG_" + date_time + ".log"
        log_file = open(log_file_path,"w")
	logging(log_file, livestatus_log)

        # Symlink Logfile  anlegen
        log_file_symlink = lastbackup_path + "DEVICELOG_" + server[0] + ".log"
        if os.path.islink(log_file_symlink):
        	os.unlink(log_file_symlink)
        os.symlink(log_file_path.replace(base_path,"../"), log_file_symlink)


        for host in backuphosts:
               	(host_name, host_alias, host_address, plugin_output, host_filename) = host

              	try:
			logging(log_file, "\n\n")
			config  =   "# CheckMK-host_name: "     + str(host_name)
			config += "\n# CheckMK-host_alias: "    + str(host_alias)
			config += "\n# CheckMK-host_address: " 	+ str(host_address)
			config += "\n# CheckMK-host_filename: " + str(host_filename)
			config += "\n# CheckMK-SNMPInfov2: "   	+ str(plugin_output)
			config += "\n#----------------------------------------------------------------\n\n\n\n"

			# Config vom Geraet holen
			if list_find(plugin_output, snmpinfo_cisco_hp):
                		device_config = get_config_cisco_hp(host,log_file)
		#	elif list_find(plugin_output, snmpinfo_f5):
		#		device_config = get_config_f5(host,log_file, path)
		#	elif list_find(plugin_output, snmpinfo_wlc):
		#		device_config = get_config_wlc(host, log_file, date)
			else:
				raise Exception("ERROR: Keine 'get_config()' Methode fuer Host gefunden!")

			if len(device_config) == 0:
                        	logging(log_file, "ERROR: Device config ist empty")
                      	config += device_config


			# Cofig in Datei schreiben
                        config_file_path = save_output(host_address, config, "config", path, date_time)
			logging(log_file,"--- Backupfile: " + config_file_path)

			# Symlink anlegen
			lastbackup_config_link = lastbackup_path + host_address + ".config"
			if os.path.islink(lastbackup_config_link):
				os.unlink(lastbackup_config_link)
			os.symlink(config_file_path.replace(base_path,"../"), lastbackup_config_link)

              	except Exception, e:
                     	logging(log_file,"ERROR: %s" % str(e) )
                        save_output(host_address, str(e), "error", path, date_time)

        # ------------------------------------------------------------
	if len(backuphosts_ignored) > 0:
		logging(log_file,"\n\n\n\nIgnored Hosts:\n\n")

	for host in backuphosts_ignored:
		(host_name, host_alias, host_address, plugin_output, host_filename) = host
		logging(log_file,"\nIP: " + host_address)
		logging(log_file,", Hosts: " + host_name)


        log_file.close()


def get_hostByLivestatus():

    	#socket_path = "/omd/sites/prod/tmp/run/live"
    	#s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    	#s.connect(socket_path)

    	all_server = [('1.1.1.1', 6557),('2.2.2.2', 6557)]

	lql  = "GET services\n"
        lql += "Columns: host_name host_alias host_address plugin_output host_filename\n"
        lql += "Filter: check_command = check_mk-snmp_info_v2\n"
        lql += "Filter: host_plugin_output !~ No IP packet received\n"
        lql += "OutputFormat: python\n"
	#lql += "Limit: 11\n"

    	for server in all_server:
		try:
			livestatus_log = ""
 			msg  = "\n#--------------------------------------------------------------------------------\n\n"
			msg += "Verbinde zu: " + str(server)
			livestatus_log += msg + "\n"
			print msg

                        max_attempts = 10
                        for attempt in range(max_attempts):
				msg = "Verbindungsversuch: #" + str(attempt)
				livestatus_log += msg + "\n"
                        	print msg

				# Verbinden zum Server und LQL abfragen
            			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            			s.connect(server)
            			s.send(lql)
            			s.shutdown(socket.SHUT_WR)
            			lql_answer = recv_timeout(s)

				if len(lql_answer) < 10:
					if attempt < max_attempts:
						time.sleep(20)
					else:
						raise Exception("ERROR: Es wurden keine Daten von Server empfangen!")
				else:
					break


            		#konvertiere Antwort in Python Sourcecode
			lql_answer_python = eval(lql_answer)

			if len(lql_answer_python) < 10:
                                raise Exception("ERROR: Die von Server empfangenen Daten konnten nicht in Python-Daten konvertiert werden!")


	    		# alle Host in der "table" werden auf die beidne Listen backuphosts, backuphosts_ignored aufgeteilt
            		(backuphosts, backuphosts_ignored, snmpinfo_cisco_hp, snmpinfo_f5, snmpinfo_wlc) = get_backuphosts(lql_answer_python)


	    		# Alle Geraete in backuphosts werden gebackupt
	    		backup_devices(backuphosts, backuphosts_ignored, server, livestatus_log, snmpinfo_cisco_hp, snmpinfo_f5, snmpinfo_wlc)
			#print backuphosts

		except Exception, e:
			livestatus_log += str(e) + "\n"
                        print str(e)
			backup_devices([], [], server, livestatus_log, [], [])




get_hostByLivestatus()
