from infi.systray import SysTrayIcon
import configparser
import webbrowser
from playsound import playsound

import os
import sys
import re
import requests
from bs4 import BeautifulSoup

import tkinter as tk
from PIL import Image, ImageTk

cfg = configparser.ConfigParser()
cfg.read('settings.ini')

def play_notification_sound(systrayicon):
    playsound(f"static\sfx\{cfg.get('DEFAULT', 'SFX')}", False)

def update_config_property(prop, val):
    cfg.set('DEFAULT', prop, val)
    
    with open('settings.ini', 'w') as cfg_file:
        cfg.write(cfg_file)

def scrape_game_title(profile_url):
    res = requests.get(profile_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.find('div', attrs={'class': 'profile_in_game_name'})

    #   TODO: Eventually handle this exception.
    if title is None:
        return

    return title.text

def convert_title_to_appid(title):
    res = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
    data = res.json()

    appid = [app['appid'] for app in data['applist']['apps'] if app['name'] == title][0]
    return appid

def scrape_achievement_no(profile_url, appid):
    res = requests.get(f'{profile_url}stats/{appid}/achievements')
    soup = BeautifulSoup(res.text, 'html.parser')

    parent_el = soup.find('div', attrs={'id': 'topSummaryAchievements'})
    messy_ach_str = parent_el.find('div', recursive=False).text

    regex_res = re.search(r'(\d+) of', messy_ach_str)
    ach_no = regex_res.group(1) if regex_res is not None else 'Not found!'

    return ach_no

#   Provided a steamid64, returns the redirected URL, because the user may have set a custom URL for their profile.
def get_profile_url(steamid64):
    res = requests.get(f'https://steamcommunity.com/profiles/{steamid64}/')
    return res.url

def setup_tray():
    sfx_tuple = (('Test sound', 'static/img/bell.ico', play_notification_sound),)

    for sfx_name in os.listdir('./static/sfx'):
        sfx_tuple = sfx_tuple + ((sfx_name, None, lambda x: update_config_property('SFX', sfx_name)),)

    root = (
        ('Options', None, (
            ('Change notification', None, sfx_tuple),
            ('Check privacy settings...', None, lambda x: webbrowser.open('https://steamcommunity.com/my/edit/settings')),
            ('Edit configuration...', None, lambda x: webbrowser.open('settings.ini')))),
        ('Help', 'static/img/github.ico', lambda x: webbrowser.open('https://github.com/aquelemiguel/steamding')),
        ('Donate', 'static/img/coffee.ico', lambda x: webbrowser.open('https://paypal.me/aquelemiguel/')))
    
    systray = SysTrayIcon('static/img/logo.ico', 'steamding', root)
    return systray

systray = setup_tray()
systray.start()


"""
profile_url = get_profile_url(76561197961739246)
print(profile_url)
title = scrape_game_title(profile_url)
print(title)
appid = convert_title_to_appid(title)
print(appid)
ach_no = scrape_achievement_no(profile_url, appid)
print(ach_no)
"""