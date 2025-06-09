import os
import random
import cv2
import numpy as np
import cv2.aruco as aruco

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'test_completion')
os.makedirs(OUTPUT_DIR, exist_ok=True)

background_path = os.path.join(SCRIPT_DIR, 'background_photo.jpg')
background = cv2.imread(background_path)
h, w = background.shape[:2]

marker_size = 100
dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

cx, cy = (w + 300) // 2, (h + 300) // 2
offset = marker_size + 20
fixed_positions = {
    1: (cx - offset - marker_size // 2, cy - offset - marker_size // 2),
    2: (cx + marker_size // 2,        cy - offset - marker_size // 2),
    3: (cx - offset - marker_size // 2, cy + marker_size // 2),
    4: (cx + marker_size // 2,        cy + marker_size // 2),
}

static_distance = marker_size + 10

def rects_overlap(x1, y1, size, x2, y2):
    return not (x1 + size <= x2 or x2 + size <= x1 or y1 + size <= y2 or y2 + size <= y1)

def find_random_non_overlapping():
    max_x = w - marker_size
    max_y = h - marker_size - static_distance

    while True:
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)
        overlap = False
        for fx, fy in fixed_positions.values():
            if rects_overlap(x, y, marker_size, fx, fy):
                overlap = True
                break
            if rects_overlap(x, y + static_distance, marker_size, fx, fy):
                overlap = True
                break
        if not overlap:
            return x, y

def overlap_position(static_id):
    fx, fy = fixed_positions[static_id]
    overlap_offset = marker_size // 2
    x = fx + overlap_offset
    y = fy + overlap_offset
    x = min(max(0, x), w - marker_size)
    y = min(max(0, y), h - marker_size - static_distance)
    return x, y

scenarios = [
    ('random', find_random_non_overlapping())
]
for sid in range(1, 5):
    scenarios.append((f'overlap_{sid}', overlap_position(sid)))

target_w = w // 2
target_h = h // 2

for idx, (name, (cx_car, cy_car)) in enumerate(scenarios):
    img = background.copy()
    if idx == 0:
        for fixed_id, (sx, sy) in fixed_positions.items():
            marker = aruco.generateImageMarker(dictionary, fixed_id, marker_size)
            marker_color = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
            img[sy : sy + marker_size, sx : sx + marker_size] = marker_color 

    front_marker = aruco.generateImageMarker(dictionary, 5, marker_size)
    img[cy_car : cy_car + marker_size, cx_car : cx_car + marker_size] = cv2.cvtColor(front_marker, cv2.COLOR_GRAY2BGR)

    bx, by = cx_car, cy_car + static_distance
    back_marker = aruco.generateImageMarker(dictionary, 6, marker_size)
    img[by : by + marker_size, bx : bx + marker_size] = cv2.cvtColor(back_marker, cv2.COLOR_GRAY2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    small = cv2.resize(gray, (target_w, target_h), interpolation=cv2.INTER_AREA)

    filename = f"marker_photo{idx + 1}.jpg"
    outfile = os.path.join(OUTPUT_DIR, filename)
    cv2.imwrite(outfile, small)

