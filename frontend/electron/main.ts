import dotenv from "dotenv";
import {app, BrowserWindow, ipcMain, dialog, webUtils} from "electron";
import path from "path";
import {getToken, saveToken, deleteToken} from "./authStore"
import fs from "fs/promises";
import mime from "mime-types";
import type { IpcMainInvokeEvent } from 'electron';

dotenv.config();

// need to register content types for those already exists in the mime library
mime.types["py"] = "text/x-python"

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const startUrl = path.join(__dirname, "../app/index.html");
const appTitle = "CodeCriticAI";
let mainWindow: BrowserWindow | null;

function createWindow() {
    
    const preloadPath = path.join(__dirname, 'preload.js');

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: preloadPath,
            contextIsolation: true,
            nodeIntegration: false,
        }
    });

    mainWindow.setTitle(appTitle);

    if (isDev) {
        const reactAppUrl = process.env.REACT_APP_URL || "http://localhost:5173";
        mainWindow.loadURL(reactAppUrl);
        // mainWindow.webContents.openDevTools();
    } else {    
        mainWindow.loadFile(startUrl);
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.on('ready', createWindow);

app.on("window-all-closed", () => {
    app.quit();
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

// secure IPC handlers
ipcMain.handle("auth:get-token", getToken);


ipcMain.handle("auth:save-token", (_: IpcMainInvokeEvent, token: string) => saveToken(token));


ipcMain.handle("auth:delete-token", deleteToken)


ipcMain.handle('dialog:select-path', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile', 'openDirectory'],
      title: 'Select a file or folder',
    });
  
    if (result.canceled || result.filePaths.length === 0) return null;
    return result.filePaths[0];
  });

ipcMain.handle('readFileAsBlob', async (event, filepath) => {
    const fileBuffer = await fs.readFile(filepath);
    const ext = path.extname(filepath).toLowerCase()
    const fileData =  {
        data: Array.from(fileBuffer),
        type: mime.lookup(ext)
    }
    return fileData
});


ipcMain.handle('getFilePathFromBlob', async (event, fileBlob) => {
    const filePath = webUtils.getPathForFile(fileBlob)
    return filePath
});
