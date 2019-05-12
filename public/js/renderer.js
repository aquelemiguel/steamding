const io = require('socket.io-client');

// Update status message.
const updateStatus = (status) => { document.getElementById('status-message').innerHTML = status; };

// Socket handling.
const initSocket = (steamID) => {
  const socket = io();
  socket.on('ACHIEVEMENT_UNLOCKED', () => new Audio(`sfx/${document.querySelector('input[name="sfx"]:checked').value}.mp3`).play());
  socket.on('REGISTERED', updateStatus('Registered socket!'));
  socket.emit('REGISTER', steamID);
};

// Steam account conformities check.
const isPrivate = (profile) => {
  if (profile.communityvisibilitystate === 1) {
    console.log('Profile is private!');
  }
};

document.getElementById('preview').addEventListener(('click'), () => {
  const snd = new Audio(`sfx/${document.querySelector('input[name="sfx"]:checked').value}.mp3`);
  snd.play();
});

const startTracking = () => {
  const xtr = new XMLHttpRequest();
  xtr.open('POST', '/track', true);
  xtr.send();
};

document.getElementById('track-achievements').addEventListener(('click'), () => {
  startTracking();
});

const isLoggedIn = () => {
  const xtr = new XMLHttpRequest();
  xtr.onload = () => {
    // If the user logged in with Steam, then register it on the socket.
    if (JSON.parse(xtr.response)) {
      initSocket(xtr.response); document.getElementById('login-btn').style.display = 'none';
    } else document.getElementById('logout-btn').style.display = 'none';
  };
  xtr.open('GET', '/auth/islogged', true);
  xtr.send();
};


const fetchProfile = () => {
  const xtr = new XMLHttpRequest();
  xtr.onload = () => {
    if (xtr.response) {
      document.getElementById('persona-name').innerHTML = xtr.response.personaname;
      document.getElementById('profile-avatar').src = xtr.response.avatarmedium;
    }
  };
  xtr.responseType = 'json';
  xtr.open('GET', '/fetchprofile', true);
  xtr.send();
};

window.onload = () => { isLoggedIn(); fetchProfile(); };
