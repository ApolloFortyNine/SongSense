from sqlalchemy import *
from database import User
from database import Beatmap
from database import Friend
from sqlalchemy.orm import sessionmaker
import operator
import random
from fill import Fill
from config import Config
import datetime


class GetFriend():
    def __init__(self, name):
        self.config = Config()
        self.engine = create_engine(self.config.engine_str)
        #self.engine = create_engine("sqlite:///test3.db")
        Session = sessionmaker(bind=self.engine)
        self.matches = 0
        self.top_friends = []
        self.session = Session()
        self.name = name
        self.user_row = self.session.query(User).filter(User.username == self.name).first()
        self.friend_id = self.get_friend_id()
        self.username = self.get_friend_name()
        self.friend_url = self.get_friend_url()
        self.recs = self.get_rec()

    def get_friend_id(self):
        if self.user_row is None:
            filler = Fill(self.engine)
            filler.fill_data(self.name)
            self.user_row = self.session.query(User).filter(User.username == self.name).first()
            # Since _ in IRC can be spaces in OSU names, if can't find a user with '_', replace them with ' ' and try
            # again. If still can't find the user, give up.
            # Possibly raise an error here (ValueError).
            if (self.user_row is None) & (self.name.find('_') == -1):
                self.friend_id = 123456
                self.username = 'DoesNotExist'
                self.friend_url = 'none'
                return
            elif self.user_row is None:
                self.name = self.name.replace('_', ' ')
                user_test = self.session.query(User).filter(User.username == self.name).first()
                if user_test is None:
                    self.friend_id = 123456
                    self.username = 'DoesNotExist'
                    self.friend_url = 'none'
                    return
        users_dict = {}
        number_of_maps = 0
        for x in self.user_row.beatmaps:
            # comparison = self.session.query(Beatmap).filter(Beatmap.beatmap_id == x.beatmap_id).\
            #    filter(Beatmap.enabled_mods == x.enabled_mods).all()
            # Hand written quarry saves about a second (SQLAlchemy adds wildcards where they don't need to be)
            comparison = self.engine.execute("SELECT * FROM beatmaps WHERE beatmaps.enabled_mods=" +
                                             str(x.enabled_mods) + " AND beatmaps.beatmap_id=" + str(x.beatmap_id))
            number_of_maps += 1
            for y in comparison:
                if str(y.user_id) in users_dict:
                    users_dict[str(y.user_id)] += 1
                else:
                    users_dict[str(y.user_id)] = 1
        users_list = sorted(users_dict.items(), key=operator.itemgetter(1), reverse=True)
        self.matches = users_list[1][1]
        self.top_friends = users_list[1:11]
        friend_list = []
        # Save friends in their own table, so we can skip searches on friends who are only a day or so old
        for x in users_list[1:11]:
            user = self.session.query(User).filter(User.user_id == int(x[0])).first()
            friend = Friend(user_id=user.user_id, owner_id=self.user_row.user_id, username=user.username,
                                      pp_rank=user.pp_rank, matches=x[1], last_updated=datetime.datetime.now())
            friend_list.append(friend)
        self.user_row.friends = friend_list
        self.session.commit()
        return users_list[1][0]

    def get_friend_name(self):
        try:
            username = self.session.query(User).filter(User.user_id == self.friend_id).first().username
        except AttributeError:
            username = 'DoesNotExist'
        return username

    def get_friend_url(self):
        return "https://osu.ppy.sh/u/" + self.username

    def get_rec(self):
        if self.username == 'DoesNotExist':
            return 'FAILED'
        top_friends_list = []
        user_beatmaps_dict = {}
        # Creates an array of User objects, each one containing the user's whole row
        for x in self.top_friends:
            user_id = x[0]
            matches = x[1]
            top_friends_list.append(self.session.query(User).filter(User.user_id == user_id).first())
        # If the beatmap is already one of the user's top 50, regardless of mods don't tell them to play it again
        for x in self.user_row.beatmaps:
            user_beatmaps_dict[str(x.beatmap_id)] = 1
        beatmaps_dict = {}
        # Here we create a dictionary of all beatmaps and their rate of occurrence
        for x in top_friends_list:
            comparison = self.session.query(Beatmap).filter(Beatmap.user_id == x.user_id).all()
            for y in comparison:
                # Creates unique string with mods
                beatmap_enabled_mods_str = (str(y.beatmap_id) + str(y.enabled_mods))
                # Skips beatmaps already in user's top 50
                if str(y.beatmap_id) in user_beatmaps_dict:
                    continue
                if beatmap_enabled_mods_str in beatmaps_dict:
                    beatmaps_dict[beatmap_enabled_mods_str][0] += 1
                else:
                    beatmaps_dict[beatmap_enabled_mods_str] = [1, y.beatmap_id]
        # Create a listed sorted by occurrence
        beatmaps_str_list = sorted(beatmaps_dict.items(), key=operator.itemgetter(1), reverse=True)
        beatmaps_list = []
        map_rec_pool = 10
        # Create list of beatmap id's of size map_rec_pool
        for x in beatmaps_str_list:
            beatmaps_list.append(x[1][1])
            map_rec_pool -= 1
            if map_rec_pool == 0:
                break
        if not beatmaps_list:
            return 'FAILED'
        return beatmaps_list

    def get_rec_url(self, rec_num=0):
        if rec_num is 0:
            rec_num = beatmap_id = self.recs[rec_num]
        return "https://osu.ppy.sh/b/" + str(beatmap_id)
    
    def get_mods_str(self, mods_int):
        mods = ""
        if mods_int == 0:
            return "NOMOD"
        if (mods_int & 1) == 1:
            mods = mods + "NF"
        if (mods_int & 2) == 2:
            mods = mods + "EZ"
        if (mods_int & 8) == 8:
            mods = mods + "HD"
        if (mods_int & 16) == 16:
            mods = mods + "HR"
        if (mods_int & 32) == 32:
            mods = mods + "SD"
        if (mods_int & 64) == 64:
            mods = mods + "DT"
        if (mods_int & 256) == 256:
            mods = mods + "HT"
        if (mods_int & 512) == 512:
            mods = mods + "NC"
        if (mods_int & 1024) == 1024:
            mods = mods + "FL"
        if (mods_int & 4096) == 4096:
            mods = mods + "SO"
        return mods


# friend_getter = GetFriend("HappyStick")
# friend1 = friend_getter.friend_url
# print(friend1)
# print(friend_getter.get_rec())
# print(friend_getter.username)
