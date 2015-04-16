from getFriend import GetFriend
import cherrypy
from sqlalchemy import *
from sqlalchemy.orm import *
from database import User, Friend, Beatmap
from config import Config


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <form method="get" action="get_friend">
              <input type="text" value="HappyStick" name="name" />
              <button type="submit">Get friend</button>
            </form>
            <form method="get" action="get_rec">
              <input type="text" value="HappyStick" name="name" />
              <button type="submit">Get recommendation</button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def get_friend(self, name="HappyStick"):
        friend = GetFriend(name)
        out_str = ''
        config = Config()
        engine = create_engine(config.engine_str)
        Session = sessionmaker(bind=engine)
        session = Session()
        friend = GetFriend(name)
        for x in friend.top_friends:
            user = session.query(User).filter(User.user_id == x.user_id).first()
            out_str += ("Name: " + user.username + " Matches: " + str(x.matches) + " Url: https://osu.ppy.sh/u/" +
                        str(user.user_id) + " :: ")
        return out_str

    @cherrypy.expose
    def get_rec(self, name="HappyStick"):
        friend = GetFriend(name)
        return "Url: " + friend.get_rec_url()

if __name__ == '__main__':
    cherrypy.server.socket_host = '23.94.12.106'
    cherrypy.quickstart(StringGenerator())