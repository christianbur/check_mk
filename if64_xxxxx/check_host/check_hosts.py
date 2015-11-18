#!/usr/bin/python
#
import socket
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
		if item.lower().startswith(i.lower()):
			found = True
			break

	return found

def list_find(item, list):
        found = False
        for i in list:
                if item.lower().find(i.lower()) != -1:
                        found = True
                        break

        return found

def read_file(filename):

	file = open(filename, 'r')

	list = []
	for line in file:
		list.append(line.strip())	

	return list



def get_neighbors(host, neighbor, neighbor_ignore_start, neighbor_ignore_find): 

    	(host_name, host_alias, host_address, plugin_output, host_filename) = host

    	######## find LLDP Hostname     
    	if plugin_output.startswith("OK - [LLDP:"):
            	lldp_hostname_with_interface = plugin_output.split(" -- ")[0].replace("OK - [LLDP: ","").strip()
            	lldp_hostname = lldp_hostname_with_interface.split("...")[0]
            	if lldp_hostname not in neighbor.keys() and not list_startswith(lldp_hostname, neighbor_ignore_start) and \
                    	not list_find(lldp_hostname, neighbor_ignore_find):

                    	neighbor[lldp_hostname] = (lldp_hostname_with_interface, "LLDP", host_name)

    	######## find CDP Hostname
    	if plugin_output.startswith("OK - [CDP:"):
            	if plugin_output.startswith("OK - [CDP: ["):
                    	plugin_output_cdp = plugin_output.split(" -- ")[0].replace("OK - [CDP: [","").replace("]","").strip().split()
                    	cdp_sysname_all = []
                    	for cdp_hostname_with_interface in plugin_output_cdp:
                            	cdp_sysname_all.append(cdp_hostname_with_interface)
            	else:
                     	cdp_hostname_with_interface = plugin_output.split(" -- ")[0].replace("OK - [CDP: ","").strip()
                     	cdp_hostname_with_interface = cdp_hostname_with_interface.replace("domain.d...","domain.de...")
                     	cdp_hostname_all = [cdp_hostname_with_interface]

            	for cdp_hostname_with_interface in cdp_hostname_all:
                    	cdp_hostname = cdp_hostname_with_interface.split("...")[0]
                    	if cdp_hostname not in neighbor.keys() and not list_startswith(cdp_hostname, neighbor_ignore_start) and \
                            	not list_find(cdp_hostname, neighbor_ignore_find):

                            	neighbor[cdp_hostname] = (cdp_hostname_with_interface, "CDP", host_name)

	
def get_sysname(host, sysname, domains, firmware_remove_domain):

	(host_name, host_alias, host_address, plugin_output, host_filename) = host

	
	hostname = plugin_output.split(" ---- ")[0].replace("OK - sysName: ","").strip()
	if hostname.startswith("WARN - SerialNum changed"):
		hostname = hostname.split(" -- ")[1].replace("sysName: ","")
	
	if hostname not in sysname:
		if list_find(plugin_output, firmware_remove_domain):
			hostname_tmp = hostname
			for domain in domains:
				if hostname_tmp.endswith(domain):
					hostname_tmp = hostname_tmp.replace(domain,"")
			sysname.append(hostname_tmp)
		else:
			sysname.append(hostname)


def get_hostname_wrong(host, domains, hostname_wrong, hostname_wrong_ignore_start):

	(host_name, host_alias, host_address, plugin_output, host_filename) = host

   	host_name_tmp = host_name.replace("-Primary","").replace("-Secondary","").lower()
	hostname = plugin_output.split(" ---- ")[0].replace("OK - sysName: ","").strip()

   	hostname_tmp = hostname.lower()
   	for domain in domains:
           	if hostname_tmp.endswith(domain):
                   	hostname_tmp = hostname_tmp.replace(domain.lower(),"")


   	if hostname.startswith("SW"):
           	hostname_wrong.append( (host_name, hostname) )


   	if host_name_tmp != hostname_tmp:
           	if not list_startswith(hostname, hostname_wrong_ignore_start):
                   	if host_name.startswith("SW"):
                           	host_name_tmp = hostname.split("_")[0] + "_" + host_name.replace("SW","")
                           	if hostname.startswith("SW"):
                                   	hostname_wrong.append( (host_name, hostname) )
                           	if host_name_tmp != hostname.split(".")[0].replace("+","A"):
                                   	hostname_wrong.append( (host_name, hostname) )
                   	else:
                           	hostname_wrong.append( (host_name, hostname) )


def get_ips_duplicate(host, ips_duplicate, ips_all):

	(host_name, host_alias, host_address, plugin_output, host_filename) = host

	if host_address in ips_all.keys():
        	ips_duplicate[host_address] = ips_all[host_address]
                ips_duplicate[host_address].append(host_name)
       	else:
          	ips_all[host_address] =  [host_name]


def check_hosts(path, lql_answer_python, ips_all, neighbor, sysname, ips_duplicate, hostname_wrong):
	neighbor_ignore_start        = read_file(path + "config/neighbor_ignore_startswith.txt")
	neighbor_ignore_find         = read_file(path + "config/neighbor_ignore_find.txt")
	hostname_wrong_ignore_start  = read_file(path + "config/hostname_wrong_ignore_startwith.txt")
	domains                      = read_file(path + "config/domains.txt")
	firmware_remove_domain       = read_file(path + "config/firmware_remove_domain.txt")
	
	for host in lql_answer_python:

		(host_name, host_alias, host_address, plugin_output, host_filename) = host
		
		get_neighbors(host, neighbor, neighbor_ignore_start, neighbor_ignore_find)	
               
		if plugin_output.startswith("OK - sysName:") or plugin_output.startswith("WARN - SerialNum changed"):                 		
			get_sysname(host, sysname, domains, firmware_remove_domain)		
			get_hostname_wrong(host, domains, hostname_wrong, hostname_wrong_ignore_start)
			get_ips_duplicate(host, ips_duplicate, ips_all)



def print_hosts(path, ips_all, neighbor, sysname, ips_duplicate, hostname_wrong, livestatus_log):
	lastcheck_path = path + "log/"
	date_time = time.strftime("%Y-%m-%d_%H-%M-%S")

	log_file_symlink = lastcheck_path + "check_host_last" + ".log"
        log_file_path = lastcheck_path + "check_hosts_" + date_time + ".log"
	log_file = open(log_file_path,"w")

	if not os.path.exists(lastcheck_path):
                os.mkdir(lastcheck_path)


	log_file.writelines(livestatus_log)



	output  = "\nChecked Hosts: %s" % (len(ips_all))
	output += "\nDate: %s\n\n" % (date_time)
	
	for host in neighbor.keys():
		if host not in sysname:
			output += "ERROR: Neuer Host: %-60s gefunden mit %4s, von:  %s\n" % neighbor[host]

	output += "\n"
        for ip in ips_duplicate.keys():
		output += "ERROR: Doppelte IP: %.20s, Hostnames: %s\n" % (ip, ips_duplicate[ip])


        output += "\n"
        for host in hostname_wrong:
                output += "ERROR: Hostname falsch -- Check_MK-Name: %-30s, SNMP-SysName: %-30s\n" % host

	print output

	if output.find("ERROR") != -1:
		log_file.writelines(output)
	

		if os.path.islink(log_file_symlink):
                	os.unlink(log_file_symlink)
        	os.symlink(log_file_path, log_file_symlink)
	
	log_file.close()
	

def get_hostByLivestatus():

    	#socket_path = "/omd/sites/prod/tmp/run/live"
    	#s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    	#s.connect(socket_path)

    	all_server = [('10.33.20.210', 6557),('10.33.20.213', 6557)]
	#all_server = [('10.33.20.213', 6557)]	


	lql  = "GET services\n"
        lql += "Columns: host_name host_alias host_address plugin_output host_filename\n"
        lql += "Filter: check_command = check_mk-snmp_info_v2\n"
	lql += "Filter: check_command = check_mk-if64_trunk\n"
	lql += "Filter: check_command = check_mk-if64_neighbor\n"
	lql += "Or: 3\n"
        lql += "Filter: host_plugin_output !~ No IP packet received\n"
	lql += "Filter: host_plugin_output !~ No Response from host\n"
	lql += "And: 3\n"
        lql += "OutputFormat: python\n"
	#lql += "Limit: 11\n"




	neighbor = {}
	sysname  = []
	ips_all	     = {}
	ips_duplicate = {}
	hostname_wrong = []

	livestatus_log = ""
	msg  = "\n#--------------------------------------------------------------------------------"
	livestatus_log += msg + "\n"
	print msg


	path = "/daten/python/PROD/check_hosts/"

    	for server in all_server:
		#try:
			msg = "\n\nVerbinde zu: " + str(server)
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
						time.sleep(10)
					else:
						raise Exception("ERROR: Es wurden keine Daten von Server empfangen!")
				else:
					break


            		#konvertiere Antwort in Python Sourcecode		
			lql_answer_python = eval(lql_answer) 

			if len(lql_answer_python) < 10:
                                raise Exception("ERROR: Die von Server empfangenen Daten konnten nicht in Python-Daten konvertiert werden!")
				
			check_hosts(path, lql_answer_python, ips_all, neighbor, sysname, ips_duplicate, hostname_wrong)

		#except Exception, e:
		#	livestatus_log += str(e) + "\n"
                 #       print str(e)	
	
	print_hosts(path, ips_all, neighbor, sysname, ips_duplicate, hostname_wrong, livestatus_log)

get_hostByLivestatus()
