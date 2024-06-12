"""After you have downloaded the image data for the selected breeds, this script renames the images in a padded 3 digit number in order, then creates test 
train val split folders in the main image folder. Next it moves the appropriate amount of images to the corresponding folders.
Finally it zips the entire image dataset"""
"""Please note that the dog_breeds here are filepaths, so if the folders are saved in a different path you must change it in the
dog_breeds list accordingly"""
#Just fill in the list of breeds with the breeds that you ran for the Image download pipeline
#I have my data structured where I have the main folder then a test, a train, and a valid folder. Then each folder has a bunch of folders, one for each class


import os
import shutil
import random
import logging
import datetime

# Set up logging
logging.basicConfig(filename='Image Changes.txt', level=logging.INFO, format='%(message)s')

# List of dog breeds
dog_breeds = ['Akita', 'Alaskan-Malamute', 'American-Foxhound', 'Cane-Corso', 'Dachshund', 'German-Shorthaired-Pointer', 'Miniature-Schnauzer', 'Stafforshire-Bull-Terrier' ]  # Add all dog breeds to this list

# Define the path to the large folder
large_folder = 'DD'

# Log the dog breeds and the current time
logging.info('***********************Zip File Change***********************')
logging.info('Time: ' + str(datetime.datetime.now()))
logging.info('Dog Breeds: ' + str(dog_breeds))


try:
    for dog_breed in dog_breeds:
        # Set the starting number
        num = 1

        # Sometimes image filenames are all over the place. This renames the files in numerical order in a folder. Loops for each breed
        for filename in os.listdir(dog_breed):
            # Check if the file is an image
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                # Construct the new filename with the numerical name
                new_filename = "{:03d}.{}".format(num, filename.split(".")[-1])
                num += 1
                # Rename the file
                os.rename(os.path.join(dog_breed, filename), os.path.join(dog_breed, new_filename))

        # Get the list of all image files in the dog_breed
        image_files = [f for f in os.listdir(dog_breed) if os.path.isfile(os.path.join(dog_breed, f))]

        # Shuffle the list to ensure randomness
        random.shuffle(image_files)

        # Split the data into test, valid, and train
        test_files = image_files[:10]
        valid_files = image_files[10:20]
        train_files = image_files[20:]

        # Define the new label name
        new_label_name = os.path.basename(dog_breed)

        # Create new label folders inside test, train, and valid folders
        os.makedirs(os.path.join(large_folder, 'test', new_label_name), exist_ok=True)
        os.makedirs(os.path.join(large_folder, 'valid', new_label_name), exist_ok=True)
        os.makedirs(os.path.join(large_folder, 'train', new_label_name), exist_ok=True)

        # Function to move files
        def move_files(files, dst_folder):
            for file in files:
                shutil.move(os.path.join(dog_breed, file), os.path.join(dst_folder, file))

        # Move the files to the appropriate folders
        move_files(test_files, os.path.join(large_folder, 'test', new_label_name))
        move_files(valid_files, os.path.join(large_folder, 'valid', new_label_name))
        move_files(train_files, os.path.join(large_folder, 'train', new_label_name))
#Useful for logging an error occurred and test train split folders were not able to be created
except Exception as e:
    logging.error('Error occurred: {}'.format(e))
    raise

#Makes a zip copy from the above data saved to large_folder variable
def zip_folder(folder_path, zip_name):
    shutil.make_archive(zip_name, 'zip', folder_path)
    # Log the zip file name
    logging.info('Zip file name: ' + zip_name + '.zip')
    logging.info('\n')
# Usage
zip_folder(large_folder, 'DD3')