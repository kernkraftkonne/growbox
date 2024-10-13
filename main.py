import network
import time
import ubinascii
import json
from machine import Pin
import dht
import utime
from umqtt.simple import MQTTClient

# Load Wi-Fi and MQTT configuration from config.json
def load_config():
    with open('config.json') as f:
        return json.load(f)

config = load_config()

# Configuration details for Wi-Fi and MQTT from the config.json file
SSID = config['SSID']
PASSWORD = config['PASSWORD']
MQTT_BROKER = config['MQTT_BROKER']
MQTT_PORT = config['MQTT_PORT']
MQTT_USER = config['MQTT_USER']
MQTT_PASSWORD = config['MQTT_PASSWORD']

# Initialize the DHT22 sensor
dht_sensor = dht.DHT22(Pin(27))

# LED setup for indicating status
led = Pin(2, Pin.OUT)

# Connect to Wi-Fi
def connect_wifi(ssid, password):
    print(f"Connecting to Wi-Fi SSID: {ssid}")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
        print("Waiting for connection...")
    print("Connected to Wi-Fi", wlan.ifconfig())
    led.on()  # Turn LED on once connected to Wi-Fi

# Connect to MQTT Broker
def connect_mqtt():
    print(f"Connecting to MQTT Broker: {MQTT_BROKER}")
    client = MQTTClient(ubinascii.hexlify(machine.unique_id()), MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD, port=MQTT_PORT)
    client.connect()
    print("Connected to MQTT Broker")
    return client

# Send message via MQTT
def send_mqtt(client, topic, message):
    print(f"Publishing {message} to topic {topic}")
    client.publish(topic, message)

# Disconnect from MQTT Broker
def disconnect_mqtt(client):
    client.disconnect()

# Read temperature and humidity from DHT22 sensor
def read_sensor_dht22():
    """Read temperature and humidity from the DHT22 sensor."""
    attempts = 0
    while attempts < 5:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()  # Temperature in Celsius
            hum = dht_sensor.humidity()  # Relative humidity in percentage
            print(f"Temperature: {temp:.1f} °C, Humidity: {hum:.1f}%")
            return temp, hum
        except OSError as e:
            # Handle failed sensor readings
            print("Failed to read sensor:", e)
            attempts += 1
            time.sleep(2)  # Wait before retrying
    return None, None

# Main function
def main():
    connect_wifi(SSID, PASSWORD)  # Connect to Wi-Fi
    mqtt_client = connect_mqtt()  # Connect to MQTT

    while True:
        time.sleep(2)
        temperature, humidity = read_sensor_dht22()

        # Only send MQTT messages for temperature and humidity
        if temperature is not None and humidity is not None:
            send_mqtt(mqtt_client, "home/temperature", str(temperature))
            send_mqtt(mqtt_client, "home/humidity", str(humidity))
        
        time.sleep(10)
        
    disconnect_mqtt(mqtt_client)

main()  # Start the main function
