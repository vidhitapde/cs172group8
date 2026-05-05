import os
import shutil 
from utils import save_json_file, parse_folder

# folder names containing the output files
folders = ["output_music", "output_film", "output_game(1)", "output_celebrities", "output_tv"]

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

data = parse_folder(output_folder)
base_dir = os.path.dirname(os.path.abspath(__file__))
save_json_file(data, os.path.join(base_dir, "outputs.json"))