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

                if payload['type'] == 'PRIVMSG':
                    if payload['msg'].find('!f') != -1:
                        friend = GetFriend(payload['sender'])
                        self.say("Name: " + friend.username + " Matches: " + str(friend.matches) + " Url: " +
                                 friend.friend_url, payload['sender'])
                        self.say("Name: " + friend.username + " Matches: " + str(friend.matches) + " Url: " +
                                 friend.friend_url, self.nickname)
                    if payload['msg'].find('!r') != -1:
                        friend = GetFriend(payload['sender'])
                        self.say("Url: " + friend.get_rec_url(), payload['sender'])

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