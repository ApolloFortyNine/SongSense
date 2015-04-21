"""
This script will remove friends older than 3 days. These friends are updated every 3 days anyways,
so they're no longer needed.
"""
import datetime
from sqlalchemy.orm import sessionmaker
from config import Config
from database import *


config = Config()
engine = create_engine(config.engine_str, **config.engine_args)
Session = sessionmaker(bind=engine)
session = Session()

session.query(Friend).filter(Friend.last_updated < (datetime.datetime.now() -
                                                    datetime.timedelta(days=3))).delete()
session.commit()