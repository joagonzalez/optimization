import time

import matplotlib.pyplot as plt
import numpy as np
from src.models.baseline_optimizer import BaselineOptimizer  # noqa
from src.models.min_max_optimizer import MinUtilizationOptimizer


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
        return result

    return wrapper


def create_combined_utilization_plot(
    initial_utilization,
    final_utilization,
    allocated_utilization,
    clusters,
    scenario_name,
    output_manager,
    vm_placement=None,
    vm_demand=None,
):
    resources = ["cpu", "mem", "disk"]
    x = np.arange(len(resources))
    width = 0.2

    # Create figure with GridSpec
    fig = plt.figure(figsize=(20, 12))
    gs = plt.GridSpec(2, 2, height_ratios=[1.5, 1])
    ax1 = fig.add_subplot(gs[0, 0])  # Top left
    ax2 = fig.add_subplot(gs[0, 1])  # Top right
    ax3 = fig.add_subplot(gs[1, :])  # Bottom (spans both columns)

    # Plot initial utilization
    for i, cluster in enumerate(clusters):
        values = [initial_utilization[cluster][r] * 100 for r in resources]
        ax1.bar(x + i * width, values, width, label=f"Cluster {cluster}")

    ax1.set_ylabel("Utilization (%)")
    ax1.set_title("Initial Cluster Utilization")
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(["CPU", "Memory", "Disk"])
    ax1.legend()
    ax1.set_ylim(0, 100)
    ax1.grid(True, linestyle="--", alpha=0.7)

    for i, cluster in enumerate(clusters):
        values = [initial_utilization[cluster][r] * 100 for r in resources]
        for j, v in enumerate(values):
            ax1.text(j + i * width, v + 1, f"{v:.1f}%", ha="center", va="bottom")

    # Plot final utilization
    for i, cluster in enumerate(clusters):
        values = [final_utilization[cluster][r] * 100 for r in resources]
        ax2.bar(x + i * width, values, width, label=f"Cluster {cluster}")

    ax2.set_ylabel("Utilization (%)")
    ax2.set_title("Final Cluster Utilization")
    ax2.set_xticks(x + width)
    ax2.set_xticklabels(["CPU", "Memory", "Disk"])
    ax2.legend()
    ax2.set_ylim(0, 100)
    ax2.grid(True, linestyle="--", alpha=0.7)

    for i, cluster in enumerate(clusters):
        values = [final_utilization[cluster][r] * 100 for r in resources]
        for j, v in enumerate(values):
            ax2.text(j + i * width, v + 1, f"{v:.1f}%", ha="center", va="bottom")

    # Add VM placement annotation
    if vm_placement is not None and vm_demand is not None:
        vm_info = ""
        for vm, cluster in vm_placement.items():
            vm_info += f"VM: {vm}\nPlaced in: Cluster {cluster}\n"
            vm_info += "Resources:\n"
            vm_info += f"  CPU: {vm_demand[vm]['cpu']} units\n"
            vm_info += f"  Memory: {vm_demand[vm]['mem']} units\n"
            vm_info += f"  Disk: {vm_demand[vm]['disk']} units\n"

        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        ax2.text(
            0.98,
            0.98,
            vm_info,
            transform=ax2.transAxes,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=props,
        )

    # Plot utilization after VM resources allocated
    for i, cluster in enumerate(clusters):
        values = [allocated_utilization[cluster][r] * 100 for r in resources]
        ax3.bar(x + i * width, values, width, label=f"Cluster {cluster}")

    ax3.set_ylabel("Utilization (%)")
    ax3.set_title("Utilization After VM Allocation")
    ax3.set_xticks(x + width)
    ax3.set_xticklabels(["CPU", "Memory", "Disk"])
    ax3.legend()
    ax3.set_ylim(0, 100)
    ax3.grid(True, linestyle="--", alpha=0.7)

    for i, cluster in enumerate(clusters):
        values = [allocated_utilization[cluster][r] * 100 for r in resources]
        for j, v in enumerate(values):
            ax3.text(j + i * width, v + 1, f"{v:.1f}%", ha="center", va="bottom")

    # Adjust layout
    plt.tight_layout()

    # Save the figure using output manager
    output_path = output_manager.get_plot_path(f"combined_utilization_{scenario_name}.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


@measure_time
def optimize_vm_placement(
    clusters,
    existing_placements,
    new_vms,
    current_usage,
    cluster_capacity,
    vm_demand,
    optimizer_class=MinUtilizationOptimizer,
):
    """
    Optimize VM placement using the specified optimizer
    """
    optimizer = optimizer_class(
        clusters,
        existing_placements,
        new_vms,
        current_usage,
        cluster_capacity,
        vm_demand,
    )
    return optimizer.optimize()


@measure_time
def main():
    clusters = ["c1", "c2"]
    existing_placements = {
        "vm1": "c1",  # vm1 is already in c1
        "vm2": "c2",  # vm2 is already in c2
    }
    new_vms = ["vm3"]

    # Current usage already includes existing VMs
    current_usage = {
        "c1": {"cpu": 0.6, "mem": 0.5, "disk": 0.4},  # Includes vm1
        "c2": {"cpu": 0.7, "mem": 0.4, "disk": 0.3},  # Includes vm2
    }

    cluster_capacity = {
        "c1": {"cpu": 100.0, "mem": 100.0, "disk": 100.0},
        "c2": {"cpu": 100.0, "mem": 100.0, "disk": 100.0},
    }

    # Only need demands for new VMs
    vm_demand = {
        "vm3": {"cpu": 5.0, "mem": 20.0, "disk": 10.0},
    }

    print("\nCurrent Cluster State:")
    for c in clusters:
        print(f"Cluster {c}:", {r: f"{v:.1%}" for r, v in current_usage[c].items()})

    print("\nVM Resource Demands:")
    for vm, demands in vm_demand.items():
        print(f"{vm}:", {r: f"{v:.1f} units" for r, v in demands.items()})

    result = optimize_vm_placement(
        clusters,
        existing_placements,
        new_vms,
        current_usage,
        cluster_capacity,
        vm_demand,
    )

    if result[0] is None:
        print("No feasible solution found")
        return

    placement_plan, cluster_utilization, final_utilization, final_placement = result

    # Calculate utilization after VM resources allocated
    allocated_utilization = {c: current_usage[c].copy() for c in clusters}
    for cluster in clusters:
        for vm, _demands in vm_demand.items():
            for r in ["cpu", "mem", "disk"]:
                allocated_utilization[cluster][r] += (
                    vm_demand[vm][r] / cluster_capacity[cluster][r]
                )

    # Create combined plot
    create_combined_utilization_plot(
        current_usage,
        cluster_utilization,
        allocated_utilization,
        clusters,
        "combined_utilization.png",
        placement_plan,
        vm_demand,
    )

    print("\nNew VM Placement Plan:")
    for vm, cluster in placement_plan.items():
        print(f"Place {vm} in cluster {cluster}")

    print("\nResulting Cluster Utilization:")
    for cluster in clusters:
        print(f"\nCluster {cluster}:")
        for resource, utilization in cluster_utilization[cluster].items():
            print(f"  {resource}: {utilization:.2%}")

    print(
        f"\nOptimized minimum utilization across all resources: {final_utilization:.2%}"
    )

    print("\nFinal VM Distribution:")
    for cluster, vms in final_placement.items():
        print(f"Cluster {cluster}: {', '.join(sorted(vms))}")


if __name__ == "__main__":
    main()
