ESP32 BLE Scanner with MQTT publisher
=====================================

This project contains an experiment with the following idea:

* Use an Espressif ESP32 microcontroller as an BLE device scanner, using micropython.
* Publish the results over WiFi with MQTT on a public MQTT broker/server.
* Retrieve the results on a PC running an MQTT client/subscriber.
* The client on the PC is written in Python, and as an experiment, 
  the same functionality will also be written in Rust later.
  
ESP32 files
-----------
* `boot.py` Runs after each boot of the ESP32.
* `main.py` The main function.
* `ble_discovery.py` Contains the BLE scanner.
* `ble_advertising.py` Contains supporting BLE functions.
* `umqttsimple.py` Contains the neccessary MQTT functions.

PC files
--------
* `mqtt_blescan_subscriber.py` An MQTT subscriber, written in Python

MQTT broker/Server
------------------
For no specific reasons, the free `mqtt.eclipseprojects.io` server will be used.
The MQTT topic is `hvable`

