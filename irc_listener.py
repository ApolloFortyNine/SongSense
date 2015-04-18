from ircbot import IRCBot
from config import Config
import logging
logging.basicConfig(filename='osufriendfinder.log', level=logging.INFO, format='%(asctime)s %(message)s')
logging.info('Started')
config = Config()
server = config.irc_server
name = config.irc_name
port = config.irc_port
channel = config.irc_channel
password = config.irc_password
ircbot = IRCBot(server, name, port, channel, password)
ircbot.listen()
