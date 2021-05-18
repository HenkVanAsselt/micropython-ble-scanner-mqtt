"""BLE discovery functions
"""

# Global imports
import time
import binascii
import bluetooth
from micropython import const
from ble_advertising import decode_services, decode_name


list_of_devices = []

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_COMPLETE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)


def bt_irq(event, data):
    """React on a Bluetooth IRQ event.
    """

    # print("bt_irq", event, data)
    if event == _IRQ_CENTRAL_CONNECT:
        # The central device is already connected to this peripheral device
        conn_handle, addr_type, addr = data
    elif event == _IRQ_CENTRAL_DISCONNECT:
        # The central device has been disconnected from this peripheral device
        conn_handle, addr_type, addr = data
    elif event == _IRQ_GATTS_WRITE:
        # The central device has written this feature or descriptor
        conn_handle, attr_handle = data
    elif event == _IRQ_GATTS_READ_REQUEST:
        # The central device has issued a read request. Note: This is a hardware IRQ
        # Return NONE to reject the read operation
        # Note: This event does not support ESP32.
        conn_handle, attr_handle = data
    elif event == _IRQ_SCAN_RESULT:
        # The result of a scan
        # print("Intermediate scan result")
        # print(data)
        addr_type, addr, connectable, rssi, adv_data = data
        # Note: addr buffer is owned by caller so need to copy it.

        # print("Addr = ", bytes(addr))
        # name = decode_name(adv_data) or "?"
        # print("Name = ", name)
        # srv = decode_services(adv_data)
        # print("Services =", srv)

        name = decode_name(adv_data) or "?"
        srv = decode_services(adv_data)
        addr_str = str(binascii.hexlify(addr, ":"))
        print("name", name, "addr", addr_str, "RSSI", rssi, "services", srv)

        if addr_str not in list_of_devices:
            print("Adding", addr_str)
            list_of_devices.append(addr_str)
        else:
            print(addr_str, "is already in the list")

    elif event == _IRQ_SCAN_COMPLETE:
        # Scan duration has been completed or manually stopped
        print("Scan complete.")
        pass
    elif event == _IRQ_PERIPHERAL_CONNECT:
        #  gap_connect() connected
        conn_handle, addr_type, addr = data
    elif event == _IRQ_PERIPHERAL_DISCONNECT:
        # Connected peripherals are disconnected
        conn_handle, addr_type, addr = data
    elif event == _IRQ_GATTC_SERVICE_RESULT:
        # Call gattc_discover_services() for each service found
        conn_handle, start_handle, end_handle, uuid = data
    elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
        # Call gattc_discover_services() every feature found
        conn_handle, def_handle, value_handle, properties, uuid = data
    elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
        # Call gattc_discover_descriptors() every descriptor found
        conn_handle, dsc_handle, uuid = data
    elif event == _IRQ_GATTC_READ_RESULT:
        # gattc_read() completed
        conn_handle, value_handle, char_data = data
    elif event == _IRQ_GATTC_WRITE_STATUS:
        # gattc_write() completed
        conn_handle, value_handle, status = data
    elif event == _IRQ_GATTC_NOTIFY:
        # The peripheral device has issued a notification request
        conn_handle, value_handle, notify_data = data
    elif event == _IRQ_GATTC_INDICATE:
        # Peripheral equipment issues instructions
        conn_handle, value_handle, notify_data = data


def scan(scantime=60):
    """Perform the BLE scan for 'scantime' seconds."""

    bt = bluetooth.BLE()
    bt.active(True)
    bt.irq(bt_irq)
    print("\nStarting BLE scan for", scantime, "seconds")
    bt.gap_scan(0)  # Scan "forever"
    time.sleep(scantime)  # Wait for xx seconds, scanning happens in background
    bt.gap_scan(None)  # Stop the scanninbg

    for device in list_of_devices:
        print(device)

    return list_of_devices

if __name__ == "__main__":
    pass