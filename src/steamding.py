import time
import requests
import configparser
from playsound import playsound
from random import randrange
import json
from threading import Lock, Thread

cfg = configparser.ConfigParser()
cfg.read('cfg.ini')

appid = -1
unlocked_cnt = -1

lock = Lock()

def fetch_playing_appid():
    while True:
        time.sleep(int(cfg['GENERAL']['ping_delay_ms']) / 1000)
        global appid

        endpoint = ("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={cfg['AUTH']['apikey']}&steamids={cfg['AUTH']['steamid64']}?__random={randrange(10000000)}")

        res = json.loads(requests.get(endpoint).content)['response']['players'][0]

        lock.acquire()
        appid = res['gameid'] if 'gameextrainfo' in res else -1
        lock.release()

def fetch_achievements():
    while True:
        time.sleep(1)
        global unlocked_cnt

        lock.acquire()
        if (appid == -1):
            unlocked_cnt = -1
            lock.release()
            continue

        endpoint = ("https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
        f"?appid={appid}&key={cfg['AUTH']['apikey']}&steamid={cfg['AUTH']['steamid64']}?__random={randrange(10000000)}")
        lock.release()

        res = json.loads(requests.get(endpoint).content)['playerstats']
        newly_achieved = [ach for ach in res['achievements'] if ach['achieved'] == 1]

        print(newly_achieved)

        if len(newly_achieved) > unlocked_cnt and unlocked_cnt != -1:
            play_notification_sound()
        unlocked_cnt = len(newly_achieved)

def play_notification_sound():
    playsound('../assets/sfx/playstation.mp3')

def start_tracking():
    fpa_t = Thread(target=fetch_playing_appid)
    ach_t = Thread(target=fetch_achievements)

    fpa_t.start()
    ach_t.start()

start_tracking()