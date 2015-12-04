#!/usr/bin/python
#
import socket
import time

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

def get_etchosts(output):

    all_hosts = {}
    for host in output:
            (host_name, address, alias, filename) = host

            if not all_hosts.has_key(filename):
                all_hosts[filename] = {}

            new_host = {address:(host_name,alias)}
            all_hosts[filename].update(new_host)


    for filename in sorted(all_hosts.keys()):
        print "\n\n#" + filename.replace("/hosts.mk","").replace("/wato","")

        for ip in sorted(all_hosts[filename].keys()):
            hostname = all_hosts[filename][ip][0]
            alias    = all_hosts[filename][ip][1]

            print "%-20s %-40s #%s" % (ip, hostname, alias)

def main():


    #socket_path = "/omd/sites/prod/tmp/run/live"
    #s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    #s.connect(socket_path)

    all_server = [('10.3.3.3', 6557),('10.2.2.2', 6557)]
    lql =  "GET hosts\n"
    lql += "Columns: host_name address alias filename\n"
    lql += "OutputFormat: python\n"

    for server in all_server:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(server)

            s.send(lql)

            s.shutdown(socket.SHUT_WR)

            answer = recv_timeout(s)
            table = eval(answer)
            get_etchosts(table)

main()
