import pycom
from SI7006A20 import SI7006A20
from MPL3115A2 import MPL3115A2
from Pysense import Pysense
from network import WLAN 
from mqtt import MQTTClient
import time
import ussl as ssl

ps = Pysense()
sensor = SI7006A20(ps)
sensor2 = MPL3115A2(ps)
pycom.heartbeat(False)

AIO = False
WLAN_PASSWD = 'TBD'
SSID = 'TBD'

MQTT_BROKER = 'broker_IP@' 
MQTT_TOPIC = 'jjpycomtest/TEMP'
MQTT_TOPIC2 = 'jjpycomtest/PRESSURE'
MQTT_TOPIC3 = 'jjpycomtest/HUMID'


net = WLAN(mode=WLAN.STA)
net.connect(ssid=SSID, auth=(WLAN.WPA2, WLAN_PASSWD))

while not net.isconnected():
    print('Trying to connect to network...')
    time.sleep(1)

print("Connected!")
print(net.ifconfig())

def subscribe_callback(topic, message):
    print("Received {} on topic {}".format(message.decode('utf-8'), topic.decode('utf-8')))

print("Creating MQTT client...")

PARAMS = {'keyfile': 'cert/device.key', 
            'certfile': 'cert/device.pem', 
            'cert_reqs': ssl.CERT_REQUIRED, 
            'ca_certs': 'cert/my-ca.pem'}

client = MQTTClient("device", MQTT_BROKER, port=1883, ssl=True, ssl_params = PARAMS)

client.set_callback(subscribe_callback)

print("Connecting to MQTT broker...")
try:
    client.connect()
    client.subscribe(topic=MQTT_TOPIC)
    client.subscribe(topic=MQTT_TOPIC2)
    client.subscribe(topic=MQTT_TOPIC3)
    print("Done")
    CONNECT = True
except OSError:
    print("Cannot connect to MQTT broker...")
    CONNECT = False

while CONNECT:
    temp = sensor.temperature()
    humid_ambient = sensor.humid_ambient(temp)
    pressure = sensor2.pressure()

    print("Sending Data to MQTT broker")

    client.publish(topic=MQTT_TOPIC, msg="{:.1f}".format(temp))
    client.publish(topic=MQTT_TOPIC2, msg="{:.2f}".format(pressure))
    client.publish(topic=MQTT_TOPIC3, msg="{:.1f}".format(humid_ambient))

    #Does not work yet... It worked with username/password but not with Cert...
    #client.check_msg()

    pycom.rgbled(0xF0000F)
    time.sleep(1)

print("Aborting now!")