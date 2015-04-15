import socket
import time
from getFriend import GetFriend
from osuApi import OsuApi
from config import Config


class IRCBot:
    def __init__(self, server, nickname, port, channel, password):
        self.socket = socket.socket()
        self.server = server
        self.nickname = nickname
        self.port = port
        self.channel = channel
        self.password = password
        self.config = Config()
        self.osu = OsuApi(self.config.osu_api_key)

    def send(self, msg):
        self.socket.send(bytes(msg+"\r\n", 'UTF-8'))

    def say(self, msg, target):
        self.send("PRIVMSG %s :%s" % (target, msg))
        time.sleep(1)

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
                if data.find('sh QUIT :'):
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
                message = ""
                if payload['type'] == 'PRIVMSG':
                    if payload['msg'].find('!') != -1:
                        message = ""
                        if payload['msg'] == '!r':
                            friend = GetFriend(payload['sender'])
                            friend.get_rec_url()
                            map_str = self.get_map_str(friend)
                            message = "Random Recommendation: " + map_str
                        elif payload['msg'] == '!h':
                            message = "Welcome to Osu Friend Finder! Type \"!f\" to find your number one friend who " \
                                      "shares beatmaps with you and \"!r\" for a recommendation! \"!rX\" where X is " \
                                      "a number 1-10 also works."
                        elif payload['msg'] == '!f':
                            friend = GetFriend(payload['sender'])
                            message = ("Your best friend: " + str(friend.friend_url) + " with " + str(friend.matches) +
                                       " matches")
                        elif payload['msg'].find('!r') != -1:
                            friend = GetFriend(payload['sender'])
                            for x in range(len(friend.recs)):
                                if (x+2) > len(friend.recs):
                                    message = "I don't have any more recommendations :/"
                                    break
                                if payload['msg'] == '!r' + str(x+1):
                                    friend.get_rec_url(rec_num=x)
                                    map_str = self.get_map_str(friend)
                                    message = ("Recommendation " + str(x+1) + ": " + map_str)
                                    break
                    self.say(message, payload['sender'])

    # It's important that get_rec_url() has been called on the friend object before calling.
    def get_map_str(self, friend):
        beatmap = self.osu.get_beatmaps(map_id=friend.beatmap_id)
        try:
            beatmap = beatmap[0]
        except IndexError:
            return 'What the hell, that map doesn\'t exist!'

        play_mods_str = ''
        if friend.enabled_mods != "NOMOD":
            play_mods_str = " Try " + friend.enabled_mods + "!"
        map_str = ("[" + friend.rec_url + " " + beatmap['artist'] + " - " + beatmap['title'] + " [" +
                   beatmap['version'] + "]]" + play_mods_str)
        return map_str

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
