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
        self.session = Session()
        self.name = name
        self.friend_id = self.get_friend_id()
        self.username = self.get_friend_name()
        self.friend_url = self.get_friend_url()

    def get_friend_id(self):
        user_test = self.session.query(User).filter(User.username == self.name).first()
        if user_test is None:
            filler = Fill("786b438aa07b502edd057387927406651b6b9698", self.engine)
            filler.fill_data(self.name)
            user_test = self.session.query(User).filter(User.username == self.name).first()
            # Since _ in IRC can be spaces in OSU names, if can't find a user with '_', replace them with ' ' and try
            # again. If still can't find the user, give up.
            if (user_test is None) & (self.name.find('_') == -1):
                self.friend_id = 123456
                self.username = 'DoesNotExist'
                self.friend_url = 'none'
                return
            # elif user_test is None:
            #     self.name = self.name.replace('_', ' ')
            #     filler.fill_data(self.name)
            #     user_test = self.session.query(User).filter(User.username == self.name).first()
            #     if user_test is None:
            #         self.friend_id = 123456
            #         self.username = 'DoesNotExist'
            #         self.friend_url = 'none'
            #         return
        # print(wubwoofwolf.beatmaps[5].beatmap_id)
        users_dict = {}
        start = time.time()

        for x in range(50):
            comparison = self.session.query(Beatmaps).filter((Beatmaps.beatmap_id == user_test.beatmaps[x].beatmap_id) &
                                                             (Beatmaps.enabled_mods ==
                                                              user_test.beatmaps[x].enabled_mods)).all()
            for y in comparison:
                if str(y.user_id) in users_dict:
                    users_dict[str(y.user_id)] += 1
                else:
                    users_dict[str(y.user_id)] = 1
        # time_passed = (time.time() - start)
        # print(time_passed)
        # print("\n")
        # new_users_dict = sorted(users_dict.items(), key=operator.itemgetter(1), reverse=True)
        # print(new_users_dict)
        best_match = 0
        best_user = ""
        for x in list(users_dict):
            if (users_dict[x] > best_match) & (users_dict[x] != 50):
                best_match = users_dict[x]
                best_user = x
        #print(best_user)
        new_users_dict = sorted(users_dict.items(), key=operator.itemgetter(1), reverse=True)
        #print(new_users_dict)
        self.matches = users_dict[best_user]
        return best_user

    def get_friend_name(self):
        try:
            username = self.session.query(User).filter(User.user_id == self.friend_id).first().username
        except AttributeError:
            username = 'DoesNotExist'
        return username

    def get_friend_url(self):
        return "https://osu.ppy.sh/u/" + self.username

# friend_getter = getFriend("HappyStick")
# friend1 = friend_getter.friend_url
# print(friend1)
# print(friend_getter.friend_id)
# print(friend_getter.username)
