from bs4 import BeautifulSoup
import requests


class Scrape():
    def __init__(self, name):
        self.name = name

    def get_scores(self, user_id):
        user_url = "https://osu.ppy.sh/u/" + str(user_id)
        r = requests.get(user_url)
        data = r.text
        soup = BeautifulSoup(data)