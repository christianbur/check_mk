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


def get_HostByLivestatus():


        #all_server = [('10.33.20.213', 6557), ('10.33.20.210', 6557)]
	all_server = [('10.33.3.3', 6557)]
        lql  = "GET services\n"
        lql += "Columns: host_name host_alias host_address plugin_output host_filename\n"
        lql += "Filter: check_command = check_mk-snmp_info_v2\n"
        lql += "Filter: host_plugin_output !~ No IP packet received\n"
        lql += "OutputFormat: python\n"


        date = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = "./"
        log_file = open(path + "UPDATELOG_" + date + ".log","w")


        for server in all_server:
                try:

                        # Verbinden zum Server und LQL abfragen
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect(server)
                        s.send(lql)
                        s.shutdown(socket.SHUT_WR)
                        lql_answer = recv_timeout(s)

                        lql_answer_python = eval(lql_answer)

                        for host in lql_answer_python:
                                (host_name, host_alias, host_address, plugin_output, host_filename) = host

				if "C2950-I6Q4L2-M" in plugin_output:
					device = Device_cisco_hp(host_address,log_file)
					device.connect('user','pass','enable_pass','enable_pass_backup')
					firmware_update(device)


                except Exception, e:
                        print str(e)


	log_file.close()

def firmware_update(device):

	#2960
        #copy tftp://10.33.20.201/IOS/c2960-lanbasek9-mz.122-44.SE6.bin flash:
	#boot system flash:/c2960-lanbasek9-mz.122-44.SE6.bin




                                show_version = device.command("show version")


			        regex = re.compile("Model number: (.*)")
			        model = regex.findall(show_version)

				if len(model) != 1:
					device.logging("ERROR: Model konnten nicht ermittelt werden!")
					device.logging(show_version)
					return

				found_model = model[0]

				device.logging("--- Model number: " + found_model)

				if found_model in ["WS-C2950G-48-EI", "WS-C2950G-24-EI", "WS-C2950-24"]:
					new_firmware_size = 3722814
					new_firmware_file = "c2950-i6k2l2q4-mz.121-22.EA14.bin"
					new_firmware_md5  = "8d3250ee253b81b7fe2762e281773fbc"

					dir = device.command("dir")

					if dir.find("html") != -1:
						#device.command_raw("delete /recursive /force flash:/html")
						#output = device.command_with_clearbuffer("\n")
						output = device.command_sequence(["delete /recursive /force flash:/html",""])
						device.logging(output)

						dir = device.command("dir")

					if dir.find(new_firmware_file) == -1:
						regex = re.compile("bytes total \(([0-9]*) bytes free\)")
						bytes_free = regex.findall(dir)

						if len(bytes_free) != 1:
							device.logging("ERROR: Fehler beim ermitteln des freien Speichers!")
							device.logging(dir)
							return

						if int(bytes_free[0]) > new_firmware_size:

							output = device.command_sequence(["copy tftp://10.3.2.1/IOS/" + new_firmware_file + " flash:", ""])
                                        	        device.logging(output)

							dir = device.command("dir")

						else:
							device.logging("ERROR: zu wenige Speicher auf Switch frei!")
							device.logging(dir)
							device.logging(device.command("show boot"))
							return
					else:
						device.logging("INFO: Neue Firmware bereits vorhanden!")


                                       	regex = re.compile(".* ([0-9]*)  [A-Z]{1}[a-z]{2} .* " + new_firmware_file)

                                        bytes_firmware = regex.findall(dir)

                                       	if len(bytes_firmware) != 1:
                                        	device.logging("ERROR: Fehler beim ermitteln der Firmware groesse!")
                                                return

                                       	if int(bytes_firmware[0]) != new_firmware_size:
						device.logging("ERROR: Groesse der Firmware Datei NICHT OK!")

					verify = device.command("verify /md5 flash:/" + new_firmware_file + " " + new_firmware_md5)

					if verify.find("Verified (flash") != -1:
						device.logging("INFO: Firmware "+ new_firmware_file + " korrekt hochgeladen")
						show_boot = device.command("show boot")

					        regex = re.compile("^BOOT path-list\:       flash:\/" + new_firmware_file + "$",re.MULTILINE)
                                                show_boot_file = regex.findall(show_boot)

						if len(show_boot_file) == 0:
							device.command("conf t")
							device.command("boot system flash:/" + new_firmware_file)
							device.command("exit")
							print device.command("wr")
							show_boot = device.command("show boot")
						else:
							device.logging("INFO: Firmware als Bootvariable korrekt gesetzt")
						print show_boot
						#print device.command_sequence(["reload at 23:00",""])
						print device.command("wr")
					elif verify.find("Error verifying flash") != -1:
                                                device.logging("ERROR: Firmware "+ new_firmware_file + " NICHT korrekt hochgeladen!")
					else:
						device.logging(verify)
						device.logging("ERROR: Firmware "+ new_firmware_file + " wahrscheinlich NICHT korrekt hochgeladen!")

                                device.disconnect()





if __name__ == "__main__":
        get_HostByLivestatus()
