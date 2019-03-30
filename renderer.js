const howler = require('howler');
const scraper = require('./scraper');

let gameid; let profileurl; let count = -1;

const monitorAchievementUpdate = () => {
  scraper.fetchAchievementCount(profileurl, gameid, (err, res) => {
    if (err) return console.log(err);
    if (count === -1) { count = res; return; }
    if (res >= count) { count = res; playNotificationSound(); }
  });
};

const monitorPlayedGame = () => {
  scraper.fetchPlayingInfo('FE308435BF852EAD4175D2A70AA87C2D', '76561198051995233', (err, res) => {
    if (err) return console.log(err);
    ({ gameid, profileurl } = res); // Object destructure's assignment without declaration.

    if (gameid && profileurl) setTimeout(monitorAchievementUpdate, 2000);
  });
  setTimeout(monitorPlayedGame, 2000);
};

const playNotificationSound = () => {
  const howl = new howler.Howl({ src: ['sounds/ps3-trophy-sound-effect.mp3'] });
  howl.play();
};

const startMonitor = () => {
  monitorPlayedGame(); monitorAchievementUpdate();
};

startMonitor();
