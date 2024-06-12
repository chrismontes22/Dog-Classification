###Here is the code for  downloading, cleaning, transforming to JSON, and uploading the data###
import requests
from bs4 import BeautifulSoup
import json
import os
import time
from transformers import pipeline
import random

#Insert your list here in the dog_breed variable
dog_breed = ['Akita', 'Alaskan-Malamute', 'American-Foxhound', 'Cane-Corso', 'Dachshund', 'German-Shorthaired-Pointer', 'Miniature-Schnauzer', 'Staffordshire-Bull-Terrier' ]
dogtime_W = {} #For the dogtime website. Most the time the variable matches the other site, so just leave it set to dog_breed. When messed up you have to do the breed individually.
dailypaws_W = {} #For the dailypaws site. Continuing from above Sometimes these two sites mess up the breed name on the url, so you need to insert the name differently.
            #In the dailypaws website, poodle was the only one saved in a different directory. need to copy the whole link directly
final_json_name = 'DD3'
USE_MASKING = True #Data Augmentation by masking then unmasking with the BERT Transformers. Adds about 30 seconds per class
MERGE_EVERY_JSON_IN_FOLDER = True #used for single breed data downloads. Especially when the website has a messed up URL dog breed name.
UPLOAD_TO_HF = True #Upload to huggingface


def dogtime_data(dog_breed):
    # Use the name from dogtime_W if it exists, otherwise use the name from dog_breed
    dogtime_name = dogtime_W.get(dog_breed, dog_breed)

    # This code is specific for this site, as it cleans the data and scrapes all at once.
    url = f'https://dogtime.com/dog-breeds/{dogtime_name}'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check that the request was successful
    if response.status_code != 200:
        print(f'Failed to retrieve {url}. Please check the full name of the specific dog breed on the site. Status code: {response.status_code}')
        return
    if not USE_MASKING:
        time.sleep(5) #Slows down the script so that it doesn't make too many requests to the site at once. The number represents how many seconds to wait PER class
            
    # Parse the HTML content with BeautifulSoup.
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <p> tags and extract the text
    texts = [p.get_text() for p in soup.find_all('p')]

    # Filter out lines that are less than 50 characters long. There are a lot of headers that this will remove.
    texts = [text for text in texts if len(text) >= 55]

    # Join the texts together with newline characters. Removes spaces to prepare for json
    text = '\n'.join(texts)

    # Save the text to a file, utf-8
    with open(f'{dog_breed}1.txt', 'w', encoding='utf-8') as f:
        f.write(text)

    # Find the length of the shortest line in the filtered data. Disabled unless necessary
    """shortest_line_length = min(len(text) for text in texts)

    print(f"The shortest line in the filtered data has {shortest_line_length} characters.")"""

#The function removes blocks of text. To do so, in the For loop you will type the begining and the end of the block of text you want to remove
#in this site there was a lot of generic text that applied to all dogs and not just the specific breed.
def remove_multiple_blocks(filename, blocks):
    # Open the file in read mode and read its content
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    for block in blocks:
        start_text, end_text = block

        # Find the start and end indices of the block of text to remove
        start_index = content.find(start_text)
        end_index = content.find(end_text)

        # If both strings are found in the file
        if start_index != -1 and end_index != -1:
            # Remove the block of text between the two strings
            content = content[:start_index] + content[end_index + len(end_text):]

    # Open the file in write mode and write the updated content
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

#The last function would remove a bunch of generic text, but leave the very last line with the dog breed.
#this removes the last line of the text files
def remove_last_line(filename):
    with open(filename, 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines[:-1]:
            f.write(line)
        f.truncate()

#Since each site has different text data in the <p> values, different cleaning methods are required for each site
def dailypaws_data(dog_breed):
    # Use the name from dogtime_W if it exists, otherwise use the name from dog_breed
    dailypaws_name = dailypaws_W.get(dog_breed, dog_breed)

    # This code is specific for this site, as it cleans the data and scrapes all at once.
    url = f'https://www.dailypaws.com/dogs-puppies/dog-breeds/{dailypaws_name}'
    
    # Send a GET request to the URL
    response = requests.get(url)

    # Check that the request was successful
    #No need to slow down time agian, doing it once does it for all the sites
    if response.status_code == 200:
        # Save the page content to a local file
        with open(f'{dog_breed}2.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
    else:
        print(f'Failed to retrieve {url}. Please check the full name of the specific dog breed on the site.  Status code: {response.status_code}')
        return

    with open(f'{dog_breed}2.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find all <p> tags and extract the text
    texts = [p.get_text() for p in soup.find_all('p')]

    # Join the texts together with newline characters
    text = '\n'.join(texts)

    # Save the text to a file
    with open(f'{dog_breed}2.txt', 'w', encoding='utf-8') as f:
        f.write(text)


#The following function combines all the text files from each website per class
def merge_files(filenames, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for fname in filenames:
            with open(fname, encoding='utf-8') as infile:
                outfile.writelines(infile.readlines())

#There were still short author bios leftover after merging. The function below removes them
def remove_lines(filename, lines_to_remove):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(filename, 'w', encoding='utf-8') as f:
        for i, line in enumerate(lines):
            if i+1 not in lines_to_remove:
                f.write(line)


###Formatting the data into JSON
def process_file(dog_breed):
    #removes any blank lines
    def remove_blank_lines(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines = [line for line in lines if line.strip()]

        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(lines)
    #adds a backslash before any double quotation marks
    #IMPORTANT TO DO BEFORE ADDING THE JSON FORMATTING
    def replace_quotes(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            contents = file.read()

        contents = contents.replace('"', '\\"')

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(contents)
    #Adds the JSON style formatting to the begining of the line
    def format_beg_of_line(filename, text):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines = [text + line for line in lines]

        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(lines)
    #Used to add the JSON format to the end of lines, including the label
    def format_end_of_line(filename, text):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines = [line.rstrip('\n') + text + '\n' for line in lines]

        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(lines)
    #Adds an open and close bracket to the begining and end of the whole json file
    def add_brackets(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines[0] = '[' + lines[0]
        lines[-1] = lines[-1].rstrip(',\n') + ']\n'

        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(lines)
    #finally converts it to json format
    def convert_txt_to_json(txt_path, json_path):
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            content = txt_file.read()

        data = json.loads(content)

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)

    filename = f'{dog_breed}.txt'
    json_path = f'{dog_breed}.json'

    remove_blank_lines(filename)
    replace_quotes(filename)
    format_beg_of_line(filename, f'{dog_breed}: ')
    format_beg_of_line(filename, '{"text": "')
    format_end_of_line(filename, f'", "label": "Please tell me something interesting about the {dog_breed} Dog"')
    format_end_of_line(filename, '},')
    add_brackets(filename)
    convert_txt_to_json(filename, json_path)


# Initialize the fill-mask pipeline with distilbert
#This goes outside the def function because we don't want it within the loop. Only need to call it once, not once per breed
#calling it multiple times is highly inefficient
if USE_MASKING:
    fill_mask = pipeline(
        "fill-mask",
        model="distilbert-base-cased",
        tokenizer="distilbert-base-cased"
    )

def mask_and_unmask(dog_breed, n=4):
    def apply_mask_unmask(text):
        # Apply n masks to the text
        for _ in range(n):
            words = text.split()
            mask_positions = [i for i, word in enumerate(words) if word.isalpha()]
            if not mask_positions:
                break
            mask_pos = random.choice(mask_positions)
            words[mask_pos] = fill_mask.tokenizer.mask_token
            text = " ".join(words)
            
            # Unmask
            predictions = fill_mask(text)
            text = predictions[0]['sequence']
        return text

    # Load the data from the input JSON file
    with open(f'{dog_breed}.json', 'r') as f:
        data = json.load(f)

    # Apply the mask and unmask operation to each "text" field
    for item in data:
        item_dog_breed, text = item['text'].split(':', 1)
        # Check if the dog breed matches the target breed
        if item_dog_breed.strip().lower() == dog_breed.lower():
            text = apply_mask_unmask(text.strip())
            item['text'] = f"{item_dog_breed}: {text}"

    # Write the augmented data to a new output JSON file
    with open(f'{dog_breed}_unmasked.json', 'w') as f:
        json.dump(data, f, indent=4)

failed_breeds = []  # List to keep track of breeds that caused errors

for breed in dog_breed: #for loop so that it runs the code for each dog breed
    #try and except so that it skips over any dog breed that doesnt fit in either of the websites.
    try:
        # Call your functions with the current breed
        dogtime_data(breed)
        remove_multiple_blocks(f'{breed}1.txt', [
            (' Advertisement', 'wonderful companions for many years to come.'), 
            ('Looking for the best dog for your apartment?', 'especially when introducing new toys or activities.'),
            ('are often purchased without any clear understanding','and behavioral issues.'),
            ('Finding a reputable dog breeder', 'and behavioral issues.')
        ])
        remove_last_line(f'{breed}1.txt')
        dailypaws_data(breed)
        merge_files([f'{breed}2.txt', f'{breed}1.txt'], f'{breed}.txt')
        remove_lines(f'{breed}.txt', [3,4,5,6])
        process_file(breed)
        if USE_MASKING:
            start_time = time.time()
            mask_and_unmask(breed)
            end_time = time.time()
            print(f"Time taken for mask_and_unmask: {end_time - start_time} seconds")
    except Exception as e:
        print(f"An error occurred with breed {breed}: {str(e)}") 
        failed_breeds.append(breed)  # Add the failed breed to the list
# Print the breeds that caused errors, so we know which ones to do manually. easy fix, just get the exact name from the website.
#I organized the data to match both websites. as of now the only problem breed is poodle

#The below function is to merge all of the JSON files into one. I use it so that it only makes one request to Huggingface instead of 70+
#That's why its after the for loop
def merge_json_files(folder_path, output_file):
  data = []
  for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
      file_path = os.path.join(folder_path, filename)
      with open(file_path, 'r') as f:
        data.append(json.load(f))

  merged_data = sum(data, [])  # Combine all JSON data into a single list
  cleaned_data = [merged_data[0]] + merged_data[1:-1] + [merged_data[-1]]  # Remove extra brackets

  with open(output_file, 'w') as f:
    json.dump(cleaned_data, f, indent=2)  # Save merged JSON with indentation

if MERGE_EVERY_JSON_IN_FOLDER:
    merge_json_files('.', f'{final_json_name}.json')


##upload to huggingface 2
#Below in triple quotations, you need to log in. If you are already logged in, skip this step
#Subprocess allows user to log in using python without actually using the terminal
if UPLOAD_TO_HF:
    import subprocess

    token = "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"

        # Login command using f-strings for secure variable insertion
    login_command = f"huggingface-cli login --token {token}"

        # Call the subprocess module to execute the login command
    subprocess.run(login_command.split())

    from huggingface_hub import HfApi
    api = HfApi()
    api.upload_file( #can also do a whole folder
        path_or_fileobj=f"{final_json_name}.json",
        path_in_repo=f"{final_json_name}.json",
        repo_id="chrismontes/DogData",
        repo_type="dataset",
    )