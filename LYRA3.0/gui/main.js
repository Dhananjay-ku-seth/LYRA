document.addEventListener('DOMContentLoaded', (event) => {
    const socket = io(); // Automatically use the current domain and port

    // Status update handlers
    socket.on('status', (data) => {
        console.log('Status:', data);
        updateConnectionStatus(data.message);
    });

    socket.on('response', (data) => {
        console.log('Response:', data);
        handleResponse(data);
    });

    // Test WebSocket connection
    socket.emit('test', { msg: 'Ping from main.js' });
    socket.on('test_reply', (data) => {
        console.log('WebSocket test successful:', data);
    });

    // UI element references
    const voiceStartButton = document.getElementById('voice-start');
    const voiceStopButton = document.getElementById('voice-stop');
    const commandTextInput = document.getElementById('command-text');
    const sendCommandButton = document.getElementById('send-command');
    const modeButtons = document.querySelectorAll('.mode-btn');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const moveButtons = document.querySelectorAll('.move-btn');
    const controlButtons = document.querySelectorAll('.control-btn');

    // Tab navigation
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    function switchTab(tabName) {
        // Remove active class from all tabs and contents
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to selected tab and content
        const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
        const activeContent = document.getElementById(`${tabName}-tab`);
        
        if (activeButton && activeContent) {
            activeButton.classList.add('active');
            activeContent.classList.add('active');
        }
    }

    // Voice interface is always listening - no buttons needed
    // Voice status will be updated automatically

    // Send text command
    sendCommandButton.addEventListener('click', () => {
        sendTextCommand();
    });

    // Enter key for command input
    commandTextInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendTextCommand();
        }
    });

    function sendTextCommand() {
        const text = commandTextInput.value.trim();
        if (text) {
            socket.emit('command', { type: 'text_command', data: { text: text } });
            commandTextInput.value = '';
            addLogEntry('USER', text);
        }
    }

    // Mode button handlers
    modeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const mode = button.getAttribute('data-mode');
            switchMode(mode);
            socket.emit('command', { type: 'system_status', data: { mode: mode } });
        });
    });

    // TRINETRA movement controls
    moveButtons.forEach(button => {
        button.addEventListener('click', () => {
            const direction = button.getAttribute('data-direction');
            socket.emit('command', {
                type: 'trinetra_command',
                data: { action: 'move', direction: direction }
            });
            addLogEntry('TRINETRA', `Moving ${direction}`);
        });
    });

    // Control button handlers
    controlButtons.forEach(button => {
        button.addEventListener('click', () => {
            const buttonText = button.textContent.trim();
            let commandType = 'system_status';
            let action = buttonText.toLowerCase();
            
            if (button.closest('.device-panel')) {
                const devicePanel = button.closest('.device-panel');
                if (devicePanel.querySelector('h3').textContent.includes('TRINETRA')) {
                    commandType = 'trinetra_command';
                } else if (devicePanel.querySelector('h3').textContent.includes('KRAIT-3')) {
                    commandType = 'krait3_command';
                }
            }
            
            socket.emit('command', {
                type: commandType,
                data: { action: action }
            });
            
            addLogEntry('SYSTEM', `${buttonText} command executed`);
        });
    });

    // File upload handlers
    const dataUploadZone = document.getElementById('data-upload');
    const configUploadZone = document.getElementById('config-upload');
    const dataFilesInput = document.getElementById('data-files');
    const configFilesInput = document.getElementById('config-files');

    // Data upload zone
    dataUploadZone.addEventListener('click', () => {
        dataFilesInput.click();
    });

    dataUploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dataUploadZone.style.borderColor = 'var(--accent-blue)';
    });

    dataUploadZone.addEventListener('dragleave', () => {
        dataUploadZone.style.borderColor = 'var(--border-color)';
    });

    dataUploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dataUploadZone.style.borderColor = 'var(--border-color)';
        handleFiles(e.dataTransfer.files, 'data');
    });

    // Config upload zone
    configUploadZone.addEventListener('click', () => {
        configFilesInput.click();
    });

    configUploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        configUploadZone.style.borderColor = 'var(--accent-blue)';
    });

    configUploadZone.addEventListener('dragleave', () => {
        configUploadZone.style.borderColor = 'var(--border-color)';
    });

    configUploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        configUploadZone.style.borderColor = 'var(--border-color)';
        handleFiles(e.dataTransfer.files, 'config');
    });

    // File input handlers
    dataFilesInput.addEventListener('change', (e) => {
        handleFiles(e.target.files, 'data');
    });

    configFilesInput.addEventListener('change', (e) => {
        handleFiles(e.target.files, 'config');
    });

    function handleFiles(files, type) {
        const uploadQueue = document.getElementById('upload-queue');
        
        Array.from(files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'upload-item';
            fileItem.innerHTML = `
                <span>${file.name}</span>
                <span>${(file.size / 1024).toFixed(1)} KB</span>
                <span class="upload-status">Queued</span>
            `;
            uploadQueue.appendChild(fileItem);
        });
        
        addLogEntry('UPLOAD', `${files.length} ${type} files queued`);
    }

    // Diagnostics
    const runDiagnosticsButton = document.getElementById('run-diagnostics');
    const exportLogsButton = document.getElementById('export-logs');

    runDiagnosticsButton?.addEventListener('click', () => {
        socket.emit('command', { type: 'system_status' });
        addLogEntry('DIAGNOSTICS', 'Running full system diagnostics...');
    });

    exportLogsButton?.addEventListener('click', () => {
        exportLogs();
    });

    // Update connection status
    function updateConnectionStatus(status) {
        const connectionStatus = document.getElementById('connection-status');
        const statusSpan = connectionStatus.querySelector('span');
        statusSpan.textContent = status;
        
        if (status.includes('Connected')) {
            connectionStatus.style.borderColor = 'var(--accent-green)';
            connectionStatus.querySelector('i').style.color = 'var(--accent-green)';
        }
    }

    // Handle response from backend
    function handleResponse(data) {
        if (data.type === 'voice_status') {
            updateVoiceStatus(data.data.status);
        } else if (data.type === 'command_result') {
            showCommandResponse(data.data);
        } else if (data.type === 'system_status') {
            updateSystemStatus(data.data);
        } else if (data.type === 'trinetra_response') {
            handleTrinetraResponse(data.data);
        } else if (data.type === 'krait3_response') {
            handleKrait3Response(data.data);
        } else if (data.type === 'error') {
            addLogEntry('ERROR', data.data.message);
        }
    }

    // Update voice recognition status
    function updateVoiceStatus(status) {
        const voiceStatus = document.getElementById('voice-status');
        voiceStatus.textContent = `Voice ${status}`;
        updateVoiceButtonStates(status === 'listening', status === 'stopped');
    }

    function updateVoiceButtonStates(startDisabled, stopDisabled) {
        voiceStartButton.disabled = startDisabled;
        voiceStopButton.disabled = stopDisabled;
    }

    // Show command response
    function showCommandResponse(response) {
        const commandResponse = document.getElementById('command-response');
        commandResponse.textContent = response.message || 'Command processed';
        addLogEntry('LYRA', response.message || 'Command processed');
    }

    // Update system status
    function updateSystemStatus(status) {
        const cpuStatus = document.getElementById('cpu-status').querySelector('span');
        const memoryStatus = document.getElementById('memory-status').querySelector('span');
        const tempStatus = document.getElementById('temp-status').querySelector('span');

        cpuStatus.textContent = `CPU: ${status.cpu_percent || 0}%`;
        memoryStatus.textContent = `RAM: ${status.memory_percent || 0}%`;
        tempStatus.textContent = `TEMP: ${status.temperature || 0}°C`;
    }

    // Handle TRINETRA responses
    function handleTrinetraResponse(response) {
        addLogEntry('TRINETRA', response.message);
        updateDeviceStatus('trinetra', response.status === 'success');
    }

    // Handle KRAIT-3 responses
    function handleKrait3Response(response) {
        addLogEntry('KRAIT-3', response.message);
        updateDeviceStatus('krait3', response.status === 'success');
    }

    // Update device status indicators
    function updateDeviceStatus(device, online) {
        const devicePanels = document.querySelectorAll('.device-panel');
        devicePanels.forEach(panel => {
            const title = panel.querySelector('h3').textContent;
            if ((device === 'trinetra' && title.includes('TRINETRA')) ||
                (device === 'krait3' && title.includes('KRAIT-3'))) {
                const statusDot = panel.querySelector('.status-dot');
                const statusText = panel.querySelector('.device-status span:last-child');
                
                if (online) {
                    statusDot.classList.remove('offline');
                    statusDot.classList.add('online');
                    statusText.textContent = 'Status: Online';
                } else {
                    statusDot.classList.remove('online');
                    statusDot.classList.add('offline');
                    statusText.textContent = 'Status: Offline';
                }
            }
        });
    }

    // Switch operation mode
    function switchMode(mode) {
        const modeDisplay = document.getElementById('current-mode');
        const modeIcon = modeDisplay.querySelector('i');
        const modeText = modeDisplay.querySelector('span');
        
        const modeConfigs = {
            home: { icon: 'fas fa-home', text: 'Home Mode', color: 'var(--accent-green)' },
            defense: { icon: 'fas fa-shield-alt', text: 'Defense Mode', color: 'var(--accent-red)' },
            night: { icon: 'fas fa-moon', text: 'Night Mode', color: 'var(--accent-blue)' },
            manual: { icon: 'fas fa-hand-paper', text: 'Manual Mode', color: 'var(--accent-orange)' }
        };
        
        const config = modeConfigs[mode];
        if (config) {
            modeIcon.className = config.icon;
            modeText.textContent = config.text;
            modeDisplay.style.borderColor = config.color;
            modeDisplay.style.color = config.color;
            addLogEntry('MODE', `Switched to ${config.text}`);
        }
    }

    // Add log entry
    function addLogEntry(level, message) {
        const logsContainer = document.getElementById('logs-container');
        const timestamp = new Date().toLocaleString();
        
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="level ${level.toLowerCase()}">${level}</span>
            <span class="message">${message}</span>
        `;
        
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    // Export logs function
    function exportLogs() {
        const logs = document.querySelectorAll('.log-entry');
        let logText = 'LYRA 3.0 System Logs\n' + '='.repeat(50) + '\n\n';
        
        logs.forEach(log => {
            const timestamp = log.querySelector('.timestamp').textContent;
            const level = log.querySelector('.level').textContent;
            const message = log.querySelector('.message').textContent;
            logText += `${timestamp} ${level} ${message}\n`;
        });
        
        const blob = new Blob([logText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lyra_logs_${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        addLogEntry('SYSTEM', 'Logs exported successfully');
    }

    // Request system status on load
    setTimeout(() => {
        socket.emit('command', { type: 'system_status' });
        addLogEntry('SYSTEM', 'LYRA 3.0 system initialized');
    }, 1000);

    // Periodic status updates
    setInterval(() => {
        socket.emit('command', { type: 'system_status' });
    }, 30000); // Every 30 seconds
});
