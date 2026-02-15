# **Aevum**

A unified Python module of CPU schedulers for educators and students, and for educational and simulation purposes.

---

## How to use?

Here's an example implementation of RR scheduling:

```python
from aevum.core import Process, SimulationEngine
from aevum.policies import RR

def main():
    processes = [
        Process(pid=1, burst_time=8, arrival_time=0),
        Process(pid=2, burst_time=4, arrival_time=1),
        Process(pid=3, burst_time=9, arrival_time=2),
        Process(pid=4, burst_time=12, arrival_time=5),
        Process(pid=5, burst_time=5, arrival_time=4),
    ]

    dispatcher_latency = 2 # optional, default to 0

    engine = SimulationEngine(RR(time_quantum=3), dispatcher_latency)
    res = engine.run(processes)
    print(res)

if __name__ == "__main__":
    main()
```

---

## **Initial TODO lists**

Supported:

- [x] First Count First Serve (FCFS)
- [x] Shortest Job First (SJF)
- [x] Shortest Time to Completion (STCF)
- [x] Round Robin (RR)
- [x] Dispatcher Feature

Plans:

- [ ] Visualizer Module - Visualizes output in the terminal

I will add more algorithms and features in the future, but I aim to finish the todo lists above before I publish it officially as a Python package.

---

## Why do this?

During my OS class, we are tasked to perform simulations of CPU scheduling algorithms in Python, and since there are no Python modules (as far as I know) for schedulers, I had to scour through the internet to look for sample implementation, and somehow refactor every algorithm that I need to fit my use case.

Because of this, it took me a few hours to perform the simulation. It could've been far more faster if there was a module, and our teacher could've provide a demo as well.

So I took the initiative in starting this project, and thought of it as my first ever open source project to give back to the community.

This project will also be a platform for me (I hope it does for you too), to practice my coding skills and strengthen our OS scheduling knowledge.
