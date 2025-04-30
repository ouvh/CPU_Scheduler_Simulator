from abc import ABC, abstractmethod
from collections import deque

class Scheduler(ABC):
    def __init__(self, processes):
        self.processes = sorted(processes, key=lambda p: p.arrival_time)
        self.ready_queue = []
        self.current_time = 0
        self.time_quantum = None

    @abstractmethod
    def next_process(self):
        pass

    def update_wait_times(self):
        for p in self.ready_queue:
            if p.arrival_time <= self.current_time and p.state == "READY":
                p.wait_time += 1

class FCFSScheduler(Scheduler):
    def next_process(self):
        # Add newly arrived processes
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            p = self.processes.pop(0)
            p.state = "READY"
            self.ready_queue.append(p)
        
        return self.ready_queue.pop(0) if self.ready_queue else None

class SJFScheduler(Scheduler):
    def next_process(self):
        # Add newly arrived processes
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            p = self.processes.pop(0)
            p.state = "READY"
            self.ready_queue.append(p)
        
        # Sort by remaining time
        self.ready_queue.sort(key=lambda p: p.remaining_time)
        return self.ready_queue.pop(0) if self.ready_queue else None

class PriorityScheduler(Scheduler):
    def next_process(self):
        # Add newly arrived processes
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            p = self.processes.pop(0)
            p.state = "READY"
            self.ready_queue.append(p)
        
        # Sort by priority (descending) and arrival time
        self.ready_queue.sort(key=lambda p: (-p.priority, p.arrival_time))
        return self.ready_queue.pop(0) if self.ready_queue else None

class RoundRobinScheduler(Scheduler):
    def __init__(self, processes, time_quantum=4):
        super().__init__(processes)
        self.time_quantum = time_quantum
        self.queue = deque()
        self.current_quantum = 0

    def next_process(self):
        # Add newly arrived processes
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            p = self.processes.pop(0)
            p.state = "READY"
            self.queue.append(p)
        
        if self.current_quantum >= self.time_quantum or not self.queue:
            if self.queue and self.queue[0].state != "TERMINATED":
                self.queue.rotate(-1)  # Move current to end
            self.current_quantum = 0
        
        return self.queue[0] if self.queue else None

class PriorityRRScheduler(PriorityScheduler):
    def __init__(self, processes, time_quantum=4):
        super().__init__(processes)
        self.time_quantum = time_quantum
        self.current_quantum = 0

    def next_process(self):
        if self.current_quantum >= self.time_quantum or not self.ready_queue:
            self.current_quantum = 0
            # Re-sort the queue
            self.ready_queue.sort(key=lambda p: (-p.priority, p.arrival_time))
        
        return super().next_process()