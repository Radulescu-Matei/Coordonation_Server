import os
import random
import time
import threading
import requests
import csv
import requests
import json

# server - 100.96.0.2
URL_INITIATE = "http://localhost:5000/api/initialize"
URL_IMAGE = "http://localhost:5000/api/image"
URL_TIMES = "http://localhost:5000/api/get_times"
# Schimbat pentru testare
NR_REQUESTS = 3

paths = [os.path.join("generate_images/test_completion", img) for img in os.listdir("generate_images/test_completion")]
paths_real = [os.path.join("generate_images/test_real", img) for img in os.listdir("generate_images/test_real")]

def phone(result):
    
    sender = "vehicle " + str(id)
    response_times = []

    for x in range(NR_REQUESTS):
        for path in paths_real:
            with open(path, 'rb') as img:
                start = time.time()
                requests.post(URL_IMAGE, files={'image': (os.path.basename(path), img, 'image/jpeg')})
                stop = time.time()
                response_times.append(stop - start)
        time.sleep(0.2)
    
    result[id] = response_times

def run(nr_vehicles, nr_of_route_markers):
    results = {}
    requests.post(URL_INITIATE, data={'number_of_route_markers': nr_of_route_markers, 'number_of_cars': nr_vehicles})
    phone(results)
    all_times = [t for ts in results.values() for t in ts]
    writer = csv.writer(open("response_times" + "_" "images", "w"))
    writer.writerow(["response_time"])
    for vehicle_id, times in results.items():
        for response_time in times:
            writer.writerow([vehicle_id, response_time])

    response = requests.get(URL_TIMES)
    if response.status_code == 200:
        data = response.json()  # {'finish': { '5': 12.34, '7': 15.67, … }}
        finish_dict = data["finish"]

        with open("finish_times_examples.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["vehicle_id", "elapsed_time_seconds"])
            for vehicle_id, time_sec in finish_dict.items():
                writer.writerow([vehicle_id, time_sec])
if __name__ == "__main__":
    nr_of_route_markers = 4
    nr_vehicles = 1
    run(nr_vehicles, nr_of_route_markers)