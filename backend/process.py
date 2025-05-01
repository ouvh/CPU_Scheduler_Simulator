import random
from dataclasses import dataclass, field

@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    priority: int  # Higher number = higher priority
    io_chance: int = 0  # 0-100% chance of IO block
    remaining_time: int = field(init=False)
    state: str = field(default="NEW", init=False)
    start_time: int = field(default=-1, init=False)
    end_time: int = field(default=-1, init=False)
    wait_time: int = field(default=0, init=False)
    io_blocks: int = field(default=0, init=False)

    def __post_init__(self):
        self.remaining_time = self.burst_time

    def execute_step(self, current_time):
        if self.remaining_time <= 0:
            return "TERMINATED"

        # Check for IO block
        if random.randint(1, 100) <= self.io_chance:
            self.state = "BLOCKED"
            self.io_blocks += 1
            return "BLOCKED"

        # First time running
        if self.start_time == -1:
            self.start_time = current_time
            self.wait_time = current_time - self.arrival_time

        self.remaining_time -= 1
        self.state = "RUNNING"

        if self.remaining_time == 0:
            self.end_time = current_time + 1
            self.state = "TERMINATED"
            return "TERMINATED"
        
        print(self.remaining_time)
        return "RUNNING"

    def reset(self):
        self.remaining_time = self.burst_time
        self.state = "NEW"
        self.start_time = -1
        self.end_time = -1
        self.wait_time = 0
        self.io_blocks = 0