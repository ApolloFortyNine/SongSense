from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    count300 = Column(BigInteger)
    count100 = Column(BigInteger)
    count50 = Column(BigInteger)
    play_count = Column(Integer)
    ranked_score = Column(BigInteger)
    total_score = Column(BigInteger)
    pp_rank = Column(Integer)
    level = Column(Float)
    pp_raw = Column(Float)
    accuracy = Column(Float)
    count_rank_ss = Column(Integer)
    count_rank_s = Column(Integer)
    count_rank_a = Column(Integer)
    country = Column(String)
    beatmaps = relationship("Beatmap", single_parent=True, cascade="save-update, merge, delete, delete-orphan",
                            backref="user")
    last_updated = Column(DateTime)
    friends = relationship("Friend", single_parent=True, cascade="save-update, merge, delete, delete-orphan",
                           backref="user")


class Beatmap(Base):
    __tablename__ = 'beatmaps'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    beatmap_id = Column(Integer)
    score = Column(Integer)
    maxcombo = Column(Integer)
    count300 = Column(BigInteger)
    count100 = Column(BigInteger)
    count50 = Column(BigInteger)
    countmiss = Column(BigInteger)
    countkatu = Column(BigInteger)
    countgeki = Column(BigInteger)
    perfect = Column(Integer)
    enabled_mods = Column(Integer)
    date = Column(DateTime)
    rank = Column(String)
    pp = Column(Float)
    pp_rank = Column(Integer)


class Friend(Base):
    __tablename__ = 'friends'

    id = Column(Integer, primary_key=True)
    owner_id = Column(BigInteger, ForeignKey('users.user_id'))
    user_id = Column(BigInteger)
    username = Column(String)
    pp_rank = Column(Integer)
    matches = Column(Integer)
    last_updated = Column(DateTime)
