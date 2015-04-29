from songsense import fill, getfriend
from songsense.database import  *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from songsense.config import Config

my_config = Config()
engine = create_engine(my_config.engine_str, **my_config.engine_args)
Session = sessionmaker(engine)
session = Session()
filler = fill.Fill(engine)


def setup_module(module):
    filler.fill_data('gelibolue')
    filler.fill_data('G_u_M_i')


def teardown_module(module):
    number = session.query(Beatmap).filter(Beatmap.user_id == 1845677).delete()
    session.query(Friend).filter(Friend.owner_id == 1845677).delete()
    session.query(User).filter(User.user_id == 1845677).delete()
    session.commit()
    assert number == 50


def test_fill():
    user = session.query(User).filter(User.username == 'gelibolue').first()
    assert user


def test_friend_name():
    friend = getfriend.GetFriend('ApolloFortyNine')
    name = friend.get_friend_name()
    assert name == 'gelibolue'


def test_rec_url():
    friend = getfriend.GetFriend('ApolloFortyNine')
    url = friend.get_rec_url()
    assert url


def test_underscore_name():
    friend = getfriend.GetFriend('G_u_M_i')
    url = friend.get_rec_url()
    assert url


def test_using_fill_twice():
    filler_force = fill.Fill(engine, force=True)
    filler_force.fill_data('ApolloFortyNine')
    rows = session.query(Beatmap).filter(Beatmap.user_id == 1845677).count()
    assert rows == 50


def test_user_doesnt_exist():
    filler.fill_data('slkjerwuiosdf')
    user = session.query(User).filter(User.username == 'slkjerwuiosdf').first()
    assert not user