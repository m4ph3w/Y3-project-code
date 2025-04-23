import os
import shutil

# Path to the folder containing XML files (path is needed)
xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"

# Ensure the folder exists
if not os.path.exists(xml_folder):
    print(f"Error: The folder '{xml_folder}' does not exist!")
    exit()

# Create the paths for the combined Train, Validate, and Test folders.
train_dir = os.path.join(xml_folder, "Train")
validate_dir = os.path.join(xml_folder, "Validate")
test_dir = os.path.join(xml_folder, "Test")

# Create the combined folders they should already been exist
os.makedirs(train_dir, exist_ok=True)
os.makedirs(validate_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# Loop through everything in the base directory
for folder_name in os.listdir(xml_folder):
    folder_path = os.path.join(xml_folder, folder_name)
    
    # Only proceed if it's actually a folder and follows the naming convention
    if not os.path.isdir(folder_path):
        continue
    
    # Check the suffix of the folder name to determine which big folder to move into
    if folder_name.endswith("_Train"):
        target_dir = train_dir
    elif folder_name.endswith("_Validate"):
        target_dir = validate_dir
    elif folder_name.endswith("_Test"):
        target_dir = test_dir
    else:
        # If it doesnt match any known pattern, skip
        continue

    # Move all files from the subfolder to the chosen target folder
    for file_name in os.listdir(folder_path):
        src_path = os.path.join(folder_path, file_name)
        dest_path = os.path.join(target_dir, file_name)
        
        # If the destination file already exists, skip to avoid overwriting
        if os.path.exists(dest_path):
            print(f"Skipping duplicate: {dest_path}")
            continue
        
        # Cut and paste the file
        shutil.move(src_path, dest_path)
    
    # Uncomment below for deleting the now-empty subfolders
    # os.rmdir(folder_path)

print("\nAll files have been moved to:")
print(f"  {train_dir}")
print(f"  {validate_dir}")
print(f"  {test_dir}")
