# sequential_placement.py

import random
import time
import matplotlib.pyplot as plt
import numpy as np
from metrics import PlacementMetrics
from optimization import optimize_vm_placement

class SequentialPlacementSimulation:
    def __init__(self, config):
        self.config = config
        self.clusters = config.clusters
        self.cluster_capacity = config.cluster_capacity
        # deep copy, replace with library
        self.current_usage = {
                cluster: {
                    resource: value
                    for resource, value in usage.items()
                }
                for cluster, usage in config.initial_usage.items()
            }
        self.existing_placements = {}
        self.placement_history = []
        self.metrics_history = []
        # Add these attributes
        self.total_time = 0
        self.execution_times = []

    def generate_vm_demand(self):
        return {
            resource: random.uniform(ranges[0], ranges[1])
            for resource, ranges in self.config.vm_demand_ranges.items()
        }

    def update_cluster_usage(self, vm_name, cluster, vm_demand):
        for resource in ['cpu', 'mem', 'disk']:
            usage_increase = vm_demand[resource] / self.cluster_capacity[cluster][resource]
            self.current_usage[cluster][resource] += usage_increase

    def run_simulation(self):
        overall_start_time = time.time()
        execution_times = []

        # Changed from self.num_vms to self.config.num_vms
        for i in range(self.config.num_vms):
            vm_name = f'vm{i+1}'
            print(f"\nPlacing {vm_name} ({i+1}/{self.config.num_vms})...")

            vm_demand = {vm_name: self.generate_vm_demand()}

            start_time = time.time()
            result = optimize_vm_placement(
                self.clusters,
                self.existing_placements,
                [vm_name],
                self.current_usage,
                self.cluster_capacity,
                vm_demand
            )
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)  # Store execution time

            if result[0] is None:
                print(f"Failed to place {vm_name}")
                break

            placement_plan, cluster_utilization, final_utilization, final_placement = result

            placed_cluster = placement_plan[vm_name]
            self.existing_placements[vm_name] = placed_cluster
            self.update_cluster_usage(vm_name, placed_cluster, vm_demand[vm_name])

            metrics = PlacementMetrics()
            metrics.execution_time = execution_time
            metrics.calculate_metrics(cluster_utilization, execution_time)
            self.metrics_history.append(metrics)

            self.placement_history.append({
                'vm': vm_name,
                'cluster': placed_cluster,
                'demand': vm_demand[vm_name],
                'utilization': cluster_utilization.copy(),
                'execution_time': execution_time
            })

        self.total_time = time.time() - overall_start_time  # Store total time
        return self.summarize_results(self.total_time, self.execution_times)

    def summarize_results(self, total_time, execution_times):
        """Summarize the simulation results with error handling"""
        if not execution_times:  # If no VMs were placed
            summary = {
                'total_time': total_time,
                'vms_placed': 0,
                'avg_placement_time': 0,
                'min_placement_time': 0,
                'max_placement_time': 0,
                'final_metrics': None,
                'cluster_distribution': {c: [] for c in self.clusters},
                'final_utilization': self.current_usage,
                'metrics_history': [],  # Empty metrics history
                'success': False,
                'error': "No VMs were successfully placed"
            }
        else:
            summary = {
                'total_time': total_time,
                'vms_placed': len(self.existing_placements),
                'avg_placement_time': np.mean(execution_times),
                'min_placement_time': min(execution_times),
                'max_placement_time': max(execution_times),
                'cluster_distribution': {c: [] for c in self.clusters},
                'final_utilization': self.current_usage,
                'metrics_history': [
                    metrics.to_dict() for metrics in self.metrics_history
                ],
                'final_metrics': self.metrics_history[-1].to_dict() if self.metrics_history else None,
                'success': True,
                'error': None
            }

            # Calculate cluster distribution
            for vm, cluster in self.existing_placements.items():
                summary['cluster_distribution'][cluster].append(vm)

        return summary

    def plot_results(self):
        """Create visualization showing initial and final states with horizontal bars and averages"""
        resources = ['cpu', 'mem', 'disk']
        y = np.arange(len(resources))
        height = 0.35

        # Create figure with 2 rows, 1 column
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Calculate averages and std for initial state
        initial_avgs = {}
        initial_stds = {}
        for resource in resources:
            values = [self.config.initial_usage[cluster][resource] * 100
                    for cluster in self.clusters]
            initial_avgs[resource] = np.mean(values)
            initial_stds[resource] = np.std(values)

        # Calculate averages and std for final state
        final_avgs = {}
        final_stds = {}
        for resource in resources:
            values = [self.current_usage[cluster][resource] * 100
                    for cluster in self.clusters]
            final_avgs[resource] = np.mean(values)
            final_stds[resource] = np.std(values)

        # Plot initial state
        for i, cluster in enumerate(self.clusters):
            values = [self.config.initial_usage[cluster][r] * 100 for r in resources]
            bars = ax1.barh(y + i*height, values, height, label=f'Cluster {cluster}')
            for idx, v in enumerate(values):
                ax1.text(v + 1, idx + i*height, f'{v:.1f}%', va='center')

        # Add average lines and std for initial state
        for idx, resource in enumerate(resources):
            avg_value = initial_avgs[resource]
            std_value = initial_stds[resource]
            ax1.axvline(x=avg_value, ymin=(idx/len(resources)), ymax=((idx+1)/len(resources)),
                    color='red', linestyle='--', alpha=0.5)
            ax1.text(avg_value, idx + height,
                    f'Avg: {avg_value:.1f}% (σ: {std_value:.1f})',
                    va='bottom', ha='right', color='red')

        ax1.set_xlabel('Utilization (%)')
        ax1.set_title('Initial Cluster State')
        ax1.set_yticks(y + height)
        ax1.set_yticklabels(['CPU', 'Memory', 'Disk'])
        ax1.legend()
        ax1.set_xlim(0, 100)
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Plot final state
        for i, cluster in enumerate(self.clusters):
            values = [self.current_usage[cluster][r] * 100 for r in resources]
            bars = ax2.barh(y + i*height, values, height, label=f'Cluster {cluster}')
            for idx, v in enumerate(values):
                ax2.text(v + 1, idx + i*height, f'{v:.1f}%', va='center')

        # Add average lines and std for final state
        for idx, resource in enumerate(resources):
            avg_value = final_avgs[resource]
            std_value = final_stds[resource]
            ax2.axvline(x=avg_value, ymin=(idx/len(resources)), ymax=((idx+1)/len(resources)),
                    color='red', linestyle='--', alpha=0.5)
            ax2.text(avg_value, idx + height,
                    f'Avg: {avg_value:.1f}% (σ: {std_value:.1f})',
                    va='bottom', ha='right', color='red')

        ax2.set_xlabel('Utilization (%)')
        ax2.set_title('Final Cluster State')
        ax2.set_yticks(y + height)
        ax2.set_yticklabels(['CPU', 'Memory', 'Disk'])
        ax2.legend()
        ax2.set_xlim(0, 100)
        ax2.grid(True, linestyle='--', alpha=0.7)

        # Calculate and add statistics
        avg_placement_time = np.mean([m.execution_time for m in self.metrics_history]) if self.metrics_history else 0
        stats_text = (
            f'Total VMs placed: {len(self.existing_placements)}\n'
            f'Avg placement time: {avg_placement_time:.3f}s\n'
            f'Initial avg utilization: {np.mean(list(initial_avgs.values())):.1f}% '
            f'(σ: {np.mean([initial_stds[r] for r in resources]):.1f})\n'
            f'Final avg utilization: {np.mean(list(final_avgs.values())):.1f}% '
            f'(σ: {np.mean([final_stds[r] for r in resources]):.1f})'
        )

        # Add stats box
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.figtext(0.98, 0.98, stats_text,
                    fontsize=10,
                    bbox=props,
                    verticalalignment='top',
                    horizontalalignment='right')

        plt.suptitle(f'Scenario: {self.config.name}', fontsize=12)
        plt.tight_layout()

        # Save with scenario name in filename
        plot_filename = f'test_results/sequential_placement_results_{self.config.name}.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
