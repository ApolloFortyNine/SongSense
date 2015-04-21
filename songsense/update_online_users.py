"""
This script will scrape the online users using an ircbot instance.
"""
import time
from sqlalchemy import *
from songsense.ircbot import IRCBot
from songsense.fill import Fill
from songsense.config import Config


config = Config()
engine = create_engine(config.engine_str, **config.engine_args)
filler = Fill(engine)
server = config.irc_server
name = config.irc_name
port = config.irc_port
channel = config.irc_channel
password = config.irc_password
ircbot = IRCBot(server, name, port, channel, password)
names = ircbot.get_names()

count = 0
count_all = 0
start = time.time()
true_start = time.time()
for name in names:
    filled = filler.fill_data(name)
    if filled is not None:
        print(name)
        count += 1
        count_all += 1
    time_passed = (time.time() - start)
    if time_passed <= 60 and (count >= 400):
        print("Throttle")
        time.sleep(60 - time_passed)
        print("Go")
        count = 0
        start = time.time()
    elif time_passed > 60:
        count = 0
        start = time.time()
print((time.time() - true_start) / count_all)
print((time.time() - true_start) / 60)