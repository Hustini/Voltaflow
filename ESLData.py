import xml.etree.ElementTree as ET
import os
from datetime import datetime

# dir_input = input('Relative Path > ')

def esl_data(directory='ESL-Files'):
    # Dictionary to store the latest data for each time period in YEAR-MONTH format
    time_period_data = {}

    # OBIS codes to filter for
    obis_codes_of_interest = ['1-1:1.8.1', '1-1:1.8.2', '1-1:2.8.1', '1-1:2.8.2']

    # Get list of all files in the directory
    all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

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

            # Initialize the dictionary to store the values for each OBIS code
            values = {}

            # Extract only the value from the ValueRow elements that match the OBIS codes of interest
            for value_row in time_period.findall('.//ValueRow'):
                obis = value_row.attrib.get('obis')  # Get the OBIS code
                value = value_row.attrib.get('value')  # Get the value

                # Only store values that match the OBIS codes of interest
                if obis in obis_codes_of_interest and value:
                    # Store the value for each OBIS code, ensuring no duplicate OBIS codes within the same time period
                    values[obis] = float(value)

            # Calculate "Bezug" (sum of 1-1:1.8.1 and 1-1:1.8.2)
            bezug = None
            if '1-1:1.8.1' in values and '1-1:1.8.2' in values:
                bezug = values['1-1:1.8.1'] + values['1-1:1.8.2']

            # Calculate "Einspeisung" (sum of 1-1:2.8.1 and 1-1:2.8.2)
            einspeisung = None
            if '1-1:2.8.1' in values and '1-1:2.8.2' in values:
                einspeisung = values['1-1:2.8.1'] + values['1-1:2.8.2']

            # If this TimePeriod already exists, update only if new values are not None
            if time_period_ym in time_period_data:
                existing_entry = time_period_data[time_period_ym]
                # Only update "Bezug" if we have a valid value
                if bezug is not None:
                    existing_entry['Bezug'] = bezug
                # Only update "Einspeisung" if we have a valid value
                if einspeisung is not None:
                    existing_entry['Einspeisung'] = einspeisung
            else:
                # Create a new entry if it does not exist
                time_period_data[time_period_ym] = {
                    'TimePeriod': time_period_ym,
                    'Bezug': bezug,
                    'Einspeisung': einspeisung
                }

    # Convert the dictionary to a list
    return list(time_period_data.values())

# Example usage
data = esl_data()
for entry in data:
    print(f"TimePeriod: {entry['TimePeriod']}, Bezug: {entry['Bezug']}, Einspeisung: {entry['Einspeisung']}")
