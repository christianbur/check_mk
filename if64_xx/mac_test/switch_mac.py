import netsnmp
import re
import threading
import Queue
import socket
import time

class MAC_SNMP(object):
        # http://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/44800-mactoport44800.html

        def __init__(self, ip_address, snmp_community, folder, mac_decode_dict):
            self.__ip_address      = ip_address
            self.__snmp_community  = snmp_community
            self.__mac_decode_dict = mac_decode_dict
            self.__folder = folder

        def __get_oid(self, oid, index = ""):

            if index != "":
                snmp_community_index = self.__snmp_community + "@" + index
            else:
                snmp_community_index = self.__snmp_community

            oid_varlist = netsnmp.VarList(netsnmp.Varbind(oid))

            session = netsnmp.Session(DestHost= self.__ip_address, Version=2, Community=snmp_community_index, Retries=1)
            session.UseLongNames = 1
            session.UseNumeric = 1

            res = session.walk(oid_varlist)


            result_dict = {}
            i = 0
            for var in oid_varlist:
                if var.tag != None:
                        oid_suffix = var.tag.replace(oid,"") + "." + var.iid

                        if oid_suffix[:1] == ".":
                                oid_suffix = oid_suffix[1:]
                        result_dict[oid_suffix] = res[i]
                        i += 1

            return result_dict


        def get_sysName(self):
            oid = '.1.3.6.1.2.1.1.5'
            res = self.__get_oid(oid)
            return res["0"]

        def get_vlans(self):
            oid = '.1.3.6.1.4.1.9.9.46.1.3.1.1.2.1'
            res = self.__get_oid(oid)
            return res.keys()



        def __convert_mac_decimal2hex(self,mac_decimal):
                mac_list = []
                for x in  mac_decimal.split("."):
                        x_string = str(hex(int(x))).replace("0x","")
                        if len(x_string) == 1:
                                x_string = "0" + x_string
                        mac_list.append(x_string)

                return "".join(mac_list)


                mac = "".join( [str(hex(int(x))).replace("0x","") for x in mac_decimal.split(".")] )

        def __get_mac_vlan_hp(self):
                oid_macs = '.1.3.6.1.2.1.17.4.3.1.2'
                macs_dict   = self.__get_oid(oid_macs)

                all_macs = []

                for mac_decimal in macs_dict:
                        if_index = macs_dict[mac_decimal]
                        vlan = "-"
                        mac = self.__convert_mac_decimal2hex(mac_decimal)

                        mac_string = "%s;%s;%s" % (vlan,if_index, self.__mac_formatter(mac))
                        all_macs.append( mac_string)

                return all_macs

        def __get_mac_vlan_cisco(self, all_vlans):
            oid_macs_vlan = '.1.3.6.1.2.1.17.4.3.1.1'
            oid_bridge_port_number = '.1.3.6.1.2.1.17.4.3.1.2'
            oid_bridge_port_2_ifIndex = ".1.3.6.1.2.1.17.1.4.1.2"

            all_macs = []

            for vlan in all_vlans:
                macs_vlan_dict   = self.__get_oid(oid_macs_vlan, vlan)
                bridge_port_number_dict = self.__get_oid(oid_bridge_port_number, vlan)
                bridge_port_2_ifIndex_dict = self.__get_oid(oid_bridge_port_2_ifIndex, vlan)

                for if_index_mac in  macs_vlan_dict.keys():
                        mac_hex =  macs_vlan_dict[if_index_mac]
                        mac =  "".join ([ "%02X" % ord( x ) for x in list(mac_hex)])
                        bridge_port_number = bridge_port_number_dict.get(if_index_mac, "UNKNOWN")
                        if_index = bridge_port_2_ifIndex_dict.get(bridge_port_number, "UNKNOWN")

                        mac_string = "%s;%s;%s" % (vlan,if_index, self.__mac_formatter(mac))
                        all_macs.append( mac_string)

            return all_macs

        def __mac_formatter(self,mac):
                mac_formatted = mac + " (ERROR)"
                if len(mac) == 12:
                        mac = mac.upper()
                        mac_formatted = "%s%s:%s%s:%s%s:%s%s:%s%s:%s%s" % (tuple(list(mac)))
                        if mac_formatted[:8] in self.__mac_decode_dict:
                                mac_formatted += " (" + self.__mac_decode_dict[mac_formatted[:8]] +")"
                return mac_formatted

        def collect_macs(self):
            hostname  = self.get_sysName()


            all_vlans = self.get_vlans()

            if len(all_vlans) != 0:
                all_macs = self.__get_mac_vlan_cisco(all_vlans)
            else:
                all_macs = self.__get_mac_vlan_hp()


            filename = self.__folder + hostname

            fh = open(filename,"w")
            fh.write("\n".join(all_macs))
            fh.close()


            return (hostname, len(all_macs))


class  MAC_SNMP_Thread(object):

        def __init__(self, number_worker, ips_community_list):
            self.__mac_decode_dict =  self.__read_mac_file("./oui_wireshark.db")


	    print self.__mac_decode_dict

            self.__IP_Queue = Queue.Queue()

            print "Starting workers..."
            for i in range(number_worker):
                        t = threading.Thread(target=self.worker)
                        t.daemon = True
                        t.start()
            print "Workers started"

            for ip in ips_community_list:
                self.__IP_Queue.put(ip)
            self.__IP_Queue.join()
            print "Exiting"

        def worker(self):
            name = threading.currentThread().getName()
            print "Thread %s started" % name

            while True:
                (ip_address, snmp_community, folder) = self.__IP_Queue.get()
                print "Processing ip %s" % ip_address
                try:
                        (hostname, count_mac) = MAC_SNMP(ip_address, snmp_community, folder, self.__mac_decode_dict).collect_macs()
                        print "Hostname: %s, MACs found: %s" % (hostname, count_mac)
                except Exception as e:
                        print str(e)


                self.__IP_Queue.task_done()

        def __read_mac_file(self, filename):

                fh = open(filename)

                mac_dict = {}
                for line in fh:
                        if line.startswith("#") or line.strip() == "" :
                                continue

                        regex = re.compile("^([0-9a-zA-z:\/]*)\s(.*)\s#(.*)$")
                        m = re.search(regex, line)
                        if m:
                                prefix_mac = m.group(1).strip()
                                vendor     = m.group(2).strip()
                                desc       = m.group(3).strip()

                                mac_dict[prefix_mac] = vendor

                return mac_dict



##################################################################
# Livestatus Abfrage
##################################################################

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



def get_backuphosts(lql_answer_python):

        backuphosts = []
        backuphosts_ignored = []

        # alle Geraete die mit folgenden SNMP-Info Strings beginnen, werden gebackupt
        snmpinfo_cisco_hp = [ "sysDescr: Cisco IOS Software",
                              "sysDescr: Cisco Internetwork Operating System Software",
                              "sysDescr: HP J",
                              "sysDescr: ProCurve J"]


        snmpinfo_all = snmpinfo_cisco_hp

        # Diese Hosts werden ignoritert
        ips_ignore = {  "10.79.175.67":"test",
                     }


        # Entscheiden ob Hosten in der Tabelle gebackupt werden soll oder nicht.
        for host in lql_answer_python:
                (host_name, host_alias, host_address, plugin_output, host_filename) = host

                if list_find(plugin_output, snmpinfo_all) and not host_address.startswith("10.126.") and not host_address in ips_ignore.keys():
                        backuphosts.append(host)
                else:

                        backuphosts_ignored.append(host)

        # Listen sortieren
        backuphosts.sort(key=lambda tup: tup[0])
        backuphosts_ignored.sort(key=lambda tup: tup[0])

        return (backuphosts,backuphosts_ignored, snmpinfo_cisco_hp)

def get_hostByLivestatus():

        #socket_path = "/omd/sites/prod/tmp/run/live"
        #s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #s.connect(socket_path)

        all_server = [('10.3.3.3', 6557)]

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
                        (backuphosts, backuphosts_ignored, snmpinfo_cisco_hp) = get_backuphosts(lql_answer_python)


                        return backuphosts

                except Exception, e:
                        livestatus_log += str(e) + "\n"
                        print str(e)


###################################################################
#Start
###################################################################


ips = get_hostByLivestatus()

snmp_community = "ctest"
folder = "/omd/sites/test/Burmeister/mac_files/"

ips_community_list =[]
for host in ips:
        (host_name, host_alias, host_address, plugin_output, host_filename) = host
        print host_name
        ips_community_list.append( (host_address, snmp_community, folder) )

t = MAC_SNMP_Thread(20, ips_community_list)
