import xml.etree.ElementTree as ET
import os
from datetime import datetime

# Specify the directory
directory = 'ESL-Files'

# Get list of all files in the directory
all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

# Dictionary to store the latest data for each time period in YEAR-MONTH format
time_period_data = {}

# Iterate through all files
for i in all_files:
    # Load the XML file from the disk
    tree = ET.parse(os.path.join(directory, i))
    root = tree.getroot()

    # Extract TimePeriod and Values
    for time_period in root.findall('.//TimePeriod'):
        time_period_end = time_period.attrib.get('end')

        # Convert the TimePeriod end to YEAR-MONTH format
        time_period_ym = datetime.strptime(time_period_end, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m')

        # Initialize the time period data if not present
        if time_period_ym not in time_period_data:
            time_period_data[time_period_ym] = []

        # Extract only the value from the ValueRow elements
        for value_row in time_period.findall('.//ValueRow'):
            value = value_row.attrib.get('value')

            # Store the value in the dictionary
            if value:
                time_period_data[time_period_ym].append(value)

# After processing all files, print the stored data (ensuring no redundancy, using YEAR-MONTH)
for period_ym, values in time_period_data.items():
    print(f'TimePeriod: {period_ym}')
    for value in values:
        print(f'\tValue: {value}')
