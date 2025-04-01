import paho.mqtt.client as mqtt
import json
import time

id = '985e346e-15d7-42c7-9311-6d1fc79fee61'  # Your device ID
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'  # Command topic added
client_name = id + '_server'

def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print(f"Message received: {payload}")
        
        # Added command logic (using temperature instead of light)
        command = {'led_on': payload['temperature'] > 25}
        print(f"Sending command: {command}")
        client.publish(server_command_topic, json.dumps(command))
        
    except Exception as e:
        print(f"Error processing message: {e}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_name)
client.connect("test.mosquitto.org")
client.subscribe(client_telemetry_topic)
client.on_message = handle_telemetry

print("Server started. Waiting for temperature data...")
client.loop_forever()