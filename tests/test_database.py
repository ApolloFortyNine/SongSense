from songsense import fill, getfriend
from songsense.database import  *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import config


def test_fill():
    my_config = config.Config()
    engine = create_engine(my_config.engine_str, **my_config.engine_args)
    Session = sessionmaker(engine)
    session = Session()
    filler = fill.Fill(engine)
    filler.fill_data('ApoxlloFortyNine')
    user = session.query(User).filter(User.username == 'ApolloFortyNine').first()
    if not user:
        assert False
