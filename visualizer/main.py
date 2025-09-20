# # visualize serial output
# from multiprocessing import Process, Lock

# import serial
# from serial.tools import list_ports

# from matplotlib import pyplot as plt
# from matplotlib.animation import FuncAnimation

# import numpy as np
# import re

# import time

# pico_devices = {}
# # pico_serial = {}

# com_updated = False

# def read_serial(s: serial.Serial):
#     return s.read_until("\n")

# def get_all_pico_com():
#     pi_devices = {}

#     RP_VID="2E8A"
#     for port, desc, hwid in sorted(list_ports.comports()):
#         if RP_VID.lower() in hwid.lower():
#             pi_devices[port] = (desc, hwid)
    
#     return pi_devices

# def notify_new_device():
#     return com_updated

# s = serial.Serial(port="COM3", baudrate=115200)

# def update_port():
#     # sleep_ms = 1
#     # time.sleep(sleep_ms/1000)

#     new_pico_devices = get_all_pico_com()
#     add_devices = new_pico_devices.keys() - pico_devices.keys()
#     rem_devices = pico_devices.keys() - new_pico_devices.keys()

#     for dev in pico_devices.keys():
#         pico_devices[dev][1] = read_serial(s)

#     print(pico_devices)

#     com_updated_flag = False                                        # might cause issues?
#     if len(add_devices) <= 0 and len(rem_devices) <= 0: return
#     com_updated_flag = True

#     for dev in add_devices:
#         # s = serial.Serial(port=dev, baudrate=115200)
#         p = Process(target=read_serial,args=(s, dev))
#         pico_devices[dev] = (p, None)
    
#     for dev in rem_devices:
#         # p = pico_devices[dev][0]
#         # p.kill()
#         pico_devices.pop(dev)

#     print(pico_devices)

# if __name__ == "__main__":
#     while(True):
#         update_port()
#     # proc1 = update_port()

# # def read_msg(s: serial):
# #     pico_devices[s.] = s.read_until(b'\n').decode().rstrip()

# # create thread pool and thread safe variable

# # s = serial.Serial(port='/dev/ttyACM0',
# #                        baudrate=115200
# #                         )

# # s = serial.Serial(port='COM3',
# #                        baudrate=115200
# #                  )

# # while(True):
# #     #print(serial.read().decode(), end='')
# #     s = serial.read_until(b'\n').decode().rstrip()
# #     voltage = float(re.search(r"voltage:\s*([0-9.]+)", s).group(1))
# #     diff = 3.3 - voltage
# #     # print(diff)

# # # X labels
# # labels = ["FSR1", "FSR2", "FSR3", "FSR4"]

# # # Initial bar heights
# # y = np.random.uniform(0, 10, size=4)

# # fig, ax = plt.subplots()
# # bars = ax.bar(labels, y, color="skyblue")

# # # Set limits
# # ax.set_ylim(0, 1)
# # ax.set_ylabel("Value")
# # ax.set_title("Animated Bar Graph")

# # # Update function for animation
# # def update(frame):
# #     # New random values between 0 and 10
# #     # new_y = np.random.uniform(0, 10, size=4)

# #     s = serial.read_until(b'\n').decode().rstrip()
# #     voltage = float(re.search(r"voltage:\s*([0-9.]+)", s).group(1))
# #     diff = 3.3 - voltage

# #     new_y = (diff, 0, 0, 0)
# #     for bar, h in zip(bars, new_y):
# #         bar.set_height(h)

# #     return bars

# # # Animate
# # ani = FuncAnimation(fig, update, frames=None, interval=1, blit=False)

# # plt.show()

import serial
import struct
import time
ser = serial.Serial("COM3", 115200, timeout=1)

# Struct format:
# <   = little endian
# 5f  = 5 floats
packet_format = "<5f"
packet_size = struct.calcsize(packet_format)
header = b"\xAA\x55"

while True:
    # Look for header
    if ser.read(1) == header[0:1]:
        if ser.read(1) == header[1:2]:
            # Read the packet payload
            data = ser.read(packet_size)
            if len(data) == packet_size:
                values = list(struct.unpack(packet_format, data))
                print("values:", values)