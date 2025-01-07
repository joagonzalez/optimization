# real_time_viz.py
import time
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np
from src.services.metrics import PlacementMetrics
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.services.optimization import optimize_vm_placement


class RealTimeVisualization:
    def __init__(self, config, is_last=False):
        self.config = config
        self.is_last = is_last
        self.root = None
        self.setup_window()

    def setup_window(self):
        self.root = tk.Tk()
        # Use self.config instead of config
        self.root.title(f"VM Placement Simulation - {self.config.name}")
        self.root.geometry("1200x800")

        # Setup main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Info panel
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.pack(fill=tk.X, pady=10)

        # Labels for statistics
        self.vm_label = ttk.Label(self.info_frame, text="Current VM: -")
        self.vm_label.pack(side=tk.LEFT, padx=10)

        self.time_label = ttk.Label(self.info_frame, text="Time: 0.000s")
        self.time_label.pack(side=tk.LEFT, padx=10)

        self.progress_label = ttk.Label(self.info_frame, text="Progress: 0%")
        self.progress_label.pack(side=tk.LEFT, padx=10)

        # Add continue button (initially disabled)
        button_text = "Finish" if self.is_last else "Continue to Next Test"
        self.continue_button = ttk.Button(
            self.info_frame,
            text=button_text,
            command=self.close_window,
            state="disabled",
        )
        self.continue_button.pack(side=tk.RIGHT, padx=10)

        self.setup_plot()

    def close_window(self):
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None

    def setup_plot(self):
        self.ax.clear()
        resources = ["cpu", "mem", "disk"]
        self.y_pos = np.arange(len(resources))
        self.height = 0.35

        self.ax.set_xlabel("Utilization (%)")
        self.ax.set_title("Cluster Utilization")
        self.ax.set_yticks(self.y_pos + self.height)
        self.ax.set_yticklabels(["CPU", "Memory", "Disk"])
        self.ax.set_xlim(0, 100)
        self.ax.grid(True, linestyle="--", alpha=0.7)

    def update_plot(self, current_usage, vm_name, execution_time, progress):
        if not self.root:
            return

        self.ax.clear()
        self.setup_plot()
        resources = ["cpu", "mem", "disk"]

        # Calculate averages and std
        resource_stats = {}
        for resource in resources:
            values = [
                current_usage[cluster][resource] * 100
                for cluster in self.config.clusters
            ]
            resource_stats[resource] = {"avg": np.mean(values), "std": np.std(values)}

        # Plot bars for each cluster
        for i, cluster in enumerate(self.config.clusters):
            values = [current_usage[cluster][r] * 100 for r in resources]
            bars = self.ax.barh(  # noqa
                self.y_pos + i * self.height,
                values,
                self.height,
                label=f"Cluster {cluster}",
            )

            for idx, v in enumerate(values):
                self.ax.text(v + 1, idx + i * self.height, f"{v:.1f}%", va="center")

        # Add average lines with std
        for idx, resource in enumerate(resources):
            avg_value = resource_stats[resource]["avg"]
            std_value = resource_stats[resource]["std"]
            self.ax.axvline(
                x=avg_value,
                ymin=(idx / len(resources)),
                ymax=((idx + 1) / len(resources)),
                color="red",
                linestyle="--",
                alpha=0.5,
            )
            self.ax.text(
                avg_value,
                idx + self.height,
                f"Avg: {avg_value:.1f}% (σ: {std_value:.1f})",
                va="bottom",
                ha="right",
                color="red",
            )

        self.ax.legend()

        # Update labels with more detailed stats
        self.vm_label.config(text=f"Current VM: {vm_name}")
        self.time_label.config(text=f"Time: {execution_time:.3f}s")
        self.progress_label.config(text=f"Progress: {progress:.1f}%")

        self.canvas.draw()
        self.root.update()


def run_visualization(simulation):
    is_last = (
        simulation.config.name == "large_vms"
    )  # Or use another way to identify the last scenario
    viz = RealTimeVisualization(simulation.config, is_last=is_last)
    overall_start_time = time.time()
    execution_times = []
    metrics_history = []  # Initialize metrics history

    try:
        for i in range(simulation.config.num_vms):
            vm_name = f"vm{i+1}"
            progress = (i / simulation.config.num_vms) * 100

            vm_demand = {vm_name: simulation.generate_vm_demand()}

            start_time = time.time()
            result = optimize_vm_placement(
                simulation.clusters,
                simulation.existing_placements,
                [vm_name],
                simulation.current_usage,
                simulation.cluster_capacity,
                vm_demand,
            )
            execution_time = time.time() - start_time

            if result[0] is None:
                print(f"Failed to place {vm_name}")
                viz.continue_button.config(state="normal")
                viz.progress_label.config(text="Placement Failed")
                simulation.total_time = time.time() - overall_start_time
                simulation.execution_times = execution_times
                viz.root.mainloop()
                return

            execution_times.append(execution_time)
            placement_plan, cluster_utilization, final_utilization, final_placement = result

            # Calculate and store metrics for this placement
            metrics = PlacementMetrics()
            metrics.calculate_metrics(cluster_utilization, execution_time)
            metrics_history.append(metrics)  # Add to metrics history

            placed_cluster = placement_plan[vm_name]
            simulation.existing_placements[vm_name] = placed_cluster
            simulation.update_cluster_usage(vm_name, placed_cluster, vm_demand[vm_name])

            # Store placement history with metrics
            simulation.placement_history.append({
                'vm': vm_name,
                'cluster': placed_cluster,
                'demand': vm_demand[vm_name],
                'utilization': cluster_utilization.copy(),
                'execution_time': execution_time,
                'metrics': metrics.to_dict()  # Include metrics in history
            })

            viz.update_plot(simulation.current_usage, vm_name, execution_time, progress)
            time.sleep(0.01)

        # Simulation complete
        viz.continue_button.config(state="normal")
        viz.progress_label.config(text="Progress: 100%")

        if viz.is_last:
            viz.continue_button.config(text="Finish")
            print("Last scenario completed. Click 'Finish' to exit.")

        # Store final results in simulation object
        simulation.metrics_history = metrics_history
        simulation.execution_times = execution_times
        simulation.total_time = time.time() - overall_start_time

        # Generate plots before waiting for user input
        if simulation.metrics_history:
            print("\nGenerating metric evolution plots...")
            simulation.plot_metrics_evolution(simulation.config.name)

        # Wait for user to close window
        if viz.root:  # Check if root window exists before calling mainloop
            viz.root.mainloop()

    except tk.TclError:
        pass
    finally:
        if viz.root:
            viz.close_window()
            if viz.is_last:
                # If this is the last scenario, ensure complete cleanup
                try:
                    root = tk.Tk()
                    root.quit()
                    root.destroy()
                except Exception:
                    pass
