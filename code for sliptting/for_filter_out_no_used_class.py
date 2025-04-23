import os
import xml.etree.ElementTree as ET

# Path to the folder containing XML files (path is needed)
xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"

# Ensure the folder exists
if not os.path.exists(xml_folder):
    print(f"Error: The folder '{xml_folder}' does not exist!")
    exit()

# List the class names to remove (exact match is used).
classes_to_remove = ["Fire_Blanket", "Flashing_Light_Orbs"]

# Walk through all subfolders and files in the base directory.
for root_dir, subdirs, files in os.walk(xml_folder):
    for file in files:
        if file.lower().endswith(".xml"):
            xml_path = os.path.join(root_dir, file)
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                removed_objects = False

                # Find all object elements
                for obj in root.findall("object"):
                    name_elem = obj.find("name")
                    if name_elem is not None and name_elem.text in classes_to_remove:
                        # Remove the <object> element from the root
                        root.remove(obj)
                        removed_objects = True

                # If any objects were removed, overwrite the file with the updated XML.
                if removed_objects:
                    tree.write(xml_path)
                    print(f"Updated: {xml_path}")
            except ET.ParseError:
                print(f"Parse error in: {xml_path}")
            except Exception as e:
                print(f"Error processing {xml_path}: {e}")
