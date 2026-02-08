from base import Process

def calculate_waiting_time(current: Process, previous: Process = None):
    if previous is None:
        current.waiting_time = 0
    else:
        if previous.waiting_time is None:
            raise ValueError(f"Cannot calculate: Previous Process (PID {previous.pid}) "
                             "has no waiting time set.")
        
        current.waiting_time = previous.waiting_time + previous.burst_time

def calculate_turnaround_time(current: Process):
    if not isinstance(current, Process):
        raise ValueError("Input must be a Process instance.")
        
    if current.waiting_time is None:
        raise ValueError(f"Waiting time for PID {current.pid} must be calculated first.")
    
    current.turnaround_time = current.waiting_time + current.burst_time