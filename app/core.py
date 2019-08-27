from infi.systray import SysTrayIcon
import configparser
import webbrowser
from playsound import playsound

import os
import re
import requests
from bs4 import BeautifulSoup

import tkinter as tk
from PIL import Image, ImageTk

cfg = configparser.ConfigParser()
cfg.read('settings.ini')

def start_tracking():
    pass

def play_notification_sound():
    playsound(f"static\sfx\{cfg.get('DEFAULT', 'SFX')}", False)

def show_interface():
    root = tk.Tk()
    root.geometry('500x300')
    root.title('steamding')

    #   Display logo.
    logo = tk.PhotoImage(file='static/b_horizontal.png').subsample(4, 4)
    tk.Label(root, image=logo).pack()
    tk.Button(root, text='Test', command=play_notification_sound).pack()
    tk.Button(root, text='Start', command=start_tracking).pack()
    
    root_menu = tk.Menu(root)
    root.config(menu=root_menu)

    options_menu = tk.Menu(root_menu, tearoff=False)
    root_menu.add_cascade(label='Settings', menu=options_menu)

    options_menu.add_command(label='steamid64', command=open_steamid64_win)
    
    sfx_submenu = tk.Menu(options_menu, tearoff=False)
    
    for sfx in os.listdir('./static/sfx'):
        sfx_submenu.add_command(label=sfx, command=lambda: update_config_property('SFX', sfx))

    options_menu.add_cascade(label='Sound effect', menu=sfx_submenu)
    
    root_menu.add_command(label='Help', command=lambda: webbrowser.open('https://github.com/aquelemiguel/steamding'))
    root.mainloop()

def open_steamid64_win():
    window = tk.Toplevel()
    tk.Label(window, text='Enter your steamid64').pack()
    entry = tk.Entry(window)
    entry.pack()
    tk.Button(window, text='Save', command=lambda: [update_config_property('STEAMID64', entry.get()), window.destroy()]).pack()

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

menu_options = (
    ('Help', None, lambda x: webbrowser.open('https://github.com/aquelemiguel/steamding')),
    ('Donate', None, lambda x: webbrowser.open('https://paypal.me/aquelemiguel/1')))

systray = SysTrayIcon('static/logo.ico', 'steamding', menu_options)

# systray.start()
show_interface()

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