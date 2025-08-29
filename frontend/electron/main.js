
/**
 * Electron Main Process
 * Mac-native desktop application for CPAS Master Agent
 */

const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;

function createWindow() {
  // Create the browser window with Mac-native styling
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    titleBarStyle: 'hiddenInset', // Mac-style title bar
    vibrancy: 'under-window', // Mac vibrancy effect
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false, // Don't show until ready
    icon: path.join(__dirname, '../assets/icon.png')
  });

  // Load the app
  const startUrl = isDev 
    ? 'http://localhost:3000/master' 
    : `file://${path.join(__dirname, '../out/master.html')}`;
  
  mainWindow.loadURL(startUrl);

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on the window
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// Mac-specific menu
function createMenu() {
  const template = [
    {
      label: 'CPAS Master Agent',
      submenu: [
        {
          label: 'About CPAS Master Agent',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About CPAS Master Agent',
              message: 'CPAS Master Agent',
              detail: 'Comprehensive Personal AI System with Master Agent Greta\nVersion 1.0.0\n\nBuilt with precision and German engineering excellence.'
            });
          }
        },
        { type: 'separator' },
        {
          label: 'Preferences...',
          accelerator: 'Cmd+,',
          click: () => {
            // Send preferences event to renderer
            mainWindow.webContents.send('open-preferences');
          }
        },
        { type: 'separator' },
        {
          label: 'Hide CPAS Master Agent',
          accelerator: 'Cmd+H',
          role: 'hide'
        },
        {
          label: 'Hide Others',
          accelerator: 'Cmd+Alt+H',
          role: 'hideothers'
        },
        {
          label: 'Show All',
          role: 'unhide'
        },
        { type: 'separator' },
        {
          label: 'Quit CPAS Master Agent',
          accelerator: 'Cmd+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'File',
      submenu: [
        {
          label: 'New Investigation',
          accelerator: 'Cmd+N',
          click: () => {
            mainWindow.webContents.send('new-investigation');
          }
        },
        {
          label: 'New Task',
          accelerator: 'Cmd+T',
          click: () => {
            mainWindow.webContents.send('new-task');
          }
        },
        { type: 'separator' },
        {
          label: 'Export Results',
          accelerator: 'Cmd+E',
          click: () => {
            mainWindow.webContents.send('export-results');
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', accelerator: 'Cmd+Z', role: 'undo' },
        { label: 'Redo', accelerator: 'Shift+Cmd+Z', role: 'redo' },
        { type: 'separator' },
        { label: 'Cut', accelerator: 'Cmd+X', role: 'cut' },
        { label: 'Copy', accelerator: 'Cmd+C', role: 'copy' },
        { label: 'Paste', accelerator: 'Cmd+V', role: 'paste' },
        { label: 'Select All', accelerator: 'Cmd+A', role: 'selectall' }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Overview',
          accelerator: 'Cmd+1',
          click: () => {
            mainWindow.webContents.send('switch-view', 'overview');
          }
        },
        {
          label: 'Agents',
          accelerator: 'Cmd+2',
          click: () => {
            mainWindow.webContents.send('switch-view', 'agents');
          }
        },
        {
          label: 'OSINT',
          accelerator: 'Cmd+3',
          click: () => {
            mainWindow.webContents.send('switch-view', 'osint');
          }
        },
        {
          label: 'Tasks',
          accelerator: 'Cmd+4',
          click: () => {
            mainWindow.webContents.send('switch-view', 'tasks');
          }
        },
        { type: 'separator' },
        {
          label: 'Toggle Voice Interface',
          accelerator: 'Cmd+Shift+V',
          click: () => {
            mainWindow.webContents.send('toggle-voice');
          }
        },
        { type: 'separator' },
        { label: 'Reload', accelerator: 'Cmd+R', role: 'reload' },
        { label: 'Force Reload', accelerator: 'Cmd+Shift+R', role: 'forceReload' },
        { label: 'Toggle Developer Tools', accelerator: 'F12', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: 'Actual Size', accelerator: 'Cmd+0', role: 'resetZoom' },
        { label: 'Zoom In', accelerator: 'Cmd+Plus', role: 'zoomIn' },
        { label: 'Zoom Out', accelerator: 'Cmd+-', role: 'zoomOut' },
        { type: 'separator' },
        { label: 'Toggle Fullscreen', accelerator: 'Ctrl+Cmd+F', role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { label: 'Minimize', accelerator: 'Cmd+M', role: 'minimize' },
        { label: 'Close', accelerator: 'Cmd+W', role: 'close' },
        { type: 'separator' },
        { label: 'Bring All to Front', role: 'front' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'CPAS Documentation',
          click: () => {
            shell.openExternal('https://github.com/cpas-ai/documentation');
          }
        },
        {
          label: 'OSINT Guidelines',
          click: () => {
            shell.openExternal('https://github.com/cpas-ai/osint-guidelines');
          }
        },
        { type: 'separator' },
        {
          label: 'Report Issue',
          click: () => {
            shell.openExternal('https://github.com/cpas-ai/issues');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(() => {
  createWindow();
  createMenu();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('show-save-dialog', async () => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [
      { name: 'JSON Files', extensions: ['json'] },
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

ipcMain.handle('show-open-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

// Handle app updates (if using auto-updater)
if (!isDev) {
  const { autoUpdater } = require('electron-updater');
  
  autoUpdater.checkForUpdatesAndNotify();
  
  autoUpdater.on('update-available', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: 'A new version of CPAS Master Agent is available. It will be downloaded in the background.',
      buttons: ['OK']
    });
  });
}
