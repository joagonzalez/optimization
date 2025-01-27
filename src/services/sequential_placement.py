# sequential_placement.py

import random
import time

import matplotlib.pyplot as plt
import numpy as np
from src.services.metrics import PlacementMetrics
from src.services.optimization import optimize_vm_placement


class SequentialPlacementSimulation:
    def __init__(self, config, output_manager):
        self.config = config
        self.output_manager = output_manager  # Add output manager
        self.clusters = config.clusters
        self.optimizer_model = config.optimizer_model
        self.cluster_capacity = config.cluster_capacity
        # deep copy, replace with library
        self.current_usage = {
            cluster: {resource: value for resource, value in usage.items()}  # noqa
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
        for resource in ["cpu", "mem", "disk"]:
            usage_increase = (
                vm_demand[resource] / self.cluster_capacity[cluster][resource]
            )
            self.current_usage[cluster][resource] += usage_increase

    def run_simulation(self):
        overall_start_time = time.time()

        for i in range(self.config.num_vms):
            vm_name = f"vm{i+1}"
            print(f"\nPlacing {vm_name} ({i+1}/{self.config.num_vms})...")

            vm_demand = {vm_name: self.generate_vm_demand()}

            # Create optimizer instance
            optimizer = self.optimizer_model(
                self.clusters,
                self.existing_placements,
                [vm_name],
                self.current_usage,
                self.cluster_capacity,
                vm_demand,
            )

            # Time the optimization
            start_time = time.time()
            result = optimizer.optimize()  # Use optimizer instance directly instead of optimize_vm_placement
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time) # Store execution time

            if result[0] is None:
                print(f"Failed to place {vm_name}")
                break

            placement_plan, cluster_utilization, final_utilization, final_placement = result

            # Calculate metrics for this placement
            metrics = PlacementMetrics()
            metrics.execution_time = execution_time
            metrics.calculate_metrics(cluster_utilization, execution_time)
            self.metrics_history.append(metrics)

            placed_cluster = placement_plan[vm_name]
            self.existing_placements[vm_name] = placed_cluster
            self.update_cluster_usage(vm_name, placed_cluster, vm_demand[vm_name])

            self.placement_history.append(
                {
                    "vm": vm_name,
                    "cluster": placed_cluster,
                    "demand": vm_demand[vm_name],
                    "utilization": cluster_utilization.copy(),
                    "execution_time": execution_time,
                    "metrics": metrics.to_dict(),
                }
            )

        self.total_time = time.time() - overall_start_time  # Store total time

        # After simulation completes
        if self.metrics_history:  # Only create plots if we have metrics
            self.plot_metrics_evolution(self.config.name)

        return self.summarize_results(self.total_time, self.execution_times)

    def summarize_results(self, total_time, execution_times):
        """Summarize the simulation results with error handling"""
        if not execution_times:  # If no VMs were placed
            summary = {
                "total_time": total_time,
                "vms_placed": 0,
                "avg_placement_time": 0,
                "min_placement_time": 0,
                "max_placement_time": 0,
                "final_metrics": None,
                "cluster_distribution": {c: [] for c in self.clusters},
                "final_utilization": self.current_usage,
                "metrics_history": [],  # Empty metrics history
                "success": False,
                "error": "No VMs were successfully placed",
            }
        else:
            summary = {
                "total_time": total_time,
                "vms_placed": len(self.existing_placements),
                "avg_placement_time": np.mean(execution_times),
                "min_placement_time": min(execution_times),
                "max_placement_time": max(execution_times),
                "cluster_distribution": {c: [] for c in self.clusters},
                "final_utilization": self.current_usage,
                "metrics_history": [
                    metrics.to_dict() for metrics in self.metrics_history
                ],
                "final_metrics": self.metrics_history[-1].to_dict()
                if self.metrics_history
                else None,
                "success": True,
                "error": None,
            }

            # Calculate cluster distribution
            for vm, cluster in self.existing_placements.items():
                summary["cluster_distribution"][cluster].append(vm)

        return summary

    def plot_results(self):
        """Create visualization showing initial and final states with horizontal bars and averages"""
        resources = ["cpu", "mem", "disk"]
        y = np.arange(len(resources))
        height = 0.35

        # Create figure with 2 rows, 1 column
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Calculate averages and std for initial state
        initial_avgs = {}
        initial_stds = {}
        for resource in resources:
            values = [
                self.config.initial_usage[cluster][resource] * 100
                for cluster in self.clusters
            ]
            initial_avgs[resource] = np.mean(values)
            initial_stds[resource] = np.std(values)

        # Calculate averages and std for final state
        final_avgs = {}
        final_stds = {}
        for resource in resources:
            values = [
                self.current_usage[cluster][resource] * 100 for cluster in self.clusters
            ]
            final_avgs[resource] = np.mean(values)
            final_stds[resource] = np.std(values)

        # Plot initial state
        for i, cluster in enumerate(self.clusters):
            values = [self.config.initial_usage[cluster][r] * 100 for r in resources]
            bars = ax1.barh(y + i * height, values, height, label=f"Cluster {cluster}")
            for idx, v in enumerate(values):
                ax1.text(v + 1, idx + i * height, f"{v:.1f}%", va="center")

        # Add average lines and std for initial state
        for idx, resource in enumerate(resources):
            avg_value = initial_avgs[resource]
            std_value = initial_stds[resource]
            ax1.axvline(
                x=avg_value,
                ymin=(idx / len(resources)),
                ymax=((idx + 1) / len(resources)),
                color="red",
                linestyle="--",
                alpha=0.5,
            )
            ax1.text(
                avg_value,
                idx + height,
                f"Avg: {avg_value:.1f}% (σ: {std_value:.1f})",
                va="bottom",
                ha="right",
                color="red",
            )

        ax1.set_xlabel("Utilization (%)")
        ax1.set_title("Initial Cluster State")
        ax1.set_yticks(y + height)
        ax1.set_yticklabels(["CPU", "Memory", "Disk"])
        ax1.legend()
        ax1.set_xlim(0, 100)
        ax1.grid(True, linestyle="--", alpha=0.7)

        # Plot final state
        for i, cluster in enumerate(self.clusters):
            values = [self.current_usage[cluster][r] * 100 for r in resources]
            bars = ax2.barh(y + i * height, values, height, label=f"Cluster {cluster}")  # noqa
            for idx, v in enumerate(values):
                ax2.text(v + 1, idx + i * height, f"{v:.1f}%", va="center")

        # Add average lines and std for final state
        for idx, resource in enumerate(resources):
            avg_value = final_avgs[resource]
            std_value = final_stds[resource]
            ax2.axvline(
                x=avg_value,
                ymin=(idx / len(resources)),
                ymax=((idx + 1) / len(resources)),
                color="red",
                linestyle="--",
                alpha=0.5,
            )
            ax2.text(
                avg_value,
                idx + height,
                f"Avg: {avg_value:.1f}% (σ: {std_value:.1f})",
                va="bottom",
                ha="right",
                color="red",
            )

        ax2.set_xlabel("Utilization (%)")
        ax2.set_title("Final Cluster State")
        ax2.set_yticks(y + height)
        ax2.set_yticklabels(["CPU", "Memory", "Disk"])
        ax2.legend()
        ax2.set_xlim(0, 100)
        ax2.grid(True, linestyle="--", alpha=0.7)

        # Calculate and add statistics
        avg_placement_time = (
            np.mean([m.execution_time for m in self.metrics_history])
            if self.metrics_history
            else 0
        )
        stats_text = (
            f"Total VMs placed: {len(self.existing_placements)}\n"
            f"Avg placement time: {avg_placement_time:.3f}s\n"
            f"Initial avg utilization: {np.mean(list(initial_avgs.values())):.1f}% "
            f"(σ: {np.mean([initial_stds[r] for r in resources]):.1f})\n"
            f"Final avg utilization: {np.mean(list(final_avgs.values())):.1f}% "
            f"(σ: {np.mean([final_stds[r] for r in resources]):.1f})"
        )

        # Add stats box
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        plt.figtext(
            0.98,
            0.98,
            stats_text,
            fontsize=10,
            bbox=props,
            verticalalignment="top",
            horizontalalignment="right",
        )

        plt.suptitle(f"Scenario: {self.config.name}", fontsize=12)
        plt.tight_layout()

        # Save with scenario name in filename
        # get_utilization_plot_path

        util_path = self.output_manager.get_utilization_plot_path(
            f'sequential_placement_results_{self.config.name}.png'
        )
        plt.savefig(util_path, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_metrics_evolution(self, output_prefix):
        """Create evolution plots for various metrics throughout VM placements."""
        if not self.metrics_history:
            print("No metrics history available for plotting")
            return

        # Set style parameters
        plt.style.use('default')
        colors = {
            'imbalance': '#1f77b4',
            'cpu': '#2ca02c',
            'mem': '#ff7f0e',
            'disk': '#d62728',
            'max': '#7f7f7f',
            'avg': '#17becf',
            'std': '#bcbd22'
        }

        # Prepare data points
        placements = range(1, len(self.metrics_history) + 1)

        # Extract metrics evolution
        imbalance_scores = [m.overall_imbalance for m in self.metrics_history]

        # Resource-specific metrics
        resource_metrics = {
            'cpu': {'max': [], 'avg': [], 'std': []},
            'mem': {'max': [], 'avg': [], 'std': []},
            'disk': {'max': [], 'avg': [], 'std': []}
        }

        for metric in self.metrics_history:
            for resource in ['cpu', 'mem', 'disk']:
                r_metrics = metric.resources[resource]
                resource_metrics[resource]['max'].append(r_metrics.max_utilization)
                resource_metrics[resource]['avg'].append(r_metrics.avg_utilization)
                resource_metrics[resource]['std'].append(r_metrics.std_dev)

        # 1. Imbalance Score Evolution
        plt.figure(figsize=(10, 6))
        plt.plot(placements, imbalance_scores, marker='o', linestyle='-',
                 color=colors['imbalance'], linewidth=2, markersize=6)
        plt.title(f'Imbalance Score Evolution - {output_prefix}')
        plt.xlabel('Number of VMs Placed')
        plt.ylabel('Imbalance Score')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        imbalance_path = self.output_manager.get_imbalance_plot_path(f'{output_prefix}_imbalance_evolution.png')
        plt.savefig(imbalance_path, dpi=300, bbox_inches='tight')
        plt.close()

        # 2. Resource Utilization Evolution (one plot per resource)
        for resource in ['cpu', 'mem', 'disk']:
            plt.figure(figsize=(12, 6))

            plt.plot(placements, resource_metrics[resource]['max'],
                    marker='o', label='Max Utilization',
                    color=colors['max'], linewidth=2)
            plt.plot(placements, resource_metrics[resource]['avg'],
                    marker='s', label='Avg Utilization',
                    color=colors['avg'], linewidth=2)
            plt.plot(placements, resource_metrics[resource]['std'],
                    marker='^', label='Standard Deviation',
                    color=colors['std'], linewidth=2)

            plt.title(f'{resource.upper()} Metrics Evolution - {output_prefix}')
            plt.xlabel('Number of VMs Placed')
            plt.ylabel('Metric Value')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            metrics_path = self.output_manager.get_metrics_plot_path(f'{output_prefix}_{resource}_metrics_evolution.png')
            plt.savefig(metrics_path, dpi=300, bbox_inches='tight')
            plt.close()

        # 3. Combined Resource Max Utilization
        plt.figure(figsize=(12, 6))
        for resource in ['cpu', 'mem', 'disk']:
            plt.plot(placements, resource_metrics[resource]['max'],
                    marker='o', label=f'{resource.upper()} Max',
                    color=colors[resource], linewidth=2)

        plt.title(f'Maximum Utilization Evolution by Resource - {output_prefix}')
        plt.xlabel('Number of VMs Placed')
        plt.ylabel('Maximum Utilization')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        combined_path = self.output_manager.get_resource_evolution_plot_path(f'{output_prefix}_combined_max_utilization.png'
        )
        plt.savefig(combined_path, dpi=300, bbox_inches='tight')
        plt.close()

        # 4. Heat map of resource utilization over time
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

        for ax, resource in zip([ax1, ax2, ax3], ['cpu', 'mem', 'disk']):
            data = np.array([
                resource_metrics[resource]['max'],
                resource_metrics[resource]['avg'],
                resource_metrics[resource]['std']
            ])

            im = ax.imshow(data, aspect='auto', cmap='YlOrRd')
            ax.set_yticks(range(3))
            ax.set_yticklabels(['Max', 'Avg', 'Std'])
            ax.set_xlabel('Number of VMs Placed')
            ax.set_title(f'{resource.upper()} Metrics Heatmap')
            plt.colorbar(im, ax=ax)

        plt.tight_layout()
        heatmap_path = self.output_manager.get_heatmap_plot_path(f'{output_prefix}_metrics_heatmap.png')
        plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
        plt.close()

        # 5. Percentage-based plots (0-100% scale)
        for resource in ['cpu', 'mem', 'disk']:
            plt.figure(figsize=(12, 6))

            # Convert to percentages
            max_util = [x * 100 for x in resource_metrics[resource]['max']]
            avg_util = [x * 100 for x in resource_metrics[resource]['avg']]
            std_util = [x * 100 for x in resource_metrics[resource]['std']]

            plt.plot(placements, max_util,
                    marker='o', label='Max Utilization',
                    color=colors['max'], linewidth=2)
            plt.plot(placements, avg_util,
                    marker='s', label='Avg Utilization',
                    color=colors['avg'], linewidth=2)
            plt.plot(placements, std_util,
                    marker='^', label='Standard Deviation',
                    color=colors['std'], linewidth=2)

            plt.title(f'{resource.upper()} Metrics Evolution (%) - {output_prefix}')
            plt.xlabel('Number of VMs Placed')
            plt.ylabel('Percentage (%)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.ylim(0, 100)  # Set y-axis from 0 to 100%
            plt.tight_layout()
            util_path = self.output_manager.get_utilization_plot_path(
                f'{output_prefix}_{resource}_metrics_evolution_percent.png'
            )
            plt.savefig(util_path, dpi=300, bbox_inches='tight')
            plt.close()


        # Add new plot for per-cluster utilization evolution
        plt.figure(figsize=(12, 6))

        # Extract utilization data per cluster
        cluster_utils = {cluster: {
            'cpu': [], 'mem': [], 'disk': []
        } for cluster in self.clusters}

        # Collect data points
        for metric in self.metrics_history:
            for cluster in self.clusters:
                for resource in ['cpu', 'mem', 'disk']:
                    cluster_utils[cluster][resource].append(
                        metric.resources[resource].cluster_distribution[cluster] * 100
                    )

        # Plot lines for each cluster and resource
        markers = ['o', 's', '^']  # Different markers for different resources
        linestyles = ['-', '--', '-.', ':']  # Different line styles for different clusters
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Different colors for clusters

        for i, (cluster, utils) in enumerate(cluster_utils.items()):
            for j, (resource, values) in enumerate(utils.items()):
                plt.plot(
                    range(1, len(values) + 1),
                    values,
                    label=f'{cluster} - {resource.upper()}',
                    marker=markers[j],
                    linestyle=linestyles[i % len(linestyles)],
                    color=colors[i % len(colors)],
                    linewidth=2,
                    markersize=6,
                    alpha=0.7
                )

        plt.title(f'Resource Utilization Evolution by Cluster - {output_prefix}')
        plt.xlabel('Number of VMs Placed')
        plt.ylabel('Utilization (%)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)

        # Adjust layout to prevent legend cutoff
        plt.tight_layout()

        # Save the new plot
        per_cluster_path = self.output_manager.get_utilization_plot_path(
            f'{output_prefix}_per_cluster_evolution.png'
        )
        plt.savefig(per_cluster_path, dpi=300, bbox_inches='tight')
        plt.close()
