from device_cisco_hp import Device_cisco_hp
import time
import sys
import re
import socket


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


def read_file(filename):

        file = open(filename, 'r')

        list = []
        for line in file:
                list.append(line.strip())

        return list


def get_HostByLivestatus():


        all_server = [('10.3.3.3', 6557)]
        lql  = "GET services\n"
        lql += "Columns: host_name host_alias host_address plugin_output host_filename\n"
        lql += "Filter: check_command = check_mk-snmp_info_v2\n"
        lql += "Filter: host_plugin_output !~ No IP packet received\n"
        lql += "OutputFormat: python\n"


	date = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = "./"
	log_file = open(path + "CHANGELOG_" + date + ".log","w")


        for server in all_server:
                try:

                	# Verbinden zum Server und LQL abfragen
                      	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                       	s.connect(server)
                      	s.send(lql)
                      	s.shutdown(socket.SHUT_WR)
                      	lql_answer = recv_timeout(s)

                        lql_answer_python = eval(lql_answer)


			lql_answer_python_dopple = []
			for host in lql_answer_python:
				lql_answer_python_dopple.append(host)
				lql_answer_python_dopple.append(host)



                        for host in lql_answer_python:
                                (host_name, host_alias, host_address, plugin_output, host_filename) = host

                		print host
				if "cisco".lower() in plugin_output:

                                                device = Device_cisco_hp(host_address,log_file)
						device.logging("--- cmk_host_filname: "+ host_filename)
                                                device.connect('user','pass',"enable_pass")
                                                config = device.command("show running-config")
                                                print config

						#device.command("wr")
						device.disconnect()
                except Exception, e:
                        print str(e)







def save_output(ip, config, extension, path,date):
        #date = time.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = str(ip) + "_" + str(date) + "." + extension
        fh = open(path + file_name,"w")
        fh.writelines(config)
        fh.close()


if __name__ == "__main__":
        get_HostByLivestatus()
