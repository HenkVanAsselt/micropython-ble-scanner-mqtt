"""PC MQTT client which will get BLE scan results messages from an ESP32
"""

# Global imports
import sys
import time
import argparse

# 3rd party imports
import paho.mqtt.client as mqtt

# Runtime in seconds. 0 means indefinitely.
runtime = 0

# Define the MQTT broker/server and the topic
mqttBroker = "mqtt.eclipseprojects.io"
topic = "hvable"


# -----------------------------------------------------------------------------
def on_message(client, userdata, message):
    """Callback function if an MQTT message is received."""

    # print("received message: ", str(message.payload.decode("utf-8")))
    print(f"{message.payload=}")


# -----------------------------------------------------------------------------
def main():
    """Main function"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--timeout",
        help='Set the timeout of this program. 0 means run indefinitely',
        default=0,
    )

    args = parser.parse_args()
    # print(f"{args=}")       # Debug message

    runtime = int(args.timeout)

    client = mqtt.Client("hva_pc")
    client.connect(mqttBroker)

    # If a specific runtime was given, start the client loop here.
    if runtime:
        client.loop_start()

    # Subscribe to the topic and set the message received callback function.
    client.subscribe(topic)
    print(f"subscribed on broker \"{mqttBroker}\", topic \"{topic}\"")
    client.on_message = on_message  # Define the callback function.

    # Start one of 2 loop possibilities, depending on the given runtime
    if runtime:
        # If a specific runtime was given...
        print(f"This client will run for {runtime} seconds.")
        time.sleep(runtime)
        client.loop_stop()
        print(f"Client loop stopped after {runtime} seconds.")
    else:
        # No specific runtime was given, loop forever.
        print("This client will loop forever")
        client.loop_forever()


# =============================================================================
if __name__ == "__main__":

    sys.exit(main())
