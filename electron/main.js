const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
let pyProc = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 1000,
    webPreferences: { nodeIntegration: false, contextIsolation: true }
  });
  win.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
}

app.whenReady().then(() => {
  pyProc = spawn('python', ['../backend/api/agi_api.py'], { stdio: 'inherit' });
  createWindow();
  app.on('before-quit', () => { if (pyProc) pyProc.kill(); });
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
