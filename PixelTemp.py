import re
import subprocess
import matplotlib.pyplot as plt
from collections import defaultdict
from subprocess import Popen, PIPE
from datetime import datetime
import threading
import time  # Added this import
import matplotlib
matplotlib.use('TkAgg')

def parse_line(line):
    temp_pattern = r'I pixel-thermal: ([a-zA-Z0-9_-]*):(-?[0-9.]*)'
    temp_match = re.search(temp_pattern, line)
    if temp_match:
        sensor, temp = temp_match.groups()
        timestamp = datetime.now()
        if temp:
            return 'temp', (sensor, float(temp), timestamp)

    return None, None

def update_plot(data, ax):
    ax.clear()
    for sensor, temps in data.items():
        if sensor != 'power_budget' and temps:
            timestamps, temps = zip(*temps)
            ax.plot(timestamps, temps, label=sensor)
    ax.legend()
    ax.set_title("Temperature Sensors")

def data_collection(data):
    with Popen(["adb", "logcat", "-s", "pixel-thermal"], stdout=PIPE, bufsize=1, universal_newlines=True) as process:
        start_time = time.time()  # Record the start time
        for line in process.stdout:
            data_type, parsed_data = parse_line(line)

            if data_type is None:
                continue

            if data_type == 'temp':
                sensor, temp, timestamp = parsed_data
                elapsed_time = time.time() - start_time  # Calculate elapsed time
                if elapsed_time >= 1.0:  # Ignore data collected in the first second
                    if temp not in [0.0, 1.0] and sensor not in ['ocp_tpu', 'ocp_gpu', 'soc', 'VIRTUAL-SKIN-HINT', 'vdroop1', 'cellular-emergency', 'VIRTUAL-SKIN-GPU', 'VIRTUAL-SKIN-CPU', 'BCL_TPU_LOW_TEMP', 'USB-MINUS-USB2', 'USB-MINUS-NEUTRAL', 'BCL_GPU_LOW_TEMP']:
                        data[sensor].append((timestamp, temp))
                        print(f"{timestamp} Temperature data: {sensor} - {temp}")

def main():
    def on_key(event):
        nonlocal data
        if event.key == 'r':
            for key in data:
                data[key] = []
            ax.clear()
            plt.draw()

    data = defaultdict(list)

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.canvas.mpl_connect('key_press_event', on_key)

    data_thread = threading.Thread(target=data_collection, args=(data,))
    data_thread.daemon = True
    data_thread.start()

    while True:
        update_plot(data, ax)
        plt.pause(0.01)

if __name__ == '__main__':
    main()
