from .types import Process, StatsCollector, Clock, Tracer, Core
from .policies import SchedulerPolicy

from typing import List, Dict
from abc import ABC, abstractmethod

class BaseEngine(ABC):
    """
    The base engine for creating custom engines of various needs for CPU scheduling. 
    """
    def __init__(self, cores: List[Core]):
        self.clock = Clock()
        self.tracer = Tracer()
        self.stats = StatsCollector()
        self.cores = cores

    @abstractmethod
    def run(self, processes: List[Process]) -> Dict:
        pass

class BasicEngine(BaseEngine):
    """Single-core, Single-queue for basic scheduling algorithms (FCFS, SJF, STCF, RR, Priority) """
    def __init__(self, policy: SchedulerPolicy, dispatch_latency: int = 0):

        # We initialize exactly ONE core for the BasicEngine
        
        single_core = Core(core_id=0, dispatch_latency=dispatch_latency)
        
        super().__init__(cores=[single_core])
        
        self.policy = policy

    def run(self, processes: List[Process]) -> Dict:        
        incoming = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
        ready_queue: List[Process] = []
        remaining_times = {p.pid: p.burst_time for p in incoming}
        
        core = self.cores[0] # Grab our only core

        while incoming or ready_queue or core.current_process or core.dispatcher.is_currently_switching:
            
            # 1. Handle Arrivals
            while incoming and incoming[0].arrival_time <= self.clock.time:
                new_proc = incoming.pop(0)
                ready_queue.append(new_proc)
                self.tracer.record(self.clock.time, "ARRIVAL", new_proc.pid)

            # 2. Decision Logic
            if not core.dispatcher.is_currently_switching:
                potential_next = self.policy.get_next_process(
                    ready_queue, core.current_process, core.current_runtime, remaining_times
                )

                if potential_next != core.current_process:
                    core.assign(potential_next)
                    if core.dispatcher.is_currently_switching:
                        self.tracer.record(self.clock.time, "SWITCH_START", potential_next.pid if potential_next else "Idle")

            # 3. Execution Phase (Delegating state to the Core)
            if core.dispatcher.is_currently_switching:
                core.switch_time += 1
                self.tracer.record(self.clock.time, "SWITCH", msg="Dispatcher busy")
                core.dispatcher.tick()
                
                # If finished switching this tick, load the process
                if not core.dispatcher.is_currently_switching:
                    core.current_process = core.target_process
                    core.current_runtime = 0

            elif core.current_process:
                self.tracer.record(self.clock.time, "EXEC", core.current_process.pid)
                remaining_times[core.current_process.pid] -= 1
                core.current_runtime += 1

                if remaining_times[core.current_process.pid] == 0:
                    self.stats.record_completion(core.current_process, self.clock.time + 1)
                    core.current_process = None
                    core.current_runtime = 0
            else:
                core.idle_time += 1
                self.tracer.record(self.clock.time, "IDLE")

            self.clock.tick()

        total_burst = sum(p.burst_time for p in processes)
        return self.stats.generate_report(self.clock.time, total_burst, self.cores, self.tracer)