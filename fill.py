#Class to fill the database with user and beatmap info

from osuApi import OsuApi
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from database import Beatmaps
from database import User
from database import Base
import time
import datetime

# TODO Create configuration class and use those properties everywhere
# TODO Take top 3 results, find most played song not already played
# TODO Create webserver
# TODO Fix enabled mods issue (sudden death). It's bitwise, might be able to figure something out fancily


class Fill:
    def __init__(self, osu_api_key, engine):
        self.osu = OsuApi(osu_api_key)
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine, checkfirst=True)

    def fill_data(self, osu_name):
        # If last updated less than 3 days ago, don't update
        current_user = self.session.query(User).filter(User.username == osu_name).first()
        if current_user is not None:
            if (datetime.datetime.now() - current_user.last_updated).days < 3:
                return
        try:
            user_info = self.osu.get_user(osu_name)[0]
        # This happened once, I assume it was just a fluke, so wait a few seconds and try again
        except ValueError:
            time.sleep(5)
            user_info = self.osu.get_user(osu_name)[0]
        # An index error means just an empty array was sent back, which means the user has been removed
        except IndexError:
            print("We got a cheater over here")
            return
        # I have no idea why this happened.
        except TypeError:
            return
        # If low rank, don't bother storing
        if user_info['pp_rank'] is None:
            return True
        elif (int(user_info['pp_rank']) > 400000) | (int(user_info['pp_rank']) == 0):
            return True
        try:
            beatmaps = self.osu.get_user_best(osu_name, limit=50)
        except ValueError:
            time.sleep(5)
            beatmaps = self.osu.get_user_best(osu_name, limit=50)
        arr = []

        # Create an array of Beatmaps objects to insert into a User. Probably could be done better but it works
        for beatmap in beatmaps:
            arr.append(Beatmaps(beatmap_id=beatmap['beatmap_id'], score=beatmap['score'], maxcombo=beatmap['maxcombo'],
                                count300=beatmap['count300'], count100=beatmap['count100'], count50=beatmap['count50'],
                                countmiss=beatmap['countmiss'], countkatu=beatmap['countkatu'],
                                countgeki=beatmap['countgeki'], perfect=beatmap['perfect'],
                                enabled_mods=beatmap['enabled_mods'], user_id=beatmap['user_id'],
                                date=datetime.datetime.strptime(beatmap['date'], "%Y-%m-%d %H:%M:%S"),
                                rank=beatmap['rank'], pp=beatmap['pp']))

        # Using merge here allows it to both refresh user info and beatmap info. Also handles changed name, since
        # user_id is the primary key
        self.session.merge(User(user_id=user_info['user_id'], username=user_info['username'],
                                count300=user_info['count300'], count100=user_info['count100'],
                                count50=user_info['count50'], play_count=user_info['playcount'],
                                ranked_score=user_info['ranked_score'], total_score=user_info['total_score'],
                                pp_rank=user_info['pp_rank'], level=user_info['level'], pp_raw=user_info['pp_raw'],
                                accuracy=user_info['accuracy'], count_rank_ss=user_info['count_rank_ss'],
                                count_rank_s=user_info['count_rank_s'], count_rank_a=user_info['count_rank_a'],
                                country=user_info['country'], beatmaps=arr, last_updated=datetime.datetime.now()))

        self.session.commit()
        self.session.close()
        return True

#engine = create_engine("sqlite:///test3.db")
#test = Fill("786b438aa07b502edd057387927406651b6b9698", engine)
#test.fill_data("CAPSLOCKLOL")
#time.sleep(5)
#Session = sessionmaker(bind=engine)
#session = Session()
#x = session.query(User).filter((User.pp_rank < 1) | (User.pp_rank == None)).all()
#for y in x:
#    print(y.username)
#session.delete(session.query(User).filter(User.username == "hvick225").first())
#session.commit()
#query = test.session.query(User).filter(User.user_id==1845677).order_by(User.id)
#print(query.all()[2].beatmaps)
#test.session.add(User(user_id=1845677))
#test.fill_beatmaps('ApolloFortyNine')
#Base.metadata.create_all(self.engine, checkfirst=True)
