import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close'),
  isMaximized: () => ipcRenderer.invoke('window-is-maximized'),
  openImageDialog: () => ipcRenderer.invoke('open-image-dialog'),
  onMessage: (callback: (msg: string) => void) =>
    ipcRenderer.on('main-process-message', (_e, msg) => callback(msg)),
})
