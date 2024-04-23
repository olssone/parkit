'''

        +----------------------------+
        |       Adaptation.py        |
        +----------------------------+

This module provides utility functions for interacting with XML files, logging messages with timestamps,
and writing/appending text to files. It includes functions to retrieve values from XML tags, update XML
tag values, log messages to a specified file, and write or append text to files.


'''

import os
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

def write_text_to_file(file_path, text):
    # Check if the provided file path is valid
    if os.path.isdir(file_path):
        print(f"Error: The path '{file_path}' is a directory, not a file.")
        log(f"Write error: {file_path} does not exist.")
        return
    if os.path.isfile(file_path):
        # Open the file in append mode and write the text to a new line
        with open(file_path, 'w') as file:
            file.write(f"{text}")
    else:
        print(f"OK: The file '{file_path}' does not exist. It will be created.")
        # Open the file in write mode, which will create the file if it doesn't exist
        with open(file_path, 'w') as file:
            file.write(text)
        log(f"File: {file_path} text written.")

def append_text_to_file(file_path, text):
    # Check if the provided file path is valid
    if os.path.isdir(file_path):
        print(f"Error: The path '{file_path}' is a directory, not a file.")
        return
    if os.path.isfile(file_path):
        # Open the file in append mode and write the text to a new line
        with open(file_path, 'a') as file:
            file.write(f"\n{text}")
    else:
        print(f"OK: The file '{file_path}' does not exist. It will be created.")
        # Open the file in write mode, which will create the file if it doesn't exist
        with open(file_path, 'w') as file:
            file.write(text)
        log(f"File: {file_path} text written.")