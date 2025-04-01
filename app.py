"""
MQTT Server for Temperature Monitoring System
Handles incoming temperature data from IoT devices and sends LED control commands
back based on temperature thresholds. Uses the public test.mosquitto.org broker.
"""

import paho.mqtt.client as mqtt  # MQTT client library
import json  # For JSON data parsing
import time  # For time-related functions (though not currently used)

# Configuration Constants
# Unique device identifier - should match the ID used in the IoT device code
id = '985e346e-15d7-42c7-9311-6d1fc79fee61'

# MQTT Topic Configuration
client_telemetry_topic = id + '/telemetry'  # Topic for receiving temperature data from devices
server_command_topic = id + '/commands'     # Topic for sending commands to devices
client_name = id + '_server'               # Unique client name for this server

def handle_telemetry(client, userdata, message):
    """
    Callback function that handles incoming temperature data messages.
    Processes the telemetry data and sends appropriate LED control commands.
    
    Args:
        client: The MQTT client instance
        userdata: Any user-defined data passed to the callback
        message: The received MQTT message containing temperature data
    """
    try:
        # Decode and parse the JSON payload from the message
        payload = json.loads(message.payload.decode())
        print(f"Message received: {payload}")
        
        # Create command based on temperature threshold (25°C)
        # If temperature > 25°C, turn LED on; otherwise turn it off
        command = {'led_on': payload['temperature'] > 25}
        print(f"Sending command: {command}")
        
        # Publish the command back to the device
        client.publish(server_command_topic, json.dumps(command))
        
    except json.JSONDecodeError:
        # Handle case where message isn't valid JSON
        print("[ERROR] Failed to decode JSON payload - message format invalid")
    except KeyError:
        # Handle case where temperature field is missing
        print("[ERROR] Invalid payload: 'temperature' field missing")
    except Exception as e:
        # Catch-all for any other unexpected errors
        print(f"[ERROR] Unexpected error processing message: {e}")

# Create MQTT client instance with:
# - Callback API Version 2 (newest)
# - Unique client name
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_name)

# Connect to the public MQTT broker
client.connect("test.mosquitto.org")

# Subscribe to the telemetry topic to receive temperature data
client.subscribe(client_telemetry_topic)

# Set the callback function for incoming messages
client.on_message = handle_telemetry

print("Server started. Waiting for temperature data...")

# Start the network loop that processes MQTT messages
# This will run indefinitely until interrupted
client.loop_forever()