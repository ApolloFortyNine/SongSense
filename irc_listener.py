from ircbot import IRCBot

server = "cho.ppy.sh"
name = "ApolloFortyNine"
port = 6667
channel = "OSU"
password = "784062"
ircbot = IRCBot(server, name, port, channel, password)
ircbot.listen()
