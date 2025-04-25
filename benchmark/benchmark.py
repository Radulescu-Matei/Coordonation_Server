import os
import random
import time
import threading
import requests
import csv
URL = "http://100.96.0.2:5000/api/upload"
# Schimbat pentru testare
NR_REQUESTS = 30

paths = [os.path.join("generate_images/test_images", img) for img in os.listdir("generate_images/test_images")]

def vehicle(id, result):
    
    sender = "vehicle " + str(id)
    response_times = []

    for x in range(NR_REQUESTS):
        path = random.choice(paths)
        with open(path, 'rb') as img:
            start = time.time()
            requests.post(URL, files={'image': (os.path.basename(path), img, 'image/jpeg')}, data={'sender': sender})
            stop = time.time()
            response_times.append(stop - start)
        time.sleep(1)
    
    result[id] = response_times

def run(nr_vehicles):
    threads =[]
    results = {}
    for i in range(0, nr_vehicles):
        t = threading.Thread(target = vehicle, args = (i, results))
        t.start(); threads.append(t)
    for t in threads: 
        t.join()

    all_times = [t for ts in results.values() for t in ts]
    writer = csv.writer(open("response_times" + "_" + str(nr_vehicles) + "vehicles_" + str(NR_REQUESTS) + "requests", "w"))
    writer.writerow(["vehicle_id", "response_time"])
    for vehicle_id, times in results.items():
        for response_time in times:
            writer.writerow([vehicle_id, response_time])

if __name__ == "__main__":
    # Pt testare
    nr_vehicles = 1
    run(nr_vehicles)