const cheerio = require('cheerio');
const request = require('request');

const fetchPlayerProfile = (key, steamID) => new Promise((resolve, reject) => {
  request.get(`https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=${key}&steamids=${steamID}`, { json: true }, (err, _res, data) => {
    if (err) reject(err);

    resolve(data.response.players[0]);
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

    const count = cheerio.load(data)('div #topSummaryAchievements').text();
    resolve(count === undefined ? 'Unavailable!' : count.trim().match(/(\d+)/)[0]);
  });
});

module.exports = {
  fetchPlayerProfile, scrapeCurrentGame, fetchAchievementNo,
};
