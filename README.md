# **Aevum**

A unified Python module of CPU schedulers for educators and students, and for educational and simulation purposes.

---

## How to use?

Here's an example implementation of FCFS scheduling:

```python
# High-Level Approach (Fastest Way)
from aevum.base import Process
from aevum.utils import sort_processes_by_arrival
from aevum.schedulers import run_fcfs_simulation

# Define unsorted processes
raw_data = [
    Process(pid=1, burst_time=10, arrival_time=5),
    Process(pid=2, burst_time=5, arrival_time=0),
    Process(pid=3, burst_time=8, arrival_time=2)
]

# Aevum enforces order for FCFS to ensure simulation integrity
ready_queue = sort_processes_by_arrival(raw_data)
results = run_fcfs_simulation(ready_queue)

print(f"Average Wait: {results['averages']['avg_waiting_time']}")

# Low-Level Approach (For Experimentation and Control)
from aevum.metrics import calculate_turnaround_time, calculate_waiting_time
from aevum.base import ProcessResult

results_list = []
current_time = 0

for proc in ready_queue:
    # Calculate metrics using Aevum's core logic
    wait = calculate_waiting_time(proc.arrival_time, current_time)
    tat = calculate_turnaround_time(proc.burst_time, wait)
    comp = proc.arrival_time + tat # or current_time + proc.burst_time (if idle accounted)

    results_list.append(ProcessResult(proc, wait, tat, comp))
    current_time = comp
```

---

## **Initial TODO lists**

Supported:

- [x] First Count First Serve (FCFS)

Planned:

- [ ] Shortest Job First (SJF)
- [ ] Shortest Time to Completion (STCF)
- [ ] Round Robin (RR)

I will add more algorithms in the future, but I aim to finish the todo lists above before I publish it officially as a Python package.

---

## Why do this?

During my OS class, we are tasked to perform simulations of CPU scheduling algorithms in Python, and since there are no Python modules (as far as I know) for schedulers, I had to scour through the internet to look for sample implementation, and somehow refactor every algorithm that I need to fit my use case.

Because of this, it took me a few hours to perform the simulation. It could've been far more faster if there was a module, and our teacher could've provide a demo as well.

So I took the initiative in starting this project, and thought of it as my first ever open source project to give back to the community.

This project will also be a platform for me (I hope it does for you too), to practice my coding skills and strengthen our OS scheduling knowledge.
