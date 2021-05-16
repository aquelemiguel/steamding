import time
import requests
import configparser
from playsound import playsound
from random import randrange
import json
from enum import Enum
from threading import Thread, Event

cfg = configparser.ConfigParser()
cfg.read('cfg.ini')

class AchievementType(Enum):
    REGULAR = 1
    RARE = 2
    PLATINUM = 3

def terminate_thread(thread, event):
    if thread.is_alive():
        event.clear()
        thread.join()   

def make_request(endpoint):
    try:
        return json.loads(requests.get(endpoint).content)
    except requests.exceptions.RequestException as e:
        print(e)
    
def fetch_achievement_percentages(appid):
    while True:
        content = make_request(("https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
        f"?gameid={appid}?__random={randrange(10000000)}"))

        # This request must not fail, so retry if it doesn't succeed
        if content is None: continue
        return {ach['name']: ach['percent'] for ach in content['achievementpercentages']['achievements']}

def fetch_playing_appid(run_event):
    appid = None
    ach_t = Thread()
    ach_run_event = Event()
    ach_run_event.set()

    while run_event.is_set():
        content = make_request(("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
        f"?key={cfg['AUTH']['apikey']}&steamids={cfg['AUTH']['steamid64']}?__random={randrange(10000000)}"))

        if content is None: continue
        res = content['response']['players'][0]

        # Started playing a new game, so we should update the appid and achievement percentages
        if 'gameid' in res and res['gameid'] != appid:
            appid = res['gameid']
            rarity_set = fetch_achievement_percentages(appid)
            
            terminate_thread(ach_t, ach_run_event)

            ach_t = Thread(target=fetch_achievements, args=(appid, rarity_set, ach_run_event,))
            ach_run_event.set()
            ach_t.start()

        if 'gameid' not in res:
            appid = None
            terminate_thread(ach_t, ach_run_event)
        
        time.sleep(int(cfg['GENERAL']['ping_delay_ms']) / 1000)
    
    terminate_thread(ach_t, ach_run_event)

def fetch_achievements(appid, rarity_set, run_event):
    achieved_set = None

    while run_event.is_set():
        print(appid)
        time.sleep(0.5)

        content = make_request(("https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
        f"?appid={appid}&key={cfg['AUTH']['apikey']}&steamid={cfg['AUTH']['steamid64']}?__random={randrange(10000000)}"))

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
        AchievementType.REGULAR: '../assets/sfx/ps5/regular.mp3',
        AchievementType.RARE: '../assets/sfx/ps5-bliss/regular.mp3',
        AchievementType.PLATINUM: '../assets/sfx/ps5/platinum.mp3'
    }[type])

def start_threading():
    fpa_run_event = Event()
    fpa_run_event.set()

    fpa_t = Thread(target=fetch_playing_appid, args=(fpa_run_event,))
    fpa_t.start()

    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("Safely closing threads...")
        fpa_run_event.clear()
        fpa_t.join()
        print("Goodbye!")

if __name__ == "__main__":
    start_threading()