import requests
import re

from bs4 import BeautifulSoup
from steam import WebAPI

def auth_steam_api(key):
    steam = WebAPI(key)
    print('Authenticated to Steam Web API!')
    return steam

def get_playing_appid(steamapi, steamid):
    res = steamapi.call('ISteamUser.GetPlayerSummaries', steamids=steamid)
    return res['response']['players'][0].get('gameid')

def get_achievement_count(appid, steamurl):
    if (appid == None): return

    url = f"https://steamcommunity.com/id/{steamurl}/stats/{appid}/achievements/"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    ach_stats = soup.find('div', {'id': 'topSummaryAchievements'})

    if (ach_stats == None):
        print(f"Couldn't retrieve achievement info from appid {appid}! Has the game been removed from the store?")
        return None

    return re.match(r"(\d+)", ach_stats.getText()).group(1)



    
    



