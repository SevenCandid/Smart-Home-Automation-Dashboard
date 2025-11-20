"""
Smart Home Automation Dashboard
Flask application with REST API for IoT device management
Ready for AI & IoT integration
"""

import os
import sqlite3
import threading
import random
import time
import json
from flask import Flask, render_template, jsonify, request

# Try to import CORS, make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("Warning: flask_cors not installed. CORS disabled. Install with: pip install flask-cors")

# Flask app initialization with explicit paths for Vercel compatibility
if os.environ.get('VERCEL'):
    # For Vercel, use absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__, 
                static_folder=os.path.join(base_dir, 'static'),
                template_folder=os.path.join(base_dir, 'templates'))
else:
    app = Flask(__name__)

# Enable CORS for IoT integration if available
if CORS_AVAILABLE:
    CORS(app)
    print("CORS enabled for IoT integration")

# Database path - use /tmp for Vercel serverless functions
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'devices.db')
# For Vercel, use /tmp directory (writable in serverless functions)
if os.environ.get('VERCEL'):
    # Try /tmp first, fallback to current directory
    tmp_db = '/tmp/devices.db'
    try:
        # Test if /tmp is writable
        test_file = '/tmp/.test_write'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        DATABASE = tmp_db
    except (OSError, PermissionError):
        # If /tmp is not writable, use current directory
        DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'devices.db')

def init_db():
    """Initialize the database with the devices table and sample data."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            state TEXT NOT NULL,
            value INTEGER,
            light_effect TEXT DEFAULT 'natural',
            ac_mode TEXT DEFAULT 'cool',
            device_mode TEXT,
            battery_level INTEGER,
            power_consumption REAL
        )
    ''')
    
    # Check and add columns if they don't exist
    cursor.execute("PRAGMA table_info(devices)")
    columns = [column[1] for column in cursor.fetchall()]
    column_additions = {
        'light_effect': 'TEXT DEFAULT "natural"',
        'ac_mode': 'TEXT DEFAULT "cool"',
        'device_mode': 'TEXT',
        'battery_level': 'INTEGER',
        'power_consumption': 'REAL'
    }
    for col_name, col_def in column_additions.items():
        if col_name not in columns:
            cursor.execute(f'ALTER TABLE devices ADD COLUMN {col_name} {col_def}')
    
    # Insert sample data - all 15 devices
    sample_devices = [
        ('Light', 'light', 'off', None, 'natural', None, None, None, None),
        ('Fan', 'fan', 'off', 0, None, None, None, None, None),
        ('Temperature', 'sensor', 'on', 26, None, None, None, None, None),
        ('Air Conditioner', 'ac', 'off', 24, None, 'cool', None, None, None),
        ('Smart Lock', 'lock', 'locked', None, None, None, 'locked', None, None),
        ('Smart Blinds', 'blinds', 'closed', 0, None, None, None, None, None),
        ('Smart Plug', 'plug', 'off', None, None, None, None, None, 0.0),
        ('Security Camera', 'camera', 'off', None, None, None, 'idle', None, None),
        ('Smart Speaker', 'speaker', 'off', 50, None, None, 'bluetooth', None, None),
        ('Garage Door', 'garage', 'closed', None, None, None, 'closed', None, None),
        ('Smart Thermostat', 'thermostat', 'off', 22, None, None, 'auto', None, None),
        ('Smart Vacuum', 'vacuum', 'off', None, None, None, 'auto', 85, None),
        ('Smart Doorbell', 'doorbell', 'on', None, None, None, 'idle', 90, None),
        ('Smart Sprinkler', 'sprinkler', 'off', None, None, None, 'zone1', None, None),
        ('Motion Sensor', 'motion', 'on', None, None, None, None, None, None),
        ('Smart TV', 'tv', 'off', 30, None, None, 'hdmi1', None, None)
    ]
    
    # Check if devices already exist
    cursor.execute('SELECT COUNT(*) FROM devices')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO devices (name, type, state, value, light_effect, ac_mode, device_mode, battery_level, power_consumption)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_devices)
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_scenes_table():
    """Initialize scenes table for scene control."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            device_states TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default scenes if they don't exist
    cursor.execute('SELECT COUNT(*) FROM scenes')
    if cursor.fetchone()[0] == 0:
        default_scenes = [
            ('Good Morning', json.dumps({'1': {'state': 'on'}, '6': {'state': 'open', 'value': 100}, '4': {'state': 'off'}})),
            ('Movie Night', json.dumps({'1': {'state': 'on', 'light_effect': 'dim'}, '16': {'state': 'on'}, '4': {'state': 'off'}})),
            ('Away', json.dumps({'1': {'state': 'off'}, '2': {'state': 'off'}, '4': {'state': 'off'}, '5': {'state': 'locked'}, '8': {'state': 'on', 'device_mode': 'recording'}})),
            ('Sleep', json.dumps({'1': {'state': 'off'}, '2': {'state': 'off'}, '4': {'state': 'off'}, '6': {'state': 'closed', 'value': 0}}))
        ]
        cursor.executemany('INSERT INTO scenes (name, device_states) VALUES (?, ?)', default_scenes)
    
    conn.commit()
    conn.close()

def init_schedules_table():
    """Initialize schedules table for automation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            device_id INTEGER,
            action TEXT NOT NULL,
            time TEXT NOT NULL,
            days TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_energy_table():
    """Initialize energy monitoring table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS energy_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            power_consumption REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE):
    init_db()
    init_scenes_table()
    init_schedules_table()
    init_energy_table()
else:
    # Check and add columns if missing, add new devices
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns
        column_additions = {
            'light_effect': ('TEXT DEFAULT "natural"', 'UPDATE devices SET light_effect = "natural" WHERE type = "light"'),
            'ac_mode': ('TEXT DEFAULT "cool"', 'UPDATE devices SET ac_mode = "cool" WHERE type = "ac"'),
            'device_mode': ('TEXT', None),
            'battery_level': ('INTEGER', None),
            'power_consumption': ('REAL', None)
        }
        
        for col_name, (col_def, update_sql) in column_additions.items():
            if col_name not in columns:
                cursor.execute(f'ALTER TABLE devices ADD COLUMN {col_name} {col_def}')
                if update_sql:
                    cursor.execute(update_sql)
        
        # Add new devices if they don't exist
        new_devices = [
            ('Smart Lock', 'lock', 'locked', None, None, None, 'locked', None, None),
            ('Smart Blinds', 'blinds', 'closed', 0, None, None, None, None, None),
            ('Smart Plug', 'plug', 'off', None, None, None, None, None, 0.0),
            ('Security Camera', 'camera', 'off', None, None, None, 'idle', None, None),
            ('Smart Speaker', 'speaker', 'off', 50, None, None, 'bluetooth', None, None),
            ('Garage Door', 'garage', 'closed', None, None, None, 'closed', None, None),
            ('Smart Thermostat', 'thermostat', 'off', 22, None, None, 'auto', None, None),
            ('Smart Vacuum', 'vacuum', 'off', None, None, None, 'auto', 85, None),
            ('Smart Doorbell', 'doorbell', 'on', None, None, None, 'idle', 90, None),
            ('Smart Sprinkler', 'sprinkler', 'off', None, None, None, 'zone1', None, None),
            ('Motion Sensor', 'motion', 'on', None, None, None, None, None, None),
            ('Smart TV', 'tv', 'off', 30, None, None, 'hdmi1', None, None)
        ]
        
        for device in new_devices:
            cursor.execute('SELECT COUNT(*) FROM devices WHERE type = ?', (device[1],))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO devices (name, type, state, value, light_effect, ac_mode, device_mode, battery_level, power_consumption)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', device)
        
        conn.commit()
        conn.close()
        
        # Initialize additional tables
        init_scenes_table()
        init_schedules_table()
        init_energy_table()
    except Exception as e:
        print(f"Error updating database schema: {e}")

def device_to_dict(row):
    """Convert a database row to a dictionary."""
    # Safely get optional fields with defaults
    def safe_get(field, default=None):
        try:
            value = row[field]
            return value if value is not None else default
        except (KeyError, IndexError):
            return default
    
    light_effect = safe_get('light_effect', 'natural')
    ac_mode = safe_get('ac_mode', 'cool')
    device_mode = safe_get('device_mode')
    battery_level = safe_get('battery_level')
    power_consumption = safe_get('power_consumption')
    
    return {
        'id': row['id'],
        'name': row['name'],
        'type': row['type'],
        'state': row['state'],
        'value': row['value'],
        'light_effect': light_effect,
        'ac_mode': ac_mode,
        'device_mode': device_mode,
        'battery_level': battery_level,
        'power_consumption': power_consumption
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """
    Get all devices.
    
    Returns:
        JSON array of device objects with id, name, type, state, and value.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices ORDER BY id')
        devices = [device_to_dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(devices), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch devices', 'message': str(e)}), 500

@app.route('/api/device/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """
    Get a single device by ID.
    
    Args:
        device_id: Integer device ID
        
    Returns:
        JSON object with device details or error message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return jsonify({'error': 'Device not found'}), 404
        
        return jsonify(device_to_dict(row)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch device', 'message': str(e)}), 500

@app.route('/api/device/<int:device_id>/toggle', methods=['POST'])
def toggle_device(device_id):
    """
    Toggle device state (on/off).
    
    Args:
        device_id: Integer device ID
        
    Returns:
        JSON object with updated device details or error message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current device state
        cursor.execute('SELECT state FROM devices WHERE id = ?', (device_id,))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            return jsonify({'error': 'Device not found'}), 404
        
        current_state = row['state']
        new_state = 'on' if current_state == 'off' else 'off'
        
        # Update device state
        cursor.execute('UPDATE devices SET state = ? WHERE id = ?', (new_state, device_id))
        conn.commit()
        
        # Get updated device
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        updated_row = cursor.fetchone()
        conn.close()
        
        return jsonify(device_to_dict(updated_row)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to toggle device', 'message': str(e)}), 500

@app.route('/api/device/<int:device_id>/set_value', methods=['POST'])
def set_device_value(device_id):
    """
    Update device value (fan speed or sensor value).
    
    Args:
        device_id: Integer device ID
        
    Request Body:
        JSON object with 'value' key (integer)
        
    Returns:
        JSON object with updated device details or error message.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if data is None or 'value' not in data:
            return jsonify({'error': 'Value is required'}), 400
        
        value = data['value']
        
        # Validate value is an integer
        try:
            value = int(value)
        except (ValueError, TypeError):
            return jsonify({'error': 'Value must be an integer'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if device exists
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            return jsonify({'error': 'Device not found'}), 404
        
        # Update device value
        cursor.execute('UPDATE devices SET value = ? WHERE id = ?', (value, device_id))
        conn.commit()
        
        # Get updated device
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        updated_row = cursor.fetchone()
        conn.close()
        
        return jsonify(device_to_dict(updated_row)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update device value', 'message': str(e)}), 500

@app.route('/api/device/<int:device_id>/set_effect', methods=['POST'])
def set_light_effect(device_id):
    """
    Update light effect mode (vivid, natural, warm, cool, etc.).
    
    Args:
        device_id: Integer device ID
        
    Request Body:
        JSON object with 'effect' key (string)
        
    Returns:
        JSON object with updated device details or error message.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if data is None or 'effect' not in data:
            return jsonify({'error': 'Effect is required'}), 400
        
        effect = data['effect']
        valid_effects = ['vivid', 'natural', 'warm', 'cool', 'dim', 'bright']
        
        if effect not in valid_effects:
            return jsonify({'error': f'Invalid effect. Must be one of: {", ".join(valid_effects)}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure light_effect column exists
        cursor.execute("PRAGMA table_info(devices)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'light_effect' not in columns:
            cursor.execute('ALTER TABLE devices ADD COLUMN light_effect TEXT DEFAULT "natural"')
            conn.commit()
        
        # Check if device exists and is a light
        cursor.execute('SELECT * FROM devices WHERE id = ? AND type = ?', (device_id, 'light'))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            return jsonify({'error': 'Device not found or is not a light'}), 404
        
        # Update light effect
        cursor.execute('UPDATE devices SET light_effect = ? WHERE id = ?', (effect, device_id))
        conn.commit()
        
        # Get updated device
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        updated_row = cursor.fetchone()
        conn.close()
        
        return jsonify(device_to_dict(updated_row)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update light effect', 'message': str(e)}), 500

@app.route('/api/device/<int:device_id>/set_ac_mode', methods=['POST'])
def set_ac_mode(device_id):
    """
    Update AC mode (cool, heat, fan, auto).
    
    Args:
        device_id: Integer device ID
        
    Request Body:
        JSON object with 'mode' key (string)
        
    Returns:
        JSON object with updated device details or error message.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if data is None or 'mode' not in data:
            return jsonify({'error': 'Mode is required'}), 400
        
        mode = data['mode']
        valid_modes = ['cool', 'heat', 'fan', 'auto']
        
        if mode not in valid_modes:
            return jsonify({'error': f'Invalid mode. Must be one of: {", ".join(valid_modes)}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure ac_mode column exists
        cursor.execute("PRAGMA table_info(devices)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'ac_mode' not in columns:
            cursor.execute('ALTER TABLE devices ADD COLUMN ac_mode TEXT DEFAULT "cool"')
            conn.commit()
        
        # Check if device exists and is an AC
        cursor.execute('SELECT * FROM devices WHERE id = ? AND type = ?', (device_id, 'ac'))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            return jsonify({'error': 'Device not found or is not an air conditioner'}), 404
        
        # Update AC mode
        cursor.execute('UPDATE devices SET ac_mode = ? WHERE id = ?', (mode, device_id))
        conn.commit()
        
        # Get updated device
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        updated_row = cursor.fetchone()
        conn.close()
        
        return jsonify(device_to_dict(updated_row)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update AC mode', 'message': str(e)}), 500

@app.route('/api/device/<int:device_id>/set_mode', methods=['POST'])
def set_device_mode(device_id):
    """
    Update device mode (for various device types).
    
    Args:
        device_id: Integer device ID
        
    Request Body:
        JSON object with 'mode' key (string)
        
    Returns:
        JSON object with updated device details or error message.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if data is None or 'mode' not in data:
            return jsonify({'error': 'Mode is required'}), 400
        
        mode = data['mode']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure device_mode column exists
        cursor.execute("PRAGMA table_info(devices)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'device_mode' not in columns:
            cursor.execute('ALTER TABLE devices ADD COLUMN device_mode TEXT')
            conn.commit()
        
        # Check if device exists
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            return jsonify({'error': 'Device not found'}), 404
        
        # Update device mode
        cursor.execute('UPDATE devices SET device_mode = ? WHERE id = ?', (mode, device_id))
        conn.commit()
        
        # Get updated device
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        updated_row = cursor.fetchone()
        conn.close()
        
        return jsonify(device_to_dict(updated_row)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update device mode', 'message': str(e)}), 500

# Scene Control API
@app.route('/api/scenes', methods=['GET'])
def get_scenes():
    """Get all scenes."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scenes ORDER BY id')
        scenes = []
        for row in cursor.fetchall():
            scenes.append({
                'id': row['id'],
                'name': row['name'],
                'device_states': json.loads(row['device_states']),
                'created_at': row['created_at']
            })
        conn.close()
        return jsonify(scenes), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch scenes', 'message': str(e)}), 500

@app.route('/api/scenes/<int:scene_id>/activate', methods=['POST'])
def activate_scene(scene_id):
    """Activate a scene by applying all device states."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scenes WHERE id = ?', (scene_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Scene not found'}), 404
        
        device_states = json.loads(row['device_states'])
        results = []
        
        for device_id, states in device_states.items():
            try:
                # Update device state
                if 'state' in states:
                    current = cursor.execute('SELECT state FROM devices WHERE id = ?', (device_id,)).fetchone()
                    if current and current['state'] != states['state']:
                        cursor.execute('UPDATE devices SET state = ? WHERE id = ?', (states['state'], device_id))
                
                # Update device value
                if 'value' in states:
                    cursor.execute('UPDATE devices SET value = ? WHERE id = ?', (states['value'], device_id))
                
                # Update light effect
                if 'light_effect' in states:
                    cursor.execute('UPDATE devices SET light_effect = ? WHERE id = ?', (states['light_effect'], device_id))
                
                # Update device mode
                if 'device_mode' in states:
                    cursor.execute('UPDATE devices SET device_mode = ? WHERE id = ?', (states['device_mode'], device_id))
                
                results.append({'device_id': device_id, 'status': 'updated'})
            except Exception as e:
                results.append({'device_id': device_id, 'status': 'error', 'message': str(e)})
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Scene activated', 'results': results}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to activate scene', 'message': str(e)}), 500

# Schedules API
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all schedules."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schedules ORDER BY id')
        schedules = []
        for row in cursor.fetchall():
            schedules.append({
                'id': row['id'],
                'name': row['name'],
                'device_id': row['device_id'],
                'action': row['action'],
                'time': row['time'],
                'days': row['days'].split(',') if row['days'] else [],
                'enabled': bool(row['enabled'])
            })
        conn.close()
        return jsonify(schedules), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch schedules', 'message': str(e)}), 500

# Energy Monitoring API
@app.route('/api/energy', methods=['GET'])
def get_energy_data():
    """Get energy consumption data."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current power consumption for all devices
        cursor.execute('''
            SELECT d.id, d.name, d.power_consumption, d.state
            FROM devices d
            WHERE d.power_consumption IS NOT NULL
        ''')
        
        devices = []
        total_power = 0.0
        for row in cursor.fetchall():
            power = row['power_consumption'] if row['state'] == 'on' else 0.0
            devices.append({
                'id': row['id'],
                'name': row['name'],
                'power': power,
                'state': row['state']
            })
            total_power += power
        
        # Get daily energy usage (last 24 hours)
        cursor.execute('''
            SELECT SUM(power_consumption) as total_energy
            FROM energy_logs
            WHERE timestamp >= datetime('now', '-24 hours')
        ''')
        daily_energy = cursor.fetchone()['total_energy'] or 0.0
        
        conn.close()
        return jsonify({
            'devices': devices,
            'total_power': total_power,
            'daily_energy': daily_energy
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch energy data', 'message': str(e)}), 500

def update_temperature_sensor():
    """Background thread function to simulate real-time temperature updates."""
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get current temperature sensor value (device id=3, type='sensor')
            cursor.execute('SELECT value FROM devices WHERE id = 3 AND type = ?', ('sensor',))
            row = cursor.fetchone()
            
            if row and row['value'] is not None:
                current_temp = row['value']
                # Randomly vary temperature by ±1°C
                variation = random.randint(-1, 1)
                new_temp = current_temp + variation
                
                # Update temperature in database
                cursor.execute('UPDATE devices SET value = ? WHERE id = 3', (new_temp,))
                conn.commit()
                print(f"Temperature updated: {current_temp}°C -> {new_temp}°C")
            
            conn.close()
        except Exception as e:
            print(f"Error updating temperature: {e}")
        
        # Wait 5 seconds before next update
        time.sleep(5)

def start_temperature_thread():
    """Start the background thread for temperature updates."""
    temperature_thread = threading.Thread(target=update_temperature_sensor, daemon=True)
    temperature_thread.start()
    print("Temperature sensor background thread started")

# Start the background thread when the app initializes (only if not in Vercel)
if not os.environ.get('VERCEL'):
    start_temperature_thread()

# Catch-all route for SPA - must be after all other routes
@app.route('/<path:path>')
def catch_all(path):
    # Don't catch API routes - let them return 404 naturally
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    # For everything else (non-API), serve the index page
    return render_template('index.html')

# Export app for Vercel
if __name__ == '__main__':
    app.run(debug=True)
else:
    # For Vercel serverless functions
    handler = app

