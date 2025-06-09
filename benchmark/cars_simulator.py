import os
import random
import time
import threading
import requests
import csv
URL = "http://localhost:5000/api/get_pos"

NR_REQUESTS = 60

def vehicle(id, result):
    
    sender = "vehicle" + str(id + 1)
    response_times = []

    for x in range(NR_REQUESTS):
        start = time.time()
        requests.get(URL, data={'sender': sender})
        stop = time.time()
        response_times.append(stop - start)
        time.sleep(0.5)
    
    result[id] = response_times

def run(nr_vehicles):
    threads =[]
    results = {}
    for i in range(0, nr_vehicles):
        t = threading.Thread(target = vehicle, args = (i, results))
        t.start()
        threads.append(t)
    for t in threads: 
        t.join()

    all_times = [t for ts in results.values() for t in ts]
    writer = csv.writer(open("response_times" + "_" + str(nr_vehicles) + "vehicles_" + str(NR_REQUESTS) + "requests", "w"))
    writer.writerow(["vehicle_id", "response_time"])
    for vehicle_id, times in results.items():
        for response_time in times:
            writer.writerow([vehicle_id, response_time])

if __name__ == "__main__":
    nr_vehicles = 1
    run(nr_vehicles)