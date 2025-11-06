/**
 * Smart Home Automation Dashboard
 * JavaScript for device management and UI updates
 * Ready for IoT integration via REST APIs
 */

// Device configuration with Font Awesome icons (fallback to SVG)
const deviceConfig = {
    1: { 
        name: 'Light', 
        type: 'light', 
        iconType: 'fontawesome', // 'svg' or 'fontawesome'
        svgPath: '/static/icons/lightbulb.svg',
        fontAwesomeIcon: 'fa-solid fa-lightbulb',
        cardClass: 'light' 
    },
    2: { 
        name: 'Fan', 
        type: 'fan', 
        iconType: 'fontawesome',
        svgPath: '/static/icons/fan.svg',
        fontAwesomeIcon: 'fa-solid fa-fan',
        cardClass: 'fan' 
    },
    3: { 
        name: 'Temperature', 
        type: 'sensor', 
        iconType: 'fontawesome',
        svgPath: '/static/icons/thermometer.svg',
        fontAwesomeIcon: 'fa-solid fa-thermometer-half',
        cardClass: 'temperature' 
    }
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
    const stateDisplay = device.type === 'sensor' 
        ? `${device.value}°C` 
        : (device.type === 'fan' && device.value !== null 
            ? `${device.value}%` 
            : (isOn ? 'ON' : 'OFF'));

    const stateClass = device.type === 'sensor' || (device.type === 'fan' && device.value !== null)
        ? 'number'
        : (isOn ? 'on' : 'off');

    // Add active class for light/fan when on, and temperature sensor when state is on
    const activeClass = (isOn && (config.type === 'light' || config.type === 'fan' || config.type === 'sensor')) ? 'active' : '';
    const effectClass = (config.type === 'light' && device.light_effect) ? `effect-${device.light_effect}` : '';
    
    // Create icon element (SVG or Font Awesome)
    const iconElement = config.iconType === 'svg'
        ? `<img src="${config.svgPath}" class="device-icon ${config.cardClass}" alt="${config.name} icon" />`
        : `<i class="${config.fontAwesomeIcon} device-icon ${config.cardClass}"></i>`;
    
    // Add fan speed data attribute for CSS animation
    const speedAttr = (config.type === 'fan' && device.value !== null) 
        ? `data-speed="${Math.round(device.value / 10) * 10}"` 
        : '';
    
    col.innerHTML = `
        <div class="device-card ${config.cardClass} ${activeClass} ${effectClass}" data-device-id="${device.id}" ${speedAttr}>
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
        
        const response = await fetch(`/api/device/${deviceId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const device = await response.json();
        updateDeviceCard(card, device);
        
        // Success toast removed
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
    // Light, fan, and temperature sensors all animate when state is "on"
    if (isOn && (config.type === 'light' || config.type === 'fan' || config.type === 'sensor')) {
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
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load devices immediately
    loadDevices();
    
    // Refresh device states every 2 seconds
    setInterval(loadDevices, 2000);
});

