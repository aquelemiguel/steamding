const publicVapidKey = 'BAHkvgY-9jD66Mwr-u4S-aGvRQ_oIuOq0cXQbAarTptQkdOZeEQOlEq14PHMCQiIG_z84_a3uZ2Pkl9xzWhf0Uo';

const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; i += 1) outputArray[i] = rawData.charCodeAt(i);
  return outputArray;
};

async function run() {
  if ('serviceWorker' in navigator) {
    const register = await navigator.serviceWorker.register('js/service-worker.js');
    const subscription = await register.pushManager.subscribe({
      userVisibleOnly: true, applicationServerKey: urlBase64ToUint8Array(publicVapidKey),
    });
    console.log('Registered!');

    await fetch('/subscribe', {
      method: 'POST', body: JSON.stringify(subscription), headers: { 'Content-Type': 'application/json' },
    });
  } else console.log('Service workers are not supported in this browser');
}

document.getElementById('preview').addEventListener(('click'), () => {
  const snd = new Audio(`sfx/${document.querySelector('input[name="sfx"]:checked').value}.mp3`);
  snd.play();
});

document.getElementById('track-achievements').addEventListener(('click'), () => {
  run().catch(error => console.log(error));
});

const isLoggedIn = () => {
  const xtr = new XMLHttpRequest();
  xtr.onload = () => {
    if (xtr.response) document.getElementById('login-btn').style.display = 'none';
    else document.getElementById('logout-btn').style.display = 'none';
  };
  xtr.responseType = 'json';
  xtr.open('GET', '/auth/islogged', true);
  xtr.send();
};

const startTracking = () => {
  const xtr = new XMLHttpRequest();
  xtr.open('POST', '/track', true);
  xtr.send();
};

const fetchProfile = () => {
  const xtr = new XMLHttpRequest();
  xtr.onload = () => {
    if (xtr.response) {
      startTracking();
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
