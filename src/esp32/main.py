"""main.py for ESP32 with the following functionality:
* Connect to an MQTT broker/server
* Run an endless loop in which a BLE scan is performed, and the results are published.
"""

# print("Running main.py")

# global imports
import time
import machine
import ubinascii

# local imports
import ble_discovery
from umqttsimple import MQTTClient

# Constants
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = "mqtt.eclipseprojects.io"
main_topic = b"hvable"

# last_message = 0
# message_interval = 5
# counter = 0

def sub_cb(topic, msg):
    """Subscriber callback"""
    print((topic, msg))


def connect_and_subscribe(clnt_id, server, topic):
    """Connect to the MQTT server and subscribe to the given topic"""
    # global client_id, mqtt_server, topic
    print("Connecting", clnt_id, "to", server)
    clnt = MQTTClient(clnt_id, server)
    clnt.set_callback(sub_cb)
    clnt.connect()
    print("Client connected")
    clnt.subscribe(topic)
    print("subscribed to", topic)
    print(
        'Connected to MQTT broker "%s", subscribed to topic "%s"'
        % (server, topic)
    )
    return clnt


def restart():
    """Restart this (ESP32) device"""
    print("Failed to connect to MQTT broker. Restarting and reconnecting...")
    time.sleep(10)
    machine.reset()


try:
    client = connect_and_subscribe(client_id, mqtt_server, main_topic)
except OSError as e:
    restart()


while True:

    scantime = 30
    s = "BLE SCANNING for %s seconds" % scantime
    client.publish(main_topic, s)

    list_of_devices = ble_discovery.scan(scantime)  # Scan for xx seconds
    print("End of BLE Scan")

    client.publish(main_topic, "BLE SCAN RESULTS:")
    for dev in list_of_devices:
        try:
            client.publish(main_topic, dev)
        except OSError as e:
            restart()
