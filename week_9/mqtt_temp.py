from gpiozero import LED
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt
import time
import json

# Hardware setup
red = LED(17)
sensor = W1ThermSensor()

# MQTT setup
id = '985e346e-15d7-42c7-9311-6d1fc79fee61'  # e.g., '67e6ce98-537b...' from GUIDGen
client_name = id + '_client'
telemetry_topic = f"{id}/telemetry"

# Connect to broker
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

try:
    while True:
        temp = sensor.get_temperature()
        print(f"Temperature: {temp}°C")
        
        if temp > 25:
            red.on()
        else:
            red.off()

        telemetry = json.dumps({'temperature': temp})
	mqtt_client.publish(telemetry_topic, telemetry)
	print(f"Published: {telemetry}")        
	time.sleep(3)
except KeyboardInterrupt:
    red.off()
    mqtt_client.disconnect()
