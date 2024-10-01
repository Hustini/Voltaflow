import xml.etree.ElementTree as ET
import os

# Specify the directory
directory = 'ESL-Files'

# Get list of all files in the directory
all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

for i in all_files:
    print(i)


"""# Load the XML file from the disk
tree = ET.parse('ESL-Files/EdmRegisterWertExport_20190131_eslevu_20190322160349.xml')  # Replace 'your_file.xml' with the actual file path
root = tree.getroot()

# Extract the 'end' attribute from the TimePeriod element
time_period = root.find(".//TimePeriod")
if time_period is not None:
    time_period_end = time_period.attrib.get('end')
    print(f"TimePeriod End: {time_period_end}")

# Extract Values from ValueRow elements
for value_row in root.findall(".//ValueRow"):
    value = value_row.attrib.get('value')  # Extract only the 'value' attribute
    if value:
        print(f"Value: {value}")"""
