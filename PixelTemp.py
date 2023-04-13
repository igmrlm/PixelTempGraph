import re
import subprocess
import matplotlib.pyplot as plt
from collections import defaultdict
from queue import Queue
from threading import Thread
from subprocess import Popen, PIPE


def logcat_reader(queue):
    adb_cmd = ['adb', 'logcat', '-s', 'pixel-thermal']
    process = subprocess.Popen(adb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        queue.put(line)

def parse_line(line):
    temp_pattern = r'pixel-thermal: ([a-zA-Z0-9_-]*):([0-9.]*)'
    power_pattern = r'power_budget=([0-9.]*)'

    temp_match = re.search(temp_pattern, line)
    if temp_match:
        sensor, temp = temp_match.groups()
        if temp:  # Make sure the temperature value is not an empty string
            return 'temp', (sensor, float(temp))

    power_match = re.search(power_pattern, line)
    if power_match:
        power = float(power_match.group(1))
        return 'power', power

    return None, None


def init_plot():
    fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 10))
    fig.suptitle('Temperature and Power Data')
    return fig, ax1, ax2

def update_plot(temp_data, power_data, fig, ax1, ax2):
    temp_lines = {}
    for sensor in temp_data:
        line, = ax1.plot(temp_data[sensor], label=sensor)
        temp_lines[sensor] = line
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend()

    power_line, = ax2.plot(power_data, label='Power Budget')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Power (mW)')
    ax2.legend()

    for sensor, values in temp_data.items():
        temp_lines[sensor].set_ydata(values)
        temp_lines[sensor].set_xdata(range(len(values)))
    ax1.relim()
    ax1.autoscale_view()

    power_line.set_ydata(power_data)
    power_line.set_xdata(range(len(power_data)))
    ax2.relim()
    ax2.autoscale_view()

    fig.canvas.draw()
    fig.canvas.flush_events()

def main():
    data = defaultdict(list)
    data['power_budget'] = []
    
    # Initialize the graphs
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))

    # Start the logcat process
    with Popen(["adb", "logcat", "-s", "pixel-thermal"], stdout=PIPE, bufsize=1, universal_newlines=True) as process:
        for line in process.stdout:
            print(f"Logcat line: {line.strip()}")  # Print the raw logcat line
            data_type, parsed_data = parse_line(line)
            
            if data_type is None:
                continue

            if data_type == 'temp':
                sensor, temp = parsed_data
                if temp not in [0.0, 1.0] and sensor not in ['ocp_tpu', 'ocp_gpu', 'soc']:
                    data[sensor].append(temp)
                    print(f"Temperature data: {sensor} - {temp}")  # Print temperature data
            elif data_type == 'power':
                data['power_budget'].append(parsed_data)
                print(f"Power data: {parsed_data}")  # Print power data

            # Update the graph
            ax.clear()
            for sensor, temps in data.items():
                if sensor != 'power_budget':
                    ax.plot(temps, label=sensor)
            ax.legend()
            ax.set_title("Temperature Sensors")
            plt.draw()
            plt.pause(0.01)

if __name__ == '__main__':
    main()
