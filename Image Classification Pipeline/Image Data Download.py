#Image Data Download

import os
import requests
from PIL import Image
from io import BytesIO
import config

#Parameters
search_query = 'cat' #Google Search query
folder_path = search_query.replace(' ', '-')
first_image = 150
last_image = 159 #Google allows max of 100 per run, It will fininsh the last page (set of 10 images)


# Set up your API key and Custom Search Engine ID
api_key = config.google_api_key
cse_id = config.google_cse_id


def google_image_search(query, api_key, cse_id, start_index, num_images=10):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'searchType': 'image',
        'start': start_index,
        'num': num_images
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    return response.json()

def download_image(url, folder_path, image_name, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image_path = os.path.join(folder_path, image_name)
        image.save(image_path)
    except requests.exceptions.Timeout:
        print(f"Request for {url} timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Could not download {url} - {e}")
    except Exception as e:
        print(f"Could not save {url} - {e}")

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

for start_index in range(first_image, last_image + 1, 10):
    search_results = google_image_search(search_query, api_key, cse_id, start_index, num_images=10)
    for i, item in enumerate(search_results.get('items', [])):
        img_url = item['link']
        image_index = start_index + i
        download_image(img_url, folder_path, f'image_{image_index}.jpg')

