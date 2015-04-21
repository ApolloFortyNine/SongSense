"""
This script checks to see if any beatmaps have yet to be inserted into the database,
then adds them
"""
import datetime
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from songsense.config import Config
from songsense.database import BeatmapInfo, Base
from songsense.osuapi.osuapi import OsuApi


config = Config()
osu = OsuApi(config.osu_api_key)
engine = create_engine(config.engine_str, **config.engine_args)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine, checkfirst=True)
# beatmaps = session.query(Beatmap).options(load_only("beatmap_id")).\
# filter(Beatmap.beatmap_id < 5000).distinct().all()
beatmaps = session.execute("SELECT DISTINCT beatmap_id FROM beatmaps b WHERE b.beatmap_id NOT IN "
                           "(SELECT beatmap_id FROM beatmap_info)")
counter = 0
start_time = time.time()
for x in beatmaps:
    beatmap = session.query(BeatmapInfo).filter(BeatmapInfo.beatmap_id == x.beatmap_id).first()
    if beatmap is None:
        print(x.beatmap_id)
        beatmaps_info = osu.get_beatmaps(map_id=x.beatmap_id)
        for y in beatmaps_info:
            y['last_update'] = datetime.datetime.strptime(y['last_update'], "%Y-%m-%d %H:%M:%S")
            if y['approved_date'] is not None:
                y['approved_date'] = datetime.datetime.strptime(y['approved_date'],
                                                                "%Y-%m-%d %H:%M:%S")
            session.add(BeatmapInfo(**y))
        counter += 1
    if (counter % 20) == 0:
        session.commit()
    now = time.time() - start_time
    if (now < 60) & counter > 400:
        time.sleep(60 - (time.time() - start_time))
        start_time = time.time()
        counter = 0
    elif now > 60:
        start_time = time.time()
        counter = 0
session.commit()
session.close()