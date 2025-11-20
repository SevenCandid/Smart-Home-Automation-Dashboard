/**
 * Smart Home Automation Dashboard
 * JavaScript for device management and UI updates
 * Ready for IoT integration via REST APIs
 */

// Device configuration with Font Awesome icons (fallback to SVG)
const deviceConfig = {
    1: { name: 'Light', type: 'light', iconType: 'fontawesome', svgPath: '/static/icons/lightbulb.svg', fontAwesomeIcon: 'fa-solid fa-lightbulb', cardClass: 'light' },
    2: { name: 'Fan', type: 'fan', iconType: 'fontawesome', svgPath: '/static/icons/fan.svg', fontAwesomeIcon: 'fa-solid fa-fan', cardClass: 'fan' },
    3: { name: 'Temperature', type: 'sensor', iconType: 'fontawesome', svgPath: '/static/icons/thermometer.svg', fontAwesomeIcon: 'fa-solid fa-thermometer-half', cardClass: 'temperature' },
    4: { name: 'Air Conditioner', type: 'ac', iconType: 'fontawesome', svgPath: '/static/icons/ac.svg', fontAwesomeIcon: 'fa-solid fa-snowflake', cardClass: 'ac' },
    5: { name: 'Smart Lock', type: 'lock', iconType: 'fontawesome', svgPath: '/static/icons/lock.svg', fontAwesomeIcon: 'fa-solid fa-lock', cardClass: 'lock' },
    6: { name: 'Smart Blinds', type: 'blinds', iconType: 'fontawesome', svgPath: '/static/icons/blinds.svg', fontAwesomeIcon: 'fa-solid fa-window-maximize', cardClass: 'blinds' },
    7: { name: 'Smart Plug', type: 'plug', iconType: 'fontawesome', svgPath: '/static/icons/plug.svg', fontAwesomeIcon: 'fa-solid fa-plug', cardClass: 'plug' },
    8: { name: 'Security Camera', type: 'camera', iconType: 'fontawesome', svgPath: '/static/icons/camera.svg', fontAwesomeIcon: 'fa-solid fa-video', cardClass: 'camera' },
    9: { name: 'Smart Speaker', type: 'speaker', iconType: 'fontawesome', svgPath: '/static/icons/speaker.svg', fontAwesomeIcon: 'fa-solid fa-volume-high', cardClass: 'speaker' },
    10: { name: 'Garage Door', type: 'garage', iconType: 'fontawesome', svgPath: '/static/icons/garage.svg', fontAwesomeIcon: 'fa-solid fa-warehouse', cardClass: 'garage' },
    11: { name: 'Smart Thermostat', type: 'thermostat', iconType: 'fontawesome', svgPath: '/static/icons/thermostat.svg', fontAwesomeIcon: 'fa-solid fa-temperature-half', cardClass: 'thermostat' },
    12: { name: 'Smart Vacuum', type: 'vacuum', iconType: 'fontawesome', svgPath: '/static/icons/vacuum.svg', fontAwesomeIcon: 'fa-solid fa-robot', cardClass: 'vacuum' },
    13: { name: 'Smart Doorbell', type: 'doorbell', iconType: 'fontawesome', svgPath: '/static/icons/doorbell.svg', fontAwesomeIcon: 'fa-solid fa-bell', cardClass: 'doorbell' },
    14: { name: 'Smart Sprinkler', type: 'sprinkler', iconType: 'fontawesome', svgPath: '/static/icons/sprinkler.svg', fontAwesomeIcon: 'fa-solid fa-droplet', cardClass: 'sprinkler' },
    15: { name: 'Motion Sensor', type: 'motion', iconType: 'fontawesome', svgPath: '/static/icons/motion.svg', fontAwesomeIcon: 'fa-solid fa-radar', cardClass: 'motion' },
    16: { name: 'Smart TV', type: 'tv', iconType: 'fontawesome', svgPath: '/static/icons/tv.svg', fontAwesomeIcon: 'fa-solid fa-tv', cardClass: 'tv' }
};

// Load all devices from API
async function loadDevices() {
    try {
        const response = await fetch('/api/devices');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const devices = await response.json();
        renderDevices(devices);
    } catch (error) {
        console.error('Error loading devices:', error);
    }
}

// Render devices in the UI
function renderDevices(devices) {
    const container = document.getElementById('devices-container');
    if (!container) return;
    
    container.innerHTML = '';

    devices.forEach(device => {
        const config = deviceConfig[device.id];
        if (!config) return;

        const card = createDeviceCard(device, config);
        container.appendChild(card);
    });
}

// Create device card element
function createDeviceCard(device, config) {
    const col = document.createElement('div');
    col.className = 'col-6 col-md-4';

    const isOn = device.state === 'on';
    let stateDisplay = 'OFF';
    let stateClass = 'off';
    
    if (device.type === 'sensor') {
        stateDisplay = `${device.value}°C`;
        stateClass = 'number';
    } else if (device.type === 'fan' && device.value !== null) {
        stateDisplay = `${device.value}%`;
        stateClass = 'number';
    } else if (device.type === 'ac' && device.value !== null) {
        stateDisplay = `${device.value}°C`;
        stateClass = 'number';
    } else if (device.type === 'lock') {
        stateDisplay = (device.state === 'locked' || device.device_mode === 'locked') ? 'LOCKED' : 'UNLOCKED';
        stateClass = (device.state === 'locked' || device.device_mode === 'locked') ? 'on' : 'off';
    } else if (device.type === 'blinds') {
        stateDisplay = device.value !== null ? `${device.value}%` : (device.state === 'open' ? 'OPEN' : 'CLOSED');
        stateClass = device.value !== null ? 'number' : (device.state === 'open' ? 'on' : 'off');
    } else if (device.type === 'plug') {
        stateDisplay = isOn ? `${(device.power_consumption || 0).toFixed(1)}W` : 'OFF';
        stateClass = isOn ? 'number' : 'off';
    } else if (device.type === 'camera') {
        stateDisplay = isOn ? (device.device_mode === 'recording' ? 'RECORDING' : 'ON') : 'OFF';
        stateClass = isOn ? 'on' : 'off';
    } else if (device.type === 'speaker') {
        stateDisplay = isOn ? `${device.value || 50}%` : 'OFF';
        stateClass = isOn ? 'number' : 'off';
    } else if (device.type === 'garage') {
        stateDisplay = (device.state === 'open' || device.device_mode === 'open') ? 'OPEN' : 'CLOSED';
        stateClass = (device.state === 'open' || device.device_mode === 'open') ? 'on' : 'off';
    } else if (device.type === 'thermostat') {
        stateDisplay = device.value !== null ? `${device.value}°C` : (isOn ? 'ON' : 'OFF');
        stateClass = device.value !== null ? 'number' : (isOn ? 'on' : 'off');
    } else if (device.type === 'vacuum') {
        stateDisplay = isOn ? `${device.battery_level || 0}%` : 'OFF';
        stateClass = isOn ? 'number' : 'off';
    } else if (device.type === 'doorbell') {
        stateDisplay = device.device_mode === 'motion' ? 'MOTION' : 'IDLE';
        stateClass = device.device_mode === 'motion' ? 'on' : 'off';
    } else if (device.type === 'sprinkler') {
        stateDisplay = isOn ? (device.device_mode || 'zone1').toUpperCase() : 'OFF';
        stateClass = isOn ? 'on' : 'off';
    } else if (device.type === 'motion') {
        stateDisplay = isOn ? 'DETECTED' : 'NO MOTION';
        stateClass = isOn ? 'on' : 'off';
    } else if (device.type === 'tv') {
        stateDisplay = isOn ? `${device.value || 30}%` : 'OFF';
        stateClass = isOn ? 'number' : 'off';
    } else {
        stateDisplay = isOn ? 'ON' : 'OFF';
        stateClass = isOn ? 'on' : 'off';
    }

    // Add active class for devices when on/active
    const activeTypes = ['light', 'fan', 'sensor', 'ac', 'lock', 'blinds', 'plug', 'camera', 'speaker', 'garage', 'thermostat', 'vacuum', 'doorbell', 'sprinkler', 'motion', 'tv'];
    const isActive = (config.type === 'lock' && (device.state === 'locked' || device.device_mode === 'locked')) ||
                     (config.type === 'garage' && (device.state === 'open' || device.device_mode === 'open')) ||
                     (config.type === 'motion' && device.state === 'on') ||
                     (config.type === 'doorbell' && device.device_mode === 'motion') ||
                     (isOn && activeTypes.includes(config.type));
    const activeClass = isActive ? 'active' : '';
    const effectClass = (config.type === 'light' && device.light_effect) ? `effect-${device.light_effect}` : '';
    const modeClass = (config.type === 'ac' && device.ac_mode) ? `mode-${device.ac_mode}` : '';
    
    // Create icon element (SVG or Font Awesome)
    const iconElement = config.iconType === 'svg'
        ? `<img src="${config.svgPath}" class="device-icon ${config.cardClass}" alt="${config.name} icon" />`
        : `<i class="${config.fontAwesomeIcon} device-icon ${config.cardClass}"></i>`;
    
    // Add fan speed data attribute for CSS animation
    const speedAttr = (config.type === 'fan' && device.value !== null) 
        ? `data-speed="${Math.round(device.value / 10) * 10}"` 
        : '';
    
    col.innerHTML = `
        <div class="device-card ${config.cardClass} ${activeClass} ${effectClass} ${modeClass}" data-device-id="${device.id}" ${speedAttr}>
            ${iconElement}
            <div class="device-name">${config.name}</div>
            <div class="device-state">
                <div class="state-label">Current State</div>
                <div class="state-value ${stateClass}">${stateDisplay}</div>
            </div>
            ${createControls(device, config)}
        </div>
    `;

    // Attach event listeners
    attachEventListeners(col, device);

    return col;
}

// Create controls based on device type
function createControls(device, config) {
    if (config.type === 'light') {
        const currentEffect = device.light_effect || 'natural';
        const effects = ['vivid', 'natural', 'warm', 'cool', 'dim', 'bright'];
        
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="light-effects mt-3">
                <div class="effect-label mb-2">Light Effect:</div>
                <div class="effect-buttons">
                    ${effects.map(effect => `
                        <button class="btn btn-effect ${effect === currentEffect ? 'active' : ''}" 
                                data-effect="${effect}" 
                                data-action="set-effect">
                            ${effect.charAt(0).toUpperCase() + effect.slice(1)}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    } else if (config.type === 'fan') {
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="speed-controls mt-2">
                <button class="btn btn-control btn-speed" data-action="decrease">
                    <i class="bi bi-dash-lg"></i> Decrease
                </button>
                <button class="btn btn-control btn-speed" data-action="increase">
                    <i class="bi bi-plus-lg"></i> Increase
                </button>
            </div>
        `;
    } else if (config.type === 'sensor') {
        return `
            <div class="text-center text-muted">
                <small>Sensor - Read Only</small>
            </div>
        `;
    } else if (config.type === 'ac') {
        const currentMode = device.ac_mode || 'cool';
        const modes = ['cool', 'heat', 'fan', 'auto'];
        const currentTemp = device.value || 24;
        
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="ac-controls mt-3">
                <div class="ac-mode-section mb-3">
                    <div class="mode-label mb-2">Mode:</div>
                    <div class="mode-buttons">
                        ${modes.map(mode => `
                            <button class="btn btn-mode ${mode === currentMode ? 'active' : ''}" 
                                    data-mode="${mode}" 
                                    data-action="set-ac-mode">
                                ${mode.charAt(0).toUpperCase() + mode.slice(1)}
                            </button>
                        `).join('')}
                    </div>
                </div>
                <div class="ac-temp-section">
                    <div class="temp-label mb-2">Temperature: <span class="temp-value">${currentTemp}°C</span></div>
                    <div class="temp-controls">
                        <button class="btn btn-control btn-temp" data-action="decrease-temp">
                            <i class="bi bi-dash-lg"></i> Decrease
                        </button>
                        <button class="btn btn-control btn-temp" data-action="increase-temp">
                            <i class="bi bi-plus-lg"></i> Increase
                        </button>
                    </div>
                </div>
            </div>
        `;
    } else if (config.type === 'lock') {
        const isLocked = device.state === 'locked' || device.device_mode === 'locked';
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${isLocked ? 'Unlock' : 'Lock'}
            </button>
            <div class="device-info mt-2">
                <small class="text-muted">Status: ${isLocked ? 'Locked' : 'Unlocked'}</small>
            </div>
        `;
    } else if (config.type === 'blinds') {
        const position = device.value || 0;
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'open' ? 'Close' : 'Open'}
            </button>
            <div class="blinds-controls mt-2">
                <div class="position-label mb-2">Position: <span class="position-value">${position}%</span></div>
                <div class="position-controls">
                    <button class="btn btn-control btn-position" data-action="decrease-position">
                        <i class="bi bi-dash-lg"></i> Down
                    </button>
                    <button class="btn btn-control btn-position" data-action="increase-position">
                        <i class="bi bi-plus-lg"></i> Up
                    </button>
                </div>
            </div>
        `;
    } else if (config.type === 'plug') {
        const power = device.power_consumption || 0;
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="power-info mt-2">
                <small class="text-muted">Power: ${power.toFixed(1)}W</small>
            </div>
        `;
    } else if (config.type === 'camera') {
        const isRecording = device.device_mode === 'recording';
        const motionDetected = device.device_mode === 'motion';
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="camera-controls mt-2">
                <button class="btn btn-control btn-camera" data-action="toggle-recording">
                    ${isRecording ? 'Stop Recording' : 'Start Recording'}
                </button>
                <button class="btn btn-control btn-camera" data-action="toggle-motion">
                    Motion: ${motionDetected ? 'On' : 'Off'}
                </button>
            </div>
        `;
    } else if (config.type === 'speaker') {
        const volume = device.value || 50;
        const source = device.device_mode || 'bluetooth';
        const sources = ['bluetooth', 'wifi', 'aux', 'usb'];
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="speaker-controls mt-2">
                <div class="volume-section mb-2">
                    <div class="volume-label mb-1">Volume: <span class="volume-value">${volume}%</span></div>
                    <div class="volume-controls">
                        <button class="btn btn-control btn-volume" data-action="decrease-volume">
                            <i class="bi bi-dash-lg"></i>
                        </button>
                        <button class="btn btn-control btn-volume" data-action="increase-volume">
                            <i class="bi bi-plus-lg"></i>
                        </button>
                    </div>
                </div>
                <div class="source-section">
                    <div class="source-label mb-1">Source:</div>
                    <div class="source-buttons">
                        ${sources.map(s => `
                            <button class="btn btn-source ${s === source ? 'active' : ''}" 
                                    data-source="${s}" 
                                    data-action="set-source">
                                ${s.toUpperCase()}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } else if (config.type === 'garage') {
        const isOpen = device.state === 'open' || device.device_mode === 'open';
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${isOpen ? 'Close' : 'Open'}
            </button>
            <div class="device-info mt-2">
                <small class="text-muted">Status: ${isOpen ? 'Open' : 'Closed'}</small>
            </div>
        `;
    } else if (config.type === 'thermostat') {
        const temp = device.value || 22;
        const mode = device.device_mode || 'auto';
        const modes = ['heat', 'cool', 'auto', 'off'];
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="thermostat-controls mt-2">
                <div class="temp-section mb-2">
                    <div class="temp-label mb-1">Set Temp: <span class="temp-value">${temp}°C</span></div>
                    <div class="temp-controls">
                        <button class="btn btn-control btn-temp" data-action="decrease-thermo-temp">
                            <i class="bi bi-dash-lg"></i>
                        </button>
                        <button class="btn btn-control btn-temp" data-action="increase-thermo-temp">
                            <i class="bi bi-plus-lg"></i>
                        </button>
                    </div>
                </div>
                <div class="mode-section">
                    <div class="mode-label mb-1">Mode:</div>
                    <div class="mode-buttons">
                        ${modes.map(m => `
                            <button class="btn btn-mode ${m === mode ? 'active' : ''}" 
                                    data-mode="${m}" 
                                    data-action="set-thermo-mode">
                                ${m.charAt(0).toUpperCase() + m.slice(1)}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } else if (config.type === 'vacuum') {
        const battery = device.battery_level || 0;
        const mode = device.device_mode || 'auto';
        const modes = ['auto', 'spot', 'edge', 'deep'];
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Stop' : 'Start'}
            </button>
            <div class="vacuum-controls mt-2">
                <div class="battery-info mb-2">
                    <small class="text-muted">Battery: ${battery}%</small>
                </div>
                <div class="mode-section">
                    <div class="mode-label mb-1">Mode:</div>
                    <div class="mode-buttons">
                        ${modes.map(m => `
                            <button class="btn btn-mode ${m === mode ? 'active' : ''}" 
                                    data-mode="${m}" 
                                    data-action="set-vacuum-mode">
                                ${m.charAt(0).toUpperCase() + m.slice(1)}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } else if (config.type === 'doorbell') {
        const battery = device.battery_level || 0;
        const motionDetected = device.device_mode === 'motion';
        return `
            <div class="doorbell-controls">
                <div class="battery-info mb-2">
                    <small class="text-muted">Battery: ${battery}%</small>
                </div>
                <button class="btn btn-control btn-doorbell" data-action="toggle-motion">
                    Motion: ${motionDetected ? 'On' : 'Off'}
                </button>
                <button class="btn btn-control btn-doorbell" data-action="test-ring">
                    Test Ring
                </button>
            </div>
        `;
    } else if (config.type === 'sprinkler') {
        const zone = device.device_mode || 'zone1';
        const zones = ['zone1', 'zone2', 'zone3', 'zone4'];
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Stop' : 'Start'}
            </button>
            <div class="sprinkler-controls mt-2">
                <div class="zone-section">
                    <div class="zone-label mb-1">Zone:</div>
                    <div class="zone-buttons">
                        ${zones.map(z => `
                            <button class="btn btn-zone ${z === zone ? 'active' : ''}" 
                                    data-zone="${z}" 
                                    data-action="set-zone">
                                ${z.toUpperCase()}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } else if (config.type === 'motion') {
        const motionDetected = device.state === 'on';
        return `
            <div class="text-center text-muted">
                <small>Motion: ${motionDetected ? 'Detected' : 'No Motion'}</small>
            </div>
        `;
    } else if (config.type === 'tv') {
        const volume = device.value || 30;
        const input = device.device_mode || 'hdmi1';
        const inputs = ['hdmi1', 'hdmi2', 'usb', 'wifi', 'antenna'];
        return `
            <button class="btn btn-control btn-toggle" data-action="toggle">
                ${device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            <div class="tv-controls mt-2">
                <div class="volume-section mb-2">
                    <div class="volume-label mb-1">Volume: <span class="volume-value">${volume}%</span></div>
                    <div class="volume-controls">
                        <button class="btn btn-control btn-volume" data-action="decrease-tv-volume">
                            <i class="bi bi-dash-lg"></i>
                        </button>
                        <button class="btn btn-control btn-volume" data-action="increase-tv-volume">
                            <i class="bi bi-plus-lg"></i>
                        </button>
                    </div>
                </div>
                <div class="input-section">
                    <div class="input-label mb-1">Input:</div>
                    <div class="input-buttons">
                        ${inputs.map(i => `
                            <button class="btn btn-input ${i === input ? 'active' : ''}" 
                                    data-input="${i}" 
                                    data-action="set-tv-input">
                                ${i.toUpperCase()}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    return '';
}

// Attach event listeners to device card
function attachEventListeners(col, device) {
    const card = col.querySelector('.device-card');
    const deviceId = device.id;

    // Toggle button
    const toggleBtn = col.querySelector('[data-action="toggle"]');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', async () => {
            await toggleDevice(deviceId, card);
        });
    }

    // Speed controls
    const increaseBtn = col.querySelector('[data-action="increase"]');
    const decreaseBtn = col.querySelector('[data-action="decrease"]');

    if (increaseBtn) {
        increaseBtn.addEventListener('click', async () => {
            await changeFanSpeed(deviceId, 1, card);
        });
    }

    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', async () => {
            await changeFanSpeed(deviceId, -1, card);
        });
    }

    // Light effect buttons
    const effectButtons = col.querySelectorAll('[data-action="set-effect"]');
    effectButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const effect = btn.dataset.effect;
            await changeLightEffect(deviceId, effect, card);
        });
    });

    // AC mode buttons
    const acModeButtons = col.querySelectorAll('[data-action="set-ac-mode"]');
    acModeButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const mode = btn.dataset.mode;
            await changeACMode(deviceId, mode, card);
        });
    });

    // AC temperature controls
    const increaseTempBtn = col.querySelector('[data-action="increase-temp"]');
    const decreaseTempBtn = col.querySelector('[data-action="decrease-temp"]');
    if (increaseTempBtn) increaseTempBtn.addEventListener('click', async () => await changeACTemperature(deviceId, 1, card));
    if (decreaseTempBtn) decreaseTempBtn.addEventListener('click', async () => await changeACTemperature(deviceId, -1, card));

    // Blinds position controls
    const increasePosBtn = col.querySelector('[data-action="increase-position"]');
    const decreasePosBtn = col.querySelector('[data-action="decrease-position"]');
    if (increasePosBtn) increasePosBtn.addEventListener('click', async () => await changeBlindsPosition(deviceId, 10, card));
    if (decreasePosBtn) decreasePosBtn.addEventListener('click', async () => await changeBlindsPosition(deviceId, -10, card));

    // Speaker volume controls
    const increaseVolBtn = col.querySelector('[data-action="increase-volume"]');
    const decreaseVolBtn = col.querySelector('[data-action="decrease-volume"]');
    if (increaseVolBtn) increaseVolBtn.addEventListener('click', async () => await changeVolume(deviceId, 5, card));
    if (decreaseVolBtn) decreaseVolBtn.addEventListener('click', async () => await changeVolume(deviceId, -5, card));

    // Speaker source selection
    const sourceButtons = col.querySelectorAll('[data-action="set-source"]');
    sourceButtons.forEach(btn => btn.addEventListener('click', async () => await changeDeviceMode(deviceId, btn.dataset.source, card)));

    // Camera controls
    const recordBtn = col.querySelector('[data-action="toggle-recording"]');
    const motionBtn = col.querySelector('[data-action="toggle-motion"]');
    if (recordBtn) recordBtn.addEventListener('click', async () => await toggleCameraRecording(deviceId, card));
    if (motionBtn) motionBtn.addEventListener('click', async () => await toggleCameraMotion(deviceId, card));

    // Thermostat controls
    const increaseThermoBtn = col.querySelector('[data-action="increase-thermo-temp"]');
    const decreaseThermoBtn = col.querySelector('[data-action="decrease-thermo-temp"]');
    if (increaseThermoBtn) increaseThermoBtn.addEventListener('click', async () => await changeThermostatTemp(deviceId, 1, card));
    if (decreaseThermoBtn) decreaseThermoBtn.addEventListener('click', async () => await changeThermostatTemp(deviceId, -1, card));
    const thermoModeButtons = col.querySelectorAll('[data-action="set-thermo-mode"]');
    thermoModeButtons.forEach(btn => btn.addEventListener('click', async () => await changeDeviceMode(deviceId, btn.dataset.mode, card)));

    // Vacuum mode
    const vacuumModeButtons = col.querySelectorAll('[data-action="set-vacuum-mode"]');
    vacuumModeButtons.forEach(btn => btn.addEventListener('click', async () => await changeDeviceMode(deviceId, btn.dataset.mode, card)));

    // Doorbell controls
    const doorbellMotionBtn = col.querySelector('[data-action="toggle-motion"]');
    const testRingBtn = col.querySelector('[data-action="test-ring"]');
    if (doorbellMotionBtn) doorbellMotionBtn.addEventListener('click', async () => await toggleDoorbellMotion(deviceId, card));
    if (testRingBtn) testRingBtn.addEventListener('click', async () => await testDoorbell(deviceId, card));

    // Sprinkler zone selection
    const zoneButtons = col.querySelectorAll('[data-action="set-zone"]');
    zoneButtons.forEach(btn => btn.addEventListener('click', async () => await changeDeviceMode(deviceId, btn.dataset.zone, card)));

    // TV controls
    const increaseTVVolBtn = col.querySelector('[data-action="increase-tv-volume"]');
    const decreaseTVVolBtn = col.querySelector('[data-action="decrease-tv-volume"]');
    if (increaseTVVolBtn) increaseTVVolBtn.addEventListener('click', async () => await changeTVVolume(deviceId, 5, card));
    if (decreaseTVVolBtn) decreaseTVVolBtn.addEventListener('click', async () => await changeTVVolume(deviceId, -5, card));
    const tvInputButtons = col.querySelectorAll('[data-action="set-tv-input"]');
    tvInputButtons.forEach(btn => btn.addEventListener('click', async () => await changeDeviceMode(deviceId, btn.dataset.input, card)));
}

// Show toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toastId = `toast-${Date.now()}`;
    const bgClass = type === 'success' ? 'bg-success' : 'bg-danger';
    const icon = type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill';
    
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <i class="bi ${icon} me-2"></i>
                <strong class="me-auto">${type === 'success' ? 'Success' : 'Error'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Disable all buttons in a card
function disableCardButtons(card) {
    const buttons = card.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.classList.add('disabled');
    });
}

// Enable all buttons in a card
function enableCardButtons(card) {
    const buttons = card.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('disabled');
    });
}

// Show updating state on buttons
function showUpdatingState(card, isUpdating = true) {
    const buttons = card.querySelectorAll('button');
    buttons.forEach(btn => {
        if (isUpdating) {
            // Store original HTML content
            if (!btn.dataset.originalHtml) {
                btn.dataset.originalHtml = btn.innerHTML;
            }
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Updating...';
        } else {
            // Restore original HTML content
            const originalHtml = btn.dataset.originalHtml;
            if (originalHtml) {
                btn.innerHTML = originalHtml;
                delete btn.dataset.originalHtml;
            }
        }
    });
}

// Toggle device state
async function toggleDevice(deviceId, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        // Show updating state and disable buttons
        card.classList.add('loading');
        disableCardButtons(card);
        showUpdatingState(card, true);
        
        // For lock and garage, we need to handle state differently
        if (config.type === 'lock') {
            const response = await fetch(`/api/device/${deviceId}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const device = await response.json();
            const newState = (device.state === 'locked' || device.device_mode === 'locked') ? 'unlocked' : 'locked';
            const newMode = newState === 'locked' ? 'locked' : 'unlocked';
            
            // Update both state and mode
            await fetch(`/api/device/${deviceId}/set_value`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value: newState === 'locked' ? 1 : 0 })
            });
            await fetch(`/api/device/${deviceId}/set_mode`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: newMode })
            });
            
            const toggleResponse = await fetch(`/api/device/${deviceId}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!toggleResponse.ok) throw new Error(`HTTP error! status: ${toggleResponse.status}`);
            const updatedDevice = await toggleResponse.json();
            updateDeviceCard(card, updatedDevice);
        } else if (config.type === 'garage') {
            const response = await fetch(`/api/device/${deviceId}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const device = await response.json();
            const newState = (device.state === 'open' || device.device_mode === 'open') ? 'closed' : 'open';
            const newMode = newState;
            
            await fetch(`/api/device/${deviceId}/set_mode`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: newMode })
            });
            
            const toggleResponse = await fetch(`/api/device/${deviceId}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!toggleResponse.ok) throw new Error(`HTTP error! status: ${toggleResponse.status}`);
            const updatedDevice = await toggleResponse.json();
            updateDeviceCard(card, updatedDevice);
        } else {
            const response = await fetch(`/api/device/${deviceId}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const device = await response.json();
            updateDeviceCard(card, device);
        }
    } catch (error) {
        console.error('Error toggling device:', error);
        showToast(`Failed to toggle ${config.name}. Please try again.`, 'error');
    } finally {
        // Restore button state
        card.classList.remove('loading');
        enableCardButtons(card);
        showUpdatingState(card, false);
    }
}

// Change fan speed
async function changeFanSpeed(deviceId, delta, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        // Show updating state and disable buttons
        card.classList.add('loading');
        disableCardButtons(card);
        showUpdatingState(card, true);
        
        // Get current device state
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        let device = await response.json();
        
        // If fan is off, turn it on first
        if (device.state === 'off') {
            const toggleResponse = await fetch(`/api/device/${deviceId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!toggleResponse.ok) {
                throw new Error('Failed to turn on fan');
            }
            // Get updated device after toggling
            device = await toggleResponse.json();
        }
        
        const currentValue = device.value || 0;
        const newValue = Math.max(0, Math.min(100, currentValue + (delta * 10)));
        
        // Don't update if value hasn't changed
        if (newValue === currentValue) {
            card.classList.remove('loading');
            enableCardButtons(card);
            showUpdatingState(card, false);
            return;
        }

        // Update device value
        const updateResponse = await fetch(`/api/device/${deviceId}/set_value`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ value: newValue })
        });
        
        if (!updateResponse.ok) {
            throw new Error(`HTTP error! status: ${updateResponse.status}`);
        }
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
        
        // Success toast removed
        
        // Log for debugging
        console.log(`Fan speed updated: ${currentValue}% -> ${newValue}%`);
    } catch (error) {
        console.error('Error changing fan speed:', error);
        showToast(`Failed to change ${config.name} speed. Please try again.`, 'error');
    } finally {
        // Restore button state
        card.classList.remove('loading');
        enableCardButtons(card);
        showUpdatingState(card, false);
    }
}

// Change light effect
async function changeLightEffect(deviceId, effect, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        // Show updating state and disable buttons
        card.classList.add('loading');
        disableCardButtons(card);
        
        const response = await fetch(`/api/device/${deviceId}/set_effect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ effect: effect })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const device = await response.json();
        updateDeviceCard(card, device);
        
        // Success toast removed
    } catch (error) {
        console.error('Error changing light effect:', error);
        showToast(`Failed to change ${config.name} effect. Please try again.`, 'error');
    } finally {
        // Restore button state
        card.classList.remove('loading');
        enableCardButtons(card);
    }
}

// Change AC mode
async function changeACMode(deviceId, mode, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        // Show updating state and disable buttons
        card.classList.add('loading');
        disableCardButtons(card);
        
        const response = await fetch(`/api/device/${deviceId}/set_ac_mode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mode: mode })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const device = await response.json();
        updateDeviceCard(card, device);
        
    } catch (error) {
        console.error('Error changing AC mode:', error);
        showToast(`Failed to change ${config.name} mode. Please try again.`, 'error');
    } finally {
        // Restore button state
        card.classList.remove('loading');
        enableCardButtons(card);
    }
}

// Change AC temperature
async function changeACTemperature(deviceId, delta, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        // Show updating state and disable buttons
        card.classList.add('loading');
        disableCardButtons(card);
        showUpdatingState(card, true);
        
        // Get current device state
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        let device = await response.json();
        
        // If AC is off, turn it on first
        if (device.state === 'off') {
            const toggleResponse = await fetch(`/api/device/${deviceId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!toggleResponse.ok) {
                throw new Error('Failed to turn on AC');
            }
            // Get updated device after toggling
            device = await toggleResponse.json();
        }
        
        const currentValue = device.value || 24;
        const newValue = Math.max(16, Math.min(30, currentValue + delta));
        
        // Don't update if value hasn't changed
        if (newValue === currentValue) {
            card.classList.remove('loading');
            enableCardButtons(card);
            showUpdatingState(card, false);
            return;
        }

        // Update device value
        const updateResponse = await fetch(`/api/device/${deviceId}/set_value`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ value: newValue })
        });
        
        if (!updateResponse.ok) {
            throw new Error(`HTTP error! status: ${updateResponse.status}`);
        }
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
        
        // Log for debugging
        console.log(`AC temperature updated: ${currentValue}°C -> ${newValue}°C`);
    } catch (error) {
        console.error('Error changing AC temperature:', error);
        showToast(`Failed to change ${config.name} temperature. Please try again.`, 'error');
    } finally {
        // Restore button state
        card.classList.remove('loading');
        enableCardButtons(card);
        showUpdatingState(card, false);
    }
}

// Change device mode (generic function for various devices)
async function changeDeviceMode(deviceId, mode, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        
        const response = await fetch(`/api/device/${deviceId}/set_mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const device = await response.json();
        updateDeviceCard(card, device);
    } catch (error) {
        console.error('Error changing device mode:', error);
        showToast(`Failed to change ${config.name} mode. Please try again.`, 'error');
    } finally {
        card.classList.remove('loading');
        enableCardButtons(card);
    }
}

// Change blinds position
async function changeBlindsPosition(deviceId, delta, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        showUpdatingState(card, true);
        
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        let device = await response.json();
        if (device.state === 'closed') {
            const toggleResponse = await fetch(`/api/device/${deviceId}/toggle`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
            if (!toggleResponse.ok) throw new Error('Failed to open blinds');
            device = await toggleResponse.json();
        }
        
        const currentValue = device.value || 0;
        const newValue = Math.max(0, Math.min(100, currentValue + delta));
        
        if (newValue === currentValue) {
            card.classList.remove('loading');
            enableCardButtons(card);
            showUpdatingState(card, false);
            return;
        }

        const updateResponse = await fetch(`/api/device/${deviceId}/set_value`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value: newValue })
        });
        
        if (!updateResponse.ok) throw new Error(`HTTP error! status: ${updateResponse.status}`);
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
    } catch (error) {
        console.error('Error changing blinds position:', error);
        showToast(`Failed to change ${config.name} position. Please try again.`, 'error');
    } finally {
        card.classList.remove('loading');
        enableCardButtons(card);
        showUpdatingState(card, false);
    }
}

// Change volume (speaker/TV)
async function changeVolume(deviceId, delta, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        showUpdatingState(card, true);
        
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        let device = await response.json();
        if (device.state === 'off') {
            const toggleResponse = await fetch(`/api/device/${deviceId}/toggle`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
            if (!toggleResponse.ok) throw new Error('Failed to turn on device');
            device = await toggleResponse.json();
        }
        
        const currentValue = device.value || 0;
        const newValue = Math.max(0, Math.min(100, currentValue + delta));
        
        if (newValue === currentValue) {
            card.classList.remove('loading');
            enableCardButtons(card);
            showUpdatingState(card, false);
            return;
        }

        const updateResponse = await fetch(`/api/device/${deviceId}/set_value`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value: newValue })
        });
        
        if (!updateResponse.ok) throw new Error(`HTTP error! status: ${updateResponse.status}`);
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
    } catch (error) {
        console.error('Error changing volume:', error);
        showToast(`Failed to change ${config.name} volume. Please try again.`, 'error');
    } finally {
        card.classList.remove('loading');
        enableCardButtons(card);
        showUpdatingState(card, false);
    }
}

// Change thermostat temperature
async function changeThermostatTemp(deviceId, delta, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        showUpdatingState(card, true);
        
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        let device = await response.json();
        if (device.state === 'off') {
            const toggleResponse = await fetch(`/api/device/${deviceId}/toggle`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
            if (!toggleResponse.ok) throw new Error('Failed to turn on thermostat');
            device = await toggleResponse.json();
        }
        
        const currentValue = device.value || 22;
        const newValue = Math.max(16, Math.min(30, currentValue + delta));
        
        if (newValue === currentValue) {
            card.classList.remove('loading');
            enableCardButtons(card);
            showUpdatingState(card, false);
            return;
        }

        const updateResponse = await fetch(`/api/device/${deviceId}/set_value`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value: newValue })
        });
        
        if (!updateResponse.ok) throw new Error(`HTTP error! status: ${updateResponse.status}`);
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
    } catch (error) {
        console.error('Error changing thermostat temperature:', error);
        showToast(`Failed to change ${config.name} temperature. Please try again.`, 'error');
    } finally {
        card.classList.remove('loading');
        enableCardButtons(card);
        showUpdatingState(card, false);
    }
}

// Change TV volume
async function changeTVVolume(deviceId, delta, card) {
    await changeVolume(deviceId, delta, card);
}

// Toggle camera recording
async function toggleCameraRecording(deviceId, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const device = await response.json();
        const newMode = device.device_mode === 'recording' ? 'idle' : 'recording';
        
        const updateResponse = await fetch(`/api/device/${deviceId}/set_mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: newMode })
        });
        
        if (!updateResponse.ok) throw new Error(`HTTP error! status: ${updateResponse.status}`);
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
    } catch (error) {
        console.error('Error toggling camera recording:', error);
        showToast(`Failed to toggle ${config.name} recording. Please try again.`, 'error');
    } finally {
        card.classList.remove('loading');
        enableCardButtons(card);
    }
}

// Toggle camera motion detection
async function toggleCameraMotion(deviceId, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const device = await response.json();
        const newMode = device.device_mode === 'motion' ? 'idle' : 'motion';
        
        const updateResponse = await fetch(`/api/device/${deviceId}/set_mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: newMode })
        });
        
        if (!updateResponse.ok) throw new Error(`HTTP error! status: ${updateResponse.status}`);
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
    } catch (error) {
        console.error('Error toggling camera motion:', error);
        showToast(`Failed to toggle ${config.name} motion detection. Please try again.`, 'error');
    } finally {
        card.classList.remove('loading');
        enableCardButtons(card);
    }
}

// Toggle doorbell motion
async function toggleDoorbellMotion(deviceId, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        
        const response = await fetch(`/api/device/${deviceId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const device = await response.json();
        const newMode = device.device_mode === 'motion' ? 'idle' : 'motion';
        
        const updateResponse = await fetch(`/api/device/${deviceId}/set_mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: newMode })
        });
        
        if (!updateResponse.ok) throw new Error(`HTTP error! status: ${updateResponse.status}`);
        
        const updatedDevice = await updateResponse.json();
        updateDeviceCard(card, updatedDevice);
    } catch (error) {
        console.error('Error toggling doorbell motion:', error);
        showToast(`Failed to toggle ${config.name} motion. Please try again.`, 'error');
    } finally {
        card.classList.remove('loading');
        enableCardButtons(card);
    }
}

// Test doorbell
async function testDoorbell(deviceId, card) {
    const config = deviceConfig[deviceId];
    if (!config) return;
    
    try {
        card.classList.add('loading');
        disableCardButtons(card);
        
        // Simulate doorbell ring
        showToast('Doorbell ringing!', 'success');
        
        // Flash the card
        card.style.animation = 'pulse 0.5s ease-in-out 3';
        setTimeout(() => {
            card.style.animation = '';
            card.classList.remove('loading');
            enableCardButtons(card);
        }, 1500);
    } catch (error) {
        console.error('Error testing doorbell:', error);
        showToast(`Failed to test ${config.name}. Please try again.`, 'error');
        card.classList.remove('loading');
        enableCardButtons(card);
    }
}

// Update device card UI dynamically
function updateDeviceCard(card, device) {
    const config = deviceConfig[device.id];
    if (!config) return;

    const isOn = device.state === 'on';
    const stateDisplay = device.type === 'sensor' 
        ? `${device.value}°C` 
        : (device.type === 'fan' && device.value !== null 
            ? `${device.value}%` 
            : (isOn ? 'ON' : 'OFF'));

    const stateClass = device.type === 'sensor' || (device.type === 'fan' && device.value !== null)
        ? 'number'
        : (isOn ? 'on' : 'off');

    // Update active class for icon animations
    const activeTypes = ['light', 'fan', 'sensor', 'ac', 'lock', 'blinds', 'plug', 'camera', 'speaker', 'garage', 'thermostat', 'vacuum', 'doorbell', 'sprinkler', 'motion', 'tv'];
    const isActive = (config.type === 'lock' && (device.state === 'locked' || device.device_mode === 'locked')) ||
                     (config.type === 'garage' && (device.state === 'open' || device.device_mode === 'open')) ||
                     (config.type === 'motion' && device.state === 'on') ||
                     (config.type === 'doorbell' && device.device_mode === 'motion') ||
                     (isOn && activeTypes.includes(config.type));
    
    if (isActive) {
        card.classList.add('active');
    } else {
        card.classList.remove('active');
    }

    // Update fan speed data attribute for CSS animation speed
    if (config.type === 'fan' && device.value !== null) {
        const speedValue = Math.round(device.value / 10) * 10; // Round to nearest 10
        card.setAttribute('data-speed', speedValue);
    } else if (config.type === 'fan') {
        card.removeAttribute('data-speed');
    }

    // Update state display text
    const stateValue = card.querySelector('.state-value');
    if (stateValue) {
        stateValue.textContent = stateDisplay;
        stateValue.className = `state-value ${stateClass}`;
    }

    // Update toggle button text
    const toggleBtn = card.querySelector('[data-action="toggle"]');
    if (toggleBtn) {
        toggleBtn.textContent = isOn ? 'Turn Off' : 'Turn On';
    }

    // Update light effect buttons
    if (config.type === 'light' && device.light_effect) {
        const effectButtons = card.querySelectorAll('[data-action="set-effect"]');
        effectButtons.forEach(btn => {
            if (btn.dataset.effect === device.light_effect) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update card class for effect styling
        card.classList.remove('effect-vivid', 'effect-natural', 'effect-warm', 'effect-cool', 'effect-dim', 'effect-bright');
        card.classList.add(`effect-${device.light_effect}`);
    }

    // Update AC mode buttons and card class
    if (config.type === 'ac' && device.ac_mode) {
        const modeButtons = card.querySelectorAll('[data-action="set-ac-mode"]');
        modeButtons.forEach(btn => {
            if (btn.dataset.mode === device.ac_mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update card class for mode styling
        card.classList.remove('mode-cool', 'mode-heat', 'mode-fan', 'mode-auto');
        card.classList.add(`mode-${device.ac_mode}`);
        
        // Update temperature display
        const tempValue = card.querySelector('.temp-value');
        if (tempValue && device.value !== null) {
            tempValue.textContent = `${device.value}°C`;
        }
    }

    // Update device mode buttons for various devices
    if (device.device_mode) {
        const modeButtons = card.querySelectorAll('[data-action="set-mode"], [data-action="set-source"], [data-action="set-thermo-mode"], [data-action="set-vacuum-mode"], [data-action="set-zone"], [data-action="set-tv-input"]');
        modeButtons.forEach(btn => {
            const modeValue = btn.dataset.mode || btn.dataset.source || btn.dataset.zone || btn.dataset.input;
            if (modeValue === device.device_mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Update blinds position
    if (config.type === 'blinds') {
        const positionValue = card.querySelector('.position-value');
        if (positionValue && device.value !== null) {
            positionValue.textContent = `${device.value}%`;
        }
    }

    // Update speaker/TV volume
    if (config.type === 'speaker' || config.type === 'tv') {
        const volumeValue = card.querySelector('.volume-value');
        if (volumeValue && device.value !== null) {
            volumeValue.textContent = `${device.value}%`;
        }
    }

    // Update thermostat temperature
    if (config.type === 'thermostat') {
        const tempValue = card.querySelector('.temp-value');
        if (tempValue && device.value !== null) {
            tempValue.textContent = `${device.value}°C`;
        }
    }

    // Update camera recording button
    if (config.type === 'camera') {
        const recordBtn = card.querySelector('[data-action="toggle-recording"]');
        if (recordBtn) {
            recordBtn.textContent = device.device_mode === 'recording' ? 'Stop Recording' : 'Start Recording';
        }
        const motionBtn = card.querySelector('[data-action="toggle-motion"]');
        if (motionBtn) {
            motionBtn.textContent = `Motion: ${device.device_mode === 'motion' ? 'On' : 'Off'}`;
        }
    }

    // Update doorbell motion button
    if (config.type === 'doorbell') {
        const motionBtn = card.querySelector('[data-action="toggle-motion"]');
        if (motionBtn) {
            motionBtn.textContent = `Motion: ${device.device_mode === 'motion' ? 'On' : 'Off'}`;
        }
    }

    // Update lock/garage toggle button
    if (config.type === 'lock') {
        const toggleBtn = card.querySelector('[data-action="toggle"]');
        if (toggleBtn) {
            const isLocked = device.state === 'locked' || device.device_mode === 'locked';
            toggleBtn.textContent = isLocked ? 'Unlock' : 'Lock';
        }
    }

    if (config.type === 'garage') {
        const toggleBtn = card.querySelector('[data-action="toggle"]');
        if (toggleBtn) {
            const isOpen = device.state === 'open' || device.device_mode === 'open';
            toggleBtn.textContent = isOpen ? 'Close' : 'Open';
        }
    }
}

// Load scenes
async function loadScenes() {
    try {
        const response = await fetch('/api/scenes');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const scenes = await response.json();
        renderScenes(scenes);
    } catch (error) {
        console.error('Error loading scenes:', error);
    }
}

// Render scenes
function renderScenes(scenes) {
    const container = document.getElementById('scenes-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    scenes.forEach(scene => {
        const col = document.createElement('div');
        col.className = 'col-6 col-md-3 mb-3';
        col.innerHTML = `
            <div class="scene-card">
                <div class="scene-name">${scene.name}</div>
                <button class="btn btn-scene" data-scene-id="${scene.id}">
                    <i class="bi bi-play-fill me-2"></i>Activate
                </button>
            </div>
        `;
        
        const btn = col.querySelector('.btn-scene');
        btn.addEventListener('click', async () => {
            await activateScene(scene.id);
        });
        
        container.appendChild(col);
    });
}

// Activate scene
async function activateScene(sceneId) {
    try {
        const response = await fetch(`/api/scenes/${sceneId}/activate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        showToast('Scene activated successfully!', 'success');
        // Reload devices to show updated states
        setTimeout(loadDevices, 500);
    } catch (error) {
        console.error('Error activating scene:', error);
        showToast('Failed to activate scene. Please try again.', 'error');
    }
}

// Load energy data
async function loadEnergyData() {
    try {
        const response = await fetch('/api/energy');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        renderEnergyData(data);
    } catch (error) {
        console.error('Error loading energy data:', error);
    }
}

// Render energy data
function renderEnergyData(data) {
    const container = document.getElementById('energy-dashboard');
    if (!container) return;
    
    const totalKW = (data.total_power / 1000).toFixed(2);
    const dailyKWh = (data.daily_energy / 1000).toFixed(2);
    
    container.innerHTML = `
        <div class="energy-summary mb-3">
            <div class="energy-card">
                <div class="energy-label">Total Power</div>
                <div class="energy-value">${totalKW} kW</div>
            </div>
            <div class="energy-card">
                <div class="energy-label">Daily Usage</div>
                <div class="energy-value">${dailyKWh} kWh</div>
            </div>
        </div>
        <div class="energy-devices">
            <h4 class="mb-2">Device Power Consumption</h4>
            <div class="device-power-list">
                ${data.devices.map(device => `
                    <div class="device-power-item">
                        <span class="device-power-name">${device.name}</span>
                        <span class="device-power-value">${device.power.toFixed(1)}W</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load devices immediately
    loadDevices();
    loadScenes();
    loadEnergyData();
    
    // Refresh device states every 2 seconds
    setInterval(loadDevices, 2000);
    // Refresh energy data every 5 seconds
    setInterval(loadEnergyData, 5000);
});

