import configparser
import requests
import re

from bs4 import BeautifulSoup
from steam import WebAPI

config = configparser.ConfigParser()
config.read('config.ini')

def auth_steam_api(key):
    steam = WebAPI(key)
    print('Authenticated to Steam Web API!')
    return steam

def get_playing_id(steam):
    res = steam.call('ISteamUser.GetPlayerSummaries', steamids='76561198051995233')
    return res['response']['players'][0].get('gameid')

def get_achievement_count(appid):
    if (appid == None): return

    url = f"https://steamcommunity.com/id/{config['PROFILE']['CustomURL']}/stats/{appid}/achievements/"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    ach_stats = soup.find('div', {'id': 'topSummaryAchievements'}).getText()

    return re.match(r"(\d+)", ach_stats).group(1)



    
    



