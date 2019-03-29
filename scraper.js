/* eslint-disable consistent-return */
/* eslint-disable no-console */
const cheerio = require('cheerio');
const request = require('request');

const fetchPlayingInfo = (key, steamid64, callback) => {
  request.get(`https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=${key}&steamids=${steamid64}`, { json: true }, (err, _res, body) => {
    if (err) return console.log(err);
    const player = body.response.players[0];

    if (player === undefined) return callback('invalid steamid64.', { gameid: player.gameid, profileurl: null });
    if (player.gameid === undefined) return callback('user not playing any game.', { gameid: null, profileurl: player.profileurl });

    callback(null, { gameid: player.gameid, profileurl: player.profileurl });
  });
};

const fetchAchievementCount = (steamurl, appid, callback) => {
  if (appid === undefined) return;

  request.get(`${steamurl}stats/${appid}/?tab=achievements`, (err, _res, html) => {
    if (err) return callback('invalid link.', null);

    const countText = cheerio.load(html)('div #topSummaryAchievements').text();

    if (countText === undefined) return callback('could not find game. has it been removed?', null);

    callback(null, countText.trim().match(/(\d+)/)[0]); // Regex to find the number of achievements.
  });
};

module.exports = {
  fetchPlayingInfo, fetchAchievementCount,
};
