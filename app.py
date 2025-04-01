"""
MQTT Server for Temperature Monitoring System
Handles incoming temperature data and sends LED control commands
"""

import paho.mqtt.client as mqtt
import json
import time
import sys
import signal

# Configuration Constants
DEVICE_ID = '985e346e-15d7-42c7-9311-6d1fc79fee61'  # Unique device identifier
BROKER_URL = "test.mosquitto.org"  # Public MQTT broker
TEMPERATURE_THRESHOLD = 25  # Temperature threshold for LED control (in °C)

# Topic Configuration
client_telemetry_topic = f"{DEVICE_ID}/telemetry"  # Incoming temperature data
server_command_topic = f"{DEVICE_ID}/commands"  # Outgoing LED commands
client_name = f"{DEVICE_ID}_server"  # Client identifier

# Global client reference for graceful shutdown
mqtt_client = None

def handle_telemetry(client, userdata, message):
    """
    Callback for incoming temperature data
    Args:
        client: MQTT client instance
        userdata: User-defined data
        message: Received message containing temperature data
    """
    try:
        payload = json.loads(message.payload.decode())
        print(f"[TELEMETRY] Received: {payload}")
        
        # Validate payload structure
        if 'temperature' not in payload:
            raise ValueError("Invalid payload: 'temperature' field missing")
            
        temperature = float(payload['temperature'])
        
        # Create and send LED control command
        command = {'led_on': temperature > TEMPERATURE_THRESHOLD}
        print(f"[COMMAND] Sending: {command}")
        
        # QoS=1 for at-least-once delivery
        client.publish(server_command_topic, json.dumps(command), qos=1)
        
    except json.JSONDecodeError:
        print("[ERROR] Failed to decode JSON payload")
    except ValueError as ve:
        print(f"[ERROR] {str(ve)}")
    except Exception as e:
        print(f"[ERROR] Unexpected error processing message: {str(e)}")

def setup_mqtt_client():
    """
    Configure and connect MQTT client
    Returns:
        Configured MQTT client instance
    """
    try:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_name,
            clean_session=False
        )
        
        # Set Last Will and Testament (notify if server disconnects unexpectedly)
        client.will_set(
            server_command_topic,
            payload=json.dumps({'server_status': 'offline'}),
            qos=1,
            retain=True
        )
        
        # Connection callbacks
        client.on_connect = lambda c, userdata, flags, rc: (
            print(f"[STATUS] Connected to broker with result code {rc}")
            if rc == 0 else
            print(f"[ERROR] Connection failed with code {rc}")
        )
        
        client.on_disconnect = lambda c, userdata, rc: (
            print("[STATUS] Disconnected from broker") 
            if rc == 0 else
            print(f"[ERROR] Unexpected disconnection (code: {rc})")
        )
        
        client.connect(BROKER_URL, keepalive=60)
        client.subscribe(client_telemetry_topic, qos=1)
        client.on_message = handle_telemetry
        
        return client
        
    except Exception as e:
        print(f"[FATAL] Failed to initialize MQTT client: {str(e)}")
        sys.exit(1)

def graceful_shutdown(signum, frame):
    """
    Handle system signals for clean shutdown
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    print("\n[SHUTDOWN] Initiating graceful shutdown...")
    if mqtt_client:
        mqtt_client.disconnect()
    sys.exit(0)

def main():
    """
    Main application entry point
    """
    global mqtt_client
    
    # Register signal handlers
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    print("[STATUS] Starting temperature monitoring server...")
    
    try:
        # Initialize and start MQTT client
        mqtt_client = setup_mqtt_client()
        print(f"[STATUS] Subscribed to: {client_telemetry_topic}")
        print(f"[STATUS] Publishing to: {server_command_topic}")
        print("[STATUS] Server ready. Waiting for temperature data...")
        
        # Start network loop
        mqtt_client.loop_forever(retry_first_connection=True)
        
    except KeyboardInterrupt:
        graceful_shutdown(signal.SIGINT, None)
    except Exception as e:
        print(f"[FATAL] Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()