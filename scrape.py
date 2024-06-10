import os
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

#function for saving the video 
def save_video(video_data):
    video_source, category_dir, video_name = video_data
    video_path = os.path.join(category_dir, video_name)
    with requests.get(video_source, stream=True) as r:
        r.raise_for_status()
        with open(video_path, "wb") as file:
            for chunk in r.iter_content(chunk_size=8192):
                file.write(chunk)

#function to process a video element
def process_video_element(video_element, existing_videos, category_dir):
    try:
        video_tag = video_element.find('video')
        video_source = video_tag['src']
        video_source = video_source.replace("360.mp4", "720.mp4")
    except:
        video_source = "No video source found"
    
    try:
        title_element = video_element.find('h2', class_='item-grid-card__title')
        video_title = title_element.find('a').get_text(strip=True)
    except:
        video_title = "No title found"

    try:
        desc_element = video_element.find('p', class_='item-grid-card__description')
        video_description = desc_element.get_text(strip=True)
    except:
        video_description = "No description found"

    #getting the video id for the name
    video_name = video_source.split("/")[-1]

    #check if the video alr exists, if so skip
    if video_name in existing_videos:
        print(f"Skipping {video_name}, already downloaded.")
        return None

    #printing out video details
    print("Video Source:", video_source)
    print("Video Title:", video_title)
    print("Video Description:", video_description)
    print("-" * 40)

    #return video details in specified format if there is a video src
    if video_source != "No video source found":
        return (video_source, category_dir, video_name), f"{video_name}|{video_title}|{video_description}\n"

#function to process all videos on the page, save it an d download videos
def download_videos_and_save_metadata(category_name, category_url, existing_videos):
    #opening the page
    html = requests.get(category_url)
    soup = BeautifulSoup(html.content, 'html.parser')

    #finding all the video elements
    video_elements = soup.find_all('div', class_='item-grid__item')
    
    #creating an output directory for the category
    category_dir = os.path.join(output_dir, category_name)
    os.makedirs(category_dir, exist_ok=True)
    
    #file to save the data and lists for the data
    videos_data_file = os.path.join(category_dir, "videos-data.txt")
    video_data_list = []
    video_data_entries = []

    #looping through each video element
    for video_element in video_elements:
        result = process_video_element(video_element, existing_videos, category_dir)
        if result:
            video_data, data_entry = result
            video_data_list.append(video_data)
            video_data_entries.append(data_entry)

    #saving the video details to the file
    with open(videos_data_file, "a", encoding="utf-8") as f:
        f.writelines(video_data_entries)
    
    #using this to download multiple videos concurrently, making the process quicker
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(save_video, video_data_list)

#function to read category details
def read_categories(file_path):
    categories = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip() and not line.startswith("mixkit.co"):
                parts = line.strip().split("]")
                category_name = parts[0].strip("[").strip()
                category_max_page = int(parts[1].strip(" [").strip())
                category_url = parts[2].strip()
                categories[category_name] = (category_url, category_max_page)
    return categories

#function to load already existing videso
def load_existing_videos(category_dir):
    videos_data_file = os.path.join(category_dir, "videos-data.txt")
    existing_videos = set()
    if os.path.exists(videos_data_file):
        with open(videos_data_file, "r", encoding="utf-8") as f:
            for line in f:
                video_name = line.split("|")[0]
                existing_videos.add(video_name)
    return existing_videos

#defining output directory, soure file and number of worker threads
output_dir = "output/mixkit.co"
source_file_path = "source.txt"
max_workers = 24 #because there are 24 videos max on a single page 

#reading categories and their urls
categories = read_categories(source_file_path)

#processing each category 
for category_name, (category_url, category_max_page) in categories.items():
    category_dir = os.path.join(output_dir, category_name)
    existing_videos = load_existing_videos(category_dir)
    
    #processing each page in the category
    for page in range(1, category_max_page + 1):
        start_time = time.time()
        page_url = f"{category_url}?page={page}"
        
        print("-" * 40)
        print(f"Page {page} out of {category_max_page}")
        print("-" * 40)

        download_videos_and_save_metadata(category_name, page_url, existing_videos)
        print("Process took %s seconds" %(time.time() - start_time))