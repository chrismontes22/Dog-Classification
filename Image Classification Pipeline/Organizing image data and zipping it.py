####upload pipeline
import os
import shutil
import random


# Define the paths to your folders
new_images_folder = 'Akita - Copy'
large_folder = 'DC6 - Copy'

# Get the list of all image files in the new_images_folder
image_files = [f for f in os.listdir(new_images_folder) if os.path.isfile(os.path.join(new_images_folder, f))]

# Shuffle the list to ensure randomness
random.shuffle(image_files)

# Split the data into test, valid, and train
test_files = image_files[:10]
valid_files = image_files[10:20]
train_files = image_files[20:]

# Define the new label name
new_label_name = os.path.basename(new_images_folder)

# Create new label folders inside test, train, and valid folders
os.makedirs(os.path.join(large_folder, 'test', new_label_name), exist_ok=True)
os.makedirs(os.path.join(large_folder, 'valid', new_label_name), exist_ok=True)
os.makedirs(os.path.join(large_folder, 'train', new_label_name), exist_ok=True)

# Function to move files
def move_files(files, dst_folder):
    for file in files:
        shutil.move(os.path.join(new_images_folder, file), os.path.join(dst_folder, file))

# Move the files to the appropriate folders
move_files(test_files, os.path.join(large_folder, 'test', new_label_name))
move_files(valid_files, os.path.join(large_folder, 'valid', new_label_name))
move_files(train_files, os.path.join(large_folder, 'train', new_label_name))


import shutil
def zip_folder(folder_path, zip_name):
    # Create a Zip file
    shutil.make_archive(zip_name, 'zip', folder_path)
# Usage
zip_folder(large_folder, 'DC7')

