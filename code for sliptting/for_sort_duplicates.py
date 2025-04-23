import os
import random

# Path to the folder containing XML files (path is needed)
xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"

# Ensure the folder exists
if not os.path.exists(xml_folder):
    print(f"Error: The folder '{xml_folder}' does not exist!")
    exit()

# Path to the classes.txt file
classes_file = os.path.join(xml_folder, "classes.txt")

# Read all class names from classes.txt
if not os.path.exists(classes_file):
    print("Error: classes.txt not found!")
    exit()

with open(classes_file, "r", encoding="utf-8") as f:
    class_names = [line.strip() for line in f if line.strip()]

# Dictionary to store class file mappings
class_files = {class_name: os.path.join(xml_folder, f"{class_name}.txt") for class_name in class_names}

# Read all class text files and count occurrences
file_counts = {}  # Tracks how many times each XML file appears

for class_name, class_file in class_files.items():
    if not os.path.exists(class_file):
        continue
    with open(class_file, "r", encoding="utf-8") as f:
        for line in f:
            xml_file = line.strip()
            if xml_file:
                file_counts.setdefault(xml_file, []).append(class_name)

# Remove duplicates (keep XML file only in the largest class)
for xml_file, classes in file_counts.items():
    if len(classes) > 1:
        # Find the class with the most XML files
        largest_class = max(classes, key=lambda cls: len(open(class_files[cls]).readlines()))
        # Remove XML file from all other classes
        for cls in classes:
            if cls != largest_class:
                class_file_path = class_files[cls]
                with open(class_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(class_file_path, "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.strip() != xml_file:
                            f.write(line)

# Read updated files, shuffle, and split
for class_name, class_file in class_files.items():
    if not os.path.exists(class_file):
        continue

    # Read the remaining XML files
    with open(class_file, "r", encoding="utf-8") as f:
        xml_files = [line.strip() for line in f if line.strip()]

    if not xml_files:
        continue  # Skip empty classes

    # Shuffle the order
    random.shuffle(xml_files)

    # Calculate split sizes
    total = len(xml_files)
    train_size = int(total * 0.6)
    validate_size = int(total * 0.2)
    test_size = total - train_size - validate_size  # Remaining 20%

    # Split files
    train_files = xml_files[:train_size]
    validate_files = xml_files[train_size:train_size + validate_size]
    test_files = xml_files[train_size + validate_size:]

    # Save new split files
    train_path = os.path.join(xml_folder, f"{class_name}_Train.txt")
    validate_path = os.path.join(xml_folder, f"{class_name}_Validate.txt")
    test_path = os.path.join(xml_folder, f"{class_name}_Test.txt")

    with open(train_path, "w", encoding="utf-8") as f:
        f.write("\n".join(train_files) + "\n")

    with open(validate_path, "w", encoding="utf-8") as f:
        f.write("\n".join(validate_files) + "\n")

    with open(test_path, "w", encoding="utf-8") as f:
        f.write("\n".join(test_files) + "\n")

    print(f"Created: {train_path}, {validate_path}, {test_path}")

print("Processing complete! All splits are saved.")
