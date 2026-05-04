import os
import shutil 

# folder names containing the output files
folders = ["output_music", "output_film", "output_game"]

# creates a new folder to store all five combined output files
output_folder = "combined_output"
os.makedirs(output_folder, exist_ok=True)

# set to track unique files and avoid duplicate files
track_files = set()

# iterate through each folder and add non-duplicate files to the combined output folder
for folder in folders:
    for file in os.listdir(folder):
        if file not in track_files:
            track_files.add(file)
            shutil.copy(os.path.join(folder, file), os.path.join("combined_output", file))