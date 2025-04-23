import os
import shutil

# Path to the folder containing XML files (path is needed)
xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"

# Ensure the folder exists
if not os.path.exists(xml_folder):
    print(f"Error: The folder '{xml_folder}' does not exist!")
    exit()

# Get available class names from folder names
available_classes = set()
for folder in os.listdir(xml_folder):
    if folder.endswith("_Train") or folder.endswith("_Validate") or folder.endswith("_Test"):
        class_name = folder.rsplit("_", 1)[0]  # Extract the class name (before _Train/_Validate/_Test)
        available_classes.add(class_name)

# Convert to a sorted list for selected
available_classes = sorted(available_classes)

# Display available classes
print("\nAvailable Classes:")
for i, cls in enumerate(available_classes, 1):
    print(f"{i}. {cls}")

# Ask what datasets to combine
selected_classes = input("\nEnter the class names to combine (comma-separated, e.g., Fire_Extinguisher, Fire_Exit): ").strip().split(",")

# Normalize the inputs (remove spaces and ensure valid classes)
selected_classes = [cls.strip() for cls in selected_classes if cls.strip() in available_classes]

if not selected_classes:
    print("No valid classes selected. Exiting.")
    exit()

print(f"\nCombining datasets for: {', '.join(selected_classes)}")

# Define the destination folders for Train, Validate, and Test
train_folder = os.path.join(xml_folder, "Train")
validate_folder = os.path.join(xml_folder, "Validate")
test_folder = os.path.join(xml_folder, "Test")

# Create combined folders if they don't exist
os.makedirs(train_folder, exist_ok=True)
os.makedirs(validate_folder, exist_ok=True)
os.makedirs(test_folder, exist_ok=True)

# Function to copy files from a class-specific folder to a combined folder
def copy_files(src_folder, dest_folder):
    if os.path.exists(src_folder):
        for file in os.listdir(src_folder):
            src_path = os.path.join(src_folder, file)
            dest_path = os.path.join(dest_folder, file)
            
            # Avoid overwriting if the file already exists
            if not os.path.exists(dest_path):
                shutil.copy2(src_path, dest_path)
            else:
                print(f"Skipping duplicate: {dest_path}")

# Copy files into the correct combined dataset folders
for cls in selected_classes:
    for split, dest_folder in [("Train", train_folder), ("Validate", validate_folder), ("Test", test_folder)]:
        class_folder = os.path.join(xml_folder, f"{cls}_{split}")
        copy_files(class_folder, dest_folder)

print("\nDataset combination complete! Check the following folders:")
print(f"- {train_folder}")
print(f"- {validate_folder}")
print(f"- {test_folder}")
