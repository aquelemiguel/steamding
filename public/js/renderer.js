document.getElementById('preview').addEventListener(('click'), () => {
  const snd = new Audio(`sfx/${document.querySelector('input[name="sfx"]:checked').value}.mp3`);
  snd.play();
});

const updateLoginStatus = () => {
  const xtr = new XMLHttpRequest();

  xtr.onload = () => {
    if (xtr.response) {
      document.getElementById('status-message-user').innerHTML = xtr.response;
      document.getElementById('login-btn').style.display = 'none';
    } else {
      document.getElementById('logout-btn').style.display = 'none';
    }
  };

  xtr.open('GET', '/auth/getid', true);
  xtr.send();
};

window.onload = () => { updateLoginStatus(); };
