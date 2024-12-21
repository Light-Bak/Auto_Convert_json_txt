import json
import os
import glob
import time

def convert_labelme_to_yolo(json_path, output_dir, class_list):
    with open(json_path, 'r') as f:
        data = json.load(f)

    image_height = data['imageHeight']
    image_width = data['imageWidth']

    yolo_annotations = []

    for shape in data['shapes']:
        label = shape['label']
        points = shape['points']
        class_id = class_list.index(label)

        # Find the bounding box coordinates
        xmin = min([p[0] for p in points])
        xmax = max([p[0] for p in points])
        ymin = min([p[1] for p in points])
        ymax = max([p[1] for p in points])

        # Convert to YOLO format
        x_center = (xmin + xmax) / 2 / image_width
        y_center = (ymin + ymax) / 2 / image_height
        bbox_width = (xmax - xmin) / image_width
        bbox_height = (ymax - ymin) / image_height

        yolo_annotations.append(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")

    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(json_path))[0] + '.txt')

    with open(output_path, 'w') as f:
        f.writelines(yolo_annotations)

def watch_directory(input_dir, output_dir, class_list):
    seen_files = set()
    os.makedirs(output_dir, exist_ok=True)

    while True:
        json_files = glob.glob(os.path.join(input_dir, '*.json'))
        new_files = [f for f in json_files if f not in seen_files]

        for json_file in new_files:
            convert_labelme_to_yolo(json_file, output_dir, class_list)
            seen_files.add(json_file)

        time.sleep(1)

if __name__ == "__main__":
    input_dir = 'images'  # Path to the directory containing LabelMe JSON files
    output_dir = 'labels'  # Path to the directory to save YOLO annotations
    class_list = ['Accident']  # Replace with your class names

    watch_directory(input_dir, output_dir, class_list)
