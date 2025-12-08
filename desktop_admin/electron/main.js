const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const DJANGO_PORT = process.env.DJANGO_PORT || '8765';
const OUTPUT_TAIL_LIMIT = 80;
let djangoProcess;
let logDirHint;
let logFileHint;
const recentStdout = [];
const recentStderr = [];

function resolvePaths() {
  const home = app.getPath('home');

  if (process.platform === 'win32') {
    const base =
      process.env.LOCALAPPDATA ||
      path.join(process.env.USERPROFILE || home, 'AppData', 'Local');
    const dataDir = path.join(base, 'GCI', 'GCI-Admin');
    return {
      dataDir,
      logDir: path.join(dataDir, 'Logs'),
    };
  }

  if (process.platform === 'darwin') {
    const dataDir = path.join(
      home,
      'Library',
      'Application Support',
      'GCI-Admin',
    );
    return {
      dataDir,
      logDir: path.join(home, 'Library', 'Logs', 'GCI-Admin'),
    };
  }

  const dataDir = path.join(home, '.local', 'share', 'GCI-Admin');
  return {
    dataDir,
    logDir: path.join(home, '.cache', 'GCI-Admin', 'log'),
  };
}

function recordOutput(buffer, target) {
  const lines = buffer
    .toString()
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  lines.forEach((line) => {
    target.push(line);
    if (target.length > OUTPUT_TAIL_LIMIT) {
      target.shift();
    }
  });
}

function copyDirectory(src, dest) {
  if (fs.existsSync(dest)) {
    return;
  }
  fs.cpSync(src, dest, { recursive: true });
}

function patchPyVenvCfg(pythonDir) {
  const cfgPath = path.join(pythonDir, 'pyvenv.cfg');
  if (!fs.existsSync(cfgPath)) {
    console.warn("No pyvenv.cfg found to patch:", cfgPath);
    return;
  }

  const home = pythonDir.replace(/\\/g, '\\\\');
  const exe = path.join(pythonDir, 'Scripts', 'python.exe').replace(/\\/g, '\\\\');

  const content = [
    `home = ${home}`,
    `executable = ${exe}`,
    `command = ${exe} -m venv "${pythonDir}"`
  ].join('\n');

  fs.writeFileSync(cfgPath, content, 'utf8');
  console.log("Patched pyvenv.cfg:", cfgPath);
}

function startDjango() {
  const { dataDir, logDir } = resolvePaths();
  logDirHint = logDir;
  logFileHint = logDir ? path.join(logDir, 'desktop_admin.log') : undefined;

  const env = {
    ...process.env,
    DJANGO_SETTINGS_MODULE: 'config.settings',
    GCI_DATA_DIR: dataDir,
    DJANGO_LOG_DIR: logDir,
  };

  if (app.isPackaged) {
    // -------- PRODUCTION: bundled Python & backend inside resources --------
    const resourcesPath = process.resourcesPath;
    const backendPath = path.join(resourcesPath, 'gci-backend');
    const bundledPythonDir = path.join(resourcesPath, 'python');
    const portablePythonDir = path.join(dataDir, 'python');

    try {
      copyDirectory(bundledPythonDir, portablePythonDir);
      patchPyVenvCfg(portablePythonDir);
    } catch (error) {
      dialog.showErrorBox(
        'Startup error',
        `Failed to prepare bundled Python runtime.\n${error.message}`,
      );
      app.quit();
      return;
    }

    // This is where the venv is copied by extraResources (python-win -> python)
    const pythonExe = path.join(portablePythonDir, 'Scripts', 'python.exe');
    const adminServer = path.join(backendPath, 'desktop_admin', 'admin_server.py');

    console.log('[main] resourcesPath =', resourcesPath);
    console.log('[main] pythonExe =', pythonExe);
    console.log('[main] adminServer =', adminServer);

    // Safety checks so we fail with a clear error instead of ENOENT
    if (!fs.existsSync(pythonExe)) {
      dialog.showErrorBox(
        'Startup error',
        `Bundled Python runtime not found.\nExpected at:\n${pythonExe}`,
      );
      app.quit();
      return;
    }

    if (!fs.existsSync(adminServer)) {
      dialog.showErrorBox(
        'Startup error',
        `Django admin_server.py not found.\nExpected at:\n${adminServer}`,
      );
      app.quit();
      return;
    }

    djangoProcess = spawn(
      pythonExe,
      [adminServer, '--port', DJANGO_PORT],
      {
        cwd: backendPath,
        env,
      },
    );
  } else {
    // -------- DEVELOPMENT: use your local Python & source tree --------
    const ROOT = path.resolve(__dirname, '..', '..');
    const python =
      process.env.DJANGO_PYTHON ||
      process.env.PYTHON ||
      (process.platform === 'win32' ? 'python' : 'python3');

    console.log('[main] DEV ROOT =', ROOT);
    console.log('[main] DEV python =', python);

    djangoProcess = spawn(
      python,
      ['-m', 'desktop_admin.admin_server', '--port', DJANGO_PORT],
      {
        cwd: ROOT,
        env,
      },
    );
  }

  djangoProcess.stdout.on('data', (data) => {
    recordOutput(data, recentStdout);
    console.log(`[django] ${data}`.trim());
  });

  djangoProcess.stderr.on('data', (data) => {
    recordOutput(data, recentStderr);
    console.error(`[django error] ${data}`.trim());
  });

  djangoProcess.on('error', (err) => {
    const logHint = logFileHint ? `\nLog file: ${logFileHint}` : '';
    dialog.showErrorBox(
      'Django failed to start',
      `Failed to launch Python: ${err.message}.${logHint}`,
    );
    app.quit();
  });

  djangoProcess.on('exit', (code) => {
    if (!app.isQuitting) {
      const recentOutput =
        recentStderr.slice(-12).join('\n') ||
        recentStdout.slice(-12).join('\n');
      const logHint = logFileHint ? `\nLog file: ${logFileHint}` : '';
      const tailHint = recentOutput
        ? `\n\nRecent output:\n${recentOutput}`
        : '';
      dialog.showErrorBox(
        'Django stopped',
        `The Django server exited with code ${code ?? 'unknown'}.${logHint}${tailHint}`,
      );
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
