class Visualizer:
    # ANSI Color Palette
    COLORS = {
        "blue": "\033[94m", "cyan": "\033[96m", "green": "\033[92m",
        "yellow": "\033[93m", "red": "\033[91m", "magenta": "\033[95m",
        "white": "\033[97m", "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m"
    }

    @staticmethod
    def _color(text, color_name):
        return f"{Visualizer.COLORS.get(color_name, '')}{text}{Visualizer.COLORS['reset']}"

    @staticmethod
    def render_gantt(res: dict, custom_colors: dict = None):
        """Prints a color-coded Gantt chart using TraceEvents."""
        events = res["structured_trace"]
        total_time = res["total_time"]
        results = {r['pid']: r for r in res['individual_results']}
        
        # Default Theme
        theme = {"EXEC": "green", "WAIT": "yellow", "CTX": "red", "IDLE": "dim"}
        if custom_colors: theme.update(custom_colors)

        # Map timeline
        cpu_map = [None] * (total_time + 1)
        for e in events:
            if e.event_type in ["EXEC", "SWITCH", "IDLE"]:
                cpu_map[e.time] = (e.event_type, e.pid)

        print(f"\n{Visualizer._color('📊 AEVUM SYSTEMS GANTT CHART', 'bold')}")
        
        pids = sorted(results.keys())
        for pid in pids:
            arrival = results[pid]['arrival']
            finish = results[pid]['completion']
            
            row = [f"P{pid:02} |"]
            for t in range(total_time):
                state = cpu_map[t]
                if state and state[0] == "EXEC" and state[1] == pid:
                    row.append(Visualizer._color("█", theme["EXEC"]))
                elif arrival <= t < finish:
                    row.append(Visualizer._color("░", theme["WAIT"]))
                else:
                    row.append(" ")
            print("".join(row))

        # Context Switch Track
        ctx_row = ["CTX |"]
        for t in range(total_time):
            state = cpu_map[t]
            if state and state[0] == "SWITCH":
                ctx_row.append(Visualizer._color("▒", theme["CTX"]))
            else:
                ctx_row.append(" ")
        print("".join(ctx_row))

        # Axis
        axis = ["    └"] + ["┸" if t % 5 == 0 else "─" for t in range(total_time)]
        print("".join(axis))
        labels = ["     "] + [f"{t:<5}" if t % 5 == 0 else "" for t in range(total_time)]
        print(Visualizer._color("".join(labels), "cyan"))

    @staticmethod
    def display_summary(res: dict):
        """Prints a clean results table and efficiency metrics."""
        print(f"\n{Visualizer._color('📋 PERFORMANCE SUMMARY', 'bold')}")
        head = f"{'PID':<4} | {'Arrival':<8} | {'Burst':<6} | {'Wait':<6} | {'TAT':<6} | {'Finish':<8}"
        print(Visualizer._color(head, "blue"))
        print("-" * len(head))

        for r in sorted(res['individual_results'], key=lambda x: x['pid']):
            print(f"P{r['pid']:02}  | {r['arrival']:<8} | {r['burst']:<6} | {r['wait']:<6.1f} | {r['turnaround']:<6.1f} | {r['completion']:<8}")
        
        print("-" * len(head))
        avgs = res['averages']
        print(f"Average Waiting Time:    {Visualizer._color(avgs['avg_waiting_time'], 'green')}")
        print(f"Average Turnaround Time: {Visualizer._color(avgs['avg_turnaround_time'], 'green')}")
        print(f"Hardware Efficiency:     {Visualizer._color(avgs['hardware_efficiency'], 'cyan')} (Actual Work / Total Time)")
        print(f"CPU Utilization:         {Visualizer._color(avgs['cpu_utilization'], 'cyan')} (Non-Idle Time / Total Time)")

    @staticmethod
    def display_audit(res: dict):
        """Prints the step-by-step calculation for each process."""
        print(f"\n{Visualizer._color('🧮 MATHEMATICAL AUDIT', 'bold')}")
        for r in sorted(res['individual_results'], key=lambda x: x['pid']):
            pid = f"P{r['pid']:02}"
            # Turnaround = Completion - Arrival
            # Wait = Turnaround - Burst
            print(f"{Visualizer._color(pid, 'magenta')}:")
            print(f"  └─ Turnaround: {r['completion']} (End) - {r['arrival']} (Start) = {Visualizer._color(r['turnaround'], 'white')}")
            print(f"  └─ Wait:       {r['turnaround']} (TAT) - {r['burst']} (Burst) = {Visualizer._color(r['wait'], 'white')}")