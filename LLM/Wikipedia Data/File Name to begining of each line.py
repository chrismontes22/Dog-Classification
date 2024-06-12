"""Takes the filename and adds it and a tab to the begining of each line in the text"""

import os

# Define the source and destination directories
src_dir = src_dir
dst_dir = dst_dir

# Create the destination directory if it doesn't exist
os.makedirs(dst_dir, exist_ok=True)

# Iterate over each file in the source directory
for filename in os.listdir(src_dir):
    # Check if the file is a text file
    if filename.endswith(".txt"):
        # Open the source file and the destination file
        with open(os.path.join(src_dir, filename), "r", encoding="utf-8") as src_file, \
             open(os.path.join(dst_dir, filename), "w", encoding="utf-8") as dst_file:
            # Iterate over each line in the source file
            for line in src_file:
                # If the line is not blank, prepend the file name and a tab
                if line.strip():
                    line = filename.replace(".txt", "") + line
                # Write the line to the destination file
                dst_file.write(line)
