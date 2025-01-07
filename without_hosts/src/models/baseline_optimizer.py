from typing import Dict, Optional, Tuple

from src.models.base_optimizer import BaseVMOptimizer


class BaselineOptimizer(BaseVMOptimizer):
    """
    Simple baseline optimizer that places VMs in clusters with most available resources,
    prioritizing CPU > Memory > Disk.
    """

    def create_model(self):
        """No optimization model needed for baseline strategy"""
        return None

    def add_objective(self):
        """No objective function needed for baseline strategy"""
        pass

    def get_available_resources(self, cluster: str) -> Dict[str, float]:
        """Calculate available resources for a given cluster"""
        available = {}
        for resource in self.resources:
            total = self.cluster_capacity[cluster][resource]
            used = self.current_usage[cluster][resource] * total
            available[resource] = total - used
        return available

    def can_place_vm(self, vm: str, cluster: str) -> bool:
        """Check if VM can be placed in cluster without exceeding capacity"""
        available = self.get_available_resources(cluster)
        for resource in self.resources:
            if self.vm_demand[vm][resource] > available[resource]:
                return False
        return True

    def select_best_cluster(self, vm: str) -> Optional[str]:
        """
        Select best cluster for VM placement based on available resources,
        prioritizing CPU > Memory > Disk
        """
        # Get available resources for each cluster
        cluster_resources = {
            cluster: self.get_available_resources(cluster) for cluster in self.clusters
        }

        # Filter clusters that can accommodate the VM
        valid_clusters = [
            cluster for cluster in self.clusters if self.can_place_vm(vm, cluster)
        ]

        if not valid_clusters:
            return None

        # Sort clusters by available resources (CPU > Memory > Disk)
        sorted_clusters = sorted(
            valid_clusters,
            key=lambda c: (
                cluster_resources[c]["cpu"],  # Primary sort: CPU
                cluster_resources[c]["mem"],  # Secondary sort: Memory
                cluster_resources[c]["disk"],  # Tertiary sort: Disk
            ),
            reverse=True,  # Most available resources first
        )

        return sorted_clusters[0]

    def update_usage(self, vm: str, cluster: str):
        """Update cluster resource usage after VM placement"""
        for resource in self.resources:
            demand = self.vm_demand[vm][resource]
            total = self.cluster_capacity[cluster][resource]
            self.current_usage[cluster][resource] += demand / total

    def solve(self) -> Tuple[Optional[Dict], Optional[Dict], Optional[float], Optional[Dict]]:
        """
        Implement baseline placement strategy
        Returns: (placement_plan, cluster_utilization, final_utilization, final_placement)
        """
        self.print_initial_state()
        placement_plan = {}
        final_placement = {c: [] for c in self.clusters}

        # Add existing VMs to final placement
        for vm, cluster in self.existing_placements.items():
            final_placement[cluster].append(vm)

        # Place each new VM
        for vm in self.new_vms:
            best_cluster = self.select_best_cluster(vm)

            if best_cluster is None:
                print(f"Failed to place VM {vm}: No cluster has sufficient resources")
                return None, None, None, None

            # Record placement
            placement_plan[vm] = best_cluster
            final_placement[best_cluster].append(vm)

            # Update cluster usage
            self.update_usage(vm, best_cluster)

        # Get final cluster utilization
        cluster_utilization = {
            cluster: {
                resource: self.current_usage[cluster][resource]
                for resource in self.resources
            }
            for cluster in self.clusters
        }

        # Calculate final utilization (maximum across all resources and clusters)
        final_utilization = max(
            max(usage.values())
            for usage in self.current_usage.values()
        )

        # Print results
        print("\nPlacement Summary:")
        for vm, cluster in placement_plan.items():
            print(f"VM {vm} → Cluster {cluster}")

        print("\nFinal Cluster Utilization:")
        for cluster, usage in cluster_utilization.items():
            print(f"{cluster}:", {r: f"{v:.1%}" for r, v in usage.items()})

        # Return early if no placements were made
        if not placement_plan:
            return None, None, None, None

        return placement_plan, cluster_utilization, final_utilization, final_placement
