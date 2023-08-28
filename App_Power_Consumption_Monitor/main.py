import subprocess
import re
import psutil
import gpu_stat
import time
import wmi

# Get user input
duration = input("Enter duration in seconds: ")
resolution = input("Enter resolution in milliseconds: ")
app_names_input = input(
    "Enter the names of the applications to measure the power consumption of, separated by commas: "
)
app_names = app_names_input.split(",")
file_name = input("Enter CSV file name: ")

# First command to execute
command1 = [
    "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe",
    "-duration",
    duration,
    "-resolution",
    resolution,
    "-file",
    file_name,
]

# Execute the first command
try:
    subprocess.run(command1, check=True)
    print("First command executed successfully.")
except subprocess.CalledProcessError:
    print("First command execution failed.")

# Initialize the WMI interface
c = wmi.WMI(namespace="root\\CIMV2")


# Function to measure power consumption of applications
def measure_power(app_names, duration):
    # Initialize a dictionary to store the power values for each application
    power_dict = {app_name: [] for app_name in app_names}

    # Start a loop to measure the cpu and gpu utilization every second for the specified duration
    for i in range(duration):
        # Iterate over each application name
        for app_name in app_names:
            # Get the process ID of the application by its name
            pid = None
            for proc in psutil.process_iter():
                if proc.name() == app_name:
                    pid = proc.pid
                    break

            # If the process ID is not found, print an error message and continue to the next app
            if pid is None:
                print(f"The application '{app_name}' does not exist.")
                continue

            # Get the CPU and memory usage of the process using psutil
            app = psutil.Process(pid)
            app_cpu = app.cpu_percent()
            app_mem = app.memory_percent()

            # Get the GPU usage for the process
            gpu_usage = None
            gpu_usage_data = c.query(
                "SELECT * FROM Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine"
            )
            for data in gpu_usage_data:
                if data.Name.endswith(f"pid_{app_name}"):
                    gpu_usage = int(data.UtilizationPercentage)
                    break

            # Estimate the power consumption of the process using a simple formula
            estimated_gpu_power = gpu_usage * (total_gpu_power / 100.0)
            estimated_cpu_power = app_cpu * (total_cpu_power / 100.0)
            estimated_memory_power = app_mem * (total_mem_power / 100.0)

            # Estimate the power consumption of the application using a simple formula
            app_power = (
                estimated_gpu_power + estimated_cpu_power + estimated_memory_power
            )

            # Append the power value to the list for this application
            power_dict[app_name].append(app_power)

        # Wait for one second
        time.sleep(1)

    # Return the dictionary of power values for each application
    return power_dict


# Execute the first command
try:
    subprocess.run(command1, check=True)
    print("First command executed successfully.")
except subprocess.CalledProcessError:
    print("First command execution failed.")

# Second command to execute
command2 = [
    "python",
    "power-gadget/power-gadget.py",
    "--power-log-file",
    file_name,
]

# Execute the second command and capture its output
try:
    second_command_output = subprocess.run(
        command2, capture_output=True, text=True, check=True
    ).stdout
    print("Second command executed successfully.")
except subprocess.CalledProcessError:
    print("Second command execution failed.")

# Regexpression to capture power values
pattern_power = r"Average (\w+) Power_0 \(Watt\): ([\d.]+)"
power_values = {}

# Find and store the values in the dictionary
matches = re.findall(pattern_power, second_command_output)
for metric, value in matches:
    power_values[metric] = float(value)

# Extract specific values
total_cpu_power = power_values.get("Processor", None)
total_mem_power = power_values.get("DRAM", None)
total_gpu_power = power_values.get("GT", None)

# Get CPU and memory utilization
cpu_utilization = psutil.cpu_percent()
memory_utilization = psutil.virtual_memory().percent


# Get GPU utilization
gpu = gpu_stat.gpu()
gpu_utilization = gpu.utilization()[0]

# Call the function to measure power consumption and get the power dictionary
power_values_dict = measure_power(app_names, int(duration))

# Print the power values for each application
for app_name, power_values in power_values_dict.items():
    print(f"Power values for {app_name}: {power_values}")
# Clean up the WMI interface
c = None

#test 
print("Total CPU Power:", total_cpu_power)
print("Total DRAM Power:", total_mem_power)
print("Total GPU Power:", total_gpu_power)
print("CPU Utilization:", cpu_utilization)
print("Memory Utilization:", memory_utilization)
print("GPU Utilization:", gpu_utilization)
