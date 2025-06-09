import os
import time
import json

from flask import Flask, request, jsonify
import redis
import cv2
import cv2.aruco as aruco
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "172.26.40.133")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    
    if not r.exists("INITIALIZED"):
        r.set("INITIALIZED", "0")
    r.set("INITIALIZED", "1")

    number_of_route_markers = int(request.form['number_of_route_markers'])
    number_of_cars = int(request.form['number_of_cars'])
    if number_of_route_markers <= 0 or number_of_cars <= 0:
        return jsonify({'erro': 'Incorrect parameters received'}), 400

    target_markers = list(range(0, number_of_route_markers))
    r.set("TARGET_MARKERS", json.dumps(target_markers))
    r.delete("VEHICLE_MARKERS")
    vehicle_markers = {}
    for i in range(number_of_cars):
        mid = number_of_route_markers + 2 * i
        name = f"vehicle{i+1}"
        vehicle_markers[name] = mid
        r.hset("VEHICLE_MARKERS", name, mid)
    r.delete("FINISHED")
    for i in range(number_of_cars):
        mid = number_of_route_markers + 2 * i
        flags = [0] * number_of_route_markers
        r.hset("FINISHED", mid, json.dumps(flags))
    r.delete("FINISH_TIMES")
    for i in range(number_of_cars):
        name = f"vehicle{i+1}"
        r.hset("FINISH_TIMES", name, "-1")
    r.delete("last_positions")
    for i in range(number_of_cars):
        mid = number_of_route_markers + 2 * i
        pos = [0, 0]
        r.hset("last_positions", str(mid), json.dumps(pos))

    r.delete("START_TIME")
    r.delete("target_marker_centers")
    return jsonify({'successful': 'Successful initialization'}), 200

@app.route('/api/get_pos', methods=['GET'])
def get_pos():
    if 'sender' not in request.form:
        return jsonify({'error': 'Missing sender field'}), 400

    initialized = (r.get("INITIALIZED") == "1")
    if not initialized:
        return jsonify({'error': 'Current session has not been initialized yet.'}), 400

    sender = request.form['sender']

    raw_t = r.get("TARGET_MARKERS")
    if raw_t is None:
        return jsonify({'error': 'No image has been received yet'}), 400
    target_markers = json.loads(raw_t)

    vehicle_map = {k: int(v) for k, v in r.hgetall("VEHICLE_MARKERS").items()}
    if sender not in vehicle_map:
        return jsonify({'error': 'Unknown sender'}), 400
    car_mid = vehicle_map[sender]

    raw_lp = r.hget("last_positions", str(car_mid))
    sx, sy = json.loads(raw_lp)

    raw_finished = r.hget("FINISHED", str(car_mid))
    finished_flags = json.loads(raw_finished)

    if 0 not in finished_flags:
        sx, sy = -999, -999

    return jsonify({
        'sender': sender,
        'markers_locations': target_markers,
        'your_location': [sx, sy],
    })

@app.route('/api/image', methods=['POST'])
def image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image sent'}), 400

    initialized = (r.get("INITIALIZED") == "1")
    if not r.exists("INITIALIZED"):
        return jsonify({'error': 'Current session has not been initialized yet.'}), 400

    if not initialized:
        return jsonify({'error': 'Current session has not been initialized yet.'}), 400

    if not r.exists("START_TIME"):
        r.set("START_TIME", str(time.time()))

    file = request.files['image']
    file_name = secure_filename(file.filename)
    if not is_image(file_name):
        return jsonify({'error': 'Invalid file'}), 400

    image = cv2.imdecode(np.asarray(bytearray(file.read()), dtype="uint8"), cv2.IMREAD_COLOR)

    marker_corners, marker_ids, _ = detector.detectMarkers(image)

    if marker_ids is not None:
        centers = [np.mean(corner[0], axis=0).tolist() for corner in marker_corners]
        markers = [{'id': id_, 'center': center} for id_, center in zip(marker_ids.flatten().tolist(), centers)]

    last_positions = {
        int(k): json.loads(v)
        for k, v in r.hgetall("last_positions").items()
    }

    for marker in markers:
        mid = marker['id']
        if mid in last_positions:
            last_positions[mid] = marker['center']
            r.hset("last_positions", str(mid), json.dumps(marker['center']))


    target_markers = json.loads(r.get("TARGET_MARKERS"))
    t_centers = {
    i: (0, 0)
    for i in target_markers
    }
    if not r.exists("target_marker_centers"):
        for marker in markers:
            if marker['id'] in target_markers:
                t_centers[marker['id']] = marker['center']
        r.set("target_marker_centers", json.dumps(t_centers))

    vehicle_map = {k: int(v) for k, v in r.hgetall("VEHICLE_MARKERS").items()}
    raw_t = r.get("target_marker_centers")
    t_pos = dict(json.loads(raw_t))
    print(t_pos)
    for car in vehicle_map.values():
        raw_flags = r.hget("FINISHED", str(car))
        fcar = json.loads(raw_flags)

        it = 0
        for center in t_pos.values():
            x, y = center
            raw_lp = r.hget("last_positions", str(car))
            sx, sy = json.loads(raw_lp)
            distance = ((x - sx)**2 + (y - sy)**2) ** 0.5
            if distance <= 80:
                print("A ajuns la markerul", it, "cu distanta", distance)
                fcar[it] = 1
                r.hset("FINISHED", str(car), json.dumps(fcar))
                if 0 not in fcar:
                    identifier = "vehicle" + str(car - len(target_markers) + 1)
                    if r.hget("FINISH_TIMES", identifier) == "-1":
                        print("A terminat")
                        elapsed = time.time() - float(r.get("START_TIME"))
                        r.hset("FINISH_TIMES", identifier, str(elapsed) + "s")
                break
            it += 1

    return jsonify({'successful': 'Successful image upload'})

@app.route('/api/get_times', methods=['GET'])
def get_times():
    finish_times_raw = r.hgetall("FINISH_TIMES")
    r.delete("INITIALIZED")
    return jsonify({'finish': finish_times_raw}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
