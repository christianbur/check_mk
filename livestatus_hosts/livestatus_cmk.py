import time
import sys
import re
import socket
import os


class Livestatus_CMK():

        def __init__(self):
                pass

        def __recv_timeout(self,the_socket,timeout=2):
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


        def get_livestatus(self,cmk_server_port, lql):


                lql_answer_python = None
                livestatus_log    = ""

                try:
                        msg  = "\n#--------------------------------------------------------------------------------\n\n"
                        msg += "Verbinde zu: " + str(cmk_server_port)
                        livestatus_log += msg + "\n"
                        print msg

                        max_attempts = 10
                        for attempt in range(max_attempts):
                                msg = "Verbindungsversuch: #" + str(attempt)
                                livestatus_log += msg + "\n"
                                print msg

                                # Verbinden zum Server und LQL abfragen
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                s.connect(cmk_server_port)
                                s.send(lql)
                                s.shutdown(socket.SHUT_WR)
                                lql_answer = self.__recv_timeout(s)

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



                except Exception, e:
                        livestatus_log += str(e) + "\n"
                        print str(e)



                return (lql_answer_python, livestatus_log)
