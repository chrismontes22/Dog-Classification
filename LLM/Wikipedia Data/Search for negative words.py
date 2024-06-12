"""This script searches for commonly used negative terms in all of the text files within a folder"""

import os
import glob
import re

def search_words_in_files(directory, words):
    # Get a list of all txt files in the specified directory
    files = glob.glob(os.path.join(directory, '*.txt'))

    for word in words:
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                contents = f.read()
                if re.search(r'\b' + word + r'\b', contents):
                    print(f"Word '{word}' found in {file}")

# Usage
search_words_in_files(r'Newdog2', ['Cancer','cancer','death','Dead','Murder, murder', 'blood', "blood", 'bleed', 'Bleed'])

