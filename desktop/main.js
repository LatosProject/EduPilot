const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'), // 预加载脚本，提升安全性
        }
    });
    win.webContents.openDevTools();

    if (process.env.NODE_ENV === 'development') {
        win.loadURL('http://localhost:5173');  // 开发时加载Vue dev server
    }
    else {
        win.loadFile(path.join(__dirname, '../frontend/dist/index.html')); // 生产环境加载Vue构建文件
    }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
