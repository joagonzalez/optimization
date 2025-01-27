from docplex.mp.model import Model

from src.models.base_optimizer import BaseVMOptimizer


class MinMaxPerClusterOptimizer(BaseVMOptimizer):
    """
    Optimizer that minimizes the maximum utilization per resource per cluster.
    This ensures balanced resource utilization within each cluster independently.
    """

    def create_model(self):
        """Create optimization model with variables and base constraints"""
        self.mdl = Model("vm_cluster_placement_min_max_per_cluster")

        # Decision variables for VM placement
        self.x = self.mdl.binary_var_dict(
            ((v, c) for v in self.new_vms for c in self.clusters), name="x"
        )

        # Variables for max utilization per resource per cluster
        self.z = self.mdl.continuous_var_dict(
            ((c, r) for c in self.clusters for r in self.resources), name="z"
        )

        self.print_decision_variables()

        # Each VM must be placed exactly once
        for v in self.new_vms:
            constraint = self.mdl.add_constraint(
                self.mdl.sum(self.x[v, c] for c in self.clusters) == 1,
                f"vm_placement_{v}",
            )
            self.print_constraints(constraint, f"Placement constraint for VM {v}")

        # Resource capacity and utilization constraints
        for c in self.clusters:
            for r in self.resources:
                current_resource_usage = (
                    self.current_usage[c][r] * self.cluster_capacity[c][r]
                )

                # Capacity constraint
                capacity_constraint = self.mdl.add_constraint(
                    self.mdl.sum(
                        self.vm_demand[v][r] * self.x[v, c] for v in self.new_vms
                    )
                    + current_resource_usage
                    <= self.cluster_capacity[c][r],
                    f"capacity_{c}_{r}",
                )
                self.print_constraints(
                    capacity_constraint,
                    f"Capacity constraint for cluster {c}, resource {r}",
                )

                # Max utilization constraint per resource per cluster
                utilization_constraint = self.mdl.add_constraint(
                    (
                        self.mdl.sum(
                            self.vm_demand[v][r] * self.x[v, c] for v in self.new_vms
                        )
                        + current_resource_usage
                    )
                    / self.cluster_capacity[c][r]
                    == self.z[c, r],
                    f"utilization_{c}_{r}",
                )
                self.print_constraints(
                    utilization_constraint,
                    f"Utilization constraint for cluster {c}, resource {r}",
                )

        return self.mdl

    def add_objective(self):
        """
        Minimize the maximum utilization across all resources and clusters.
        Using sum of max utilizations per cluster to balance across clusters.
        """
        self.mdl.minimize(
            self.mdl.sum(self.z[c, r] for c in self.clusters for r in self.resources)
        )

    def optimize(self):
        """Main optimization workflow"""
        self.print_initial_state()
        model = self.create_model()
        if model is None:
            return None, None, None, None

        self.add_objective()

        return self.solve()

    def solve(self):
        """Solve the optimization model and return results"""
        solution = self.mdl.solve()
        if solution is None:
            return None, None, None, None

        # Create placement plan
        placement_plan = {}
        for v in self.new_vms:
            for c in self.clusters:
                if solution.get_value(self.x[v, c]) > 0.5:
                    placement_plan[v] = c

        # Calculate final utilization per cluster and resource
        cluster_utilization = {
            c: {r: 0.0 for r in self.resources} for c in self.clusters
        }

        for c in self.clusters:
            for r in self.resources:
                cluster_utilization[c][r] = solution.get_value(self.z[c, r])

        # Get overall maximum utilization
        final_utilization = max(
            max(utilization.values()) for utilization in cluster_utilization.values()
        )

        # Calculate final placement
        final_placement = {c: [] for c in self.clusters}
        for vm, cluster in self.existing_placements.items():
            final_placement[cluster].append(vm)
        for vm, cluster in placement_plan.items():
            final_placement[cluster].append(vm)

        # Print optimization results
        print("\nOptimization Results:")
        print("\nFinal Utilization per Cluster and Resource:")
        for c in self.clusters:
            print(f"\nCluster {c}:")
            for r in self.resources:
                print(f"  {r}: {cluster_utilization[c][r]:.2%}")

        print(f"\nMaximum utilization across all clusters: {final_utilization:.2%}")
        print("\nPlacement Plan:")
        for vm, cluster in placement_plan.items():
            print(f"VM {vm} → Cluster {cluster}")

        return placement_plan, cluster_utilization, final_utilization, final_placement
