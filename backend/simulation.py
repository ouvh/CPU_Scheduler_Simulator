import time
from typing import Dict, List
import random

from process import Process
from schedulers import *

class CPUSimulation:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.current_process = None
        self.blocked: List[Process] = []
        self.history = []
        self.metrics: Dict = {
            "total_time": 0,
            "cpu_utilization": 0,
            "throughput": 0,
            "avg_turnaround": 0,
            "avg_waiting": 0,
            "total_io_blocks": 0
        }
        self.running = False

    def step(self):
        current_time = self.scheduler.current_time

        # Update blocked processes
        for p in self.blocked[:]:
            if random.random() < 0.3:  # 30% chance to unblock
                p.state = "READY"
                self.scheduler.ready_queue.append(p)
                self.blocked.remove(p)

        # Update wait times for ready processes
        self.scheduler.update_wait_times()

        # Get next process if none running
        if not self.current_process:
            self.current_process = self.scheduler.next_process()


        flag = 0
        # Execute current process
        if self.current_process:
            result = self.current_process.execute_step(current_time)
            
            if result == "BLOCKED":
                self.blocked.append(self.current_process)
                self.current_process = None
            elif result == "TERMINATED":
                self._record_metrics()
                flag = 1
               
            else:
                if isinstance(self.scheduler, (RoundRobinScheduler, PriorityRRScheduler)):
                    self.scheduler.current_quantum += 1

        # Record history for visualization
        self.history.append({
            "time": current_time,
            "running": self.current_process.pid if self.current_process else None,
            "ready": [p.pid for p in self.scheduler.ready_queue if p != self.current_process],
            "blocked": [p.pid for p in self.blocked]
        })
       

        self.scheduler.current_time += 1
        return flag


    def _record_metrics(self):
        p = self.current_process
        turnaround = p.end_time - p.arrival_time
        waiting = p.wait_time
        
        self.metrics["avg_turnaround"] = (
            self.metrics["avg_turnaround"] * self.metrics["throughput"] + turnaround
        ) / (self.metrics["throughput"] + 1)
        
        self.metrics["avg_waiting"] = (
            self.metrics["avg_waiting"] * self.metrics["throughput"] + waiting
        ) / (self.metrics["throughput"] + 1)
        
        self.metrics["throughput"] += 1
        self.metrics["total_io_blocks"] += p.io_blocks

    def calculate_final_metrics(self):
        total_time = self.scheduler.current_time
        busy_time = sum(1 for entry in self.history if entry["running"] is not None)
        
        self.metrics.update({
            "total_time": total_time,
            "cpu_utilization": (busy_time / total_time) * 100 if total_time > 0 else 0,
        })
        return self.metrics