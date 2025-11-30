const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const DJANGO_PORT = process.env.DJANGO_PORT || '8765';

let djangoProcess;

function startDjango() {
  const python = process.env.DJANGO_PYTHON || process.env.PYTHON || 'python3';
  const env = { ...process.env, DJANGO_SETTINGS_MODULE: 'config.settings' };

  djangoProcess = spawn(python, ['-m', 'desktop_admin.admin_server', '--port', DJANGO_PORT], {
    cwd: ROOT,
    env,
  });

  djangoProcess.stdout.on('data', (data) => {
    console.log(`[django] ${data}`.trim());
  });

  djangoProcess.stderr.on('data', (data) => {
    console.error(`[django error] ${data}`.trim());
  });

  djangoProcess.on('exit', (code) => {
    if (!app.isQuitting) {
      dialog.showErrorBox('Django stopped', `The Django server exited with code ${code ?? 'unknown'}.`);
      app.quit();
    }
  });
}

async function waitForServer(retries = 20, delay = 500) {
  const url = `http://127.0.0.1:${DJANGO_PORT}/admin/login/`;
  for (let attempt = 0; attempt < retries; attempt += 1) {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      if (response.ok || response.status === 302) {
        return;
      }
    } catch (error) {
      console.log(`Waiting for Django to start (${attempt + 1}/${retries})...`);
    }
    await new Promise((resolve) => setTimeout(resolve, delay));
  }
  throw new Error('Timed out waiting for Django server to start.');
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 900,
    webPreferences: {
      contextIsolation: true,
    },
  });

  win.loadURL(`http://127.0.0.1:${DJANGO_PORT}/admin/`);
}

app.whenReady().then(async () => {
  startDjango();
  try {
    await waitForServer();
    createWindow();
  } catch (error) {
    dialog.showErrorBox('Startup error', error.message);
    app.quit();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('before-quit', () => {
  app.isQuitting = true;
  if (djangoProcess) {
    djangoProcess.kill();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
