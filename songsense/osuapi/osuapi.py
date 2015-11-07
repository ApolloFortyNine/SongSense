"""
Osu Api Implementation by Ryan Quinn
Tested with Python 3.4

Functions
    get_beatmaps(since='', set_id=-1, map_id=-1, user_id=-1)
    get_user(user, mode=0, user_type='string', event_days=1)
    get_scores(map_id, user_id=-1, mode=0)
    get_user_best(user, mode=0, limit=10, user_type='string')
    get_user_recent(user, mode=0, user_type='id')
    get_match(match_id)

See https://github.com/peppy/osu-api/wiki for full documentation
"""
import httplib2
import urllib
import json


class OsuApi:
    def __init__(self, api_key):
        self.api_key = api_key
        self.h = httplib2.Http()

    def get_beatmaps(self, since='', set_id=-1, map_id=-1, user_id=-1):
        base_url = 'https://osu.ppy.sh/api/get_beatmaps?'
        params = urllib.parse.urlencode({'k': self.api_key})
        if since != '':
            params += '&' + urllib.parse.urlencode({'since': since})
        if set_id != -1:
            params += '&' + urllib.parse.urlencode({'s': set_id})
        if map_id != -1:
            params += '&' + urllib.parse.urlencode({'b': map_id})
        if user_id != -1:
            params += '&' + urllib.parse.urlencode({'u': user_id})
        full_url = base_url + params
        response, content = self.h.request(full_url)
        obj = json.loads(content.decode('utf-8'))
        return obj

    def get_user(self, user, mode=0, user_type='string', event_days=1):
        base_url = 'https://osu.ppy.sh/api/get_user?'
        params = urllib.parse.urlencode({'k': self.api_key, 'u': user, 'mode': mode, 'type': user_type,
                                         'event_days': event_days})
        full_url = base_url + params
        response, content = self.h.request(full_url)
        obj = json.loads(content.decode('utf-8'))
        return obj

    def get_scores(self, map_id, user_id=-1, mode=0):
        base_url = 'https://osu.ppy.sh/api/get_scores?'
        if user_id == -1:
            params = urllib.parse.urlencode({'k': self.api_key, 'b': map_id, 'mode': mode})
        else:
            params = urllib.parse.urlencode({'k': self.api_key, 'u': user_id, 'mode': mode})
        full_url = base_url + params
        response, content = self.h.request(full_url)
        obj = json.loads(content.decode('utf-8'))
        return obj

    def get_user_best(self, user, mode=0, limit=10, user_type='string'):
        base_url = 'https://osu.ppy.sh/api/get_user_best?'
        params = urllib.parse.urlencode({'k': self.api_key, 'u': user, 'mode': mode, 'limit': limit, 'type': user_type})
        full_url = base_url + params
        response, content = self.h.request(full_url)
        obj = json.loads(content.decode('utf-8'))
        return obj

    def get_user_recent(self, user, mode=0, user_type='id'):
        base_url = 'https://osu.ppy.sh/api/get_user_recent?'
        params = urllib.parse.urlencode({'k': self.api_key, 'u': user, 'mode': mode, 'type': user_type})
        full_url = base_url + params
        response, content = self.h.request(full_url)
        obj = json.loads(content.decode('utf-8'))
        return obj

    def get_match(self, match_id):
        base_url = 'https://osu.ppy.sh/api/get_match?'
        params = urllib.parse.urlencode({'k': self.api_key, 'mp': match_id})
        full_url = base_url + params
        response, content = self.h.request(full_url)
        obj = json.loads(content.decode('utf-8'))
        return obj

