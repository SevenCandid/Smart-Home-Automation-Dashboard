# Smart Home Automation Dashboard

A modern, responsive web dashboard for controlling IoT devices with a Flask backend and real-time updates.

## Features

- 🏠 **Smart Device Control**: Control lights, fans, and monitor temperature sensors
- 🎨 **Modern Dark Theme**: Beautiful UI with glowing effects and smooth animations
- 📱 **Fully Responsive**: Optimized for mobile, tablet, and desktop
- ⚡ **Real-time Updates**: Live temperature monitoring with automatic updates
- 🎯 **Light Effects**: Multiple light modes (vivid, natural, warm, cool, dim, bright)
- 🌪️ **Fan Speed Control**: Adjustable fan speed with visual feedback
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

- `GET /api/devices` - Get all devices
- `GET /api/device/<id>` - Get a specific device
- `POST /api/device/<id>/toggle` - Toggle device on/off
- `POST /api/device/<id>/set_value` - Update device value (fan speed)
- `POST /api/device/<id>/set_effect` - Set light effect

## Developer

Developed by **Seven**

## License

This project is open source and available for use.

