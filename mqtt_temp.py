# Import required libraries.
# Note: Fixed typo in 'from' and corrected library names
from gpiozero import LED          # For controlling the LED
from w1thermsensor import W1ThermSensor  # For DS18B20 temperature sensor
import paho.mqtt.client as mqtt   # For MQTT communication
import time                       # For sleep/delays
import json                       # For JSON data formatting

# Hardware initialization
red = LED(17)                     # Red LED connected to GPIO pin 17
sensor = W1ThermSensor()          # DS18B20 temperature sensor

# MQTT configuration
device_id = '985e346e-15d7-42c7-9311-6d1fc79fee61'  # Unique device identifier
client_name = device_id + '_client'  # Client identifier for MQTT broker
telemetry_topic = f"{device_id}/telemetry"  # Topic for publishing temperature data

# Set up MQTT client and connect to broker
mqtt_client = mqtt.Client(client_name)  # Create MQTT client instance
mqtt_client.connect('test.mosquitto.org')  # Connect to public MQTT broker
mqtt_client.loop_start()              # Start network loop in background thread

try:
    # Main program loop
    while True:
        # Read current temperature from sensor
        temp = sensor.get_temperature()
        print(f"Temperature: {temp}°C")
        
        # Control LED based on temperature threshold (25°C)
        if temp > 25:
            red.on()    # Turn LED on if temperature > 25°C
        else:
            red.off()   # Turn LED off if temperature <= 25°C
        
        # Create and publish telemetry message
        telemetry = json.dumps({'temperature': temp})  # Convert to JSON
        mqtt_client.publish(telemetry_topic, telemetry)  # Publish to broker
        print(f"Published: {telemetry}")
        
        time.sleep(3)  # Wait 3 seconds before next reading

# Handle keyboard interrupt (Ctrl+C) for graceful shutdown
except KeyboardInterrupt:
    print("\nShutting down...")
    red.off()               # Turn off LED
    mqtt_client.disconnect()  # Disconnect from MQTT broker
