import os
import random
import time
import threading
import requests
import csv

URL_INITIATE = "http://localhost:5000/api/initialize"
URL_IMAGE = "http://localhost:5000/api/image"
# Schimbat pentru testare
NR_REQUESTS = 60

paths_black_and_white= [os.path.join("generate_images/test_black_and_white_images/3_cars", img) for img in os.listdir("generate_images/test_black_and_white_images/3_cars")]
paths_clored = [os.path.join("generate_images/test_colored_images", img) for img in os.listdir("generate_images/test_colored_images")]
def phone(result):
    
    sender = "vehicle " + str(id)
    response_times = []

    for x in range(NR_REQUESTS):
        path = random.choice(paths_black_and_white)
        with open(path, 'rb') as img:
            start = time.time()
            requests.post(URL_IMAGE, files={'image': (os.path.basename(path), img, 'image/jpeg')})
            stop = time.time()
            response_times.append(stop - start)
        time.sleep(1)
    
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

if __name__ == "__main__":
    nr_of_route_markers = 4
    nr_vehicles = 3
    run(nr_vehicles, nr_of_route_markers)