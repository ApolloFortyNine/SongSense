from ircbot import IRCBot
from config import Config

config = Config()
server = config.irc_server
name = config.irc_name
port = config.irc_port
channel = config.irc_channel
password = config.irc_password
ircbot = IRCBot(server, name, port, channel, password)
ircbot.listen()