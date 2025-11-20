# Smart Home Automation Dashboard

A modern, responsive web dashboard for controlling IoT devices with a Flask backend and real-time updates.

## Features

### 🏠 **16 Smart Devices**
- 💡 **Light** - Multiple light effects (vivid, natural, warm, cool, dim, bright)
- 🌪️ **Fan** - Adjustable speed control (0-100%)
- 🌡️ **Temperature Sensor** - Real-time temperature monitoring
- ❄️ **Air Conditioner** - Temperature and mode control (cool, heat, fan, auto)
- 🔒 **Smart Lock** - Lock/unlock control
- 🪟 **Smart Blinds** - Position control (0-100%)
- 🔌 **Smart Plug** - On/off with power monitoring
- 📹 **Security Camera** - Recording and motion detection
- 🔊 **Smart Speaker** - Volume and source control (Bluetooth, WiFi, AUX, USB)
- 🚗 **Garage Door** - Open/close control
- 🌡️ **Smart Thermostat** - Temperature and mode control
- 🤖 **Smart Vacuum** - Cleaning modes with battery indicator
- 🔔 **Smart Doorbell** - Motion detection and test ring
- 💧 **Smart Sprinkler** - Zone control (4 zones)
- 📡 **Motion Sensor** - Motion detection status
- 📺 **Smart TV** - Volume and input control

### ⚡ **Advanced Features**
- 🎬 **Scene Control** - Preset scenes (Good Morning, Movie Night, Away, Sleep)
- ⏰ **Schedules/Automations** - Time-based automation (API ready)
- ⚡ **Energy Monitoring** - Real-time power consumption dashboard

### 🎨 **UI Features**
- 🎨 **Modern Dark Theme**: Beautiful UI with glowing effects and smooth animations
- 📱 **Fully Responsive**: Optimized for mobile, tablet, and desktop
- ⚡ **Real-time Updates**: Live device monitoring with automatic updates
- 🔄 **RESTful API**: Ready for IoT integration via REST APIs

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome, Bootstrap Icons

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SevenCandid/Smart-Home-Automation-Dashboard.git
cd Smart-Home-Automation-Dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Deployment on Vercel

This project is configured for deployment on Vercel:

1. Push your code to GitHub
2. Import the repository in Vercel
3. Vercel will automatically detect the configuration and deploy

### Vercel Configuration

- The `vercel.json` file configures the serverless function
- The Flask app is wrapped in `api/index.py` for Vercel compatibility
- Static files are served directly from the `/static` directory

## Project Structure

```
home_automation_dashboard/
├── app.py                 # Flask application and API routes
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment configuration
├── api/
│   └── index.py         # Vercel serverless function handler
├── templates/
│   └── index.html       # Main dashboard HTML
├── static/
│   ├── css/
│   │   └── style.css    # Custom styles and animations
│   ├── js/
│   │   └── dashboard.js # Client-side logic
│   └── icons/
│       ├── lightbulb.svg
│       ├── fan.svg
│       └── thermometer.svg
└── README.md
```

## API Endpoints

### Device Management
- `GET /api/devices` - Get all devices
- `GET /api/device/<id>` - Get a specific device
- `POST /api/device/<id>/toggle` - Toggle device on/off
- `POST /api/device/<id>/set_value` - Update device value (fan speed, temperature, etc.)
- `POST /api/device/<id>/set_effect` - Set light effect
- `POST /api/device/<id>/set_ac_mode` - Set AC mode (cool, heat, fan, auto)
- `POST /api/device/<id>/set_mode` - Set device mode (for various devices)

### Scene Control
- `GET /api/scenes` - Get all scenes
- `POST /api/scenes/<id>/activate` - Activate a scene

### Energy Monitoring
- `GET /api/energy` - Get energy consumption data

### Schedules (API Ready)
- `GET /api/schedules` - Get all schedules

## Developer

Developed by **Seven**

## License

This project is open source and available for use.

