import serial
import struct

ser = serial.Serial("COM3", 115200, timeout=1)

packet_format = "<5f"
packet_size = struct.calcsize(packet_format)
header = b"\xAA\x55"

while True:
    # Look for header
    if ser.read(1) == header[0:1] and ser.read(1) == header[1:2]:
            # Read the packet payload
            data = ser.read(packet_size)
            if len(data) == packet_size:
                values = list(struct.unpack(packet_format, data))
                print("values:", values)