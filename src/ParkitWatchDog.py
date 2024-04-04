import subprocess
import time
import os
import xml.etree.ElementTree as ET
from Adaptation import get_value_from_tag, update_xml_tag_value, log

sys_config = "src/ParkitConfiguration.xml"
main_script = "src/ObjectOccupancyDetector.py"
output_stream = get_value_from_tag(sys_config, "system-output-location")

logfile_path = "parkit.log"
os.remove(logfile_path)

while True:
    process = subprocess.Popen(['python', main_script])
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

