const { app, BrowserWindow, Menu, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

class LyraElectronApp {
    constructor() {
        this.mainWindow = null;
        this.isDev = process.argv.includes('--debug');
        
        // Initialize app
        this.init();
    }
    
    init() {
        // App event handlers
        app.whenReady().then(() => {
            this.createMainWindow();
            this.setupMenu();
            
            app.on('activate', () => {
                if (BrowserWindow.getAllWindows().length === 0) {
                    this.createMainWindow();
                }
            });
        });
        
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });
        
        // IPC handlers
        this.setupIPC();
    }
    
    createMainWindow() {
        // Main window configuration
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1200,
            minHeight: 800,
            title: 'LYRA 3.0 - AI Assistant',
            icon: path.join(__dirname, 'assets', 'icon.png'),
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                enableRemoteModule: true,
                webSecurity: false // Required for local file access
            },
            frame: true,
            titleBarStyle: 'default',
            backgroundColor: '#0a0a0a',
            show: false // Don't show until ready
        });
        
        // Load the GUI
        const indexPath = path.join(__dirname, 'gui', 'index.html');
        this.mainWindow.loadFile(indexPath);
        
        // Show window when ready
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            
            if (this.isDev) {
                this.mainWindow.webContents.openDevTools();
            }
            
            // Welcome message
            console.log('🤖 LYRA 3.0 Electron Frontend Started');
            console.log('🚀 Connecting to backend on port 5000...');
        });
        
        // Handle window closed
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });
        
        // Handle external links
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
        
        // Handle page errors
        this.mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
            console.error('Failed to load page:', errorDescription);
        });
    }
    
    setupMenu() {
        const template = [
            {
                label: 'LYRA 3.0',
                submenu: [
                    {
                        label: 'About LYRA 3.0',
                        click: () => {
                            this.showAboutDialog();
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Preferences',
                        accelerator: 'CmdOrCtrl+,',
                        click: () => {
                            this.mainWindow.webContents.executeJavaScript(
                                "document.querySelector('[data-tab=\"settings\"]').click();"
                            );
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Quit',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => {
                            app.quit();
                        }
                    }
                ]
            },
            {
                label: 'View',
                submenu: [
                    {
                        label: 'Home',
                        accelerator: 'CmdOrCtrl+1',
                        click: () => {
                            this.switchTab('home');
                        }
                    },
                    {
                        label: 'System Control',
                        accelerator: 'CmdOrCtrl+2',
                        click: () => {
                            this.switchTab('system');
                        }
                    },
                    {
                        label: 'Data & Config',
                        accelerator: 'CmdOrCtrl+3',
                        click: () => {
                            this.switchTab('upload');
                        }
                    },
                    {
                        label: 'Logs & Diagnostics',
                        accelerator: 'CmdOrCtrl+4',
                        click: () => {
                            this.switchTab('logs');
                        }
                    },
                    {
                        label: 'Settings',
                        accelerator: 'CmdOrCtrl+5',
                        click: () => {
                            this.switchTab('settings');
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Reload',
                        accelerator: 'CmdOrCtrl+R',
                        click: () => {
                            this.mainWindow.reload();
                        }
                    },
                    {
                        label: 'Force Reload',
                        accelerator: 'CmdOrCtrl+Shift+R',
                        click: () => {
                            this.mainWindow.webContents.reloadIgnoringCache();
                        }
                    },
                    {
                        label: 'Toggle Developer Tools',
                        accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
                        click: () => {
                            this.mainWindow.webContents.toggleDevTools();
                        }
                    }
                ]
            },
            {
                label: 'Control',
                submenu: [
                    {
                        label: 'Emergency Stop',
                        accelerator: 'CmdOrCtrl+Shift+E',
                        click: () => {
                            this.emergencyStop();
                        }
                    },
                    {
                        label: 'System Status',
                        accelerator: 'CmdOrCtrl+I',
                        click: () => {
                            this.getSystemStatus();
                        }
                    }
                ]
            },
            {
                label: 'Help',
                submenu: [
                    {
                        label: 'Documentation',
                        click: () => {
                            shell.openExternal('https://github.com/lyra-ai/lyra3.0/wiki');
                        }
                    },
                    {
                        label: 'Report Issue',
                        click: () => {
                            shell.openExternal('https://github.com/lyra-ai/lyra3.0/issues');
                        }
                    }
                ]
            }
        ];
        
        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }
    
    setupIPC() {
        // Handle backend communication
        ipcMain.handle('send-command', async (event, command) => {
            console.log('Command from renderer:', command);
            return { status: 'received', command };
        });
        
        // Handle file operations
        ipcMain.handle('save-file', async (event, data) => {
            // Implement file saving logic
            return { status: 'saved' };
        });
    }
    
    switchTab(tabName) {
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(
                `document.querySelector('[data-tab="${tabName}"]').click();`
            );
        }
    }
    
    emergencyStop() {
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                // Send emergency stop command
                if (window.socket) {
                    window.socket.emit('command', { type: 'emergency_stop' });
                }
                alert('🚨 EMERGENCY STOP ACTIVATED');
            `);
        }
    }
    
    getSystemStatus() {
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                // Request system status
                if (window.socket) {
                    window.socket.emit('command', { type: 'system_status' });
                }
            `);
        }
    }
    
    showAboutDialog() {
        const { dialog } = require('electron');
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'About LYRA 3.0',
            message: 'LYRA 3.0 - Logical Yielding Response Algorithm',
            detail: 'Advanced AI Assistant & Control Dashboard\n\nVersion: 3.0.0\nBuilt with Electron\n\n🤖 JARVIS-inspired interface\n🚗 TRINETRA Ground Bot Control\n🚁 KRAIT-3 UAV Control\n\nDeveloped for autonomous robotics applications.',
            buttons: ['OK'],
            icon: path.join(__dirname, 'assets', 'icon.png')
        });
    }
}

// Initialize the Electron app
new LyraElectronApp();

// Handle app startup errors
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
