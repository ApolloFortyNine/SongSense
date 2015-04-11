from sqlalchemy import *
from database import User
from database import Beatmaps
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
import operator
import time

engine = create_engine("sqlite:///test3.db")

Session = sessionmaker(bind=engine)
session = Session()

# x = session.query(User).filter(User.username == "ApolloFortyNine").all()
# if x:
#    print("hey")
# for y in x:
#    session.delete(y)


# wubwoofwolf = session.query(User).filter(User.username == "WubWoofWolf").first()
user_test = session.query(User).filter(User.username == "CAPSLOCKLOL").first()
# print(wubwoofwolf.beatmaps[5].beatmap_id)
users_dict = {}
start = time.time()

for x in range(50):
    print(x)
    comparison = session.query(Beatmaps).filter((Beatmaps.beatmap_id == user_test.beatmaps[x].beatmap_id) &
                                                (Beatmaps.enabled_mods == user_test.beatmaps[x].enabled_mods)).all()
    for y in comparison:
        #print(y.user_id)
        if str(y.user_id) in users_dict:
            users_dict[str(y.user_id)] += 1
        else:
            users_dict[str(y.user_id)] = 1
time_passed = (time.time() - start)
print(time_passed)
print("\n")
# new_users_dict = sorted(users_dict.items(), key=operator.itemgetter(1), reverse=True)
# print(new_users_dict)
best_match = 0
best_user = ""
for x in list(users_dict):
    if (users_dict[x] > best_match) & (users_dict[x] != 50):
        best_match = users_dict[x]
        best_user = x
print(best_user)
new_users_dict = sorted(users_dict.items(), key=operator.itemgetter(1), reverse=True)
print(new_users_dict)