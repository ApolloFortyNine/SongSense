# On windows run
# easy_install http://www.stickpeople.com/projects/python/win-psycopg/2.6.0/psycopg2-2.6.0.win32-py3.4-pg9.4.1-release.exe
# For postgresql support. On linux, pip install psycopg2
from distutils.core import setup

setup(name='SongSense',
      version='0.2',
      description='OSU Recommendation Bot',
      author='Ryan Quinn',
      author_email='forwardingtoyou@gmail.com',
      url='https://github.com/ApolloFortyNine/SongSense',
      install_requires=['sqlalchemy', 'cherrypy', 'httplib2', 'jinja2'],
      packages=['songsense', 'songsense.osuapi'],
      package_dir={'songsense': 'songsense'},
      )
