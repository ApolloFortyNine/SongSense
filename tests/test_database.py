from songsense import fill, getfriend
from songsense.database import  *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import config

my_config = config.Config()
engine = create_engine(my_config.engine_str, **my_config.engine_args)
Session = sessionmaker(engine)
session = Session()


def setup_module(module):
    filler = fill.Fill(engine)
    filler.fill_data('ApolloFortyNine')
    filler.fill_data('gelibolue')


def test_fill():
    user = session.query(User).filter(User.username == 'ApolloFortyNine').first()
    if not user:
        assert False


def test_friend_name():
    friend = getfriend.GetFriend('ApolloFortyNine')
    name = friend.get_friend_name()
    assert name == 'gelibolue'


def test_rec_url():
    friend = getfriend.GetFriend('ApolloFortyNine')
    url = friend.get_rec_url(rec_num=5)
    if not url:
        assert False