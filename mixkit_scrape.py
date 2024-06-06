import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Function to download video and save metadata
def download_videos_and_save_metadata(driver, category_name, category_url):
    # Open the category page
    driver.get(category_url)

    # Wait for the elements to be present
    wait = WebDriverWait(driver, 10)
    if "vertical" in category_url:
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "item-grid-card"))
        )
        video_elements = driver.find_elements(By.CLASS_NAME, "item-grid-card")
    else:
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "item-grid__item"))
        )
        video_elements = driver.find_elements(By.CLASS_NAME, "item-grid__item")

    # Create output directory for the category
    category_dir = os.path.join(output_dir, category_name)
    os.makedirs(category_dir, exist_ok=True)

    # File to store video data
    videos_data_file = os.path.join(category_dir, "videos-data.txt")

    # Check existing videos
    existing_videos = set()
    if os.path.exists(videos_data_file):
        with open(videos_data_file, "r") as f:
            for line in f:
                video_name = line.split("|")[0]
                existing_videos.add(video_name)

    # Loop through each video element and extract the details
    with open(videos_data_file, "a") as f:
        for video_element in video_elements:
            try:
                video_tag = video_element.find_element(By.TAG_NAME, "video")
                video_source = video_tag.get_attribute("src")
                video_source = video_source.replace("360.mp4", "720.mp4")
            except:
                video_source = "No video source found"

            try:
                video_title = video_element.find_element(
                    By.CLASS_NAME, "item-grid-card__title"
                ).text
            except:
                video_title = "No title found"

            try:
                video_description = video_element.find_element(
                    By.CLASS_NAME, "item-grid-card__description"
                ).text
            except:
                video_description = "No description found"

            # Get the video id or name
            video_name = video_source.split("/")[-1]

            # Skip if video already exists
            if video_name in existing_videos:
                print(f"Skipping {video_name}, already downloaded.")
                continue

            # Print the video details
            print("Video Source:", video_source)
            print("Video Title:", video_title)
            print("Video Description:", video_description)
            print("-" * 40)

            # Save the video
            if video_source != "No video source found":
                video_path = os.path.join(category_dir, video_name)
                with requests.get(video_source, stream=True) as r:
                    r.raise_for_status()
                    with open(video_path, "wb") as file:
                        for chunk in r.iter_content(chunk_size=8192):
                            file.write(chunk)

            # Save the video details in the specified format
            f.write(f"{video_name}|{video_title}|{video_description}\n")


# Read categories from source.txt
def read_categories(file_path):
    categories = {}
    with open(file_path, "r") as file:
        for line in file:
            if line.strip() and not line.startswith("mixkit.co"):
                parts = line.strip().split("]")
                category_name = parts[0].strip("[").strip()
                category_max_page = parts[1].strip(" [").strip()
                category_url = parts[2].strip()
                categories[category_name] = (category_url, category_max_page)
    return categories


# Initialize the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Directory for saving output
output_dir = "output/mixkit.co"

# Path to the source file
source_file_path = "source.txt"

# Read categories and their URLs
categories = read_categories(source_file_path)

# # Process each category
for category_name, (category_url, category_max_page) in categories.items():
    # download_videos_and_save_metadata(driver, category_name, category_url)
    print(category_name)
    print(category_max_page)
    print(category_url)

# Close the WebDriver
driver.quit()
