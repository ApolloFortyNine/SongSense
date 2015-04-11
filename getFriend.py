from sqlalchemy import *
from database import User
from database import Beatmaps
from sqlalchemy.orm import sessionmaker
import operator
import time
from fill import Fill


class GetFriend():
    def __init__(self, name):
        self.engine = create_engine("postgresql://osu:osupassword@localhost/osu")
        #self.engine = create_engine("sqlite:///test3.db")
        Session = sessionmaker(bind=self.engine)
        self.matches = 0
        self.top5 = []
        self.session = Session()
        self.name = name
        self.user_row = self.session.query(User).filter(User.username == self.name).first()
        self.friend_id = self.get_friend_id()
        self.username = self.get_friend_name()
        self.friend_url = self.get_friend_url()

    def get_friend_id(self):
        if self.user_row is None:
            filler = Fill("786b438aa07b502edd057387927406651b6b9698", self.engine)
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
            comparison = self.session.query(Beatmaps).filter((Beatmaps.beatmap_id == x.beatmap_id) &
                                                             (Beatmaps.enabled_mods ==
                                                              x.enabled_mods)).all()
            number_of_maps += 1
            for y in comparison:
                if str(y.user_id) in users_dict:
                    users_dict[str(y.user_id)] += 1
                else:
                    users_dict[str(y.user_id)] = 1
        users_list = sorted(users_dict.items(), key=operator.itemgetter(1), reverse=True)
        self.matches = users_list[1][1]
        self.top5 = users_list[1:6]
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
        top5_list = []
        user_beatmaps_dict = {}
        for x in self.top5:
            user_id = x[0]
            matches = x[1]
            top5_list.append(self.session.query(User).filter(User.user_id == user_id).first())
        for x in self.user_row.beatmaps:
            user_beatmaps_dict[str(x.beatmap_id) + str(x.enabled_mods)] = 1
        beatmaps_dict = {}
        for x in top5_list:
            comparison = self.session.query(Beatmaps).filter(Beatmaps.user_id == x.user_id).all()
            for y in comparison:
                beatmap_enabled_mods_str = (str(y.beatmap_id) + str(y.enabled_mods))
                if beatmap_enabled_mods_str in user_beatmaps_dict:
                    continue
                if beatmap_enabled_mods_str in beatmaps_dict:
                    beatmaps_dict[beatmap_enabled_mods_str] += 1
                else:
                    beatmaps_dict[beatmap_enabled_mods_str] = 1

        beatmaps_list = sorted(beatmaps_dict.items(), key=operator.itemgetter(1), reverse=True)
        return beatmaps_list[0:5]

# friend_getter = GetFriend("HappyStick")
# friend1 = friend_getter.friend_url
# print(friend1)
# print(friend_getter.get_rec())
# print(friend_getter.username)
