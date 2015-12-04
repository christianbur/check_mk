#!/usr/bin/python
import os, errno
import sys
import imp
import shutil
import optparse


def csv2mk(csv_filename, mk_filename):

        hosttag_available = {
        # dropdown tags
           'cmk-agent': 'agent',
           'snmp-only': 'agent',
           'snmp-tcp':  'agent',
           'snmp-v1':  'agent',
           'ping': 'agent',

           'prod': 'criticality',
           'critical': 'criticality',
           'test': 'criticality',
           'offline': 'criticality',

           'lan': 'networking',
           'wan': 'networking',
           'dmz': 'networking',


        # auxiliary tags
           'snmp': '',
           'tcp': '',
           'ping': '',


        }


        # MK-Datei einlesen
        folder_dir = {}

        csv_format = "scan"

        csv_file = open(csv_filename,'r')
        for line in csv_file:

                if csv_format == "scan":
                        line=line.replace('\n',';\n')
                        hostname, alias, parents, ip, tags = line.split(';')[:5]
                elif csv_format == "nagios_csv":
                        group, hostname, alias, ip, hostgroup = line.split(';')[:5]
                        parents = ""
                        tags = ""
                else:
                        print "Falsches Format"
                        return

                folder_dir.setdefault("mk_config",[])
                folder_dir["mk_config"].append((hostname,alias,parents,ip,tags))
        csv_file.close()

        for folder in folder_dir:
                all_hosts = []
                host_attributes = []
                ipaddresses = []
                alias_details = []
                parent_details = []
                for hostname, alias, parents, ip, tags in folder_dir[folder]:

                  tags_temp = tags.replace('|wato|/" + FOLDER_PATH + "/"','').strip()
                  all_hosts.append(    '  "%s|%swato|/" + FOLDER_PATH + "/"' % (hostname, tags_temp))

                  if ip != "":
                        ipaddresses.append( "  '%s': u'%s'," % (hostname, ip))

                  if alias != "":
                        alias_details.append("  (u'%s', ['%s'])," % (alias, hostname))

                  if parents != "":
                        parent_details.append("  ('%s', ['%s'])," % (parents, hostname))


                  # Parameter fuer WATOi
                  host_attributes.append("  '%s': {" % (hostname))
                  if alias != "":
                        host_attributes.append("    'alias': u'%s'," % (alias))
                  if ip != "":
                        host_attributes.append("    'ipaddress': u'%s'," % (ip))
                  if parents != "":
                        parents2 = parents.replace(",","', '")
                        host_attributes.append("    'parents': ['%s']," % (parents2))


                  all_tags = tags.replace('|wato|/" + FOLDER_PATH + "/"','').split("|")
                #  for tag_wato in all_tags:
                #        if hosttag_available.has_key(tag_wato):
                #          if hosttag_available[tag_wato] != "":
                #                host_attributes.append("    'tag_%s': '%s'," % (hosttag_available[tag_wato], tag_wato))
                #        else:
                #          if tag_wato != "":
                #                  print ("Hosttag '%s' von Host '%s' wurde nicht erkannt" % (tag_wato, hostname))
                #                  sys.exit()

                  host_attributes.append("  },")



                ###########################################################################################################
                # MK Datei erstellen

                mk_file = open(mk_filename,'w')
                mk_file.write('# encoding: utf-8\n\n')


                mk_file.write('all_hosts += [\n')
                mk_file.write(",\n".join(all_hosts))
                mk_file.write('\n]\n\n')


                if len(ipaddresses) > 0:
                        mk_file.write('# Explicit IP addresses\n')
                        mk_file.write('ipaddresses.update({\n')
                        mk_file.write("\n".join(ipaddresses))
                        mk_file.write('\n})\n\n')

                if len(alias_details) > 0:
                        mk_file.write("# Settings for alias\n")
                        mk_file.write("extra_host_conf.setdefault('alias', []).extend([\n")
                        mk_file.write("\n".join(alias_details))
                        mk_file.write('\n])\n\n')

                if len(parent_details) > 0:
                        mk_file.write("# Settings for parents\n")
                        mk_file.write("extra_host_conf.setdefault('parents', []).extend([\n")
                        mk_file.write("\n".join(parent_details))
                        mk_file.write('\n])\n\n')

                mk_file.write("# Host attributes (needed for WATO)\n")
                mk_file.write('host_attributes.update({\n')
                mk_file.write("\n".join(host_attributes))
                mk_file.write('\n})\n')

                mk_file.close()


def mk2csv(mk_filename, csv_filename):

        #CSV-Format : hostname, alias, parents, ipaddress, tags

        # Temp-MK-Datei importieren
        variables = {
            "FOLDER_PATH"               : 'REMOVE',
            "ALL_HOSTS"                 : [],
            "all_hosts"                 : [],
            "clusters"                  : {},
            "ipaddresses"               : {},
            "explicit_snmp_communities" : {},
            "extra_host_conf"           : { "alias" : [] },
            "extra_service_conf"        : { "_WATO" : [] },
            "host_attributes"           : {},
            "host_contactgroups"        : [],
            "_lock"                     : False,
        }
        execfile(mk_filename, variables, variables)

        # CSV-Datei mit den Datein aus der Temp-MK-Datei erstellen
        csv_file = open(csv_filename,'w')

        for host in variables["all_hosts"]:
                host_split = host.split("|")
                hostname = host_split[0]
                tags = host[len(hostname)+1:].replace('wato|/REMOVE/','')
                if 'alias' in variables["host_attributes"].get(hostname):
                        alias = variables["host_attributes"].get(hostname)['alias']
                else:
                        alias = ""

                if 'ipaddress' in variables["host_attributes"].get(hostname):
                        ipaddress = variables["host_attributes"].get(hostname)['ipaddress']
                else:
                        ipaddress = ""

                parents = ""
                if 'parents' in variables["host_attributes"].get(hostname):
                        for parent in variables["host_attributes"].get(hostname)['parents']:
                                if parents == "":
                                        parents = parent
                                else:
                                        parents += "," + parent

                csv_file.write("%s;%s;%s;%s;%s\n" % (hostname, alias, parents, ipaddress, tags))

        csv_file.close()


def main():

        parser = optparse.OptionParser("usage: %prog -c csv2mk -i ./input.csv -o ./output.mk    or \n       %prog -c mk2csv -i ./input.mk  -o ./output.csv")
        parser.add_option("-i", "--input" , dest="file_input" , type="string", help="Imput Filename")
        parser.add_option("-o", "--output", dest="file_output", type="string", help="Output Filename")
        parser.add_option("-c", "--convert", dest="convert_format", type="string", help="Convert mk-csv")

        (options, args) = parser.parse_args()
        file_input  = options.file_input
        file_output = options.file_output
        convert_format = options.convert_format


        if convert_format  == "csv2mk":
                print "Konvertiere %s in %s (csv2mk)" % (file_input, file_output)
                csv2mk(file_input, file_output)

        elif convert_format == "mk2csv":
                print "Konvertiere %s in %s (mk2csv)" % (file_input, file_output)
                mk2csv(file_input, file_output)
        else:
                raise NameError('ERROR: Es konnte nicht ermittelt werden was gemacht werden soll (csv2mk oder mk2csv')

if __name__=="__main__":
        main()
