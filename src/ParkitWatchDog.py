import subprocess
import time
import os
import xml.etree.ElementTree as ET
from Adaptation import update_xml_tag_value, log

logfile_path = "parkit.log"
os.remove(logfile_path)
    
sys_config = "src/ParkitConfiguration.xml"
main_script = "src/ObjectOccupancyDetector.py"

while True:
    process = subprocess.Popen(['python', main_script])
    process.wait()  # Wait for the process to exit
    if process.returncode != 0:
        print("Script crashed. Restarting...")
        update_xml_tag_value(sys_config, "status", "failed")
        log("System failed. Restarting...")
        time.sleep(5)  # Delay before restarting
    else:
        update_xml_tag_value(sys_config, "status", "success")
        log("System exiting safely...")
        break  # Exit loop if the script exits cleanly

