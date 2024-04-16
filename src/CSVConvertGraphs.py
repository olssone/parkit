import csv
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.lines import Line2D  # Import this for custom legend handles
from Adaptation import get_value_from_tag, log  # Assuming you have a function to get values from XML

# Path to system configuration file
sys_config = "src/ParkitConfiguration.xml"

# Function to read data from a CSV file
def read_csv(filename):
    log(f"Reading CSV File: {filename}")  # Print out the filename
    data = []
    skip = False
    skip_count = 0

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        # Skip the line with "### SYSTEM RESTART ###" and 3 lines after.
        for row in reader:
            if skip:
                if skip_count < 4:
                    skip_count += 1
                    continue  
                else:
                    skip = False
                    skip_count = 0

            if row[0] == "### SYSTEM RESTART ###":
                skip = True 
                continue  

            if row[0].startswith("#"):
                continue 

            status_car = row[1] == 'CAR IN SPACE'
            time = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            rectangle_x = float(row[3])
            rectangle_y = float(row[4])
            rectangle_width = float(row[5])
            rectangle_height = float(row[6])

            data.append((status_car, time, rectangle_x, rectangle_y, rectangle_width, rectangle_height))

    return data

# Function to plot graph and save it to a PNG file
def plot_and_save_graph(data, filename):
    # Extract data for plotting
    times = [entry[1] for entry in data]
    car_presence = [1 if entry[0] else 0 for entry in data]  # 1 if car is in space, 0 if not
    
    # Create the plot
    plt.figure(figsize=(13, 6))
    
    # Plot each point, color it based on car presence
    for i in range(len(times)-1):
        plt.plot(times[i:i+2], car_presence[i:i+2], color='red' if car_presence[i] == 1 else 'green')
    
    plt.xlabel('Time')
    plt.ylabel('Space Occupancy')
    plt.title('Parking Space Occupancy over Time')
    plt.yticks([0, 1], ['Space Vacant', 'Space Occupied'])  # Custom labels for y-axis
    plt.grid(True)
    
    # Create custom legend
    legend_elements = [Line2D([0], [0], color='green', lw=4, label='Space Vacant'),
                       Line2D([0], [0], color='red', lw=4, label='Space Occupied')]
    
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
 
    # Adjust layout to not cut off legend since it needs to be outside of the graph.
    plt.tight_layout()  

    # Save the plot as a PNG file
    plt.savefig(filename)
    log(f"Graph saved to {filename}")
