"""
Insert your info here
Engine_str is the part in quotes from http://docs.sqlalchemy.org/en/latest/core/engines.html
If just testing out on your own, sqlite is included by default with python, however can only handle one write at a time
"""

class Config():
    def __init__(self):
        self.engine_str = "engine string"
        self.osu_api_key = "api key"
        self.irc_server = "cho.ppy.sh"
        self.irc_name = "name"
        self.irc_port = 6667
        self.irc_channel = "OSU"
        self.irc_password = "password"
