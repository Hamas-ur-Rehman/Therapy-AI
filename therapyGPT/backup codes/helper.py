"""
This file contains code for helper functions
"""

import re


def fix_collection_name(collection_name):
    # Replace spaces with underscores
    collection_name = collection_name.replace(' ', '_')

    # Add underscore placeholders if the name is too short
    if len(collection_name) < 3:
        collection_name += '_' * (3 - len(collection_name))

    # Cut off the name if it is too long
    if len(collection_name) > 63:
        collection_name = collection_name[:63]

    # Replace consecutive periods with a single period
    collection_name = re.sub(r'\.\.', '.', collection_name)

    # Replace any invalid characters with underscores
    collection_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', collection_name)

    # Ensure that the name starts and ends with an alphanumeric character
    if not collection_name[0].isalnum():
        collection_name = 'X' + collection_name[1:]
    if not collection_name[-1].isalnum():
        collection_name = collection_name[:-1] + 'X'

    return collection_name

