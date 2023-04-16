import re
import subprocess
import matplotlib.pyplot as plt
from collections import defaultdict
from subprocess import Popen, PIPE
from datetime import datetime

def parse_line(line):
    temp_pattern = r'I pixel-thermal: ([a-zA-Z0-9_-]*):(-?[0-9.]*)'
    temp_match = re.search(temp_pattern, line)
    if temp_match:
        sensor, temp = temp_match.groups()
        timestamp = datetime.now()
        if temp:  # Make sure the temperature value is not an empty string
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
    plt.draw()
    plt.pause(0.01)

def main():
    def on_key(event):
        nonlocal data
        if event.key == 'r':
            # Clear sensor data
            for key in data:
                data[key] = []
            # Clear plot
            ax.clear()
            plt.draw()
            
    data = defaultdict(list)

    # Initialize the graphs
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.canvas.mpl_connect('key_press_event', on_key)  # Connect the event handler
    # Start the logcat process
    with Popen(["adb", "logcat", "-s", "pixel-thermal"], stdout=PIPE, bufsize=1, universal_newlines=True) as process:
        for line in process.stdout:
            # print(f"Logcat line: {line.strip()}")  # Print the raw logcat line
            data_type, parsed_data = parse_line(line)
           
            if data_type is None:
                continue

            if data_type == 'temp':
                sensor, temp, timestamp = parsed_data
                if temp not in [0.0, 1.0] and sensor not in ['ocp_tpu', 'ocp_gpu', 'soc', 'VIRTUAL-SKIN-HINT', 'cellular-emergency', 'VIRTUAL-SKIN-GPU', 'VIRTUAL-SKIN-CPU', 'BCL_TPU_LOW_TEMP', 'USB-MINUS-USB2', 'USB-MINUS-NEUTRAL', 'BCL_GPU_LOW_TEMP']:
                    data[sensor].append((timestamp, temp))
                    print(f"{timestamp} Temperature data: {sensor} - {temp}")  # Print temperature data

            # Update the graph
            ax.clear()
            update_plot(data, ax)

if __name__ == '__main__':
    main()
