"""
IRCBot is used to listen for requests, as well as to scrape online users.
"""
import socket
import time
from threading import Thread
import datetime
import random
import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from getfriend import GetFriend
from osuapi.osuapi import OsuApi
from config import Config
from database import *
from fill import Fill


logger = logging.getLogger('main')
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
        self.engine = create_engine(self.config.engine_str, **self.config.engine_args)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

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

                if payload['type'] == 'PRIVMSG':
                    t = Thread(target=self.respond, args=(payload,))
                    t.start()

    # It's important that get_rec_url() has been called on the friend object before calling.
    # Session's aren't thread safe, so create a new one whenever it's used
    def get_map_str(self, friend):
        session = self.Session()
        beatmap = session.query(BeatmapInfo).filter(BeatmapInfo.beatmap_id ==
                                                    friend.beatmap_id).first()
        if not beatmap:
            logger.info("Beatmap {0} didn't appear in beatmap table".format(friend.beatmap_id))
            beatmap = self.osu.get_beatmaps(map_id=friend.beatmap_id)
            try:
                beatmap = beatmap[0]
            except IndexError:
                return 'That map doesn\'t exist!'
            beatmap['last_update'] = datetime.datetime.strptime(beatmap['last_update'],
                                                                "%Y-%m-%d %H:%M:%S")
            if beatmap['approved_date'] is not None:
                beatmap['approved_date'] = datetime.datetime.strptime(beatmap['approved_date'],
                                                                      "%Y-%m-%d %H:%M:%S")
            session.add(BeatmapInfo(**beatmap))
            beatmap = session.query(BeatmapInfo).filter(BeatmapInfo.beatmap_id ==
                                                        friend.beatmap_id).first()

        play_mods_str = ''
        if friend.enabled_mods != "NOMOD":
            play_mods_str = " Try " + friend.enabled_mods + "!"
        map_str = ("[" + friend.rec_url + " " + beatmap.artist + " - " + beatmap.title +
                   " [" + beatmap.version + "]]" + play_mods_str)
        session.commit()
        session.close()
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
            elif payload['msg'] == '!update':
                filler = Fill(self.engine, force=True)
                future = self.pool.submit(filler.fill_data, payload['sender'])
                future.result()
                session = self.Session()
                user = session.query(User).filter(User.username == payload['sender']).first()
                user.friends = []
                session.commit()
                session.close()
                message = "Updated successfully!"
            elif payload['msg'].find(' length=') != -1:
                future = self.pool.submit(GetFriend, payload['sender'])
                friend = future.result()
                msg_params = payload['msg'].split(" ")
                try:
                    length_raw = float(msg_params[1][7:])
                except ValueError:
                    message = ("Format is '!r length=X', where X is minutes."
                               " Such as 1.5 for 1:30.")
                    if payload['sender'] == self.nickname:
                        return
                    self.say(message, payload['sender'])
                    return
                length = length_raw * 60
                session = self.Session()
                random_recs = random.sample(friend.recs, len(friend.recs))
                friend.recs = random_recs
                for x in range(len(friend.recs)):
                    friend.get_rec_url(rec_num=x)
                    beatmap_info = session.query(BeatmapInfo).filter(BeatmapInfo.beatmap_id ==
                                                                     friend.beatmap_id).first()
                    if beatmap_info.total_length <= length:
                        map_str = self.get_map_str(friend)
                        message = ("Recommendation less than " + str(length_raw) + " minutes" +
                                   ": " + map_str)
                        break
                else:
                    message = ("Sorry, none of the found recommendations are less than " +
                               str(length_raw) + " minutes.")
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
                    if payload['sender'] == self.nickname:
                        return
                    message = "I don't have any more recommendations :/"
        if message:
            logger.info(message)
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
