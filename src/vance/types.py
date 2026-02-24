from dataclasses import dataclass
from typing import List, Union, Dict, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class Process:
    """The input data for a process."""
    pid: int
    burst_time: int
    arrival_time: int = 0
    priority_time: int = 0

@dataclass
class TraceEvent:
    """ """
    time: int
    event_type: str  # "ARRIVAL", "SWITCH", "EXEC", "IDLE", "FINISHED"
    pid: Optional[Union[int, str]] = None


class Tracer:
    """ """
    def __init__(self):
        self.events: List[TraceEvent] = []
        self._log: List[str] = []

    def record(
        self,
        time: int,
        event_type: str,
        pid: Optional[Union[int, str]] = None,
        msg: str = "",
    ):
        """Records a structured event and a string message simultaneously.

        Args:
          time: int:
          event_type: str:
          pid: Optional[Union[int:
          str: Default value = None)
          msg: str:  (Default value = "")
          time: int:
          event_type: str:
          pid: Optional[Union[int:
          str: Default value = None)
          msg: str:  (Default value = "")
          time: int: 
          event_type: str: 
          pid: Optional[Union[int: 
          str]]:  (Default value = None)
          msg: str:  (Default value = "")

        Returns:

        """
        self.events.append(TraceEvent(time, event_type, pid))
        if msg:
            self._log.append(f"T={time}: {msg}")

    def get_log(self) -> List[str]:
        """ """
        return self._log

    def get_structured_data(self) -> List[TraceEvent]:
        """ """
        return self.events

@dataclass(frozen=True)
class ProcessResult:
    """The outcome of a process after simulation."""

    process: Process
    waiting_time: int
    turnaround_time: int
    completion_time: int

class Core:
    def __init__(self, core_id: int, dispatch_latency: int = 0):
        self.core_id = core_id
        self.dispatcher = Dispatcher(dispatch_latency)
        
        self.current_process: Optional[Process] = None
        self.target_process: Optional[Process] = None # Who runs after the switch?
        
        # Hardware Metrics
        self.current_runtime: int = 0
        self.idle_time: int = 0
        self.switch_time: int = 0

    def assign(self, process: Optional[Process]):
        """Tells the core to start running a new process."""
        if self.dispatcher.dispatch_latency > 0:
            self.dispatcher.start_switch(process.pid if process else None)
            self.target_process = process
        else:
            self.current_process = process
            self.current_runtime = 0


class StatsCollector:
    """Handles all mathematical calculations and output formatting."""
    def __init__(self):
        self.results: List[ProcessResult] = []

    def record_completion(self, process: Process, finish_time: int) -> None:
        turnaround = finish_time - process.arrival_time
        wait = turnaround - process.burst_time
        self.results.append(ProcessResult(process, wait, turnaround, finish_time))

    def generate_report(self, total_time: int, total_burst: int, cores: List[Core], tracer: Tracer) -> Dict:
        n_results = len(self.results)

        avg_wait = sum(r.waiting_time for r in self.results) / n_results if n_results else 0
        avg_tat = sum(r.turnaround_time for r in self.results) / n_results if n_results else 0

        # Sum up the switch times from ALL cores
        total_switch_time = sum(core.switch_time for core in cores)
        
        if total_time > 0:
            utilization = (total_burst / total_time) * 100
        else:
            utilization = 0
        
        if (total_burst + total_switch_time) > 0:
            efficiency = (total_burst / (total_burst + total_switch_time)) * 100
        else:
            efficiency = 0
        
        if total_time > 0:
            throughput = n_results / total_time
        else:
            throughput = 0

        return {
            "individual_results": [
                {
                    "pid": r.process.pid,
                    "arrival": r.process.arrival_time,
                    "burst": r.process.burst_time,
                    "wait": r.waiting_time,
                    "turnaround": r.turnaround_time,
                    "completion": r.completion_time,
                }
                for r in self.results
            ], 
            "averages": {
                "avg_waiting_time": round(avg_wait, 2),
                "avg_turnaround_time": round(avg_tat, 2),
                "cpu_utilization": f"{utilization:.1f}%",
                "hardware_efficiency": f"{efficiency:.1f}%",
                "throughput": round(throughput, 4)
            },
            "structured_trace": tracer.get_structured_data(),
            "total_time": total_time,
        }

class Clock:
    """ """
    def __init__(self):
        self._time = 0

    @property
    def time(self) -> int:
        """ """
        return self._time

    def tick(self) -> int:
        """Advance the system heartbeat by 1 unit."""
        self._time += 1
        return self._time


class Dispatcher:
    """Represents a dispatcher, for managing context switches of processes"""

    def __init__(self, dispatch_latency: int = 0):

        if dispatch_latency < 0:
            self.dispatch_latency = 0
        else:
            self.dispatch_latency = dispatch_latency
        self.current_switch_remaining = 0
        self.target_process_id: Optional[int] = None

    @property
    def is_currently_switching(self) -> bool:
        """ """
        return self.current_switch_remaining > 0

    def start_switch(self, process_id: int):
        """Begin the overhead period for a new process.

        Args:
          process_id: int:
          process_id: int:
          process_id: int: 

        Returns:

        """
        self.target_process_id = process_id
        self.current_switch_remaining = self.dispatch_latency

    def tick(self):
        """Reduce the overhead timer by 1."""
        if self.current_switch_remaining <= 0:
            raise ValueError(
                "No context switch remaining!"
                "There must be a problem with your dispatcher logic."
            )
        else:
            self.current_switch_remaining -= 1