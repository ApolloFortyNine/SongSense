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
        return ("Name: " + friend.username + " Matches: " + str(friend.matches) + " Url: " +
                friend.friend_url)

    @cherrypy.expose
    def get_rec(self, name="HappyStick"):
        friend = GetFriend(name)
        return "Url: " + friend.get_rec_url()

if __name__ == '__main__':
    cherrypy.server.socket_host = '23.94.12.106'
    cherrypy.quickstart(StringGenerator())