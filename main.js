const { app, BrowserWindow } = require('electron');

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800, height: 600, webPreferences: { nodeIntegration: true, devTools: true },
  });
  win.loadFile('app/index.html');
};

app.on('ready', createWindow);
