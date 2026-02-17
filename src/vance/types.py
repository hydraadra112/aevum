from dataclasses import dataclass
@dataclass(frozen=True)
class Process:
    """The input data for a process."""
    pid: int
    burst_time: int
    arrival_time: int = 0

@dataclass(frozen=True)
class ProcessResult:
    """The outcome of a process after simulation."""
    process: Process
    waiting_time: int
    turnaround_time: int
    completion_time: int