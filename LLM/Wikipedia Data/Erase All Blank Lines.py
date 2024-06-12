"""Erases blank lines so that the spacing is normalized for formatting"""
#For a single file, not the whole folder

import os

# Define the path to the input and output directories
input_dir = 'input_dir'
output_dir = 'output_dir'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Iterate over all files in the input directory
for filename in os.listdir(input_dir):
    # If the file is a text file
    if filename.endswith(".txt"):
        # Open the input file and the output file
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as input_file, \
             open(os.path.join(output_dir, filename), "w", encoding="utf-8") as output_file:
            # Iterate over all lines in the input file
            for line in input_file:
                # If the line is not blank, write it to the output file
                if line.strip():
                    output_file.write(line)
