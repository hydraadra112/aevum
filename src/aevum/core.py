from typing import List, Dict
from aevum.types import Process, ProcessResult
from aevum.policies import SchedulerPolicy

class Clock:
    def __init__(self):
        self._time = 0

    @property
    def time(self) -> int:
        return self._time

    def tick(self) -> int:
        """Advance the system heartbeat by 1 unit."""
        self._time += 1
        return self._time

class SimulationEngine:
    def __init__(self, policy: SchedulerPolicy):
        self.policy = policy
        self.clock = Clock()
        self.results: List[ProcessResult] = []
        self.trace_log: List[str] = []
        
    def run(self, processes: List[Process]) -> Dict:
        """
        The main logic for process execution with policies for queue and process handling

        Args:
            processes(list[Process]): A list of processes that you wish to execute

        Returns:
            dict: A dictionary formatted output
        """
        if not processes:
            raise ValueError("Process list is empty")
            
        # 1. Setup
        incoming = list(processes) # Copy to avoid messing up original list
        ready_queue: List[Process] = []
        remaining_times = {p.pid: p.burst_time for p in incoming}
        
        current_process: Process = None
        current_job_runtime = 0 # Tracks how long current job has been running (for RR)

        # 2. The Loop
        while incoming or ready_queue or current_process:
            
            # A. Handle Arrivals
            # We check arrivals before asking the policy so the policy sees everyone
            while incoming and incoming[0].arrival_time <= self.clock.time:
                new_proc = incoming.pop(0)
                ready_queue.append(new_proc)
                self.trace_log.append(f"T={self.clock.time}: Process {new_proc.pid} arrived.")

            # B. Ask Policy for Decision (Policy Responsibility)
            # We pass the mutable ready_queue so the policy can pop/append if needed
            next_process = self.policy.get_next_process(
                ready_queue, 
                current_process, 
                current_job_runtime, 
                remaining_times
            )

            # TODO: Add Dispatcher class to handle context switching
            
            # C. Detect Context Switch
            if next_process != current_process:
                if current_process: 
                    # We are switching AWAY from someone
                    pass 
                if next_process:
                    self.trace_log.append(f"T={self.clock.time}: Context Switch -> Process {next_process.pid}")
                
                current_process = next_process
                current_job_runtime = 0 # Reset runtime tracker for the new guy

            # D. Execute System Tick
            if current_process:
                remaining_times[current_process.pid] -= 1
                current_job_runtime += 1
                
                # Check Completion
                if remaining_times[current_process.pid] == 0:
                    self._record_completion(
                        current_process, 
                    )
                    current_process = None # Job done, CPU is free
                    current_job_runtime = 0

            self.clock.tick()

        return self._get_output()

    def _record_completion(self, process: Process):
        """Helper to calculate metrics when a process finishes."""
        completion_time = self.clock.time + 1 # +1 because we finish at end of tick
        turnaround = completion_time - process.arrival_time
        wait = turnaround - process.burst_time
        
        self.results.append(ProcessResult(
            process, wait, turnaround, completion_time
        ))
        self.trace_log.append(f"T={completion_time}: Process {process.pid} FINISHED.")

    def _get_output(self) -> Dict:
        """Standardized dictionary output."""
        avg_wait = sum(r.waiting_time for r in self.results) / len(self.results)
        avg_tat = sum(r.turnaround_time for r in self.results) / len(self.results)
        
        return {
            "individual_results": [
                {
                    "pid": r.process.pid,
                    "wait": r.waiting_time,
                    "turnaround": r.turnaround_time,
                    "completion": r.completion_time
                } for r in self.results
            ],
            "averages": {
                "avg_waiting_time": round(avg_wait, 2),
                "avg_turnaround_time": round(avg_tat, 2)
            },
            "trace": self.trace_log
        }