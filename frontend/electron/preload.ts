import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  getToken: () => ipcRenderer.invoke("auth:get-token"),
  saveToken: (token:string) => ipcRenderer.invoke("auth:save-token", token),
  deleteToken: () => ipcRenderer.invoke("auth:delete-token"),
  selectPath: () => ipcRenderer.invoke('dialog:select-path'),
  readFileStream: (filepath:string) => ipcRenderer.invoke("readFileAsBlob", filepath),
});
