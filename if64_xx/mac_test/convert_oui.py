import re,os,sys

def __read_mac_file( filename):

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





mac = __read_mac_file("./oui_wireshark.db")

fh = open("./testmac.txt", "w")
fh.writelines(str(mac).replace(",",",\n"))
fh.close()
