/* eslint-disable no-console */
const howler = require('howler');
const scraper = require('../src/scraper');

let gameid; let profileurl; let count = null;

// Play an achievement unlocked sound stored at file path ./resources/...
const playUnlockSound = (sfxPath) => {
  const howl = new howler.Howl({
    src: [`../resources/${sfxPath}.mp3`],
    onloaderror: () => console.log('Invalid path!'), // TODO: Eventually throw a cooler alert instead of this default one.
    onload: () => howl.play(),
  });
};

// Handling of changes to the steamid64 text input while Steam login isn't implemented.
document.getElementById('steamid64-btn').addEventListener('click', () => {
  scraper.fetchPlayerInfo('FE308435BF852EAD4175D2A70AA87C2D', document.getElementById('steamid64').value, (err, res) => {
    if (err) { console.log(err); return; }
    document.getElementById('status-message').innerHTML = `Tracking ${res.personaname}`; // Set persona name.
    console.log(res);
  });
});

// Handling of preview selected sound effect.
document.getElementById('preview-sfx-btn').addEventListener('click', () => {
  playUnlockSound(document.getElementById('sfxpath').value);
});

const monitorAchievementUpdate = () => {
  scraper.fetchAchievementCount(profileurl, gameid, (err, res) => {
    if (err) return console.log(err);
    if (count !== null && res > count) playNotificationSound('xbox-360');
    count = res;
  });
};

const monitorPlayedGame = () => {
  scraper.fetchPlayingInfo('FE308435BF852EAD4175D2A70AA87C2D', '76561198051995233', (err, res) => {
    if (err) return console.log(err);
    if (gameid && profileurl) setTimeout(monitorAchievementUpdate, 1000);
    ({ gameid, profileurl } = res); // Object destructure's assignment without declaration.
  });
  setTimeout(monitorPlayedGame, 1000);
};


const startMonitor = () => {
  //monitorPlayedGame(); monitorAchievementUpdate();
};

startMonitor();
