from sqlalchemy import *
from database import User
from database import Beatmaps
from sqlalchemy.orm import sessionmaker
import operator
import time


class GetFriend():
    def __init__(self, name):
        #engine = create_engine("postgresql://osu:osupassword@localhost/osu")
        engine = create_engine("sqlite:///test3.db")
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.name = name
        self.friend_id = self.get_friend_id()
        self.username = self.get_friend_name()
        self.friend_url = self.get_friend_url()

    def get_friend_id(self):
        user_test = self.session.query(User).filter(User.username == self.name).first()
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
        return best_user

    def get_friend_name(self):
        return self.session.query(User).filter(User.user_id == self.friend_id).first().username

    def get_friend_url(self):
        return "https://osu.ppy.sh/u/" + str(self.friend_id)

# friend_getter = getFriend("HappyStick")
# friend1 = friend_getter.friend_url
# print(friend1)
# print(friend_getter.friend_id)
# print(friend_getter.username)
