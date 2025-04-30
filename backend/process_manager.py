import csv
import json
from pathlib import Path
from typing import List
from process import Process
import random

class ProcessManager:
    @staticmethod
    def generate_random_processes(count=5, max_arrival=10, max_burst=10, max_priority=5):
        processes = []
        for pid in range(1, count+1):
            processes.append(Process(
                pid=pid,
                arrival_time=random.randint(0, max_arrival),
                burst_time=random.randint(1, max_burst),
                priority=random.randint(1, max_priority),
                io_chance=random.randint(0, 30)
            ))
        return processes

    @staticmethod
    def save_to_file(processes: List[Process], filename):
        path = Path(filename)
        data = [{
            "pid": p.pid,
            "arrival_time": p.arrival_time,
            "burst_time": p.burst_time,
            "priority": p.priority,
            "io_chance": p.io_chance
        } for p in processes]

        if path.suffix == ".csv":
            with open(path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        elif path.suffix == ".json":
            with open(path, 'w') as f:
                json.dump(data, f)
        else:
            raise ValueError("Unsupported file format")

    @staticmethod
    def load_from_file(filename):
        path = Path(filename)
        processes = []
        
        try:
            if path.suffix == ".csv":
                with open(path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        processes.append(Process(
                            pid=int(row['pid']),
                            arrival_time=int(row['arrival_time']),
                            burst_time=int(row['burst_time']),
                            priority=int(row['priority']),
                            io_chance=int(row.get('io_chance', 0))
                        ))
            elif path.suffix == ".json":
                with open(path, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        processes.append(Process(**item))
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error loading file: {e}")
            return []
        
        return processes