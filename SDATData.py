import os
import xml.etree.ElementTree as ET
from datetime import datetime
import datetime as dt

def sdat_data(directory='SDAT-Files'):
    # Load the XML content from files in the specified directory
    all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # List to store sequences per day
    sequences_unique = []
    sequences_duplicate = []
    document_ids = []

    # Set to track unique datetimes
    unique_datetimes = set()

    for filename in all_files:
        # Parse the XML file
        namespace = {'rsm': 'http://www.strom.ch'}
        tree = ET.parse(os.path.join(directory, filename))
        root = tree.getroot()

        document_id = root.find('.//rsm:DocumentID', namespace).text
        document_ids.append(document_id)

        # Extract report period start and end times
        start_datetime_str = root.find('.//rsm:StartDateTime', namespace).text
        end_datetime_str = root.find('.//rsm:EndDateTime', namespace).text

        start_datetime = datetime.fromisoformat(start_datetime_str[:-1])  # Remove 'Z'
        end_datetime = datetime.fromisoformat(end_datetime_str[:-1])  # Remove 'Z'

        # Initialize counter and temporary storage for sequences
        counter = 1
        tmp_list = []

        for observation in root.findall('.//rsm:Observation', namespace):
            volume = observation.find('.//rsm:Volume', namespace).text
            tmp_list.append(volume)
            if counter == 96:
                # Check if the datetime is unique
                if start_datetime not in unique_datetimes:
                    # Add the datetime to the set and list of unique sequences
                    unique_datetimes.add(start_datetime)
                    sequences_unique.append([start_datetime, tmp_list])
                tmp_list = []
                start_datetime += dt.timedelta(days=1)
                counter = 1
            else:
                counter += 1
        # Append any remaining sequences if they haven't been appended yet (handles last day)
        if tmp_list:
            if start_datetime not in unique_datetimes:
                unique_datetimes.add(start_datetime)
                sequences_unique.append([start_datetime, tmp_list])

    return sequences_unique

# Call the function to execute
sequences_unique = sdat_data()

# Print the unique sequences
print("Unique sequences:")
for i in sequences_unique:
    print(i)

print(f"Total unique sequences: {len(sequences_unique)}")