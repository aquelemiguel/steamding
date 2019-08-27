from infi.systray import SysTrayIcon
import configparser

import re
import requests
from bs4 import BeautifulSoup

import pymsgbox

cfg = configparser.ConfigParser()
cfg.read('settings.ini')

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

def open_settings(systray):
    steamid64 = pymsgbox.prompt('Insert your steamid64 below')
    cfg.set('DEFAULT', 'STEAMID64', str(steamid64))
    
    with open('settings.ini', 'w') as cfg_file:
        cfg.write(cfg_file)


menu_options = (('Settings', None, open_settings),)
systray = SysTrayIcon('static/logo.ico', 'steamding', menu_options)

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