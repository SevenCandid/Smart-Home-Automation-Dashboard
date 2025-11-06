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
from flask import Flask, render_template, jsonify, request

# Try to import CORS, make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("Warning: flask_cors not installed. CORS disabled. Install with: pip install flask-cors")

app = Flask(__name__)

# Enable CORS for IoT integration if available
if CORS_AVAILABLE:
    CORS(app)
    print("CORS enabled for IoT integration")

DATABASE = 'devices.db'

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
            light_effect TEXT DEFAULT 'natural'
        )
    ''')
    
    # Check if light_effect column exists, if not add it
    cursor.execute("PRAGMA table_info(devices)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'light_effect' not in columns:
        cursor.execute('ALTER TABLE devices ADD COLUMN light_effect TEXT DEFAULT "natural"')
    
    # Insert sample data
    sample_devices = [
        ('Light', 'light', 'off', None, 'natural'),
        ('Fan', 'fan', 'off', 0, None),
        ('Temperature', 'sensor', 'on', 26, None)
    ]
    
    # Check if devices already exist
    cursor.execute('SELECT COUNT(*) FROM devices')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO devices (name, type, state, value, light_effect)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_devices)
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE):
    init_db()
else:
    # Check if light_effect column exists, add if missing
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'light_effect' not in columns:
            cursor.execute('ALTER TABLE devices ADD COLUMN light_effect TEXT DEFAULT "natural"')
            # Update existing light device
            cursor.execute('UPDATE devices SET light_effect = "natural" WHERE type = "light"')
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating database schema: {e}")

def device_to_dict(row):
    """Convert a database row to a dictionary."""
    # Safely get light_effect, default to 'natural' if not present
    light_effect = 'natural'
    try:
        # Try to get light_effect from row
        light_effect = row['light_effect']
        if light_effect is None:
            light_effect = 'natural'
    except (KeyError, IndexError):
        # Column doesn't exist, use default
        light_effect = 'natural'
    
    return {
        'id': row['id'],
        'name': row['name'],
        'type': row['type'],
        'state': row['state'],
        'value': row['value'],
        'light_effect': light_effect
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

# Start the background thread when the app initializes
start_temperature_thread()

if __name__ == '__main__':
    app.run(debug=True)

