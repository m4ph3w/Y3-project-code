import os
import xml.etree.ElementTree as ET

# Path to the folder containing XML files (path is needed)
xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"

# Ensure the folder exists
if not os.path.exists(xml_folder):
    print(f"Error: The folder '{xml_folder}' does not exist!")
    exit()

# Set output file paths inside the same folder
output_file = os.path.join(xml_folder, "output.txt")
classes_file = os.path.join(xml_folder, "classes.txt")

# Initialize a dictionary to store filenames per class
class_files = {}

# Open output file for writing
with open(output_file, "w", encoding="utf-8") as out_f:
    for i in range(1452):  # Loop from 0000.xml to 1451.xml
        xml_filename = f"{i:04d}.xml"  # Generates filenames: 0000.xml, 0001.xml, etc.
        xml_path = os.path.join(xml_folder, xml_filename)
        
        # Check if the file exists
        if not os.path.exists(xml_path):
            print(f"Skipping {xml_filename}, file not found.")
            continue

        try:
            # Parse XML
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Extract object classes
            object_classes = set()
            for obj in root.findall("object"):
                name_tag = obj.find("name")
                if name_tag is not None:
                    class_name = name_tag.text.strip()
                    object_classes.add(class_name)

                    # Track filenames per class
                    if class_name not in class_files:
                        class_files[class_name] = []
                    class_files[class_name].append(xml_filename)

            # Write to output.txt
            if object_classes:
                out_f.write(f"{xml_filename} | {', '.join(sorted(object_classes))}\n")
        
        except ET.ParseError:
            print(f"Error parsing {xml_filename}, skipping.")

# Save unique classes to a separate file
with open(classes_file, "w", encoding="utf-8") as class_f:
    for class_name in sorted(class_files.keys()):
        class_f.write(f"{class_name}\n")

# Write filenames to individual class files
for class_name, filenames in class_files.items():
    class_file_path = os.path.join(xml_folder, f"{class_name}.txt")
    with open(class_file_path, "w", encoding="utf-8") as class_f:
        for filename in filenames:
            class_f.write(f"{filename}\n")

print(f"Processing complete! Files saved in '{xml_folder}':")
print(f"- {output_file}")
print(f"- {classes_file}")
print(f"- Individual class files (e.g., Fire_Extinguisher.txt, Fire_Suppression_Signage.txt)")
