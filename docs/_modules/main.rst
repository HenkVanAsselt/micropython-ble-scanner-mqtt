:mod:`main` -- ESP32 boot main
==============================

.. module:: main
   :synopsis: This module is run when the ESP32 is booting, after `boot.py`

This module will:

* Connect to an MQTT broker/server
* Run an endless loop in which a BLE scan is performed, and the results are published.
