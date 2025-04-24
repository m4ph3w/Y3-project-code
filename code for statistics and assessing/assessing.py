import os
import glob
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

def parse_annotation(xml_file):
    """
    Parse a Pascal VOC XML annotation file.
    Returns a list of objects, each a dict with:
      - 'class': class label
      - 'bbox': [xmin, ymin, xmax, ymax]
      - 'score': detection confidence (defaults to 1.0 if not provided)
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    objects = []
    for obj in root.findall('object'):
        cls = obj.find('name').text.strip()
        bbox_node = obj.find('bndbox')
        xmin = int(bbox_node.find('xmin').text)
        ymin = int(bbox_node.find('ymin').text)
        xmax = int(bbox_node.find('xmax').text)
        ymax = int(bbox_node.find('ymax').text)
        # Some prediction XML files might include a score; if missing, default to 1.0.
        score_node = obj.find('score')
        score = float(score_node.text) if score_node is not None else 1.0
        objects.append({'class': cls, 'bbox': [xmin, ymin, xmax, ymax], 'score': score})
    return objects

def compute_iou(box1, box2):
    """
    Compute IoU for two boxes.
    Boxes are expected in [xmin, ymin, xmax, ymax] format.
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)
    box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0

def evaluate_detections(iou_threshold, gt_folder, pred_folder):
    """
    Loop through ground truth and predicted XML files and calculate:
      - Per-class precision, recall, and AP.
      - Confusion matrix counts.
    Assumes that matching between files is done by comparing the numeric ID at the beginning of the filename.
    """
    # Retrieve all XML files from both directories.
    gt_files = glob.glob(os.path.join(gt_folder, '*.xml'))
    pred_files = glob.glob(os.path.join(pred_folder, '*.xml'))

    # Dictionaries keyed by image id (filename here starts with a numeric ID only cuz RoboFlow).
    gt_dict = {}
    for file in gt_files:
        filename = os.path.basename(file)
        m = re.match(r'^(\d+)', filename)
        if m:
            img_id = m.group(1)
            gt_dict[img_id] = file

    pred_dict = {}
    for file in pred_files:
        filename = os.path.basename(file)
        m = re.match(r'^(\d+)', filename)
        if m:
            img_id = m.group(1)
            pred_dict[img_id] = file

    # For AP calculation:
    # For each class, stores a list of tuples (score, is_true_positive)
    class_detections = defaultdict(list)
    # Count total number of ground truth objects per class.
    gt_counter_per_class = defaultdict(int)

    # For confusion matrix: counts for ground truth vs. predicted classes.
    # Count mismatches and the case where either is missing with a 'background' label.
    confusion_counts = defaultdict(lambda: defaultdict(int))
    all_classes = set()

    # Process each image based on the union of ground truth and prediction file IDs.
    all_image_ids = set(gt_dict.keys()).union(pred_dict.keys())
    for img_id in all_image_ids:
        gt_file = gt_dict.get(img_id, None)
        pred_file = pred_dict.get(img_id, None)
        gt_objects = parse_annotation(gt_file) if gt_file is not None else []
        pred_objects = parse_annotation(pred_file) if pred_file is not None else []

        # Update class list and ground truth counts.
        for obj in gt_objects:
            all_classes.add(obj['class'])
            gt_counter_per_class[obj['class']] += 1
        for obj in pred_objects:
            all_classes.add(obj['class'])

        # Keep track of which ground truth boxes have already been matched.
        gt_matched = [False] * len(gt_objects)

        # Sort predictions by score (highest first) for AP computation.
        pred_objects = sorted(pred_objects, key=lambda x: x['score'], reverse=True)

        # For each predicted object, try to match with a ground truth box.
        for pred in pred_objects:
            best_iou = 0
            best_match_idx = -1
            for i, gt in enumerate(gt_objects):
                if not gt_matched[i]:
                    iou = compute_iou(pred['bbox'], gt['bbox'])
                    if iou > best_iou:
                        best_iou = iou
                        best_match_idx = i
            # If a match is found and IoU exceeds the threshold:
            if best_iou >= iou_threshold and best_match_idx != -1:
                gt_match = gt_objects[best_match_idx]
                gt_matched[best_match_idx] = True
                if pred['class'] == gt_match['class']:
                    # Correct detection.
                    class_detections[pred['class']].append((pred['score'], 1))
                    confusion_counts[gt_match['class']][pred['class']] += 1
                else:
                    # Misclassification: count as FP for predicted class.
                    class_detections[pred['class']].append((pred['score'], 0))
                    confusion_counts[gt_match['class']][pred['class']] += 1
            else:
                # No matching ground truth -> false positive.
                class_detections[pred['class']].append((pred['score'], 0))
                confusion_counts['background'][pred['class']] += 1

        # For any ground truth objects not matched, count as false negatives.
        for i, gt in enumerate(gt_objects):
            if not gt_matched[i]:
                confusion_counts[gt['class']]['background'] += 1

    # Calculate per-class precision, recall, and AP.
    results = {}
    for cls in all_classes:
        detections = class_detections[cls]
        if len(detections) == 0:
            results[cls] = {'precision': 0, 'recall': 0, 'AP': 0}
            continue
        # Sort detections by score (descending).
        detections = sorted(detections, key=lambda x: x[0], reverse=True)
        tp = np.array([det[1] for det in detections])
        fp = 1 - tp
        cum_tp = np.cumsum(tp)
        cum_fp = np.cumsum(fp)
        total_gt = gt_counter_per_class[cls]
        recall_curve = cum_tp / total_gt if total_gt > 0 else np.zeros_like(cum_tp)
        precision_curve = cum_tp / (cum_tp + cum_fp + 1e-6)
        # Calculate AP using numerical integration (trapezoidal rule).
        AP = np.trapz(precision_curve, recall_curve)
        results[cls] = {
            'precision': precision_curve[-1],
            'recall': recall_curve[-1],
            'AP': AP
        }
    mAP = np.mean([results[cls]['AP'] for cls in results])
    results['mAP'] = mAP

    return results, confusion_counts, all_classes

def plot_confusion_matrix(confusion_counts, classes):
    """
    Plot a confusion matrix using matplotlib.
    The matrix compares ground truth labels (rows) to predicted labels (columns).
    """
    classes = sorted(list(classes))
    # Include a 'background' category if it exists.
    if 'background' in confusion_counts or any('background' in dic for dic in confusion_counts.values()):
        if 'background' not in classes:
            classes.append('background')
    matrix = np.zeros((len(classes), len(classes)), dtype=int)
    class_to_idx = {cls: idx for idx, cls in enumerate(classes)}
    for gt_cls, preds in confusion_counts.items():
        for pred_cls, count in preds.items():
            if gt_cls not in class_to_idx:
                class_to_idx[gt_cls] = len(class_to_idx)
                classes.append(gt_cls)
            if pred_cls not in class_to_idx:
                class_to_idx[pred_cls] = len(class_to_idx)
                classes.append(pred_cls)
            i = class_to_idx[gt_cls]
            j = class_to_idx[pred_cls]
            matrix[i, j] = count

    plt.figure(figsize=(10, 8))
    plt.imshow(matrix, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("Confusion Matrix")
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    thresh = matrix.max() / 2.0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            plt.text(j, i, format(matrix[i, j], 'd'),
                     horizontalalignment="center",
                     color="white" if matrix[i, j] > thresh else "black")
    plt.ylabel('Ground Truth')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Setting for IoU threshold.
    iou_threshold = float(input("Enter Model Evaluation Maximum Overlap Threshold (e.g. 0.5): "))
    
    # Path to the root folder containing different sub-folders (path is needed).
    xml_folder = r"REPLACE_WITH_PATH_TO_COMBINED_XML_FOLDER"
    
    # Ensure the folder exists (e.g. C:\Users\username\Download\Y3 Proj)
    if not os.path.exists(xml_folder):
        print(f"Error: The folder '{xml_folder}' does not exist!")
        exit()
    
    # Need update accordingly for train and validation (e.g. C:/Users/username/Download/Y3 Proj/)
    gt_folder = os.path.join(xml_folder, "trusted labels", "REPLACE_WITH_TRAIN_OR_VALIDATION_THE_SAME_AS_OTHER_PAIR") # for trusted train sub folder; (e.g. ./trusted labels/train)
    pred_folder = os.path.join(xml_folder, "pseudo labels", "REPLACE_WITH_TRAIN_OR_VALIDATION_THE_SAME_AS_OTHER_PAIR") # for predicted train sub folder; (e.g. ./pseudo labels/train)
    
    # Run evaluation.
    results, confusion_counts, classes = evaluate_detections(iou_threshold, gt_folder, pred_folder)
    
    # Print evaluation results.
    print("Evaluation Results:")
    for cls, metrics in results.items():
        if cls != "mAP":
            print(f"Class {cls}: Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}, AP: {metrics['AP']:.3f}")
    print(f"mAP: {results['mAP']:.3f}")
    
    # Plot the confusion matrix.
    plot_confusion_matrix(confusion_counts, classes)




