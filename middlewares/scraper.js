const cheerio = require('cheerio');
const request = require('request');

const fetchPlayerProfile = (key, steamID) => new Promise((resolve, reject) => {
  request.get(`https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=${key}&steamids=${steamID}`, { json: true }, (err, _res, data) => {
    if (err) reject(err);
    resolve(data.response.players[0]);
  });
});

const getAppIDByGameName = name => new Promise((resolve, reject) => {
  request.get('https://api.steampowered.com/ISteamApps/GetAppList/v2', { json: true }, (err, _res, data) => {
    if (err) reject(err);
    resolve(data.applist.apps.filter(game => game.name === name)[0].appid);
  });
});

const scrapeCurrentGame = profileurl => new Promise((resolve, reject) => {
  request.get(profileurl, { json: true }, (err, _res, data) => {
    if (err) reject(err);

    const $ = cheerio.load(data);
    resolve($('div').hasClass('profile_in_game_name') ? `Playing ${$('.profile_in_game_name').text()}` : 'Online');
  });
});

const fetchAchievementNo = (profileurl, appid) => new Promise((resolve, reject) => {
  if (!appid) return;
  request.get(`${profileurl}stats/${appid}/?tab=achievements`, (err, _res, data) => {
    if (err) reject(err);

    //  If the privacy settings of a user aren't set so that the app can see unlocked
    //  achievement pages, the browser will redirect back to the user's community profile
    //  page. So, if the scraping returns the persona name, it means we got redirected
    //  to the profile page and the privacy settings aren't ideal.
    if (!(cheerio.load(data)('span[class=actual_persona_name]').text())) {
      resolve('PRIVACY_INCORRECT'); return;
    }

    const count = cheerio.load(data)('div #topSummaryAchievements').text();
    resolve(!count ? count.trim().match(/(\d+)/)[0] : 'GAME_DELETED');
  });
});

module.exports = {
  fetchPlayerProfile, scrapeCurrentGame, fetchAchievementNo, getAppIDByGameName,
};
