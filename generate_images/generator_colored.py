import os
import cv2
import numpy as np
import random

import cv2.aruco as aruco


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


number_of_cars = 1

PARENT_FOLDER_NAME = 'test_colored_images'

PARENT_FOLDER = os.path.join(SCRIPT_DIR, PARENT_FOLDER_NAME)

SUBFOLDER = f"{number_of_cars}_cars"
OUTPUT_FOLDER = os.path.join(PARENT_FOLDER, SUBFOLDER)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


background_path = os.path.join(SCRIPT_DIR, 'background_photo.jpg')
background = cv2.imread(background_path)
if background is None:
    raise FileNotFoundError(f"Cannot find 'background_photo.jpg' in {SCRIPT_DIR!r}")

h, w = background.shape[:2]


marker_size = 100
dictionary  = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

nr_images = 300

static_distance = marker_size + 10

max_x = w - marker_size
max_y = h - marker_size - static_distance


cx, cy = w // 2, h // 2
offset = marker_size + 20

fixed_positions = {
    0: (cx - offset - marker_size // 2, cy - offset - marker_size // 2),
    1: (cx + marker_size // 2,        cy - offset - marker_size // 2),
    2: (cx - offset - marker_size // 2, cy + marker_size // 2),
    3: (cx + marker_size // 2,        cy + marker_size // 2),
}

for i in range(nr_images):
    img = background.copy()

    for fixed_id, (fx, fy) in fixed_positions.items():
        marker = aruco.generateImageMarker(dictionary, fixed_id, marker_size)
        marker_color = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
        img[fy : fy + marker_size, fx : fx + marker_size] = marker_color

    for car_idx in range(number_of_cars):
        front_id = len(fixed_positions) + 2 * car_idx
        back_id  = len(fixed_positions) + 1 + 2 * car_idx

        x = random.randint(0, max_x)
        y = random.randint(0, max_y)

        front_marker = aruco.generateImageMarker(dictionary, front_id, marker_size)
        front_color  = cv2.cvtColor(front_marker, cv2.COLOR_GRAY2BGR)
        img[y : y + marker_size, x : x + marker_size] = front_color

        back_x = x
        back_y = y + static_distance

        back_marker = aruco.generateImageMarker(dictionary, back_id, marker_size)
        back_color  = cv2.cvtColor(back_marker, cv2.COLOR_GRAY2BGR)
        img[back_y : back_y + marker_size, back_x : back_x + marker_size] = back_color

    filename = f"marker_photo_{i:d}.jpg"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    cv2.imwrite(output_path, img)

