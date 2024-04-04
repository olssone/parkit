
from datetime import datetime
import subprocess
import time
import os
import xml.etree.ElementTree as ET
from Adaptation import get_value_from_tag, update_xml_tag_value, log, write_text_to_file, append_text_to_file

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log(f"Watch dog started at {now}")

sys_config = "src/ParkitConfiguration.xml"
main_script = "src/ObjectOccupancyDetector.py"
csv_file = get_value_from_tag(sys_config, "csv-file-location")
csv_columns = get_value_from_tag(sys_config, "csv-column-names")
output_stream = get_value_from_tag(sys_config, "system-output-location")

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
os.remove(csv_file)

if not os.path.exists(csv_file):
    append_text_to_file(csv_file,csv_columns)

try:
    while True:
        process = subprocess.Popen(['python', main_script])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log(f"System started at {now}")
        loading_dots = ""
        for _ in range(5):  # Number of dots to append
            loading_dots += '.'
            write_text_to_file(output_stream, f"Park-It is loading {loading_dots}")
            time.sleep(0.5) 
        process.wait()  # Wait for the process to exit
        if process.returncode != 0:
            print("Script crashed. Restarting...")
            update_xml_tag_value(sys_config, "status", "failed")
            log("System failed. Restarting...")
            # Clean up
            os.remove(output_stream)
            time.sleep(5)  # Delay before restarting
        else:
            update_xml_tag_value(sys_config, "status", "success")
            log("System exiting safely...")
            # Clean up
            os.remove(output_stream)
            break  # Exit loop if the script exits cleanly
except KeyboardInterrupt:
    # Log the keyboard interrupt
    log("System terminated with force. Keyboard interrupt.")
    print("Program terminated by user.")
    os.remove(output_stream)
    


