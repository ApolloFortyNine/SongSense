from songsense import fill, getfriend, config
from songsense.database import  *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *


def test_fill():
    my_config = config.Config()
    engine = create_engine(my_config.engine_str, **my_config.engine_args)
    Session = sessionmaker(engine)
    session = Session()
    filler = fill.Fill(engine)
    filler.fill_data('ApolloFortyNine')
    user = session.query(User).filter(User.username == 'ApolloFortyNine').first()
    if not user:
        assert False
