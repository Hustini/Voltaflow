import os
import xml.etree.ElementTree as ET
from datetime import datetime


def sdat_data(directory='SDAT-Files'):
    # Load the XML content from a file
    all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    for i in all_files:
        # Parse the XML string
        namespace = {'rsm': 'http://www.strom.ch'}
        tree = ET.parse(os.path.join(directory, i))
        root = tree.getroot()

        # Extract values
        start_datetime_str= root.find('.//rsm:StartDateTime', namespace).text
        end_datetime_str = root.find('.//rsm:EndDateTime', namespace).text

        start_datetime = datetime.fromisoformat(start_datetime_str[:-1])  # Remove 'Z' before conversion
        end_datetime = datetime.fromisoformat(end_datetime_str[:-1])  # Remove 'Z' before conversion

        print(f'{i}, Start: {start_datetime}, End: {end_datetime}, Duration: {end_datetime - start_datetime}')

sdat_data()