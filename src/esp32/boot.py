"""boot.py for ESP32 with the following functionality:
* run garbage collector
* connect to WiFi
* start WebREPL
"""


# Standard imports
import gc
import network
import esp
import webrepl

# Local imports
import config


print("Running boot.py")
gc.collect()
esp.osdebug(None)


def do_connect(ssid, psk):
    """Connect wifi to the given ssid and psk key"""
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect(ssid, psk)
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ifconfig())


# Attempt to connect to WiFi network
# The SSID and PSK are stored in the file config.py
do_connect(config.SSID, config.PSK)

# Start WEBREPL
webrepl.start()


