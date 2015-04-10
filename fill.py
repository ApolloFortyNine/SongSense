#Class to fill the database with user and beatmap info

from osuApi import OsuApi
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from database import Beatmaps
from database import User
from database import Base
import time
import datetime

# TODO Last updated column, take into account in fill class (3 days maybe?)
# TODO Modify fill to work with updating and new users (delete old user, add new; try update first though)
# TODO Take top 3 results, find most played song not already played
# TODO Create webserver
# TODO Make sure if someone changes their name it works (remove old by user_id?; test manually)
# TODO Fix enabled mods issue (sudden death). It's bitwise, might be able to figure something out fancily


class Fill:
    def __init__(self, osu_api_key, engine):
        self.osu = OsuApi(osu_api_key)
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine, checkfirst=True)

    def fill_data(self, osu_name):
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
                                enabled_mods=beatmap['enabled_mods'], user_id=beatmap['user_id'], date=datetime.datetime.strptime(beatmap['date'], "%Y-%m-%d %H:%M:%S"),
                                rank=beatmap['rank'], pp=beatmap['pp']))

        # Using merge here allows it to both refresh user info and beatmap info
        self.session.merge(User(user_id=user_info['user_id'], username=user_info['username'],
                                count300=user_info['count300'], count100=user_info['count100'],
                                count50=user_info['count50'], play_count=user_info['playcount'],
                                ranked_score=user_info['ranked_score'], total_score=user_info['total_score'],
                                pp_rank=user_info['pp_rank'], level=user_info['level'], pp_raw=user_info['pp_raw'],
                                accuracy=user_info['accuracy'], count_rank_ss=user_info['count_rank_ss'],
                                count_rank_s=user_info['count_rank_s'], count_rank_a=user_info['count_rank_a'],
                                country=user_info['country'], beatmaps=arr))

        self.session.commit()
        self.session.close()

    def in_db(self, osu_name):
        if self.session.query(User).filter(User.username == osu_name).first():
            return True
        else:
            return False

#test = Fill()
#test.fill_data(1897182)
#query = test.session.query(User).filter(User.user_id==1845677).order_by(User.id)
#print(query.all()[2].beatmaps)
#test.session.add(User(user_id=1845677))
#test.fill_beatmaps('ApolloFortyNine')
#Base.metadata.create_all(self.engine, checkfirst=True)
