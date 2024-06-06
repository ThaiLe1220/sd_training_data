import os
import shutil


def merge_video_data_and_files(output_dir, merged_dir):
    merged_data_file = os.path.join(merged_dir, "data.txt")

    # Create the merged directory if it doesn't exist
    os.makedirs(merged_dir, exist_ok=True)

    video_data_set = set()

    # Iterate through each category directory
    for category_dir in os.listdir(output_dir):
        category_path = os.path.join(output_dir, category_dir)
        if os.path.isdir(category_path):
            videos_data_file = os.path.join(category_path, "videos-data.txt")
            if os.path.exists(videos_data_file):
                # Open the category's video data file in read mode
                with open(videos_data_file, "r", encoding="utf-8") as f:
                    # Read each line and add it to the set
                    for line in f:
                        parts = line.strip().split("|")
                        if len(parts) == 3:
                            video_name, video_title, video_description = parts
                            if video_title.strip() != "No title found":
                                if video_description.strip() == "No description found":
                                    video_data_set.add(f"{video_name}|{video_title}")
                                else:
                                    video_data_set.add(
                                        f"{video_name}|{video_description}"
                                    )

                                # Copy the video file to the merged directory
                                src_video_path = os.path.join(category_path, video_name)
                                if os.path.exists(src_video_path):
                                    dst_video_path = os.path.join(
                                        merged_dir, video_name
                                    )
                                    shutil.copy(src_video_path, dst_video_path)

    # Sort the video data and write it to the merged data file
    with open(merged_data_file, "w", encoding="utf-8") as merged_file:
        for data in sorted(video_data_set):
            merged_file.write(data + "\n")


# Directory containing the original output data
output_dir = "output/mixkit.co"

# Directory for saving merged data and videos
merged_dir = "output/mixkit.co/__merged__"

# Merge all video data into one file and copy valid videos
merge_video_data_and_files(output_dir, merged_dir)

print(f"All valid video data and files have been merged into {merged_dir}")
