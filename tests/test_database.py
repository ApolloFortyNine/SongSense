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


def test_fill():
    user = session.query(User).filter(User.username == 'ApolloFortyNine').first()
    if not user:
        assert False
