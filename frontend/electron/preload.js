
/**
 * Electron Preload Script
 * Secure bridge between main and renderer processes
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // File dialogs
  showSaveDialog: () => ipcRenderer.invoke('show-save-dialog'),
  showOpenDialog: () => ipcRenderer.invoke('show-open-dialog'),
  
  // Menu events
  onMenuAction: (callback) => {
    ipcRenderer.on('new-investigation', callback);
    ipcRenderer.on('new-task', callback);
    ipcRenderer.on('export-results', callback);
    ipcRenderer.on('switch-view', callback);
    ipcRenderer.on('toggle-voice', callback);
    ipcRenderer.on('open-preferences', callback);
  },
  
  // Remove listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// System information
contextBridge.exposeInMainWorld('systemAPI', {
  platform: process.platform,
  arch: process.arch,
  versions: process.versions
});
