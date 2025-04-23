import os
import xml.etree.ElementTree as ET

# Path to the folder containing XML files (path is needed)
xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"

# Ensure the folder exists
if not os.path.exists(xml_folder):
    print(f"Error: The folder '{xml_folder}' does not exist!")
    exit()

# Output files
output_file = os.path.join(xml_folder, "output.txt")  # Stores file names and object classes
classes_file = os.path.join(xml_folder, "classes.txt")  # Stores unique object classes found

# Initialize a set to store unique classes
unique_classes = set()

# Open output file for writing
with open(output_file, "w") as out_f:
    for i in range(1452):  # Loop from 0000.xml to 1451.xml
        xml_filename = f"{i:04d}.xml"  # Generates filenames like 0000.xml, 0001.xml, etc.
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
                    unique_classes.add(class_name)  # Add to global class set

            # Write to output file if objects exist
            if object_classes:
                out_f.write(f"{xml_filename} | {', '.join(sorted(object_classes))}\n")
        
        except ET.ParseError:
            print(f"Error parsing {xml_filename}, skipping.")

# Save unique classes to a separate file
with open(classes_file, "w") as class_f:
    for class_name in sorted(unique_classes):
        class_f.write(f"{class_name}\n")

print(f"Processing complete! Check '{output_file}' and '{classes_file}'.")
