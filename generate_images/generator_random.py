import cv2
import numpy as np
import os
import random
import cv2.aruco as aruco

#incercare de teste
OUTPUT_FOLDER = 'test_images'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Background image of a floor
background = cv2.imread('background_photo.jpg')

# Aruco markers parameters
marker_size = 100 # 100 px size of generated marker
dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

nr_images = 300

# Background margins
max_x = background.shape[1] - marker_size
max_y = background.shape[0] - 4 * marker_size

for i in range(nr_images):
    # Numar aleator de markere
    nr_markers = random.randint(0, 3)
    copy = background.copy()

    for j in range(nr_markers):
        marker_id = random.randint(0, 99)
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)

        marker = aruco.generateImageMarker(dictionary, marker_id, marker_size)
        # Imread : (height, width,  colors)
        marker_color = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)

        copy[y:y+marker_size, x:x+marker_size] = marker_color

    # 300 de poze pt dataset
    output_path = os.path.join(OUTPUT_FOLDER, f"marker_photo{i}.jpg")
    cv2.imwrite(output_path, copy)

