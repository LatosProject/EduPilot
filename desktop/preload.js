// preload.js

const { contextBridge, ipcRenderer } = require('electron');

// 安全暴露接口给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
    send: (channel, data) => ipcRenderer.send(channel, data),
    on: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args))
});
