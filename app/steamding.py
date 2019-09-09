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
from functools import partial

cfg = configparser.ConfigParser()
gd_t, sa_t = None, None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def play_notification_sound(systrayicon = None):
    playsound(resource_path(f"static/sfx/{cfg.get('DEFAULT', 'SFX')}"), False)

def update_config_property(prop, val, systrayicon=None):
    cfg.set('DEFAULT', prop, val)
    
    with open(resource_path('settings.ini'), 'w') as cfg_file:
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

    appid = [app['appid'] for app in data['applist']['apps'] if app['name'] == title]
    return appid[0] if len(appid) > 0 else None

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
    sfx_tuple = (('Test sound', resource_path('static/img/bell.ico'), play_notification_sound),)

    for sfx_name in os.listdir(resource_path('static/sfx')):
        sfx_tuple = sfx_tuple + ((sfx_name, None, partial(update_config_property, 'SFX', sfx_name)),)

    root = (
        ('Reload', None, start_tracking),
        ('Options', None, (
            ('Change notification', None, sfx_tuple),
            ('Check privacy settings...', None, lambda x: webbrowser.open('https://steamcommunity.com/my/edit/settings')),
            ('Edit configuration...', None, lambda x: webbrowser.open('.\settings.ini')))),
        ('Help', 'static/img/github.ico', lambda x: webbrowser.open('https://github.com/aquelemiguel/steamding')),
        ('Donate', 'static/img/coffee.ico', lambda x: webbrowser.open('https://paypal.me/aquelemiguel/')))
    
    systray = SysTrayIcon(resource_path('static/img/logo.ico'), 'steamding', root)
    return systray

def show_toast(header, body, duration = 5):
    toaster.show_toast(header, body, icon_path=resource_path('static/img/w_logo.ico'), duration=duration, threaded=True)

def run_state_machine(persona_name, profile_url, out_queue):
    title = None

    while True:
        temp_title = scrape_game_title(profile_url)

        #   If the state has changed...
        if title != temp_title:
            title = temp_title
            
            #   The player is Online.
            if title == 'Currently Online':
                out_queue.put(('Online', -1))
                show_toast('Sucessfully running!', f'Welcome {persona_name}, you\'re currently not playing anything.')
                
            #   The player is Offline.
            elif title == 'Currently Offline':
                out_queue.put(('Offline', -1))
                show_toast('Successfully running!', f'Welcome {persona_name}, you\'re currently offline.')
            
            #   The player is Playing.
            else:
                appid = convert_title_to_appid(title)
                out_queue.put((title, appid))
            

def scrape_achievements_thread(persona_name, profile_url, in_queue):
    appid_curr = appid_new = -1
    ach_no_curr = -1

    while True:
        #   Lock until appid matches a game.
        while appid_new == -1:
            appid_curr = -1  # Reset because of Playing -> Online, Online -> Playing the same game.
            (title, appid_new) = in_queue.get(block=True)
        
        try:
            if appid_new != -1:
                (title, appid_new) = in_queue.get(block=False)
        except queue.Empty:
            pass    # If we didn't receive anything, means we're remaining in the same state.

        if appid_new != -1:
            ach_info = scrape_achievements(profile_url, appid_new)

            if appid_new != appid_curr:
                appid_curr = appid_new
                ach_no_curr = -1  # Reset the achievement tracking for the new game.

                #   TODO: This alert will probably not display the correct title if the game switches.
                show_toast('Successfully running!', f'Welcome {persona_name}! Now tracking {title}, having unlocked {ach_info[0]} out of {ach_info[1]} ({ach_info[2]}%) achievements.')

            if ach_no_curr == -1:
                ach_no_curr = ach_info[0]

            if ach_no_curr != -1 and ach_info[0] != ach_no_curr:
                ach_no_curr = ach_info[0]
                play_notification_sound()


def start_tracking(systrayicon = None):
    cfg.read(resource_path('settings.ini'))
    steamid64 = cfg.get('DEFAULT', 'steamid64')
    profile_url = get_profile_url(steamid64)

    if profile_url is 'UNEXISTENT':
        show_toast('Could not find your profile!', 'Are you sure you\'ve correctly inputted your steamid64?')

    elif profile_url is 'PRIVATE':
        show_toast('Your profile appears to be private!', 'This app needs your profile to be public to fetch achievement info.')

    else:
        q = queue.Queue()
        persona_name = scrape_persona_name(profile_url)
        gd_t = threading.Thread(target=run_state_machine, args=(persona_name, profile_url, q,))
        sa_t = threading.Thread(target=scrape_achievements_thread, args=(persona_name, profile_url, q,))

        if gd_t == None: gd_t.kill()
        if sa_t == None: sa_t.kill()
        gd_t, sa_t = gd_t.start(), sa_t.start()

        gd_t.join()
        sa_t.join()

systray = setup_tray()
systray.start()

start_tracking()
