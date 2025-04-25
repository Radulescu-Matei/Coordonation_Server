from flask import Flask, request, jsonify, send_from_directory
import cv2
import cv2.aruco as aruco
import os
import numpy as np
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Tipuri de imagini
EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

def is_image(file_name):
    return any(file_name.lower().endswith(ext) for ext in EXTENSIONS)

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image sent'}), 400
    
    if 'sender' not in request.form:
        return jsonify({'error': 'Missing sender field'}), 400

    sender = request.form['sender']
    file = request.files['image']

    if not is_image(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    file_name = secure_filename(file.filename)
    image = cv2.imdecode(np.asarray(bytearray(file.read()), dtype="uint8"), cv2.IMREAD_COLOR)


    marker_corners, marker_ids, _ = detector.detectMarkers(image)
    if marker_ids is not None:
        centers = [np.mean(corner[0], axis=0).tolist() for corner in marker_corners]
        markers = [{'id': id_, 'center': center} for id_, center in zip(marker_ids.flatten().tolist(), centers)]

        return jsonify({
            'sender': sender,
            'message': 'Markers locations',
            'markers': markers,
            'image_name': os.path.join(sender, file_name)
        })
    else:
        return jsonify({
            'sender': sender,
            'message': 'No markers',
            'image_name': os.path.join(sender, file_name)
        })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
