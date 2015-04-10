import socket
import time

server = "cho.ppy.sh"
name = "ApolloFortyNine"
port = 6667
channel = "#Osu"
password = "784062"

def send(msg):
    print("I>" + msg)
    socket.send(bytes(msg+"\r\n", 'UTF-8'))

socket = socket.socket()
socket.connect((server, port))
send("PASS 784062\r\n")
send("NICK " + name + "\r\n")
send("USER ApolloFortyNine ApolloFortyNine Ryan :ApolloFortyNine \r\n")
duerig = True
stuff = ""
start = time.time()
begin_names = False
while (time.time() - start) < 10:
        buf = socket.recv(4096)
        lines = buf.split(b'\n')
        for data in lines:
            data = str(data.decode('utf-8')).strip()
            if data == '':
                continue
            # This will handle when a line wasn't finished being received
            if (data.find(":cho.ppy.sh 353 ApolloFortyNine = OSU :") != -1) | begin_names:
                begin_names = True
                if data.find("End of /NAMES list.") == -1:
                    stuff += data
                else:
                    begin_names = False
            print("I<" + data)
            if data.find('PING') != -1:
                n = data.split(':')[1]
                send('PONG :' + n)
            #if connected == False:
               # perform()
               # connected = True
        if ((time.time() - start) > 5) & duerig:
            duerig = False
            send("NAMES OSU")
time.sleep(1)
stuff = stuff.replace(":cho.ppy.sh 353 ApolloFortyNine = OSU :", "")
stuff = stuff.replace("@", "")
stuff = stuff.replace("+", "")
print(stuff)
#    def perform():
        #self.send("PRIVMSG R : Register <>")
#        send("PRIVMSG R : Login <>")
#        send("MODE %s +x" % nickname)
#        for c in self.channels:
#            send("JOIN %s" % c)
#            # say hello to every channel
#            say('hello world!', c)