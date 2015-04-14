from ircbot import IRCBot
from config import Config

server = "cho.ppy.sh"
name = "benderx"
port = 6667
channel = "OSU"
password = "e945f2"
ircbot = IRCBot(server, name, port, channel, password)
ircbot.listen()
