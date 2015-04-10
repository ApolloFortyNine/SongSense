from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

engine = create_engine("sqlite:///test.db")

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    count300 = Column(Integer)
    count100 = Column(Integer)
    count50 = Column(Integer)
    play_count = Column(Integer)
    ranked_score = Column(Integer)
    total_score = Column(Integer)
    pp_rank = Column(Integer)
    level = Column(Float)
    pp_raw = Column(Integer)
    accuracy = Column(Float)
    count_rank_ss = Column(Integer)
    count_rank_s = Column(Integer)
    count_rank_a = Column(Integer)
    country = Column(String)
    beatmaps = relationship("Beatmaps", single_parent=True, cascade="save-update, merge, "
                            "delete, delete-orphan")
    last_updated = Column(DateTime)

class Beatmaps(Base):
    __tablename__ = 'beatmaps'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey('users.id'))
    beatmap_id = Column(Integer)
    score = Column(Integer)
    maxcombo = Column(Integer)
    count300 = Column(Integer)
    count100 = Column(Integer)
    count50 = Column(Integer)
    countmiss = Column(Integer)
    countkatu = Column(Integer)
    countgeki = Column(Integer)
    perfect = Column(Integer)
    enabled_mods = Column(Integer)
    user_id = Column(Integer)
    date = Column(DateTime)
    rank = Column(String)
    pp = Column(Float)

#Session = sessionmaker(bind=engine)

#session = Session()

#test = User(username='test')
#test.beatmaps = [Beatmaps(beatmap_id=50), Beatmaps(beatmap_id=51)]
#print(test.beatmaps)
#session.add(test)
#session.commit()
#session.close()