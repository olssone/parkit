'''

        +----------------------------+
        |     ParkitWatchDog.py      |
        +----------------------------+

This Python script serves as a watchdog for the Parkit system. It monitors the execution of 
the main script 'ObjectOccupancyDetector.py', restarts it if it crashes, and logs system events. 
The watchdog ensures that the system runs smoothly and handles any unexpected errors gracefully.
        
'''

from datetime import datetime
import shutil
import subprocess
import time
import os
import xml.etree.ElementTree as ET
from Adaptation import get_value_from_tag, update_xml_tag_value, log, write_text_to_file, append_text_to_file
from CSVConvertGraphs import append_file_to_file

def get_formatted_datetime():
    # Get current date and time
    now = datetime.now()
    # Format the datetime string
    datetime_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    return datetime_string


def copy_and_rename_file(source, destination):
    try:
        # Move and rename the file
        shutil.copy(source, destination)
        log(f"File moved and renamed from {source} to {destination}")
    except FileNotFoundError:
        print("The source file does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log(f"Watch dog started at {now}")

sys_config            = "src/ParkitConfiguration.xml"
main_script           = "src/ObjectOccupancyDetector.py"
csv_file              = get_value_from_tag(sys_config, "csv-file-location")
csv_columns           = get_value_from_tag(sys_config, "csv-column-names")
target_total_csv      = get_value_from_tag(sys_config, "total-csv-location")
output_stream         = get_value_from_tag(sys_config, "system-output-location")
log_file_location     = get_value_from_tag(sys_config, "log-file-location")
gallery_location      = get_value_from_tag(sys_config, "gallery-location")
graph_file_location   = get_value_from_tag(sys_config, "data-analytics-graph")
streak_file_location  = get_value_from_tag(sys_config, "streak-file-location")
optimal_file_location = get_value_from_tag(sys_config, "optimal-file-location")
graph_base_name       = os.path.basename(graph_file_location)[0:-4]

gallery_graph         = gallery_location + "/" + graph_base_name + "-" + get_formatted_datetime() + ".png"

# Added protection as RunParkit script already performs this check.
current_directory = os.path.basename(os.getcwd())
all_items = os.listdir('./')
if current_directory != "parkit":
    print("Please run watch dog from the parkit root directory.")
    print(f"Current directory: {current_directory}")
    log("User attemped to run system not in root directory.")
    log("Exiting safely...")
    exit()
elif 'src' not in all_items:
    print("No src directory found.")
    log("There was an error finding src directory.")
    exit()

# Create CSV file and give column names
if not os.path.exists(csv_file):
    append_text_to_file(csv_file,csv_columns)
else:
    append_file_to_file(csv_file, target_total_csv)
    os.remove(csv_file)
    

# Make sure there is a log file
if not os.path.exists(log_file_location):
    open(log_file_location, "x")

# Catch only keyboard exceptions so user can manually kill the process
try:
    while True:
        process = subprocess.Popen(['python', main_script])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log(f"System started at {now}")

        write_text_to_file(output_stream, "Park-It is loading... ")
        write_text_to_file(streak_file_location, "No Streak Available.")
        process.wait()
        # Once process finishes, check its return code, then handle
        if process.returncode != 0:
            print("System crashed. Restarting...")
            update_xml_tag_value(sys_config, "status", "failed")
            log("System crashed. Restarting...")
            # Clean up
            os.remove(output_stream)
            os.remove(streak_file_location)
            time.sleep(3)  
        else:
            update_xml_tag_value(sys_config, "status", "success")
            log("System exiting safely...")
            copy_and_rename_file(graph_file_location, gallery_graph)
            # Clean up
            os.remove(output_stream)
            os.remove(streak_file_location)
            break 
except KeyboardInterrupt:
    # Log the keyboard interrupt
    log("System terminated with force. Keyboard interrupt.")
    print("Program terminated by user.")
    
    copy_and_rename_file(graph_file_location, gallery_graph)
    os.remove(output_stream)
    os.remove(streak_file_location)

