"""
This is an extremely rudimentary webserver. It works, and that's about all that can be said
about it
"""
import logging
import logging.handlers
import cherrypy
from songsense.getfriend import GetFriend
from songsense.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader('templates'))
logger = logging.getLogger('main')
handler = logging.handlers.RotatingFileHandler(filename='web.log', maxBytes=5000000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
config = Config()
engine = create_engine(config.engine_str, **config.engine_args)
# Base.metadata.create_all(self.engine, checkfirst=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
# Then call session = Session() inside functions, and pass as second argument to getfriend. Also modify filler
# and update_online_users, as well as irc_bot


class WebServer(object):
    @cherrypy.expose
    def index(self):
        template = env.get_template('index.jinja')
        return template.render()

    @cherrypy.expose
    def get_friend(self, name="HappyStick"):
        session = Session()
        friend = GetFriend(session, name)
        friends_arr = []
        for x in friend.top_friends:
            url_str = "https://osu.ppy.sh/u/{0}".format(x.user_id)
            friends_arr.append([x.username, x.matches, url_str])
        template = env.get_template('friends.jinja')
        return template.render(allRows=friends_arr, name=name)

    @cherrypy.expose
    def get_recs(self, name="HappyStick"):
        session = Session()
        friend = GetFriend(session, name)
        friends_with_links = friend.recs
        for x in friends_with_links:
            url_str = "https://osu.ppy.sh/b/{0}".format(x[0])
            x.append(url_str)
        template = env.get_template('recs.jinja')
        return template.render(allRows=friend.recs, name=name)


if __name__ == '__main__':
    config = Config()
    cherrypy.server.socket_host = config.ip
    cherrypy.quickstart(WebServer())
