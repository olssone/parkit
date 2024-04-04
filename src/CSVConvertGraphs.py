import csv
import matplotlib.pyplot as plt
from datetime import datetime
from Adaptation import get_value_from_tag, log  # Assuming you have a function to get values from XML

# Path to system configuration file
sys_config = "src/ParkitConfiguration.xml"

# Function to read data from a CSV file
def read_csv(filename):
    log(f"Reading CSV File: {filename}")  # Print out the filename
    data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            # Convert data types
            if row[0].startswith("#"):
                continue
            status_occupied = row[0] == 'SPACE OCCUPIED'
            status_car = row[1] == 'CAR IN SPACE'
            time = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            rectangle_x = float(row[3])
            rectangle_y = float(row[4])
            rectangle_width = float(row[5])
            rectangle_height = float(row[6])
            # Append data as tuple to the list
            data.append((status_occupied, status_car, time, rectangle_x, rectangle_y, rectangle_width, rectangle_height))
    return data

# Function to plot graph and save it to a PNG file
def plot_and_save_graph(data, filename):
    # Extract data for plotting
    times = [entry[2] for entry in data]
    car = [entry[1] for entry in data]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(times, car, label='Car', color='green')
    plt.xlabel('Time')
    plt.ylabel('Status')
    plt.title('Status over Time')
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a PNG file
    plt.savefig(filename)

    log(f"Graph saved to {filename}")