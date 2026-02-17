from .core import Process
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class SchedulerPolicy(ABC):
    """
    The Base Class (Interface) that all schedulers must inherit from.
    """
    @abstractmethod
    def get_next_process(
        self, 
        ready_queue: List[Process], 
        current_process: Optional[Process], 
        current_runtime: int,
        remaining_times: Dict[int, int]
    ) -> Optional[Process]:
    
        """
        Determines which process should occupy the CPU for the next clock tick.

        Args:
            ready_queue (list[Process]): Processes currently waiting for CPU time.
            current_process (Process | None): The process currently occupying the CPU.
            current_runtime (int): Ticks elapsed since the current process started its slice.
            remaining_times (dict[int, int]): Map of PID to remaining burst units.

        Returns:
            Process | None: The process to run next, or None for an idle CPU.
        """
        pass

class FCFS(SchedulerPolicy):
    """
    First-Come, First-Served (FCFS) scheduling policy.
    
    A non-preemptive algorithm where the process that requests the CPU first 
    is allocated the CPU first. It maintains execution until the current 
    process completes or blocks.
    """
    def get_next_process(self, ready_queue, current_process, _current_runtime, _remaining_times):
        # If something is already running, keep running them (Non-preemptive)
        if current_process:
            return current_process
        
        # If CPU is idle, pick the first person in line
        if ready_queue:
            return ready_queue.pop(0)
        
        return None

class SJF(SchedulerPolicy):
    """ Shortest Job First (SJF) scheduling policy.
    
    A non-preemptive algorithm that selects the waiting process with the 
    smallest initial burst time. Once a process starts, it holds the CPU 
    until completion, regardless of new arrivals.
    """
    def get_next_process(self, ready_queue, current_process, _current_runtime, _remaining_times):
        # Non-preemptive: If running, don't stop.
        if current_process:
            return current_process
        
        # Pick the shortest job
        if ready_queue:
            # Find process with smallest burst time
            shortest = min(ready_queue, key=lambda p: p.burst_time)
            ready_queue.remove(shortest)
            return shortest
        
        return None

class STCF(SchedulerPolicy):
    """
    Shortest Time-to-Completion First (STCF) scheduling policy.
    
    A preemptive version of SJF. The scheduler always chooses the process 
    with the shortest remaining time to finish. If a newly arrived process 
    has a shorter remaining burst than the current job, the current job 
    is preempted and returned to the ready queue.
    """
    def get_next_process(self, ready_queue, current_process, _current_runtime, remaining_times):
        if not ready_queue and not current_process:
            return None
        
        # 1. Find the best candidate in the ready queue
        best_in_queue = None
        if ready_queue:
            # Tie-breaker: smallest remaining time, then lower PID
            best_in_queue = min(ready_queue, key=lambda p: (remaining_times[p.pid], p.pid))

        # 2. THE SNIPPET GOES HERE: Decision Logic
        if current_process:
            current_rem = remaining_times[current_process.pid]
            
            # Check if the new arrival is STRICTLY shorter than the current one
            if best_in_queue and remaining_times[best_in_queue.pid] < current_rem:
                # Preempt: Swap them out
                ready_queue.append(current_process)
                ready_queue.remove(best_in_queue)
                return best_in_queue
            
            # No better candidate? Keep running the current process.
            # This ensures (potential_next == current_process) in the Engine.
            return current_process
        
        # 3. CPU was idle, just pick the best from queue
        ready_queue.remove(best_in_queue)
        return best_in_queue

class RR(SchedulerPolicy):
    """
    Round Robin (RR) scheduling policy.
    
    A preemptive, time-sharing algorithm. Each process is assigned a 
    fixed time unit (Time Quantum). If a process does not complete 
    within its quantum, it is preempted and placed at the end of the 
    ready queue to allow the next process a turn.
    """
    def __init__(self, time_quantum: int):
        self.time_quantum = time_quantum

    def get_next_process(self, ready_queue, current_process, current_runtime, _remaining_times):
        # Check if Quantum Expired for the current guy
        if current_process and current_runtime >= self.time_quantum:
            # Preemptive: Move him to the back of the line
            ready_queue.append(current_process)
            current_process = None # Force a re-pick
            
        # 2. If no one is running (or we just preempted), pick head of queue
        if not current_process:
            if ready_queue:
                return ready_queue.pop(0)
            return None

        # Otherwise, keep running the current guy
        return current_process