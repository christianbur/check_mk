import socket
import paramiko
import telnetlib
import datetime
import time
import re
import sys
import traceback

class Device_cisco_hp(object):
        def __init__(self, ip, log_file=None):
                self.__ip = None
                self.__tacacs_username = None
                self.__tacacs_password = None
                self.__local_password = None
                self.__enable_password = None
                self.__use_local_password = False
                self.__use_enable_password = False
                self.__force_enable_password = False
                self.__port = None
                self.__ssh_client = None
                self.__ssh_conn = None
                self.__telnet_conn = None
                self.__state = "disconnected"
                self.__switchname_raw = ""
                self.__loginsequence = []
                self.__debug_mode = False
                self.__demo_config_mode = False
                self.__debug_ssh_expect = False
                self.__ssh_buffer = ""
                self.__current_prompt = "ERROR"
                self.__log_file = None
                self.__command_counter = 0
                self.__preferred_protocol = "ssh"
                self.__connection_time_beginn = datetime.datetime.now()


                if log_file != None:
                        self.__log_file = log_file

                self.logging("\n\n#----------------------------------------------------------------------------------")
                self.logging("--- try ip: " + ip)
                self.logging("--- start connection: " + str(self.__connection_time_beginn))
                self.__set_ip(ip)

        def get_ip(self):
                return self.__ip

        def get_command_counter(self):
                return self.__command_counter

        def set_debug_mode(self,mode):
                if mode == True:
                        self.__debug_mode = True
                        self.__debug_ssh_expect = True
                        self.logging("--- DEBUG_MODE: enabled")
                elif mode == False:
                        self.__debug_mode = False
                        self.__debug_ssh_expect = False
                        self.logging("--- DEBUG_MODE: disabled")

        def set_demo_config_mode(self,mode):
                if mode == True:
                        self.__demo_config_mode = True
                        self.logging("--- DEMO_CONFIG_MODE: enabled")
                elif mode == False:
                        self.__demo_config_mode = False
                        self.logging("--- DEMO_CONFIG_MODE: disabled")

        def get_demo_config_mode(self):
                return self.__demo_config_mode

        def __set_ip(self,ip):
                try:
                        socket.inet_aton(ip)
                        self.__ip = ip
                except:
                        try:

                                hostname = ip
                                ip = ""
                                ip = socket.gethostbyname(hostname)
                                socket.inet_aton(ip)
                                self.__ip = ip
                        except:
                                self.__error("ip/hostname not valid")

        def set_prefer_ssh(self):
                self.__preferred_protocol = "ssh"

        def set_prefer_telnet(self):
                self.__preferred_protocol = "telnet"

        def get_tacacs_username(self):
                return self.__tacacs_username

        def get_tacacs_password(self):
                return self.__tacacs_password

        def get_local_password(self):
                return self.__local_password

        def get_enable_password(self):
                return self.__enable_password

        def use_local_password(self):
                return self.__use_local_password

        def use_enable_password(self):
                return self.__use_enable_password

        def set_force_enable_password(self):
                self.__force_enable_password = True

        def get_loginsequence(self):
                return "-".join(self.__loginsequence)

        def __get_userprompt(self):
                return re.escape(self.__switchname_raw[:28]) + "[+A-Za-z0-9_-]{0,15}>"

        def __get_privprompt(self):
                # beachte  c = re.compile(r"([a-zA-Z0-9_-]+)(#).*",re.MULTILINE) in __find_prompt()
                return re.escape(self.__switchname_raw[:28]) + "[+A-Za-z0-9_-]{0,15}#"

        def __get_configprompt(self):
                #http://rubular.com/
                return re.escape(self.__switchname_raw[:11]) + "[+A-Za-z0-9_-]{0,15}\(config[+A-Za-z0-9_-]{0,15}\)#"

        def logging(self,text):
                if self.__log_file != None:
                        self.__log_file.write(text + "\n")

                print text

        def __error(self,text):
                if self.__log_file != None:
                        self.__log_file.write("ERROR: (" + self.__ip + "): " + text + "\n")

                raise Exception("ERROR: (" + self.__ip + "): " + text)

        def get_port(self):
                if self.__port == None:

                        socket.setdefaulttimeout(2)

                        socket_telnet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result_telnet = socket_telnet.connect_ex((self.get_ip(), 23))
                        socket_telnet.close()

                        socket_ssh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result_ssh = socket_ssh.connect_ex((self.get_ip(), 22))
                        socket_ssh.close()

                        time.sleep(1)  # sonst /gibt es einen Fehler bei HP

                        if result_telnet == 0 and self.__preferred_protocol == "telnet":
                                self.__port = 23
                                self.__loginsequence.append("CONNECT_TELNET")
                        elif result_ssh == 0 and self.__preferred_protocol == "ssh":
                                self.__port = 22
                                self.__loginsequence.append("CONNECT_SSH")
                        elif result_telnet == 0:
                                self.__port = 23
                                self.__loginsequence.append("CONNECT_TELNET")
                        elif result_ssh == 0:
                                self.__port = 22
                                self.__loginsequence.append("CONNECT_SSH")
                        else:
                                self.__error("device don't support ssh or telnet")

                return self.__port

        def get_switchname(self):
                return self.__switchname_raw

        def is_alive(self):
                if self.get_port() == 22 or self.get_port() == 23:
                        return True
                else:
                        return False

        def __vt100_cleaner(self,text):
                # remove the vt100 encoding from the HP switch output

                vt100_1 = re.compile(r'\x1B\[[^A-Za-z]*[A-Za-z]')
                vt100_2 = re.compile(r'\x1B[A-Za-z]')

                clear_text = vt100_1.sub('', text)
                clear_text = vt100_2.sub('', clear_text)
                clear_text = clear_text.replace('\r','')
                clear_text = "".join(self.__backspace_cleaner(list(clear_text)))

                return clear_text


        def __backspace_cleaner(self,text_list):
                for i in range(len(text_list)):
                        if text_list[i] == '\x08':
                                del text_list[i]
                                del text_list[i-1]
                                self.__backspace_cleaner(text_list)
                                return text_list

                # Return, if no backspace found
                return text_list

        def connect(self,tacacs_username, tacacs_password, local_password = None, enable_password = None):

                self.__tacacs_username  = tacacs_username
                self.__tacacs_password  = tacacs_password
                self.__local_password   = local_password
                self.__enable_password  = enable_password


                if self.__state == "disconnected" and self.is_alive():

                        if self.__debug_mode:
                                debug_file = open("./debug/debug_" + self.get_ip() + ".txt","w")
                        else:
                                debug_file = None

                        self.logging("--- connect to ip: " + self.get_ip() + ", port: " + str(self.get_port()))

                        try:

                                if self.get_port() == 22:
                                        #self.__error("ERROR: SSH not supported")

                                        self.__ssh_client = paramiko.SSHClient()
                                        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                        self.logging("--- SSH Login")
                                        self.__loginsequence.append("SSHLOGIN")
                                        self.__ssh_client.connect(self.get_ip(), username=self.get_tacacs_username(), 
                                                                                 password=self.get_tacacs_password(),
                                                                                 allow_agent=False,look_for_keys=False,
                                                                                 timeout=60)
                                        self.__ssh_conn = self.__ssh_client.invoke_shell()

                                        self.__find_prompt(debug_file)
                                        self.__set_prompt(debug_file)
                                        self.__init_terminal()

                                        self.logging("--- SSH connection established to: " + self.get_ip())
                                        self.__state = "connected"

                                elif self.get_port() == 23:
                                        self.__telnet_conn =  telnetlib.Telnet(self.get_ip(),self.get_port())
                                        #self.__telnet_conn.interact()

                                        self.__find_prompt(debug_file)
                                        self.__set_prompt(debug_file)
                                        self.__init_terminal()

                                        self.logging("--- Telnet connection established to: " + self.get_ip())
                                        self.__state = "connected"

                        except Exception, e:
                                self.__error(str(e))

                        if self.__debug_mode:
                                debug_file.close()



        def __find_prompt(self,debug_file):

                found_priv = False
                RESET_COUNTER = 0
                loop_counter = RESET_COUNTER
                MAX_ATTEMPTS = 10

                while found_priv != True:

                        regex_list = ['[Uu]sername:','[Ll]ogin:','[Pp]assword:', self.__get_userprompt(), self.__get_configprompt(), self.__get_privprompt()]
                        regex_list.extend(['Invalid password','Press any key to continue','Invalid input','Login invalid','DISABLED_Connecting to Tacacs server'])
                        regex_list.extend(['No Tacacs servers responding','maximum number of telnet sessions are active','Authentication failed'])
                        regex_list.extend(['Connection closed by '])
                        (index, match, output) = self.__expect(regex_list)

                        if self.__debug_mode:
                                debug_file.write("\n(---BEGIN-("+ str(loop_counter) + ")---) regex match: "
                                                + str(index) + ", text:" + output + ", list-output: " + str(list(output)) +  "(---END---)\n")

                        if index == -1:
                                self.__loginsequence.append("ExpectERROR")
                                self.__error("expect error (not able to find the priv prompt)")
                        elif index == 0 or index == 1:
                                if self.__use_local_password == True:
                                        self.logging("--- use -TACACS PASSWORD- for login")
                                        self.__use_local_password = False

                                if self.__loginsequence[-1] == "TUSERNAME":
                                        self.logging("--- HP-Telnet-BUG: skip second username prompt")
                                else:

                                        self.logging("--- Found: username prompt, enter -" + self.get_tacacs_username() + "-")
                                        self.__send_cmd(self.get_tacacs_username()+"\n")
                                        self.__loginsequence.append("TUSERNAME")

                        elif index == 2:
                                self.__clear_buffer()

                                if self.__use_local_password == False and self.get_loginsequence().find("TUSERNAME") == -1: 
                                        if self.get_port() == 23:
                                                self.__use_local_password = True
                                                self.logging("--- use -LOCAL PASSWORD- for login")
                                if self.get_enable_password() != None and self.__use_local_password == True and \
                                   self.get_loginsequence().find("USERPROMPT_ENABLE-LOCALPASSWORD") != -1:
                                        self.__use_enable_password = True
                                        self.logging("--- Found: password prompt, enter -ENABLE PASSWORD- (LOCAL PASSWORD didn't work)")
                                        self.__send_cmd(self.get_enable_password()+"\n")
                                        self.__loginsequence.append("ENABLEPASSWORD")
                                elif self.__use_local_password:
                                        self.logging("--- Found: password prompt, enter -LOCAL PASSWORD- ")
                                        if self.get_local_password() == None:
                                                self.__error("-LOCAL PASSWORD- not set in connect()-Methode")
                                        self.__send_cmd(self.get_local_password()+"\n")
                                        self.__loginsequence.append("LOCALPASSWORD")
                                elif self.__force_enable_password and self.get_loginsequence().endswith("USERPROMPT_ENABLE"):
                                        self.logging("--- Found: password prompt, enter -ENABLE PASSWORD- (FORCE)")
                                        if self.get_enable_password() == None:
                                                self.__error("-ENABLE PASSWORD- not set in connect()-Methode")
                                        self.__send_cmd(self.get_enable_password()+"\n")
                                        self.__loginsequence.append("ENABLEPASSWORDFORCE")
                                else:
                                        self.logging("--- Found: password prompt, enter -TACACS PASSWORD- ")
                                        self.__send_cmd(self.get_tacacs_password()+"\n")
                                        self.__loginsequence.append("TPASSWORD")
                        elif index == 3:
                                self.logging("--- Found: user prompt, sent -enable- command")
                                self.__send_cmd("enable\n")
                                self.__loginsequence.append("USERPROMPT_ENABLE")
                        elif index == 4:
                                self.logging("--- Found: config prompt, send -exit- command")
                                self.__send_cmd("exit\n")
                                self.__loginsequence.append("CONFIGPROMPT")
                        elif index == 5:
                                self.logging("--- Found: priv prompt (Exit Loop)")
                                found_priv = True
                                self.__current_prompt = "PRIVE "
                                self.__loginsequence.append("PRIVPROMPT")
                                break
                        elif index == 6:
                                # HP-Telnet message
                                self.logging("--- Found: INVALID PASSWORD")
                                self.__loginsequence.append("INVALIDPASSWORD")
                        elif index == 7:
                                self.__clear_buffer()

                                # HP-Telnet message
                                self.logging("--- Found: Press any key to continue, send -k-")
                                self.__send_cmd("k\n")
                                self.__loginsequence.append("PRESSKEY")
                        elif index == 8:
                                self.logging("--- Found: INVALID INPUT")
                                self.__loginsequence.append("InvalidInput")
                        elif index == 9:
                                self.logging("--- Found: LOGING INVALID")
                                self.__loginsequence.append("LoginInvalid")
                        elif index == 10:
                                self.logging("--- Found: Connecting to Tacacs server")
                                self.__loginsequence.append("ConnectTacacs")
                        elif index == 11:
                                self.logging("--- Found: No Tacacs servers responding")
                                self.__loginsequence.append("NoTacacs")
                        elif index == 12:
                                self.logging("--- Found: Sorry, the maximum number of telnet sessions are activ")
                                self.__loginsequence.append("MaxSessions")
                        elif index == 13:
                                self.logging("--- Found: Authentication failed")
                                self.__loginsequence.append("AuthFailed")
                        elif index == 14:
                                self.logging("--- Found: Connection closed by ...")
                                self.__loginsequence.append("ConnClosed")


                        loop_counter += 1
                        if MAX_ATTEMPTS == loop_counter:
                                 self.__error("not able to find the priv prompt")

                self.logging("--- login sequence: " + self.get_loginsequence())

                #self.__debug_interact()

                # Clear Buffer
                self.__clear_buffer()


        def __set_prompt(self,debug_file):

                #self.__debug_interact()

                regex_list = [self.__get_privprompt()] 

                # press Enter for clean prompt
                self.__send_cmd("\n")
                (index, match, output) = self.__expect(regex_list)
                clear_output = self.__vt100_cleaner(output).replace('\n','').strip()

                #self.__debug_interact()

                if self.__debug_mode:
                        debug_file.write("(---BEGIN-(findprompt)--) clear_output list: " + str(list(clear_output))  + "(---END---)")

                c = re.compile(r"([a-zA-Z0-9._+-]+)(#).*",re.MULTILINE)
                m = c.search(clear_output)
                if not m:
                         self.__error("not able to find promptname")
                else:
                        self.__switchname_raw = m.group(1)
                        self.logging("--- switchname: " + self.__switchname_raw)
                        self.logging("--- set prompt: " + self.__get_userprompt() + ", priv: " + self.__get_privprompt() + ", config: " + self.__get_configprompt())

                if self.__debug_mode:
                        debug_file.write("(---BEGIN---) switchname: " + self.get_switchname() + " list: " + str(list(clear_output))      + "(---END---)")


        def __init_terminal(self):
                
                regex_list = [self.__get_privprompt()]

                # No paging fuer Cisco Switche
                self.__send_cmd("terminal length 0\n")
                (index_1, match_1, output_1) = self.__expect(regex_list)

                # No paging fuer HP Switche
                self.__send_cmd("terminal length 1000\n") 
                (index_2, match_2, output_2) = self.__expect(regex_list)

                if output_1.find("Invalid input detected") != -1 and  output_2.find("Invalid input detected") != -1:
                        # No paging fuer Cisco ASA Fiewall
                        self.__send_cmd("terminal pager 0\n") 
                        (index_3, match_3, output_3) = self.__expect(regex_list)


        def __expect(self, regex_list='', timeout=35):
                if self.get_port() == 22:
                        return self.__ssh_expect(regex_list,timeout)
                elif self.get_port() == 23:
                        return self.__telnet_conn.expect(regex_list,timeout)

        def __clear_buffer(self):
                regex_list = ['[Uu]sername:','login:','[Pp]assword:', self.__get_userprompt(), self.__get_configprompt(), self.__get_privprompt()]
                regex_list.extend(['Invalid password','Press any key to continue','Invalid input','Login invalid','Connecting to Tacacs server'])
                regex_list.extend(['No Tacacs servers responding','maximum number of telnet sessions are active','Authentication failed'])

                if self.__debug_mode:
                        self.logging("--- Clear Buffer")

                timeout = 1
                output = []
                output.append(self.__expect(regex_list,timeout))
                output.append(self.__expect(regex_list,timeout))
                output.append(self.__expect(regex_list,timeout))
                output.append(self.__expect(regex_list,timeout))
                output.append(self.__expect(regex_list,timeout))

                return output


        def __send_cmd(self, cmd):
                if self.get_port() == 22:
                        return self.__ssh_conn.send(cmd)
                elif self.get_port() == 23:
                        return self.__telnet_conn.write(cmd)

        def __debug_interact(self):
                if self.get_port() == 22:
                        pass
                        # kein interact bei ssh verfuegbar
                elif self.get_port() == 23:
                        self.__telnet_conn.interact()


        def __ssh_expect(self, regex_list='', timeout=10):

                 

                buffer_size=100
                buffer = ""
                index = None
                match = None
                output = self.__ssh_buffer

                self.__ssh_conn.settimeout(timeout)

                found = False

                try: 
                    while found != True:

                        buffer = self.__ssh_conn.recv(buffer_size)

                        if self.__debug_ssh_expect:
                                sys.stdout.write("\nssh_buffer: " + buffer.strip() + "\n")
                                sys.stdout.flush()

                        if len(buffer) == 0:
                                break

                        output += buffer

                        i = -1
                        for regex in regex_list:
                                i = i + 1
                                if re.search(regex ,output, re.DOTALL) != None:
                                        if self.__debug_ssh_expect:
                                                sys.stdout.write("\nssh_regex-index : " + str(i) + ", regex: " + regex + " output: " + output + "\n")
                                                sys.stdout.flush()

                                        found = True
                                        match = regex
                                        index = i

                                        break

                    regex_position = re.search(match, output)
                    self.__ssh_buffer =  output[regex_position.end():]
                    output = output[:regex_position.end()]
                except socket.timeout:
                        index = -1
                        match = ""
                        output = "error_ssh_expect_timeout"


                return (index, match, output)


        def command(self,cmd,timeout_prompt=300):
                if self.__state == "connected":

                        if self.__demo_config_mode and self.__current_prompt == "CONFIG" and cmd != "exit":
                                self.logging("--- DEMO_CONFIG_MODE command (Prompt: " + self.__current_prompt + "): " + cmd)
                                self.__command_counter += 1
                                clear_output = "OUTPUT: DEMO_CONFIG_MODE"

                        else:
                                self.logging("--- execute command (Prompt: " + self.__current_prompt + "): " + cmd)
                                self.__send_cmd(cmd + "\n")
                                self.__command_counter += 1

                                prompt_list = [self.__get_userprompt(), self.__get_configprompt(), self.__get_privprompt()]
                                (index, match, output) = self.__expect(prompt_list,timeout_prompt)

                                if index == 0:
                                        self.__current_prompt = "USER  "
                                elif index == 1:
                                        self.__current_prompt = "CONFIG"
                                elif index == 2:
                                        self.__current_prompt = "PRIVE "


                                clear_output = self.__vt100_cleaner(output)
                                clear_output = re.sub(r'' + self.__get_userprompt(),'',clear_output)
                                clear_output = re.sub(r'' + self.__get_privprompt(),'',clear_output)
                                clear_output = re.sub(r'' + self.__get_configprompt(),'',clear_output)

                                clear_output = clear_output.replace(cmd,"")

                                if clear_output.find("Invalid") != -1 or clear_output.find("Incomplete") != -1:
                                        self.logging("ERROR: command output: (" + clear_output.replace('\n','') + ")")
                                elif self.__current_prompt == "CONFIG" and clear_output.strip() != "" and cmd != "conf t":
                                        if not clear_output.strip().endswith(cmd[-40:]):
                                                self.logging("--  COMMAND OUTPUT: (" + clear_output.replace('\n','') + ")")
                        return clear_output

        def command_sequence(self,cmd_list,time_between=2,timeout_prompt=300):
                self.__command_counter += 1

                self.logging("--- execute command (Prompt: " + self.__current_prompt + "): " + str(cmd_list))

                for cmd in cmd_list:
                        self.logging("--- execute command sequence        : " + cmd)
                        self.__send_cmd(cmd + "\n")
                        time.sleep(time_between)

                prompt_list = [self.__get_userprompt(), self.__get_configprompt(), self.__get_privprompt()]
                (index, match, output) = self.__expect(prompt_list,timeout_prompt)
                output_all = output
                (index, match, output) = self.__expect(prompt_list,2)
                output_all += output
                (index, match, output) = self.__expect(prompt_list,2)
                output_all += output

                clear_output = self.__vt100_cleaner(output_all)
                clear_output = re.sub(r'' + self.__get_userprompt(),'',clear_output)
                clear_output = re.sub(r'' + self.__get_privprompt(),'',clear_output)
                clear_output = re.sub(r'' + self.__get_configprompt(),'',clear_output)

                return clear_output




        def disconnect(self):
                if self.__state == "connected":


                        processing_time = datetime.datetime.now() - self.__connection_time_beginn
                        self.logging("--- end connection: " + str(datetime.datetime.now()) + " (processing time: " + str(processing_time) + ")" )

                        if self.get_port() == 22 and self.__ssh_conn != None:

                                self.logging("--- disconnect - ip: " + self.get_ip())
                                self.__ssh_conn.close()
                                self.__ssh_client.close()

                        elif self.get_port() == 23 and self.__telnet_conn != None:
                                self.__send_cmd("logout\ny\nn\n")
                                self.logging("--- disconnect - ip: " + self.get_ip())
                                self.__telnet_conn.close()
                        else:
                                self.logging("--- device dont't support ssh or telnet - ip: " + self.get_ip())
                self.__state = "disconnected"
