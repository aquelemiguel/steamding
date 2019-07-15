const cheerio = require('cheerio');
const request = require('request');

const fetchPlayerProfile = (key, steamID) => new Promise((resolve, reject) => {
  request.get(`https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=${key}&steamids=${steamID}`, { json: true }, (err, _res, data) => {
    if (err) { reject(err); return; }

    if (!data.response) {
      reject(new Error('USER_NOT_LOGGED')); return;
    }

    resolve(data.response.players[0]);
  });
});

const getAppIDByGameName = name => new Promise((resolve, reject) => {
  request.get('https://api.steampowered.com/ISteamApps/GetAppList/v2', { json: true }, (err, _res, data) => {
    if (err) reject(err);
    const found = data.applist.apps.filter(game => game.name === name);

    if (found.length === 0) {
      reject(new Error(`GAME_DELETED: ${name}`)); return;
    }

    resolve(found[0].appid);
  });
});

const scrapeCurrentGame = profile => new Promise((resolve, reject) => {
  if (!profile) {
    reject(new Error('USER_NOT_LOGGED')); return;
  }

  request.get(profile.profileurl, { json: true }, (err, _res, data) => {
    if (err) { reject(err); return; }

    if (profile.communityvisibilitystate === 1) {
      reject(new Error('PRIVATE_PROFILE')); return;
    }

    const $ = cheerio.load(data);
    resolve($('div').hasClass('profile_in_game_name') ? $('.profile_in_game_name').text() : 'Online');
  });
});

const fetchAchievementNo = (profile, appid) => new Promise((resolve, reject) => {
  //  If the profile is unset, the user hasn't logged in.
  if (!profile) {
    reject(new Error('USER_NOT_LOGGED')); return;
  }

  //  If the appid is set to -1, the player isn't playing any game.
  if (appid === -1 || !appid) {
    reject(new Error('NOT_PLAYING')); return;
  }

  //  The community visibility state should be set to 3 (public).
  //  Otherwise (set to 1, meaning private), the scraper won't find the achievement page.
  if (profile.communityvisibilitystate === 1) {
    reject(new Error('PRIVATE_PROFILE')); return;
  }

  if (!profile || !appid) { reject(new Error('Undefined!')); return; }
  request.get(`${profile.profileurl}stats/${appid}/?tab=achievements`, (err, _res, data) => {
    console.log(`${profile.profileurl}stats/${appid}/?tab=achievements`);
    if (err) { reject(err); return; }

    //  If the privacy settings of a user aren't set so that the app can see unlocked
    //  achievement pages, the browser will redirect back to the user's community profile
    //  page. So, if the scraping returns the persona name, it means we got redirected
    //  to the profile page and the privacy settings aren't ideal.
    if (cheerio.load(data)('span[class=actual_persona_name]').text()) {
      reject(new Error('PRIVACY_INCORRECT')); return;
    }

    const count = cheerio.load(data)('div #topSummaryAchievements').text();
    if (!count) {
      reject(new Error('GAME_DELETED')); return;
    }

    resolve(count.trim().match(/(\d+)/)[0]);
  });
});

module.exports = {
  fetchPlayerProfile, scrapeCurrentGame, fetchAchievementNo, getAppIDByGameName,
};
