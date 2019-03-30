const howler = require('howler');
const scraper = require('../src/scraper');

let gameid; let profileurl; let count = null;

const playNotificationSound = () => {
  const howl = new howler.Howl({ src: ['resources/xbox-360.mp3'] });
  howl.play();
};

const monitorAchievementUpdate = () => {
  scraper.fetchAchievementCount(profileurl, gameid, (err, res) => {
    if (err) return console.log(err);
    if (count !== null && res > count) playNotificationSound();
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
  monitorPlayedGame(); monitorAchievementUpdate();
};

startMonitor();
