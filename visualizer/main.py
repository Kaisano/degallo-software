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

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import serial
import struct
from enum import Enum

class SERIAL_STATES(Enum):
    CONNECT=0,
    SYNC=1,
    PARSE=2

class app_t():
    def __init__(self):        
        # Struct format:
        # <   = little endian
        # 5f  = 5 floats
        self.__packet_format = "<5f"
        self.__packet_size = struct.calcsize(self.__packet_format)

        self.__key1 = b"\xAA"
        self.__key2 = b"\x55"

        self.ser: serial.Serial
        self.state = SERIAL_STATES.CONNECT
        self.pad_data = list()
    
    def connect(self, port: str, baudrate: int):
        self.ser = serial.Serial(port=port, baudrate=baudrate)
    
    def read_packet(self):
        data = self.ser.read(self.__packet_size)
        if len(data) == self.__packet_size:
            self.pad_data = list(struct.unpack(self.__packet_format, data))
    
    def sync(self):
        return \
            self.ser.read() == self.__key1 and \
            self.ser.read() == self.__key2
        

def app_loop(app: app_t):
    match app.state:
        case SERIAL_STATES.CONNECT:
            try:
                app.connect("COM3", 115200)
                app.state = SERIAL_STATES.SYNC

            except Exception as e:
                print(e)
                # kill thread
                exit()
        
        case SERIAL_STATES.SYNC:
            try:
                if app.sync():
                    app.state = SERIAL_STATES.PARSE

            except Exception as e:
                print(e)
                app.ser.close()
                # kill thread
                exit()
        
        case SERIAL_STATES.PARSE:
            try: 
                app.read_packet()
                print(app.pad_data)
                app.state = SERIAL_STATES.SYNC

            except Exception as e:
                print(e)
                # kill thread
                exit()
    

# X labels
labels = ["FSR1", "FSR2", "FSR3", "FSR4", "FSR5"]

# Initial bar heights
y = [0.0, 0.0, 0.0, 0.0, 0.0]

fig, ax = plt.subplots()
bars = ax.bar(labels, y, color="skyblue")

# Set limits
ax.set_ylim(0, 3.3)
ax.set_ylabel("Value")
ax.set_title("Animated Bar Graph")

# Update function for animation
def update(frame, app:app_t):
    # New random values between 0 and 10
    # new_y = np.random.uniform(0, 10, size=4)

    new_y = app.pad_data
    for bar, h in zip(bars, new_y):
        bar.set_height(h)

    return bars

def thread1_proc(app:app_t):
    while True:
        app_loop(app)

if __name__ == "__main__":
    app = app_t()

    import threading
    t1 = threading.Thread(target=thread1_proc, args=(app,), daemon=True)
    t1.start()
    
    ani = FuncAnimation(fig, update, frames=None, interval=1, fargs=(app,))
    plt.show()