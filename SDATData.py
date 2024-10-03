import os
import xml.etree.ElementTree as ET
from datetime import datetime
import datetime as dt


def sdat_data(directory='SDAT-Files'):
    # Load the XML content from files in the specified directory
    all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Lists to store sequences per day (daily) and cumulative data
    sequences_daily = []
    sequences_cumulative = []

    # Set to track unique (label, datetime) pairs
    unique_entries = set()

    # Dictionary to track cumulative totals for each label
    cumulative_totals = {'Einspeisung': 0, 'Bezug': 0}

    for filename in all_files:
        # Parse the XML file
        namespace = {'rsm': 'http://www.strom.ch'}
        tree = ET.parse(os.path.join(directory, filename))
        root = tree.getroot()

        document_id = root.find('.//rsm:DocumentID', namespace).text

        # Determine if this is "Einspeisung" or "Bezug"
        if 'ID735' in document_id:
            label = 'Einspeisung'
        elif 'ID742' in document_id:
            label = 'Bezug'

        # Extract report period start and end times
        start_datetime_str = root.find('.//rsm:StartDateTime', namespace).text
        end_datetime_str = root.find('.//rsm:EndDateTime', namespace).text

        start_datetime = datetime.fromisoformat(start_datetime_str[:-1])  # Remove 'Z'
        end_datetime = datetime.fromisoformat(end_datetime_str[:-1])  # Remove 'Z'

        # Initialize counter and temporary storage for sequences
        counter = 1
        daily_amount = 0

        for observation in root.findall('.//rsm:Observation', namespace):
            volume = observation.find('.//rsm:Volume', namespace).text
            daily_amount += float(volume)
            if counter == 96:
                # Create a unique key combining document_id and start_datetime
                unique_key = (label, start_datetime)

                # Check if this combination is unique for daily data
                if unique_key not in unique_entries:
                    # Add the unique key to the set and list of unique sequences (daily)
                    unique_entries.add(unique_key)
                    sequences_daily.append([label, start_datetime, daily_amount])

                    # Update cumulative totals and store cumulative sequence
                    cumulative_totals[label] += daily_amount
                    sequences_cumulative.append([label, start_datetime, cumulative_totals[label]])

                # Reset for the next day
                daily_amount = 0
                start_datetime += dt.timedelta(days=1)
                counter = 1
            else:
                counter += 1

        # Append any remaining sequences if they haven't been appended yet (handles last day)
        if daily_amount:
            unique_key = (label, start_datetime)
            if unique_key not in unique_entries:
                unique_entries.add(unique_key)
                sequences_daily.append([label, start_datetime, daily_amount])

                # Update cumulative totals and store cumulative sequence
                cumulative_totals[label] += daily_amount
                sequences_cumulative.append([label, start_datetime, cumulative_totals[label]])

    return sequences_cumulative, sequences_daily


# Call the function to execute
data = sdat_data()
for entry in data[0]:
    print(f'{entry}')
