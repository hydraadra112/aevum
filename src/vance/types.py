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
    """ Represents a Tracer event. Event type shall include the following: 
    "ARRIVAL", "SWITCH", "EXEC", "IDLE", "FINISHED"
    """
    time: int
    event_type: str  # "ARRIVAL", "SWITCH", "EXEC", "IDLE", "FINISHED"
    pid: Optional[Union[int, str]] = None


class Tracer:
    """ Represents a CPU tracer, storing TraceEvent objects """
    def __init__(self):
        self.events: List[TraceEvent] = []
        self._log: List[str] = []

    def record(
        self,
        time: int,
        event_type: str,
        pid: Optional[Union[int, str]] = None,
        msg: str = "",
    ) -> None:
        """ Records a structured event and a string message simultaneously.

        Args:
          time: int:
          event_type: str:
          pid: Optional[Union[int:
          str: Default value = None)
          msg: str:  (Default value = "")

        Returns:
            None

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
    """ Represents a CPU core """
    def __init__(self, core_id: int, dispatch_latency: int = 0):
        self.core_id = core_id
        self.dispatcher = Dispatcher(dispatch_latency)
        
        self.current_process: Optional[Process] = None
        self.target_process: Optional[Process] = None
        
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
        """Calculates turnaround and waiting time for a finished process."""
        turnaround = finish_time - process.arrival_time
        wait = turnaround - process.burst_time
        
        result = ProcessResult(process, wait, turnaround, finish_time)
        self.results.append(result)

    def generate_report(self, total_time: int, total_burst: int, cores: List[Core], tracer: Tracer) -> Dict:
        """The main entry point for generating the final simulation report."""
        
        # 1. Individual Process Results
        formatted_individual_results = []
        for r in self.results:
            data = {
                "pid": r.process.pid,
                "arrival": r.process.arrival_time,
                "burst": r.process.burst_time,
                "wait": r.waiting_time,
                "turnaround": r.turnaround_time,
                "completion": r.completion_time,
            }
            formatted_individual_results.append(data)

        # 2. Average Calculations
        averages = self._calculate_averages()

        # 3. Hardware Performance Metrics
        hardware_stats = self._calculate_hardware_metrics(total_time, total_burst, cores)

        # 4. Final Compilation
        return {
            "individual_results": formatted_individual_results,
            "averages": {
                **averages,
                **hardware_stats
            },
            "structured_trace": tracer.get_structured_data(),
            "total_time": total_time,
        }

    def _calculate_averages(self) -> Dict:
        """Calculates mean Wait and Turnaround times."""
        n_results = len(self.results)
        if n_results == 0:
            return {"avg_waiting_time": 0, "avg_turnaround_time": 0}

        total_wait = 0
        total_tat = 0
        for r in self.results:
            total_wait += r.waiting_time
            total_tat += r.turnaround_time

        return {
            "avg_waiting_time": round(total_wait / n_results, 2),
            "avg_turnaround_time": round(total_tat / n_results, 2)
        }

    def _calculate_hardware_metrics(self, total_time: int, total_burst: int, cores: List[Core]) -> Dict:
        """ Calculate CPU utilization, throughput, and hardware efficiency """
        if total_time == 0:
            return {"cpu_utilization": "0%", "hardware_efficiency": "0%", "throughput": 0}

        # Utilization: Was the CPU doing *something*? (Work + Switching)
        total_switch_time = 0
        for core in cores:
            total_switch_time += core.switch_time
        
        busy_time = total_burst + total_switch_time
        utilization = (busy_time / total_time) * 100

        # Efficiency: Was the CPU doing *useful* work? (Just Burst)
        efficiency = (total_burst / total_time) * 100

        # Throughput: Processes finished per unit of time
        throughput = len(self.results) / total_time

        return {
            "cpu_utilization": f"{min(utilization, 100.0):.1f}%",
            "hardware_efficiency": f"{efficiency:.1f}%",
            "throughput": round(throughput, 4)
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