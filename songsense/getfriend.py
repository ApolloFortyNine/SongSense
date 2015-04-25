"""
GetFriend creates an object that contains a user's top 10 friends and can create there top 20
recommendations. It's probably easiest to understand if you see how it's used in ircbot.py
"""
import operator
import random
import datetime
import logging
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from songsense.database import User
from songsense.database import Beatmap
from songsense.database import Friend
from songsense.fill import Fill
from songsense.config import Config


logger = logging.getLogger('main')


class GetFriend():
    def __init__(self, name):
        logger.info('Top of GetFriend.__init__')
        self.recs = []
        self.enabled_mods = ''
        self.beatmap_id = 0
        self.config = Config()
        self.engine = create_engine(self.config.engine_str, **self.config.engine_args)
        Session = sessionmaker(bind=self.engine)
        self.matches = 0
        self.top_friends = []
        self.session = Session()
        self.name = name
        logger.info('Before get user_row')
        self.user_row = self.session.query(User).filter(User.username == self.name).first()
        logger.info('After get user_row')
        self.friend_id = self.get_friend_id()
        logger.info('After get friend_id')
        self.username = self.get_friend_name()
        logger.info('After get friend_name')
        self.friend_url = self.get_friend_url()
        logger.info('After get friend_url')
        self.get_rec()
        logger.info('After get get_rec')
        self.rec_url = self.get_rec_url()
        logger.info('After get rec_url')

    def get_friend_id(self):
        if self.user_row is None:
            filler = Fill(self.engine)
            filler.fill_data(self.name)
            self.user_row = self.session.query(User).filter(User.username == self.name).first()
            # Since _ in IRC can be spaces in OSU names, if can't find a user with '_', replace
            # them with ' ' and try again. If still can't find the user, give up.
            # Possibly raise an error here (ValueError).
            if (self.user_row is None) & (self.name.find('_') == -1):
                self.friend_id = 123456
                self.username = 'DoesNotExist'
                self.friend_url = 'none'
                return
            elif self.user_row is None:
                self.name = self.name.replace('_', ' ')
                self.user_row = self.session.query(User).filter(User.username == self.name).first()
                if self.user_row is None:
                    self.friend_id = 123456
                    self.username = 'DoesNotExist'
                    self.friend_url = 'none'
                    return
        return self.check_friends()

    def check_friends(self):
        users_dict = {}
        number_of_maps = 0
        logger.debug("update_friends_bool %s", str(self.update_friends_bool()))
        if self.update_friends_bool():
            logger.debug("Before comparison queries")
            for x in self.user_row.beatmaps:
                # comparison = self.session.query(Beatmap).options(load_only("user_id")).\
                # filter(Beatmap.beatmap_id == x.beatmap_id).\
                # filter(Beatmap.enabled_mods == x.enabled_mods).all()
                # Hand written quarry saves about a second (SQLAlchemy adds wildcards where they
                # don't need to be)
                query_str = ("SELECT user_id FROM beatmaps WHERE  beatmaps.beatmap_id=" +
                             str(x.beatmap_id) + " AND beatmaps.enabled_mods=" +
                             str(x.enabled_mods))
                comparison = self.engine.execute(query_str)
                logger.debug("After %d comparison", number_of_maps)
                logger.debug("Current comparison: %d enabled_mods=%d", x.beatmap_id, x.enabled_mods)
                number_of_maps += 1
                for y in comparison:
                    if str(y.user_id) in users_dict:
                        users_dict[str(y.user_id)] += 1
                    else:
                        users_dict[str(y.user_id)] = 1
            logger.debug("After comparison queries")
            users_list = sorted(users_dict.items(), key=operator.itemgetter(1), reverse=True)
            try:
                self.matches = users_list[1][1]
                self.top_friends = users_list[1:11]
            except IndexError:
                self.matches = 0
                self.top_friends = []
            friend_list = []
            # Save friends in their own table, so we can skip searches on friends who are only
            # a day or so old
            for x in users_list[1:11]:
                user = self.session.query(User).filter(User.user_id == int(x[0])).first()
                friend = Friend(user_id=user.user_id, owner_id=self.user_row.user_id,
                                username=user.username, pp_rank=user.pp_rank, matches=x[1],
                                last_updated=datetime.datetime.now())
                friend_list.append(friend)
            self.user_row.friends = friend_list
            self.session.commit()
            return users_list[1][0]
        else:
            max_matches = 0
            max_matches_id = ''
            for x in self.user_row.friends:
                if x.matches > max_matches:
                    max_matches_id = x.user_id
                    max_matches = x.matches
            self.top_friends = self.user_row.friends
            self.matches = max_matches
            return max_matches_id

    def update_friends_bool(self):
        if not self.user_row.friends:
            return True
        elif (datetime.datetime.now() - self.user_row.friends[0].last_updated).days > 2:
            return True
        else:
            return False

    def get_friend_name(self):
        try:
            username = self.session.query(User).filter(User.user_id ==
                                                       self.friend_id).first().username
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
            if type(x) != Friend:
                user_id = x[0]
            else:
                user_id = x.user_id
            top_friends_list.append(self.session.query(User).filter(User.user_id ==
                                                                    user_id).first())
        # If the beatmap is already one of the user's top 50, regardless of mods don't tell
        # them to play it again
        for x in self.user_row.beatmaps:
            user_beatmaps_dict[str(x.beatmap_id)] = 1
        beatmaps_dict = {}
        # Here we create a dictionary of all beatmaps and their rate of occurrence
        for x in top_friends_list:
            comparison = self.session.query(Beatmap).filter(Beatmap.user_id == x.user_id).all()
            for y in comparison:
                # Creates unique string with mods
                beatmap_enabled_mods_str = (str(y.beatmap_id) + self.get_mods_str(y.enabled_mods))
                # Skips beatmaps already in user's top 50
                if str(y.beatmap_id) in user_beatmaps_dict:
                    continue
                if beatmap_enabled_mods_str in beatmaps_dict:
                    beatmaps_dict[beatmap_enabled_mods_str][0] += 1
                else:
                    beatmaps_dict[beatmap_enabled_mods_str] = [1, y.beatmap_id,
                                                               self.get_mods_str(y.enabled_mods)]
        # Create a listed sorted by occurrence
        beatmaps_str_list = sorted(beatmaps_dict.items(), key=operator.itemgetter(1), reverse=True)
        beatmaps_list = []
        map_rec_pool = 20
        # Create list of beatmap id's of size map_rec_pool
        for x in beatmaps_str_list:
            # First is id, second is mods, third is matches
            beatmaps_list.append([x[1][1], x[1][2], x[1][0]])
            map_rec_pool -= 1
            if map_rec_pool == 0:
                break
        if not beatmaps_list:
            return 'FAILED'
        logger.info(str(beatmaps_list))
        # Leave as (0, 10) as first 10 are the best matches
        rand_int = random.randrange(0, 10)
        self.recs = beatmaps_list
        return beatmaps_list[rand_int]

    def get_rec_url(self, rec_num=None):
        if rec_num is None:
            rec_num = random.randrange(0, 10)
        if not self.recs:
            return "Username does not exist"
        self.beatmap_id = self.recs[rec_num][0]
        self.enabled_mods = self.recs[rec_num][1]
        self.rec_url = "https://osu.ppy.sh/b/" + str(self.beatmap_id)
        return "https://osu.ppy.sh/b/" + str(self.beatmap_id)

    @staticmethod
    def get_mods_str(mods_int):
        mods = ""
        if mods_int == 0:
            return "NOMOD"
        if (mods_int & 1) == 1:
            mods += mods + "NF"
        if (mods_int & 2) == 2:
            mods += mods + "EZ"
        if (mods_int & 8) == 8:
            mods += mods + "HD"
        if (mods_int & 16) == 16:
            mods += mods + "HR"
        if (mods_int & 32) == 32:
            mods += mods + "SD"
        if (mods_int & 64) == 64:
            mods += mods + "DT"
        if (mods_int & 256) == 256:
            mods += mods + "HT"
        # if (mods_int & 512) == 512:
        #    mods = mods + "NC"
        if (mods_int & 1024) == 1024:
            mods += mods + "FL"
        if (mods_int & 4096) == 4096:
            mods += mods + "SO"
        if mods == "DTNC":
            mods = "DT"
        return mods
