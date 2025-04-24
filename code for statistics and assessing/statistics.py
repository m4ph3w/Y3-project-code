import os
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

def parse_annotations(annotation_dir):
    """
    Parse Pascal VOC XML annotation files in a directory and compute:
    
    - Total objects count per class.
    - Number of unique images where each class appears.
    
    Args:
        annotation_dir (str): The directory that contains XML annotation files.
    
    Returns:
        total_objects (Counter): Counts of objects per class.
        images_per_class (dict): Counts of images per class (each image counted once per class).
    """
    total_objects = Counter()
    class_image_set = defaultdict(set)
    
    # Iterate over all files in the given directory
    for file in os.listdir(annotation_dir):
        # Check for XML files only
        if file.lower().endswith('.xml'):
            file_path = os.path.join(annotation_dir, file)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Get the filename for identifying the image
                filename_tag = root.find('filename')
                if filename_tag is None:
                    image_id = file  # fallback: use the XML file name
                else:
                    image_id = filename_tag.text.strip()
                
                # Find all objects in the annotation
                objects = root.findall('object')
                for obj in objects:
                    name_tag = obj.find('name')
                    if name_tag is not None:
                        class_name = name_tag.text.strip()
                        total_objects[class_name] += 1
                        class_image_set[class_name].add(image_id)
            except ET.ParseError as e:
                print(f"Error parsing {file_path}: {e}")

    # Convert the set of images for each class to counts (i.e. number of unique images per class)
    images_per_class = {cls: len(image_ids) for cls, image_ids in class_image_set.items()}
    
    return total_objects, images_per_class

if __name__ == '__main__':
    # Path to the folder containing annotated labels by Grounding DINO via Pascal VOC XML files format. (e.g. C:\Users\username\Download\Y3 Proj\predicted labels\train)
    xml_sub_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_SUB_FOLDER"
    
    # Compute statistics
    objects_stats, images_stats = parse_annotations(xml_sub_folder)
    
    # Print overall statistics
    print("Object Counts per Class:")
    for cls, count in objects_stats.items():
        print(f" - {cls}: {count} object(s)")
    
    print("\nImage Counts per Class (number of images in which each class appears):")
    for cls, count in images_stats.items():
        print(f" - {cls}: {count} image(s)")
