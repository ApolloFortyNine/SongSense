from ircbot import IRCBot
import time
from fill import Fill
from sqlalchemy import *

engine = create_engine("sqlite:///test4.db")
filler = Fill("786b438aa07b502edd057387927406651b6b9698", engine)
server = "cho.ppy.sh"
name = "ApolloFortyNine"
port = 6667
channel = "OSU"
password = "784062"
ircbot = IRCBot(server, name, port, channel, password)
names = ircbot.get_names()
print(names[1])

count = 0
count_all = 0
start = time.time()
true_start = time.time()
for name in names:
    print(name)
    filled = filler.fill_data(name)
    if filled is not None:
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