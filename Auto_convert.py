import json
import os
import glob
import time
import numpy as np

def convert_labelme_to_yolo(json_path, output_dir, class_list):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {json_path}. Skipping.")
        return

    image_height = data.get('imageHeight')
    image_width = data.get('imageWidth')

    if image_height is None or image_width is None:
        print(f"Image height or width missing in {json_path}. Skipping.")
        return

    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(json_path))[0] + '.txt')

    with open(output_path, 'w') as outfile:
        for shape in data.get('shapes', []):
            label = shape.get('label')
            points = shape.get('points')

            if label is None or points is None or not points:
                print(f"Shape data incomplete in {json_path}. Skipping shape.")
                continue

            try:
                class_id = class_list.index(label)
            except ValueError:
                print(f"Label '{label}' not found in class list. Skipping shape.")
                continue

            
            points = np.array(points)
            xmin, ymin = points.min(axis=0)
            xmax, ymax = points.max(axis=0)

            x_center = (xmin + xmax) / 2 / image_width
            y_center = (ymin + ymax) / 2 / image_height
            bbox_width = (xmax - xmin) / image_width
            bbox_height = (ymax - ymin) / image_height

            outfile.write(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")

def watch_directory(input_dir, output_dir, class_list):
    os.makedirs(output_dir, exist_ok=True)
    processed_files = set()

    while True:
        json_files = {f for f in glob.glob(os.path.join(input_dir, '*.json')) if f not in processed_files}

        if json_files: 
            for json_file in json_files:
                convert_labelme_to_yolo(json_file, output_dir, class_list)
                processed_files.add(json_file)

        time.sleep(1)

if __name__ == "__main__":
    input_dir = 'images'
    output_dir = 'labels'
    class_list = ['Accident']

    watch_directory(input_dir, output_dir, class_list)