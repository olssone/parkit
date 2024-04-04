import csv
import matplotlib.pyplot as plt
from datetime import datetime
from Adaptation import get_value_from_tag  # Assuming you have a function to get values from XML

# Path to system configuration file
sys_config = "src/ParkitConfiguration.xml"

# Function to read data from a CSV file
def read_csv(filename):
    print("Filename:", filename)  # Print out the filename
    data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            # Convert data types
            status_occupied = row[0] == 't'
            status_car = row[1] == 't'
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
    occupied = [entry[0] for entry in data]
    car = [entry[1] for entry in data]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(times, occupied, label='Occupied', color='blue')
    plt.plot(times, car, label='Car', color='green')
    plt.xlabel('Time')
    plt.ylabel('Status')
    plt.title('Status over Time')
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a PNG file
    plt.savefig(filename)

    print(f"Graph saved to {filename}")

if __name__ == "__main__":
    # Get the filename of the CSV file from the system configuration
    filename = get_value_from_tag(sys_config, "csv-file-location")
    # Read data from the CSV file
    data = read_csv(filename)
    # Generate a filename for the PNG file based on current date and time
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    png_filename = f"parkit-data-analytics-graph_{current_time}.png"
    # Plot the graph and save it to a PNG file
    plot_and_save_graph(data, png_filename)