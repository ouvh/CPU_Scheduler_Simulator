from abc import ABC, abstractmethod
from collections import deque
from queue import PriorityQueue

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
        self.queue = PriorityQueue()
        self.current_quantum = 0
        self.counter = 0

    def next_process(self):
        # Add newly arrived processes
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            p = self.processes.pop(0)
            p.state = "READY"
            self.queue.put((1,self.counter,p))
            self.counter += 1
           
        


        if self.current_quantum >= self.time_quantum or not self.queue:
            if self.queue:
                # Move current to end
                current = self.queue.get()
                self.queue.put((current[0],self.counter,current[2]))
                self.counter += 1

            self.current_quantum = 0
       
        return self.queue.queue[0][2] if self.queue else None
    
    def remove_from_queue(self):
        self.queue.get()
    
    def add(self,p):
        self.queue.put((1,self.counter,p))
        self.counter += 1


class PriorityRRScheduler(RoundRobinScheduler):
    def __init__(self, processes, time_quantum=4):
        super().__init__(processes,time_quantum)
    

    def next_process(self):
        # Add newly arrived processes
        while self.processes and self.processes[0].arrival_time <= self.current_time:
            p = self.processes.pop(0)
            p.state = "READY"
            self.queue.put((-1 * p.priority,self.counter,p))
            self.counter += 1

        return super().next_process()

    def add(self,p):
        self.queue.put((-1 * p.priority,self.counter,p))
        self.counter += 1
