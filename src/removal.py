# Modules
import os
import re
import argparse

# Define command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("folder_path", help="path to folder containing DITA files")
args = parser.parse_args()

# Get a list of all DITA files in the folder
file_list = [f for f in os.listdir(args.folder_path) if f.endswith(".dita")]

# Loop through the files in the folder
for file_name in file_list:

    # Open the file in read mode
    with open(os.path.join(args.folder_path, file_name), "r", encoding="utf-8") as f:
        
        # Read the entire file as a string
        file_contents = f.read()

        # Remove all existing indexterm tags and their content
        file_contents = re.sub(r"<indexterm>([^<]*)</indexterm>", "", file_contents)
    
    # Open the file in write mode
    with open(os.path.join(args.folder_path, file_name), "w", encoding="utf-8") as f:

        # Write the updated file contents to the file
        f.write(file_contents)