class Config():
    def __init__(self):
        self.engine_str = "postgresql://osudb:osudbpassword@localhost/osudb"
        self.engine_args = {}
        if self.engine_str.find('sqlite:/') == -1:
            self.engine_args = {'client_encoding': 'utf8'}
        self.osu_api_key = "f4c74ca9bbcf3bd71045af80f8d81d42419e9392"
        self.irc_server = "cho.ppy.sh"
        self.irc_name = "ApolloFortyNine"
        self.irc_port = 6667
        self.irc_channel = "OSU"
        self.irc_password = "a975d9b0"
        self.ip = 'localhost'