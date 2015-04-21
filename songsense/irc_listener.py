"""
This script initiates an irc listening service.
"""
import logging
import logging.handlers

from ircbot import IRCBot
from config import Config


logger = logging.getLogger('main')
handler = logging.handlers.RotatingFileHandler(filename='irc.log', maxBytes=5000000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
config = Config()
server = config.irc_server
name = config.irc_name
port = config.irc_port
channel = config.irc_channel
password = config.irc_password
ircbot = IRCBot(server, name, port, channel, password)
ircbot.listen()
