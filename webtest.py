from getFriend import GetFriend
import cherrypy


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <form method="get" action="get_friend">
              <input type="text" value="HappyStick" name="name" />
              <button type="submit">Your username</button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def get_friend(self, name="HappyStick"):
        friend = GetFriend(name)
        return ("Name: " + friend.username + " Matches: " + str(friend.matches) + " Url: " +
                                 friend.friend_url)

if __name__ == '__main__':
    cherrypy.quickstart(StringGenerator())