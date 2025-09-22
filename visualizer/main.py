# visualize serial output
import multiprocessing
from multiprocessing import Manager, Process, Event
from multiprocessing.managers import DictProxy

import serial
from serial.tools import list_ports

import struct
from enum import Enum

class serial_device():
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

    def connect(self, port: str, baudrate: int):
        self.ser = serial.Serial(port=port, baudrate=baudrate)
    
    def read_packet(self):
        data = self.ser.read(self.__packet_size)
        if len(data) == self.__packet_size:
            return list(struct.unpack(self.__packet_format, data))
    
    def sync(self):
        return \
            self.ser.read() == self.__key1 and \
            self.ser.read() == self.__key2

class serial_device_process(Process):
    def __init__(self, port: str, baudrate: int, shared_device_data: DictProxy[str, list[float]]):
        super().__init__(daemon=True)
        self.exit = multiprocessing.Event()

        self.serial_dev = serial_device()
        self.port = port
        self.baudrate = baudrate

        self.shared_device_data = shared_device_data

    def proc_loop(self):
        match self.serial_dev.state:
            case SERIAL_STATES.CONNECT:
                try:
                    self.serial_dev.connect(self.port, self.baudrate)
                    self.serial_dev.state = SERIAL_STATES.SYNC

                except Exception as e:
                    self.shutdown()
                    print(e)
            
            case SERIAL_STATES.SYNC:
                try:
                    if self.serial_dev.sync():
                        self.serial_dev.state = SERIAL_STATES.PARSE

                except Exception as e:
                    self.shutdown()
                    print(e)
            
            case SERIAL_STATES.PARSE:
                try: 
                    self.shared_device_data[self.port] = self.serial_dev.read_packet().copy()

                    self.serial_dev.state = SERIAL_STATES.SYNC

                except Exception as e:
                    self.shutdown()
                    print(e)

    def run(self):
        while not self.exit.is_set():
            self.proc_loop()

    def shutdown(self):
        try:
            self.app.ser.close()
        except Exception as e:
            print(e)

        self.exit.set()

class SERIAL_STATES(Enum):
    CONNECT=0,
    SYNC=1,
    PARSE=2

class serial_device_manager():
    def __init__(self, shared_dict: DictProxy[str, list[float]]):
        self.shared_device_data = shared_dict
        self.serial_devices = {}

    def __get_all_pico_com(self):
        pi_devices = set()

        RP_VID="2E8A"
        for port, desc, hwid in sorted(list_ports.comports()):
            if RP_VID.lower() in hwid.lower():
                pi_devices.add(port)
        
        return pi_devices
    
    def update_port(self):
        new_serial_devices = self.__get_all_pico_com()
        add_devices = new_serial_devices - self.serial_devices.keys()
        rem_devices = self.serial_devices.keys() - new_serial_devices

        if len(add_devices) <= 0 and len(rem_devices) <= 0: return
        
        for device in add_devices:
            self.serial_devices[device] = serial_device_process(device, 115200, self.shared_device_data)
            self.serial_devices[device].start()
            # print("Serial Process Started")

        for device in rem_devices:
            self.serial_devices[device].shutdown()
            # print("Serial Process Shutdown")

            self.shared_device_data.pop(device)
            self.serial_devices.pop(device)
    
    def shutdown(self):
        try:
            for proc in self.serial_devices.values():
                proc.shutdown()
            pass
        except Exception as e:
            print(e)

if __name__ == "__main__":
    with Manager() as manager:
        d = manager.dict()
        device_manager = serial_device_manager(shared_dict=d)

        while True:
            device_manager.update_port()
            print(d)