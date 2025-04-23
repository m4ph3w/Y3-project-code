import os
import shutil

# Path to the folder containing XML files (path is needed)
xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"

# Ensure the folder exists
if not os.path.exists(xml_folder):
    print(f"Error: The folder '{xml_folder}' does not exist!")
    exit()

# Get all class split text files (e.g., Fire_Extinguisher_Train.txt)
split_files = [f for f in os.listdir(xml_folder) if f.endswith("_Train.txt") or f.endswith("_Validate.txt") or f.endswith("_Test.txt")]

# Process each split file
for split_file in split_files:
    # Extract the class name and split type (e.g., Fire_Extinguisher_Train)
    split_name = os.path.splitext(split_file)[0]  # Remove .txt extension

    # Create a new folder for this split
    split_folder = os.path.join(xml_folder, split_name)
    os.makedirs(split_folder, exist_ok=True)

    # Read the XML filenames from the split file
    split_file_path = os.path.join(xml_folder, split_file)
    with open(split_file_path, "r", encoding="utf-8") as f:
        xml_files = [line.strip() for line in f if line.strip()]

    # Move each XML file and its corresponding JPG file
    for xml_file in xml_files:
        xml_path = os.path.join(xml_folder, xml_file)
        jpg_path = os.path.join(xml_folder, xml_file.replace(".xml", ".jpg"))

        # Move XML file if it exists
        if os.path.exists(xml_path):
            shutil.move(xml_path, os.path.join(split_folder, xml_file))
        else:
            print(f"Warning: {xml_file} not found!")

        # Move JPG file if it exists
        if os.path.exists(jpg_path):
            shutil.move(jpg_path, os.path.join(split_folder, os.path.basename(jpg_path)))
        else:
            print(f"Warning: {jpg_path} not found!")

    print(f"Moved files to {split_folder}")

print("Processing complete! All files moved to respective folders.")
