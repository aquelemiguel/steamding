import winsound
import os

from crawler import *
from threading import Thread
from time import sleep

appid, counter, sfx = None, 0, ""

def init():
    config = configparser.ConfigParser()
    config.read('config.ini')

    sfx = os.listdir('../res/')[int(config['SETTINGS']['sfx'])]
    return (auth_steam_api('390FBBE3C9EA8D2947AECEE45478159A'), sfx)

def actively_check_playing(steam):
    global appid

    while (True):
        appid = get_playing_id(steam)
        sleep(5)

def actively_check_achievement_count(sfx):
    global counter, appid
    prev_appid, prev_counter = None, 0

    while (True):
        counter = get_achievement_count(appid)

        if counter == None: 
            continue

        if prev_appid == appid and prev_counter < counter:
            winsound.PlaySound(f"../res/{sfx}", winsound.SND_FILENAME)

        prev_appid = appid
        prev_counter = counter 

def loop(steam, sfx):
    app_t = Thread(target=actively_check_playing, args=(steam,))
    app_t.start()

    ach_t = Thread(target=actively_check_achievement_count, args=(sfx,))
    ach_t.start()

boot = init()
loop(boot[0], boot[1])