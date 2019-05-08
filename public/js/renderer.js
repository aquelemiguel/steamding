/* eslint-disable no-console */
const howler = require('howler');
const scraper = require('./scraper.js');

let user; let playingTitle = ''; let count = null;

// Play an achievement unlocked sound stored at file path ./resources/...
const playUnlockSound = (sfxPath) => {
  const howl = new howler.Howl({
    src: [`sfx/${sfxPath}.mp3`],
    onloaderror: () => console.log('Invalid path!'), // TODO: Eventually throw a cool alert instead of this default one.
    onload: () => howl.play(),
  });
};

const trackAchievements = (profileurl, gameid) => {
  scraper.fetchAchievementCount(profileurl, gameid, (err, res) => {
    if (err) return console.log(err);
    if (count && res > count) playUnlockSound(document.getElementById('sfxpath').value);
    count = res; return true;
  });
};

// Check for changes on the game currently being played.
const trackPlayingInfo = (profileurl) => {
  scraper.scrapeCurrentlyPlayingGame(profileurl, (err, res) => {
    if (err) console.log(err);
    if (res !== playingTitle) {
      playingTitle = res;
      document.getElementById('status-message-game').innerHTML = res;
    }
  });
  if (!user) return; // No need to track gameplay if user isn't defined.
  const pr = document.getElementById('polling-rate').value;
  setTimeout(trackPlayingInfo, pr, user ? user.profileurl : user);
  setTimeout(trackAchievements, pr, user ? user.profileurl : user, user ? user.gameid : user);
};

// Handling of changes to the steamid64 text input while Steam login isn't implemented.
document.getElementById('steamid64-btn').addEventListener('click', () => {
  scraper.fetchPlayerInfo('FE308435BF852EAD4175D2A70AA87C2D', document.getElementById('steamid64').value, (err, res) => {
    if (err) { console.log(err); return; } user = res;
    document.getElementById('status-message-user').innerHTML = user.personaname; // Set persona name.

    if (user.gameextrainfo) document.getElementById('status-message-game').innerHTML = `Playing ${user.gameextrainfo}`;
    else document.getElementById('status-message-game').innerHTML = 'Online';

    trackPlayingInfo(user ? user.profileurl : user); // Start tracking the player info.
  });
});

// Handling of preview selected sound effect.
document.getElementById('preview-sfx-btn').addEventListener('click', () => {
  playUnlockSound(document.getElementById('sfxpath').value);
});

// Key: FE308435BF852EAD4175D2A70AA87C2D
// ID:  76561198051995233
