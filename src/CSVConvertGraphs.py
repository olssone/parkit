'''

        +----------------------------+
        |    CSVConvertGraphs.py     |
        +----------------------------+

This Python script reads data from a CSV file containing information about parking space occupancy status
over time, plots the data on a graph, and saves it as a PNG file. It is designed to visualize the
occupancy of parking spaces, indicating whether each space is vacant or occupied at different points
in time.

'''

from collections import deque
import csv
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.lines import Line2D  # Import this for custom legend handles
from Adaptation import get_value_from_tag, log  # Assuming you have a function to get values from XML

# Path to system configuration file
sys_config = "src/ParkitConfiguration.xml"

# Function to read data from a CSV file
def read_csv(filename):
    data = []
    skip = False
    skip_count = 0
    window_size = 5  # Define the size of the sliding window
    window = deque(maxlen=window_size)  # Initialize a deque for the sliding window

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if skip:
                if skip_count < 4:
                    skip_count += 1
                    continue  # Skip the current loop iteration
                else:
                    skip = False
                    skip_count = 0

            if row[0] == "### SYSTEM RESTART ###":
                skip = True  # Initiate skipping
                continue  # Skip the line with "### SYSTEM RESTART ###"

            if row[0].startswith("#"):
                continue  # Skip any row that starts with "#"

            # Append current status to the sliding window
            window.append(row[1] == 'CAR IN SPACE')

            # Determine if a car is present based on the sliding window
            # Considering true if the majority within the window are 'CAR IN SPACE'
            status_car = window.count(True) > len(window) / 2

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
    plt.figure(figsize=(13, 6))  # Increased resolution for clearer output

    # Plot each point, color it based on car presence, with thicker lines
    for i in range(len(times)-1):
        plt.plot(times[i:i+2], car_presence[i:i+2], color='red' if car_presence[i] == 1 else 'green', lw=4)

    plt.xlabel('Time', fontsize=24)  # x-axis
    plt.ylabel('Space Occupancy', fontsize=24)  # y-axis
    plt.title('Parking Lot Status', fontsize=36)  # title label
    plt.yticks([0, 1], ['Space Vacant', 'Space Occupied'], fontsize=18)  # Adjusted font size for better fit
    plt.ylim(-0.1, 1.1)  # Adjust y-axis limits to close gap
    plt.grid(True)

    # Create custom legend with thicker lines
    legend_elements = [Line2D([0], [0], color='green', lw=4, label='Space Vacant'),
                       Line2D([0], [0], color='red', lw=4, label='Space Occupied')]

    plt.legend(handles=legend_elements, fontsize=18, loc='lower left', bbox_to_anchor=(1, 1))  # legend

    # Adjust layout to not cut off legend since it needs to be outside of the graph.
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig(filename)

# This function will parse the CSV file and determine the longest streak of
# the parking space being occupied

def parse_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

def find_longest_streak(file_path):
    longest_streak = 0
    current_streak = 0
    streak_start = None
    streak_end = None
    longest_streak_start = None
    longest_streak_end = None

    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            if row:  # check if the row is not empty
                if row[0].startswith('#'):
                    continue  # skip comments
                status = row[1].strip()
                timestamp = row[2].strip()

                if status == "CAR IN SPACE":
                    current_streak += 1
                    if current_streak == 1:
                        streak_start = timestamp
                    streak_end = timestamp
                else:
                    if current_streak > longest_streak:
                        longest_streak = current_streak
                        longest_streak_start = streak_start
                        longest_streak_end = streak_end
                    current_streak = 0

        # Check last streak at the end of file
        if current_streak > longest_streak:
            longest_streak = current_streak
            longest_streak_start = streak_start
            longest_streak_end = streak_end

    # Calculate the duration of the longest streak
    if longest_streak_start and longest_streak_end:
        duration = parse_datetime(longest_streak_end) - parse_datetime(longest_streak_start)
        log(f"Longest Streak: {longest_streak} times. Start: {longest_streak_start}. \
            End: {longest_streak_end}. Duration: {duration}")
        return f"{longest_streak_start},{longest_streak_end }"

