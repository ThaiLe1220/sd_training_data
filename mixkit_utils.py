import os
import cv2


def get_video_resolution(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cap.release()
    return width, height


def save_resolutions(directory, output_file):
    with open(output_file, "w") as file:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".mp4"):
                    video_path = os.path.join(root, filename)
                    resolution = get_video_resolution(video_path)
                    if resolution:
                        file.write(f"{filename}|{resolution[0]}x{resolution[1]}\n")


# Directory containing the .mp4 files
video_directory = (
    "/home/ubuntu/Desktop/Eugene/sd_training_data/output/mixkit.co/__merged__"
)

# Output file path
output_file_path = "/home/ubuntu/Desktop/Eugene/sd_training_data/output/mixkit.co/__merged__/resolution.txt"

save_resolutions(video_directory, output_file_path)


import os


def load_resolutions(file_path):
    resolutions = {}
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split("|")
            if len(parts) == 2:
                resolutions[parts[0]] = parts[1]
    return resolutions


def merge_and_sort_files(data_file_path, resolution_file_path, output_file_path):
    resolutions = load_resolutions(resolution_file_path)
    merged_data = []

    with open(data_file_path, "r") as data_file:
        for line in data_file:
            parts = line.strip().split("|")
            if len(parts) == 2:
                video_name = parts[0]
                description = parts[1]
                resolution = resolutions.get(video_name, "Unknown")
                merged_data.append((video_name, resolution, description))

    # Sort the merged data by video ID (assuming video ID is the part before the first dash in the video name)
    merged_data.sort(key=lambda x: int(x[0].split("-")[0]))

    with open(output_file_path, "w") as output_file:
        for data in merged_data:
            output_file.write(f"{data[0]}|{data[1]}|{data[2]}\n")


# Paths to the input and output files
data_file_path = (
    "/home/ubuntu/Desktop/Eugene/sd_training_data/output/mixkit.co/__merged__/data.txt"
)
resolution_file_path = "/home/ubuntu/Desktop/Eugene/sd_training_data/output/mixkit.co/__merged__/resolution.txt"
output_file_path = "/home/ubuntu/Desktop/Eugene/sd_training_data/output/mixkit.co/__merged__/data_c.txt"

merge_and_sort_files(data_file_path, resolution_file_path, output_file_path)
