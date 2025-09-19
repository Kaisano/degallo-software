# visualize serial output
import serial

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np

import random

import re

serial = serial.Serial(port='/dev/ttyACM0',
                       baudrate=115200
                        )
# while(True):
#     #print(serial.read().decode(), end='')
#     s = serial.read_until(b'\n').decode().rstrip()
#     voltage = float(re.search(r"voltage:\s*([0-9.]+)", s).group(1))
#     diff = 3.3 - voltage
#     # print(diff)

# TODO: multithread. Use one to obtain the serial output and the other to update the bar graph

# X labels
labels = ["FSR1", "FSR2", "FSR3", "FSR4"]

# Initial bar heights
y = np.random.uniform(0, 10, size=4)

fig, ax = plt.subplots()
bars = ax.bar(labels, y, color="skyblue")

# Set limits
ax.set_ylim(0, 1)
ax.set_ylabel("Value")
ax.set_title("Animated Bar Graph")

# Update function for animation
def update(frame):
    # New random values between 0 and 10
    # new_y = np.random.uniform(0, 10, size=4)

    s = serial.read_until(b'\n').decode().rstrip()
    voltage = float(re.search(r"voltage:\s*([0-9.]+)", s).group(1))
    diff = 3.3 - voltage

    new_y = (diff, 0, 0, 0)
    for bar, h in zip(bars, new_y):
        bar.set_height(h)

    return bars

# Animate
ani = FuncAnimation(fig, update, frames=None, interval=1, blit=False)

plt.show()