const io = require('socket.io-client');

// Socket handling.
const initSocket = (steamID) => {
  const socket = io();
  socket.on('connect', () => socket.emit('ADD_CLIENT', steamID));
  socket.on('ACHIEVEMENT_UNLOCKED', () => new Audio(`sfx/${document.querySelector('input[name="sfx"]:checked').value}.mp3`).play());
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

if (document.getElementById('track-achivements')) {
  document.getElementById('track-achievements').addEventListener(('click'), () => {
    startTracking();
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
    }
  };
  xtr.responseType = 'json';
  xtr.open('GET', '/fetchprofile', true);
  xtr.send();
};

window.onload = () => { isLoggedIn(); fetchProfile(); };
