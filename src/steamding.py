import time
import requests
import configparser
from playsound import playsound
from random import randrange
import json
from enum import Enum
from threading import Lock, Thread

cfg = configparser.ConfigParser()
cfg.read('./src/cfg.ini')

class AchievementType(Enum):
    REGULAR = 1
    RARE = 2
    PLATINUM = 3

appid = -1
achieved_set = None
rarity_set = {}

lock = Lock()

def update_appid(new_appid):
    global appid
    lock.acquire()
    appid = new_appid
    lock.release()

def make_request(endpoint):
    try:
        return json.loads(requests.get(endpoint).content)
    except requests.exceptions.RequestException as e:
        print(e)
    
def fetch_achievement_percentages(appid):
    while True:
        content = make_request(("https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/"
        f"?gameid={appid}?__random={randrange(10000000)}"))

        # This request must not fail, so retry if it doesn't succeed
        if content is None: continue
        return {ach['name']: ach['percent'] for ach in content['achievementpercentages']['achievements']}

def fetch_playing_appid():
    while True:
        global appid, rarity_set

        content = make_request(("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={cfg['AUTH']['apikey']}&steamids={cfg['AUTH']['steamid64']}?__random={randrange(10000000)}"))

        if content is None: continue
        res = content['response']['players'][0]

        # Started playing a new game, so we should update the appid and achievement percentages
        if 'gameid' in res and res['gameid'] != appid:
            update_appid(res['gameid'])
            rarity_set = fetch_achievement_percentages(appid)

        if 'gameid' not in res:
            update_appid(-1)
        
        time.sleep(int(cfg['GENERAL']['ping_delay_ms']) / 1000)

def fetch_achievements():
    while True:
        time.sleep(0.5)
        global achieved_set

        lock.acquire()
        if (appid == -1):
            achieved_set = None
            print('Waiting...')
            lock.release()
            continue

        content = make_request(("https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
        f"?appid={appid}&key={cfg['AUTH']['apikey']}&steamid={cfg['AUTH']['steamid64']}?__random={randrange(10000000)}"))
        lock.release()

        if content is None: continue
        new_achieved_set = {ach['apiname'] for ach in content['playerstats']['achievements'] if ach['achieved'] == 1}

        # Player has just booted the game, so load the achievements into the set and don't play notification
        if achieved_set is None:
            achieved_set = new_achieved_set
            print(f"Tracking '{content['playerstats']['gameName']}' ({len(new_achieved_set)}/{len(rarity_set)} achievements unlocked)")
            continue

        # An achievement has unlocked...
        if len(new_achieved_set - achieved_set) > 0:
            for new_ach in new_achieved_set - achieved_set:
                print(f"\nUnlocked {new_ach}! ({len(new_achieved_set)}/{len(rarity_set)})")

                if len(new_achieved_set) == len(rarity_set):
                    play_notification_sound(AchievementType.PLATINUM)
                
                elif rarity_set[new_ach] < float(cfg['GENERAL']['rare_percent']):
                    play_notification_sound(AchievementType.RARE)

                else:
                    play_notification_sound(AchievementType.REGULAR)
            
            achieved_set = new_achieved_set

def play_notification_sound(type):
    playsound({
        AchievementType.REGULAR: './assets/sfx/ps5/regular.mp3',
        AchievementType.RARE: './assets/sfx/ps5-bliss/regular.mp3',
        AchievementType.PLATINUM: './assets/sfx/ps5/platinum.mp3'
    }[type])

def start_tracking():
    fpa_t = Thread(target=fetch_playing_appid)
    ach_t = Thread(target=fetch_achievements)

    fpa_t.start()
    ach_t.start()

if __name__ == "__main__":
    start_tracking()