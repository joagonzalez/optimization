# AM1-TP/optimization/without_hosts/optimization.py

import time
import numpy as np
import matplotlib.pyplot as plt
from docplex.mp.model import Model



def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
        return result
    return wrapper

def create_combined_utilization_plot(initial_utilization, final_utilization, allocated_utilization, clusters, output_file):
    resources = ['cpu', 'mem', 'disk']
    x = np.arange(len(resources))
    width = 0.2

    # Create figure with GridSpec
    fig = plt.figure(figsize=(20, 12))

    # Create a 2x2 grid, then merge the bottom row
    gs = plt.GridSpec(2, 2, height_ratios=[1, 1.5])
    ax1 = fig.add_subplot(gs[0, 0])  # Top left
    ax2 = fig.add_subplot(gs[0, 1])  # Top right
    ax3 = fig.add_subplot(gs[1, :])  # Bottom (spans both columns)

    # Remove the unused subplot if it exists
    if len(fig.axes) > 3:
        fig.delaxes(fig.axes[3])

    # Plot initial utilization
    for i, cluster in enumerate(clusters):
        values = [initial_utilization[cluster][r] * 100 for r in resources]
        ax1.bar(x + i*width, values, width, label=f'Cluster {cluster}')

    ax1.set_ylabel('Utilization (%)')
    ax1.set_title('Initial Cluster Utilization')
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(['CPU', 'Memory', 'Disk'])
    ax1.legend()
    ax1.set_ylim(0, 100)
    ax1.grid(True, linestyle='--', alpha=0.7)

    for i, cluster in enumerate(clusters):
        values = [initial_utilization[cluster][r] * 100 for r in resources]
        for j, v in enumerate(values):
            ax1.text(j + i*width, v + 1, f'{v:.1f}%', ha='center', va='bottom')

    # Plot final utilization
    for i, cluster in enumerate(clusters):
        values = [final_utilization[cluster][r] * 100 for r in resources]
        ax2.bar(x + i*width, values, width, label=f'Cluster {cluster}')

    ax2.set_ylabel('Utilization (%)')
    ax2.set_title('Final Cluster Utilization')
    ax2.set_xticks(x + width)
    ax2.set_xticklabels(['CPU', 'Memory', 'Disk'])
    ax2.legend()
    ax2.set_ylim(0, 100)
    ax2.grid(True, linestyle='--', alpha=0.7)

    for i, cluster in enumerate(clusters):
        values = [final_utilization[cluster][r] * 100 for r in resources]
        for j, v in enumerate(values):
            ax2.text(j + i*width, v + 1, f'{v:.1f}%', ha='center', va='bottom')

    # Plot utilization after VM resources allocated
    for i, cluster in enumerate(clusters):
        values = [allocated_utilization[cluster][r] * 100 for r in resources]
        ax3.bar(x + i*width, values, width, label=f'Cluster {cluster}')

    ax3.set_ylabel('Utilization (%)')
    ax3.set_title('Utilization After VM Allocation')
    ax3.set_xticks(x + width)
    ax3.set_xticklabels(['CPU', 'Memory', 'Disk'])
    ax3.legend()
    ax3.set_ylim(0, 100)
    ax3.grid(True, linestyle='--', alpha=0.7)

    for i, cluster in enumerate(clusters):
        values = [allocated_utilization[cluster][r] * 100 for r in resources]
        for j, v in enumerate(values):
            ax3.text(j + i*width, v + 1, f'{v:.1f}%', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

@measure_time
def optimize_vm_placement(clusters, existing_placements, new_vms, current_usage, cluster_capacity, vm_demand):
    # Create model
    mdl = Model('vm_cluster_placement')

    # Decision variables only for new VMs
    print("\nDecision Variables Generated:")
    x = mdl.binary_var_dict(((v, c) for v in new_vms for c in clusters), name='x')
    print("Binary variables x[v,c]:")
    for v in new_vms:
        for c in clusters:
            print(f"x[{v},{c}] ∈ {{0,1}}")

    z = mdl.continuous_var(name='z')
    print("\nContinuous variable z:")
    print("z ∈ ℝ")

    print("\nInitial State:")
    for vm, cluster in existing_placements.items():
        print(f"VM {vm} is already placed in cluster {cluster}")

    # Each new VM must be placed exactly once
    for v in new_vms:
        constraint = mdl.add_constraint(mdl.sum(x[v,c] for c in clusters) == 1)
        print(f"Constraint for VM {v}: {constraint}")

    # Resource capacity constraints
    resources = ['cpu', 'mem', 'disk']
    for c in clusters:
        for r in resources:
            # We only consider current cluster utilization and new VMs
            current_resource_usage = current_usage[c][r] * cluster_capacity[c][r]
            constraint = mdl.add_constraint(
                mdl.sum(vm_demand[v][r] * x[v,c] for v in new_vms) +
                current_resource_usage <= cluster_capacity[c][r]
            )
            print(f"Constraint for cluster {c}, resource {r}: {constraint}")

    # Min utilization constraints
    for r in resources:
        for c in clusters:
            total_capacity = cluster_capacity[c][r]
            current_resource_usage = current_usage[c][r] * total_capacity

            constraint = mdl.add_constraint(
                (mdl.sum(vm_demand[v][r] * x[v,c] for v in new_vms) +
                current_resource_usage) / total_capacity >= z
            )
            print(f"Constraint for cluster {c}, resource {r}: {constraint}")

    # Objective
    mdl.maximize(z)

    # Solve
    solution = mdl.solve()

    if solution is None:
        return None, None, None, None

    # Create placement plan (only for new VMs)
    placement_plan = {}
    final_utilization = solution.get_value(z)

    # Get the optimal value (z) and explain what it means
    final_utilization = solution.get_value(z)
    print("\nOptimization Results:")
    print(f"z = {final_utilization:.2%} (minimum utilization across all resources and clusters)")

    print("\nDetailed resource utilization per cluster:")
    for c in clusters:
        print(f"\nCluster {c}:")
        for r in resources:
            # Calculate total resource usage after placement
            current_resource_usage = current_usage[c][r] * cluster_capacity[c][r]
            new_vm_usage = sum(vm_demand[v][r] * solution.get_value(x[v,c]) for v in new_vms)
            total_usage = (current_resource_usage + new_vm_usage) / cluster_capacity[c][r]
            print(f"  {r}: {total_usage:.2%} {'(minimum)' if abs(total_usage - final_utilization) < 1e-6 else ''}")

    # Extract the placement decisions
    for v in new_vms:
        for c in clusters:
            if solution.get_value(x[v,c]) > 0.5:
                placement_plan[v] = c

    # Calculate resulting utilization for each cluster and resource
    cluster_utilization = {c: {r: 0.0 for r in resources} for c in clusters}

    # Start with current cluster usage (which includes existing VMs)
    for c in clusters:
        for r in resources:
            cluster_utilization[c][r] = current_usage[c][r]

    # Add only new VM placements
    for v, c in placement_plan.items():
        for r in resources:
            cluster_utilization[c][r] += vm_demand[v][r] / cluster_capacity[c][r]

    # Calculate final VM placement distribution
    final_placement = {c: [] for c in clusters}
    # Add existing VMs to final placement
    for vm, cluster in existing_placements.items():
        final_placement[cluster].append(vm)
    # Add new VMs to final placement
    for vm, cluster in placement_plan.items():
        final_placement[cluster].append(vm)

    return placement_plan, cluster_utilization, final_utilization, final_placement

@measure_time
def main():
    clusters = ['c1', 'c2']
    existing_placements = {
        'vm1': 'c1',  # vm1 is already in c1
        'vm2': 'c2'   # vm2 is already in c2
    }
    new_vms = ['vm3']

    # Current usage already includes existing VMs
    current_usage = {
        'c1': {'cpu': 0.6, 'mem': 0.5, 'disk': 0.4},  # Includes vm1
        'c2': {'cpu': 0.7, 'mem': 0.4, 'disk': 0.3}   # Includes vm2
    }

    cluster_capacity = {
        'c1': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
        'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0}
    }

    # Only need demands for new VMs
    vm_demand = {
        'vm3': {'cpu': 5.0, 'mem': 20.0, 'disk': 10.0},
    }

    print("\nCurrent Cluster State:")
    for c in clusters:
        print(f"Cluster {c}:", {r: f"{v:.1%}" for r, v in current_usage[c].items()})

    print("\nVM Resource Demands:")
    for vm, demands in vm_demand.items():
        print(f"{vm}:", {r: f"{v:.1f} units" for r, v in demands.items()})

    result = optimize_vm_placement(
        clusters, existing_placements, new_vms, current_usage,
        cluster_capacity, vm_demand
    )

    if result[0] is None:
        print("No feasible solution found")
        return

    placement_plan, cluster_utilization, final_utilization, final_placement = result

    # Calculate utilization after VM resources allocated
    allocated_utilization = {c: current_usage[c].copy() for c in clusters}
    for cluster in clusters:
        for vm, demands in vm_demand.items():
            for r in ['cpu', 'mem', 'disk']:
                allocated_utilization[cluster][r] += vm_demand[vm][r] / cluster_capacity[cluster][r]

    # Create combined plot
    create_combined_utilization_plot(
        current_usage,
        cluster_utilization,
        allocated_utilization,
        clusters,
        'combined_utilization.png'
    )

    print("\nNew VM Placement Plan:")
    for vm, cluster in placement_plan.items():
        print(f"Place {vm} in cluster {cluster}")

    print("\nResulting Cluster Utilization:")
    for cluster in clusters:
        print(f"\nCluster {cluster}:")
        for resource, utilization in cluster_utilization[cluster].items():
            print(f"  {resource}: {utilization:.2%}")

    print(f"\nOptimized minimum utilization across all resources: {final_utilization:.2%}")

    print("\nFinal VM Distribution:")
    for cluster, vms in final_placement.items():
        print(f"Cluster {cluster}: {', '.join(sorted(vms))}")

if __name__ == "__main__":
    main()
