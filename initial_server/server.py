from flask import Flask, request, jsonify
import cv2
import cv2.aruco as aruco
import time
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
INITIALIZED = False

FINISHED = {}
TARGET_MARKERS = []
VEHICLE_MARKERS = {}

START_TIME = None
FINISH_TIMES = {}

markers = {}
target_markers = None
last_positions = {}

dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

def is_image(file_name):
    return any(file_name.lower().endswith(ext) for ext in EXTENSIONS)

@app.route('/api/initialize', methods=['POST'])
def initialize():
    if 'number_of_route_markers' not in request.form:
        return jsonify({'error': 'Missing number of route markers'}), 400
    if 'number_of_cars' not in request.form:
        return jsonify({'error': 'Missing number of cars'}), 400


    global INITIALIZED
    if INITIALIZED:
        return jsonify({'error': 'Already initialized'}), 400

    INITIALIZED = True

    number_of_route_markers = int(request.form['number_of_route_markers'])

    number_of_cars = int(request.form['number_of_cars'])

    if number_of_route_markers  <= 0 or number_of_cars <= 0:
        return jsonify({'erro': 'Incorrect parameters received'}), 400
    
    global TARGET_MARKERS
    TARGET_MARKERS = range(0, number_of_route_markers)

    global VEHICLE_MARKERS
    VEHICLE_MARKERS = {
        f"vehicle{i+1}": number_of_route_markers  + 2 * i
        for i in range(0, number_of_cars)
    }

    global FINISHED
    FINISHED = {
        number_of_route_markers  + 2 * i: [0] * number_of_route_markers
        for i in range(0, number_of_cars)
    }
    global FINISH_TIMES
    FINISH_TIMES = {
        f"vehicle{i+1}": -1
        for i in range(0, number_of_cars)
    }

    global last_positions
    last_positions = {
        number_of_route_markers + 2 * i: [0 , 0]
        for i in range(number_of_cars)
    }
    return jsonify({'successful': 'Successful initialization'})
@app.route('/api/get_pos', methods=['GET'])
def get_pos():
    if 'sender' not in request.form:
        return jsonify({'error': 'Missing sender field'}), 400
    
    if not INITIALIZED:
        return jsonify({'error': 'Current session has not been initialized yet.'}), 400
    
    sender = request.form['sender']
    if target_markers is not None:
        sx, sy = last_positions[VEHICLE_MARKERS[sender]]
        if 0 not in FINISHED[VEHICLE_MARKERS[sender]]:
            sx, sy = [-999, -999]
        return jsonify({
                'sender': sender,
                'markers_locations': target_markers,
                'your_location': [sx, sy],
            })
    else:
        return jsonify({'error': 'No image has been received yet'}), 400

@app.route('/api/image', methods=['POST'])
def image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image sent'}), 400

    if not INITIALIZED:
        return jsonify({'error': 'Current session has not been initialized yet.'}), 400
    file = request.files['image']
    file_name = secure_filename(file.filename)
    if not is_image(file_name):
        return jsonify({'error': 'Invalid file'}), 400

    image = cv2.imdecode(np.asarray(bytearray(file.read()), dtype="uint8"), cv2.IMREAD_COLOR)

    marker_corners, marker_ids, _ = detector.detectMarkers(image)
    global markers
    if marker_ids is not None:
        centers = [np.mean(corner[0], axis=0).tolist() for corner in marker_corners]
        markers = [{'id': id_, 'center': center} for id_, center in zip(marker_ids.flatten().tolist(), centers)]

    global target_markers
    if target_markers is None:
        global START_TIME
        START_TIME =  time.time()
        target_markers = {
            marker['id']: marker['center']
            for marker in markers
            if marker['id'] in TARGET_MARKERS
        }

    global FINISHED
    global FINISH_TIMES
    global last_positions
    for marker in markers:
        if marker['id']  in last_positions.keys():
            last_positions[marker['id']] = marker['center']

    for car in  VEHICLE_MARKERS.values():
        it = 0
        for center in target_markers.values():
            [x , y] = center
            sx , sy = last_positions[car]
            distance = ((x - sx)**2 + (y - sy)**2) **0.5
            if distance <= 80:
                FINISHED[car][it] = 1
                if 0 not in FINISHED[car]:
                    identifier = "vehicle" + str(car - len(TARGET_MARKERS)  + 1)
                    if FINISH_TIMES[identifier] == -1:
                        FINISH_TIMES[identifier] = str((time.time() - START_TIME)) + "s"
                break
            it += 1
    
    return jsonify({'successful': 'Successful image upload'})

@app.route('/api/get_times', methods=['GET'])
def get_times():
    return jsonify({'finish': FINISH_TIMES}), 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
