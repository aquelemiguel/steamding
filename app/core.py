from infi.systray import SysTrayIcon
import configparser
import webbrowser
from playsound import playsound

import os
import sys
import re
import requests
from bs4 import BeautifulSoup

from win10toast import ToastNotifier
toaster = ToastNotifier()

import threading
import queue

cfg = configparser.ConfigParser()

def play_notification_sound(systrayicon = None):
    playsound(f"static/sfx/{cfg.get('DEFAULT', 'SFX')}", False)

def update_config_property(prop, val):
    cfg.set('DEFAULT', prop, val)
    
    with open('settings.ini', 'w') as cfg_file:
        cfg.write(cfg_file)

def scrape_game_title(profile_url):
    res = requests.get(profile_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    header = soup.find('div', attrs={'class': 'profile_in_game_header'})

    if header.text == 'Currently In-Game':
        title = soup.find('div', attrs={'class': 'profile_in_game_name'})
        return title.text
    
    return header.text

def scrape_persona_name(profile_url):
    res = requests.get(profile_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    persona_name = soup.find('span', attrs={'class': 'actual_persona_name'})
    return persona_name.text

def convert_title_to_appid(title):
    res = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
    data = res.json()

    appid = [app['appid'] for app in data['applist']['apps'] if app['name'] == title][0]
    return appid

def scrape_achievements(profile_url, appid):
    res = requests.get(f'{profile_url}stats/{appid}/achievements')
    soup = BeautifulSoup(res.text, 'html.parser')

    parent_el = soup.find('div', attrs={'id': 'topSummaryAchievements'})
    messy_ach_str = parent_el.find('div', recursive=False).text

    regex_res = re.search(r'(\d+) of (\d+) \((\d+)%\)', messy_ach_str)
    return regex_res.groups() if regex_res is not None else None

#   Provided a steamid64, returns the redirected URL, because the user may have set a custom URL for their profile.
def get_profile_url(steamid64):
    res = requests.get(f'https://steamcommunity.com/profiles/{steamid64}/')
    soup = BeautifulSoup(res.text, 'html.parser')

    if soup.find('h3', text='The specified profile could not be found.') is not None:
        return 'UNEXISTENT'

    if soup.find('div', attrs={'class': 'profile_private_info'}) is not None:
        return 'PRIVATE'

    return res.url

def setup_tray():
    sfx_tuple = (('Test sound', 'static/img/bell.ico', play_notification_sound),)

    for sfx_name in os.listdir('./static/sfx'):
        sfx_tuple = sfx_tuple + ((sfx_name, None, lambda x: update_config_property('SFX', sfx_name)),)

    root = (
        ('Reload', None, start_tracking),
        ('Options', None, (
            ('Change notification', None, sfx_tuple),
            ('Check privacy settings...', None, lambda x: webbrowser.open('https://steamcommunity.com/my/edit/settings')),
            ('Edit configuration...', None, lambda x: webbrowser.open('settings.ini')))),
        ('Help', 'static/img/github.ico', lambda x: webbrowser.open('https://github.com/aquelemiguel/steamding')),
        ('Donate', 'static/img/coffee.ico', lambda x: webbrowser.open('https://paypal.me/aquelemiguel/')))
    
    systray = SysTrayIcon('static/img/logo.ico', 'steamding', root)
    return systray

def show_toast(header, body, duration = 5):
    toaster.show_toast(header, body, icon_path='static/img/w_logo.ico', duration=duration, threaded=True)

def scrape_game_title_thread(profile_url, out_queue):
    while True:
        title = scrape_game_title(profile_url)
        appid = convert_title_to_appid(title)
        out_queue.put((title, appid))

def scrape_achievements_thread(persona_name, profile_url, in_queue):
    appid_curr = -1
    ach_no_curr = -1

    while True:
        try:
            (title, appid) = in_queue.get(block=True if appid_curr == -1 else False)
        except queue.Empty:
            pass

        ach_info = scrape_achievements(profile_url, appid)

        if appid != appid_curr:
            appid_curr = appid
            ach_no_curr = -1  # Reset the achievement tracking for the new game.

            #   TODO: This alert will probably not display the correct title if the game switches.
            show_toast('Successfully running!', f'Welcome {persona_name}! Now tracking {title}, having unlocked {ach_info[0]} out of {ach_info[1]} ({ach_info[2]}%) achievements.')

        if ach_no_curr == -1:
            ach_no_curr = ach_info[0]

        if ach_no_curr != -1 and ach_info[0] != ach_no_curr:
            ach_no_curr = ach_info[0]
            play_notification_sound()


def start_tracking(systrayicon = None):
    cfg.read('settings.ini')
    steamid64 = cfg.get('DEFAULT', 'steamid64')
    profile_url = get_profile_url(steamid64)

    if profile_url is 'UNEXISTENT':
        show_toast('Could not find your profile!', 'Are you sure you\'ve correctly inputted your steamid64?')

    if profile_url is 'PRIVATE':
        show_toast('Your profile appears to be private!', 'This app needs your profile to be public to fetch achievement info.')

    title = scrape_game_title(profile_url)
    persona_name = scrape_persona_name(profile_url)

    if title == 'Currently Online':
        show_toast('Sucessfully running!', f'Welcome {persona_name}, you\'re currently not playing anything.')

    elif title == 'Currently Offline':
        show_toast('Successfully running!', f'Welcome {persona_name}, you\'re currently offline.')
    
    else:
        q = queue.Queue()
        gd_t = threading.Thread(target=scrape_game_title_thread, args=(profile_url, q,))
        sa_t = threading.Thread(target=scrape_achievements_thread, args=(persona_name, profile_url, q,))

        gd_t.start()
        sa_t.start()

systray = setup_tray()
systray.start()

start_tracking()