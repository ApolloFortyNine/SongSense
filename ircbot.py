import socket
import time
from getFriend import GetFriend


class IRCBot:
    def __init__(self, server, nickname, port, channel, password):
        self.socket = socket.socket()
        self.server = server
        self.nickname = nickname
        self.port = port
        self.channel = channel
        self.password = password
        self.send_allowed = False

    def send(self, msg):
        self.socket.send(bytes(msg+"\r\n", 'UTF-8'))

    def say(self, msg, target):
        self.send("PRIVMSG %s :%s" % (target, msg))

    def listen(self):
        self.socket.connect((self.server, self.port))
        time.sleep(.05)
        self.send("PASS " + self.password + "\r\n")
        time.sleep(.05)
        self.send("NICK " + self.nickname + "\r\n")
        time.sleep(.05)
        self.send("USER " + self.nickname + " " + self.nickname + " " + self.nickname + " :" + self.nickname + "\r\n")
        time.sleep(.05)
        raw_names = ""
        begin_read_names = False

        while True:
            buffer = self.socket.recv(4096)
            lines = buffer.split(b'\n')

            if self.send_allowed is False:
                time.sleep(1)
                self.send_allowed = True

            for data in lines:
                data = str(data.decode('utf-8'))
                if data == '':
                    continue
                # This will handle when a line wasn't finished being received
                print(data)
                # I got this error once...
                try:
                    if (data.find(":" + self.server + " 353 " + self.nickname + " = " + self.channel + " :") != -1) |\
                            begin_read_names:
                        begin_read_names = True
                        if data.find("End of /NAMES list.") == -1:
                            raw_names += data
                        else:
                            begin_read_names = False
                except UnicodeEncodeError:
                    continue
                if data.find('PING') != -1:
                    n = data.replace('PING ', '')
                    self.send('PONG :' + n)

                args = data.split(None, 3)
                if len(args) != 4:
                    continue
                payload = dict()
                payload['sender'] = args[0][1:]
                payload['sender'] = payload['sender'].split('!')[0]
                payload['type'] = args[1]
                payload['target'] = args[2]
                payload['msg'] = args[3][1:]

                if payload['type'] == 'PRIVMSG' & self.send_allowed:
                    if payload['msg'] == '!r':
                        friend = GetFriend(payload['sender'])
                        self.say("Url: " + friend.get_rec_url(), payload['sender'])
                    elif payload['msg'] == '!h':
                        self.say("Welcome to Osu Friend Finder! Type \"!f\" to find your number one friend who shares beatmaps with you and \"!r\" for a recommendation!", payload['sender'])
                    elif payload['msg'].find('!r') != -1:
                        for x in range(10):
                            if payload['msg'] == '!r ' + str(x+1):
                                friend = GetFriend(payload['sender'])
                                self.say("Reccomendation " + str(x+1) + " Url: " + friend.get_rec_url(rec_num=x), payload['sender'])
                                break
                    elif payload['msg'].find('!') != -1:
                        self.say(payload['msg'] + " Isn't recognized as a command, type !h for help.", payload['sender'])

    def get_names(self):
        self.socket.connect((self.server, self.port))
        time.sleep(.05)
        self.send("PASS " + self.password + "\r\n")
        time.sleep(.05)
        self.send("NICK " + self.nickname + "\r\n")
        time.sleep(.05)
        self.send("USER " + self.nickname + " " + self.nickname + " " + self.nickname + " :" + self.nickname + "\r\n")
        time.sleep(.05)
        raw_names = ""
        start = time.time()
        begin_read_names = False
        send_names_bool = True

        while (time.time() - start) < 4:
            buffer = self.socket.recv(4096)
            lines = buffer.split(b'\n')

            for data in lines:
                data = str(data.decode('utf-8'))
                if data == '':
                    continue
                # This will handle when a line wasn't finished being received
                if (data.find(":" + self.server + " 353 " + self.nickname + " = " + self.channel + " :") != -1) |\
                        begin_read_names:
                    begin_read_names = True
                    if data.find("End of /NAMES list.") == -1:
                        raw_names += data
                    else:
                        begin_read_names = False
                if data.find('PING') != -1:
                    n = data.replace('PING ', '')
                    self.send('PONG :' + n)
            if ((time.time() - start) > 2) & send_names_bool:
                send_names_bool = False
                self.send("NAMES " + self.channel)

        time.sleep(.05)
        # Remove junk data
        raw_names = raw_names.replace((":" + self.server + " 353 " + self.nickname + " = " + self.channel + " :"), "")
        raw_names = raw_names.replace("@", "")
        raw_names = raw_names.replace("+", "")
        names_list = raw_names.split(" ")
        return names_list

# server = "cho.ppy.sh"
# name = "ApolloFortyNine"
# port = 6667
# channel = "OSU"
# password = "784062"
# ircbot = IRCBot(server, name, port, channel, password)
# ircbot.listen()