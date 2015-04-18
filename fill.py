# Class to fill the database with user and beatmap info
from config import Config
from osuApi import OsuApi
from sqlalchemy.orm import sessionmaker
from database import Beatmap
from database import User
from database import Base
from database import BeatmapInfo
import time
import datetime
import logging

logger = logging.getLogger('main')


class Fill:
    def __init__(self, engine):
        self.config = Config()
        self.osu = OsuApi(self.config.osu_api_key)
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine, checkfirst=True)

    def fill_data(self, osu_name):
        # If last updated less than 3 days ago, don't update
        current_user = self.session.query(User).filter(User.username == osu_name).first()
        if current_user is not None:
            if (datetime.datetime.now() - current_user.last_updated).days < 2:
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
            if 'enabled_mods' in beatmap:
                # Removes nightcore mod
                beatmap['enabled_mods'] = int(beatmap['enabled_mods'])
                if (beatmap['enabled_mods'] & 512) == 512:
                    beatmap['enabled_mods'] -= 512
                # Removes suddendeath mod
                if (beatmap['enabled_mods'] & 32) == 32:
                    beatmap['enabled_mods'] -= 32
                # Removes perfect mod
                if (beatmap['enabled_mods'] & 16384) == 16384:
                    beatmap['enabled_mods'] -= 16384
            arr.append(Beatmap(beatmap_id=beatmap['beatmap_id'], score=beatmap['score'], maxcombo=beatmap['maxcombo'],
                                count300=beatmap['count300'], count100=beatmap['count100'], count50=beatmap['count50'],
                                countmiss=beatmap['countmiss'], countkatu=beatmap['countkatu'],
                                countgeki=beatmap['countgeki'], perfect=beatmap['perfect'],
                                enabled_mods=beatmap['enabled_mods'], user_id=beatmap['user_id'],
                                date=datetime.datetime.strptime(beatmap['date'], "%Y-%m-%d %H:%M:%S"),
                                rank=beatmap['rank'], pp=beatmap['pp'], pp_rank=user_info['pp_rank']))
            beatmap_info = self.session.query(BeatmapInfo).filter(BeatmapInfo.beatmap_id == beatmap['beatmap_id']).\
                first()
            if beatmap_info is None:
                beatmaps_info = self.osu.get_beatmaps(map_id=beatmap['beatmap_id'])
                for x in beatmaps_info:
                    x['last_update'] = datetime.datetime.strptime(beatmap['date'], "%Y-%m-%d %H:%M:%S")
                    x['approved_date'] = datetime.datetime.strptime(beatmap['date'], "%Y-%m-%d %H:%M:%S")
                    self.session.add(BeatmapInfo(**x))
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

