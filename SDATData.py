import os
import xml.etree.ElementTree as ET


def sdat_data(directory='SDAT-Files'):
    # Load the XML content from a file
    tree = ET.parse(f'{directory}/20190313_093127_12X-0000001216-O_E66_12X-LIPPUNEREM-T_ESLEVU121963_-279617263.xml')
    root = tree.getroot()

    # Define the namespace
    namespaces = {'rsm': 'http://www.strom.ch'}

    # Find the DocumentID within the header
    document_id = root.find('.//rsm:DocumentID', namespaces=namespaces).text

    # Find all Observation tags
    observations = root.findall('.//rsm:Observation', namespaces=namespaces)

    sequences = []
    # Iterate through each Observation and print its contents
    for obs in observations:
        sequence = obs.find('.//rsm:Sequence', namespaces=namespaces).text
        volume = obs.find('.//rsm:Volume', namespaces=namespaces).text
        sequences.append([sequence, volume])

    return document_id, sequences


data = sdat_data()
minute = 15
print(f'DocumentID: {data[0]}')
for i in data[1]:
    print(f'\tMinute {minute}, Volume: {i[1]}')
    minute += 15