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
    """ A basic simulation engine. Supports only uniprocessor and single queue scheduling."""
    def __init__(self, policy: SchedulerPolicy, dispatch_latency: int = 0):
        super().__init__(cores=[Core(core_id=0, dispatch_latency=dispatch_latency)])
        self.policy = policy
        self.ready_queue: List[Process] = []
        self.remaining_times: Dict[int, int] = {}

    def run(self, processes: List[Process]) -> Dict:
        incoming = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
        self.remaining_times = {p.pid: p.burst_time for p in incoming}
        
        while self._simulation_is_active(incoming):
            self._handle_arrivals(incoming)
            self._assess_process()
            self._execute_tick()
            self.clock.tick()

        return self._generate_final_report(processes)

    def _simulation_is_active(self, incoming: List[Process]) -> bool:
        """ Check if any process is still in the system or being processed """
        return (incoming or self.ready_queue or 
                any(c.current_process or c.dispatcher.is_currently_switching for c in self.cores))

    def _handle_arrivals(self, incoming: List[Process]) -> None:
        """ Append arrivals to ready queue when they arrived at their clock time """
        while incoming and incoming[0].arrival_time <= self.clock.time:
            new_proc = incoming.pop(0)
            self.ready_queue.append(new_proc)
            self.tracer.record(self.clock.time, "ARRIVAL", new_proc.pid)
    def _assess_process(self) -> None:
        """Checks current process if it's still ongoing, or ready to be popped from the queue, and get next process"""
        for core in self.cores:
            if not core.dispatcher.is_currently_switching:
                potential_next = self.policy.get_next_process(
                    self.ready_queue, core.current_process, 
                    core.current_runtime, self.remaining_times
                )

                if potential_next != core.current_process:
                    # 1. If we are preempting a process, put the old one BACK in the queue
                    if core.current_process is not None:
                        self.ready_queue.append(core.current_process)

                    # 2. If we are picking a new process, take it OUT of the queue
                    if potential_next and potential_next in self.ready_queue:
                        self.ready_queue.remove(potential_next)
                    
                    # 3. Inform the hardware of the change
                    core.assign(potential_next)
                    
                    if core.dispatcher.is_currently_switching:
                        self.tracer.record(self.clock.time, "SWITCH_START", 
                                         potential_next.pid if potential_next else "Idle")

    def _execute_tick(self) -> None:
        """Time passing by 1 unit for hardware"""
        for core in self.cores:
            if core.dispatcher.is_currently_switching:
                self._handle_core_switching(core)
            elif core.current_process:
                self._handle_core_execution(core)
            else:
                self._handle_core_idle(core)

    def _handle_core_switching(self, core: Core) -> None:
        """ Handles core switching overhead with dispatcher """
        core.switch_time += 1
        self.tracer.record(self.clock.time, "SWITCH", msg="Dispatcher busy")
        core.dispatcher.tick()
        
        if not core.dispatcher.is_currently_switching:
            core.current_process = core.target_process
            core.current_runtime = 0

    def _handle_core_execution(self, core: Core) -> None:
        """ Handles core execution by Tracer log, decrement remaining times (via PID), and increments current runtime"""
        pid = core.current_process.pid
        self.tracer.record(self.clock.time, "EXEC", pid)
        self.remaining_times[pid] -= 1
        core.current_runtime += 1

        if self.remaining_times[pid] == 0:
            self.stats.record_completion(core.current_process, self.clock.time + 1)
            core.current_process = None
            core.current_runtime = 0

    def _handle_core_idle(self, core: Core) -> None:
        """ Increments core idle time by 1 unit and logs in Tracer """
        core.idle_time += 1
        self.tracer.record(self.clock.time, "IDLE")

    def _generate_final_report(self, processes: List[Process]) -> Dict:
        total_burst = sum(p.burst_time for p in processes)
        return self.stats.generate_report(self.clock.time, total_burst, self.cores, self.tracer)