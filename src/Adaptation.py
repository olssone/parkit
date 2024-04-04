import xml.etree.ElementTree as ET
from datetime import datetime

def get_value_from_tag(file_path, tag):
    """
    Parses an XML file and returns the text content of the first occurrence of a specified tag.
    
    :param file_path: The path to the XML file.
    :param tag: The tag name to search for.
    :return: The text content of the first occurrence of the specified tag, or None if the tag is not found.
    """
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Find the first occurrence of the tag
        element = root.find(f'.//{tag}')
        if element is not None:
            log(f"get_value_from_tag: found {tag}={element.text}")
            return element.text
        else:
            log(f"get_value_from_tag: Could not find {tag}")
            return None
    except ET.ParseError:
        print("Error parsing XML file.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def log(message):
    """
    Logs a message to a specified file with a timestamp.

    :param message: The text message to log.
    :param filename: The name of the file where the log should be written.
    """
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = "src/data/parkit.log"
    
    # Open the file in append mode and write the message
    with open(filename, 'a') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def update_xml_tag_value(file_path, tag, new_value):
    """
    Updates the value of a specified tag in an XML file.

    Parameters:
    - file_path: Path to the XML file.
    - tag: The tag whose value is to be updated.
    - new_value: The new value to assign to the tag.

    Returns:
    - True if the tag was found and updated, False otherwise.
    """
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Find the first occurrence of the tag
        element = root.find(f'.//{tag}')
        if element is not None:
            # Update the tag's value
            element.text = new_value
            # Write the changes back to the file
            tree.write(file_path)
            return True
        else:
            return False
    except ET.ParseError:
        print("Error parsing the XML file.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False