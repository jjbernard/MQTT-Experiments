import paho.mqtt.client as mqtt
import time
import requests
import ssl
import datetime
import pytz
import pprint

MQTT_BROKER = 'broker_IP@'
MQTT_TOPIC = 'topic/TEMP'
MQTT_TOPIC2 = 'topic/PRESSURE'
MQTT_TOPIC3 = 'topic/HUMID'

URL_TEMP = "url_for_rest_api_server/TEMP/"
URL_PRES = "url_for_rest_api_server/PRESSURE/"
URL_HUMID = "url_for_rest_api_server/HUMID/"

TOPIC_DATA = {
    MQTT_TOPIC:
        {"name": "Temperature",
         "id": "101",
         "url": URL_TEMP},
    MQTT_TOPIC2:
        {"name": "Pressure",
         'id': "102",
         "url": URL_PRES},
    MQTT_TOPIC3:
        {"name": "Humidity",
         "id": "103",
         "url": URL_HUMID}
}


# def callback_on_connect(client, userdata, flags, rc):
#     print(f'Connected with result code {rc} and flags {flags}')
#     client.subscribe()

def callback_on_message(client, userdata, msg):
    print(f"In topic: {msg.topic}, received payload {msg.payload.decode('utf-8')}.")

    data = prepare_data(msg)

    post_data(data, TOPIC_DATA.get(msg.topic).get('url'))


def prepare_data(msg):
    date = datetime.datetime.now().astimezone(tz=pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {"id": TOPIC_DATA.get(msg.topic).get("id"),
            "name": TOPIC_DATA.get(msg.topic).get("name"),
            "values": [
                {"date_time": date,
                 "value": float(msg.payload.decode('utf-8'))}
            ]}
    return data


def post_data(data, url):
    r = requests.put(url, json=data)
    r.raise_for_status()


if __name__ == '__main__':
    print('Creating Client')
    client = mqtt.Client("Python Client")
    client.on_message = callback_on_message
    print('Connecting to broker...')
    client.tls_set(ca_certs="certs/my-ca.pem", certfile="certs/client.pem",
                   keyfile="certs/client.key", cert_reqs=ssl.CERT_REQUIRED)

    # to be removed at a later stage!
    client.tls_insecure_set(True)

    # Connect to broker
    client.connect(MQTT_BROKER)

    # Start loop and subscribe to topics
    client.loop_start()
    print(f'Subscribing to topic {MQTT_TOPIC}, {MQTT_TOPIC2} and {MQTT_TOPIC3}')
    client.subscribe(MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC2)
    client.subscribe(MQTT_TOPIC3)

    # Go for 1000 iterations
    i = 0
    while i < 1000:
        time.sleep(1)
        i += 1

    client.loop_stop()
    print('Exiting...')
