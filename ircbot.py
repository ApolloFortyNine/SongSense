import socket
import time
from getFriend import GetFriend
from osuApi import OsuApi
from config import Config
from threading import Thread
# Can't use process pool because GetFriend isn't pickleable, but it shouldn't be bound by cpu
# (just SQL calls) so threads alone should be fine
from concurrent.futures import ThreadPoolExecutor as Pool


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
        self.pool = Pool(8)

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
        self.send("USER " + self.nickname + " " + self.nickname + " " + self.nickname + " :" +
                  self.nickname + "\r\n")
        time.sleep(.05)

        while True:
            buffer = self.socket.recv(4096)
            lines = buffer.split(b'\n')

            for data in lines:
                data = str(data.decode('utf-8'))
                if data == '':
                    continue
                if data.find('sh QUIT :') != -1:
                    continue
                print(data)
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
                # This should spawn a thread instead, possible in another function, while true
                # adding the friend job to a concurrent_futures pool, waiting for a response.
                # Thread(target=PAYLOAD_LOOP_FUNCTION, args=(payload), daemon = True)
                # future = pool.submit(GetFriend, payload['sender'])
                # friend = future.result()
                if payload['type'] == 'PRIVMSG':
                    t = Thread(target=self.respond, args=(payload,))
                    t.daemon = True
                    t.start()

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
        map_str = ("[" + friend.rec_url + " " + beatmap['artist'] + " - " + beatmap['title'] +
                   " [" + beatmap['version'] + "]]" + play_mods_str)
        return map_str

    def respond(self, payload):
        message = ""
        if payload['msg'].find('!') != -1:
            if payload['msg'] == '!r':
                future = self.pool.submit(GetFriend, payload['sender'])
                friend = future.result()
                friend.get_rec_url()
                map_str = self.get_map_str(friend)
                message = ("Random Recommendation: " + map_str +
                           " For more recommendations type \"!rX\" where X is a number 1-20")
            elif payload['msg'] == '!h':
                message = ("Welcome to Osu Friend Finder! Type \"!f\" to find your number one"
                           " friend who shares beatmaps with you and \"!r\" for a recommendation!"
                           " \"!rX\" where X is a number 1-20 also works.")
            elif payload['msg'] == '!f':
                future = self.pool.submit(GetFriend, payload['sender'])
                friend = future.result()
                message = ("Your best friend: " + str(friend.friend_url) + " with " +
                           str(friend.matches) + " matches")
            elif payload['msg'].find('!r') != -1:
                future = self.pool.submit(GetFriend, payload['sender'])
                friend = future.result()
                for x in range(len(friend.recs)):
                    if payload['msg'] == '!r' + str(x+1):
                        friend.get_rec_url(rec_num=x)
                        map_str = self.get_map_str(friend)
                        message = ("Recommendation " + str(x+1) + ": " + map_str)
                        break
                # If no break is hit.
                else:
                    message = "I don't have any more recommendations :/"
        self.say(message, payload['sender'])

    def get_names(self):
        self.socket.connect((self.server, self.port))
        time.sleep(.05)
        self.send("PASS " + self.password + "\r\n")
        time.sleep(.05)
        self.send("NICK " + self.nickname + "\r\n")
        time.sleep(.05)
        self.send("USER " + self.nickname + " " + self.nickname + " " + self.nickname + " :" +
                  self.nickname + "\r\n")
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
                begin_str = (":" + self.server + " 353 " + self.nickname + " = " +
                             self.channel + " :")
                if (data.find(begin_str) != -1) | begin_read_names:
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
        replace_str = (":" + self.server + " 353 " + self.nickname + " = " + self.channel + " :")
        raw_names = raw_names.replace(replace_str, "")
        raw_names = raw_names.replace("@", "")
        raw_names = raw_names.replace("+", "")
        names_list = raw_names.split(" ")
        return names_list
