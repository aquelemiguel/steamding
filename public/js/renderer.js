const io = require('socket.io-client');

// Socket handling.
const initSocket = (steamID) => {
  const socket = io();
  socket.on('connect', () => socket.emit('ADD_CLIENT', steamID));
  socket.on('ACHIEVEMENT_UNLOCKED', () => new Audio(`sfx/${document.querySelector('#sfx-select').value}.mp3`).play());
  socket.on('LOG', (log) => { document.getElementById('logger').value = `${document.getElementById('logger').value}\n${log}`; });
};

const startTracking = () => {
  const xtr = new XMLHttpRequest();
  xtr.open('POST', '/track', true);
  xtr.send();
};

if (document.getElementById('preview')) {
  document.getElementById('preview').addEventListener(('click'), () => {
    const snd = new Audio(`sfx/${document.querySelector('#sfx-select').value}.mp3`);
    snd.play();
  });
}

if (document.getElementById('track')) {
  const elem = document.getElementById('track');
  document.getElementById('track').addEventListener(('click'), () => {
    if (elem.innerHTML === 'Start tracking') {
      elem.innerHTML = 'Stop tracking';
      startTracking();
    } else {
      elem.innerHTML = 'Start tracking';
    }
  });
}

const isLoggedIn = () => {
  const xtr = new XMLHttpRequest();
  xtr.onload = () => {
    // If the user logged in with Steam, then register it on the socket.
    if (JSON.parse(xtr.response)) {
      initSocket(xtr.response);
    }
  };
  xtr.open('GET', '/auth/islogged', true);
  xtr.send();
};

const fetchProfile = () => {
  const xtr = new XMLHttpRequest();
  xtr.onload = () => {
    if (xtr.response) {
      console.log(xtr.response);
      document.getElementById('persona-name').innerHTML = xtr.response.personaname;
      document.getElementById('profile-avatar').src = xtr.response.avatarmedium;
      document.getElementById('persona-playing').innerHTML = (xtr.response.gameextrainfo ? `Playing ${xtr.response.gameextrainfo}` : 'Not playing');
    }
  };
  xtr.responseType = 'json';
  xtr.open('GET', '/fetchprofile', true);
  xtr.send();
};

window.onload = () => { isLoggedIn(); fetchProfile(); };
