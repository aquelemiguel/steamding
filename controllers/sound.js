const howler = require('howler');
const path = require('path');

const previewUnlockSound = (sfxPath) => {
  console.log(path.join(`sfx/${sfxPath}.mp3`));
  const howl = new howler.Howl({
    src: [path.join(`sfx/${sfxPath}.mp3`)],
    onloaderror: (err) => { console.log(err); },
    onload: () => howl.play(),
  });
};

module.exports = { previewUnlockSound };
