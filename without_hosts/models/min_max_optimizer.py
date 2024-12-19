from docplex.mp.model import Model
from models.base_optimizer import BaseVMOptimizer


class MinUtilizationOptimizer(BaseVMOptimizer):
    def create_model(self):
        self.mdl = Model('vm_cluster_placement')

        # Decision variables
        self.x = self.mdl.binary_var_dict(
            ((v, c) for v in self.new_vms for c in self.clusters),
            name='x'
        )
        self.z = self.mdl.continuous_var(name='z')

        self.print_decision_variables()

        # Each new VM must be placed exactly once
        for v in self.new_vms:
            constraint = self.mdl.add_constraint(
                self.mdl.sum(self.x[v,c] for c in self.clusters) == 1
            )
            self.print_constraints(constraint, f"Constraint for VM {v}")

        # Resource capacity constraints
        for c in self.clusters:
            for r in self.resources:
                current_resource_usage = self.current_usage[c][r] * self.cluster_capacity[c][r]

                # Capacity constraint
                constraint = self.mdl.add_constraint(
                    self.mdl.sum(self.vm_demand[v][r] * self.x[v,c] for v in self.new_vms) +
                    current_resource_usage <= self.cluster_capacity[c][r]
                )
                self.print_constraints(constraint, f"Constraint for cluster {c}, resource {r}")

                # Utilization constraint
                z_constraint = self.mdl.add_constraint(
                    (self.mdl.sum(self.vm_demand[v][r] * self.x[v,c] for v in self.new_vms) +
                    current_resource_usage) / self.cluster_capacity[c][r] <= self.z
                )
                self.print_constraints(z_constraint, f"Z Constraint - Cluster {c}, Resource {r}")

        return self.mdl

    def add_objective(self):
        self.mdl.minimize(self.z)

    def solve(self):
        solution = self.mdl.solve()
        if solution is None:
            return None, None, None, None

        # Create placement plan
        placement_plan = {}
        final_utilization = solution.get_value(self.z)

        self.print_optimization_results(final_utilization)

        for v in self.new_vms:
            for c in self.clusters:
                if solution.get_value(self.x[v,c]) > 0.5:
                    placement_plan[v] = c

        cluster_utilization = self.calculate_utilization(solution, placement_plan)

        # Calculate final placement
        final_placement = {c: [] for c in self.clusters}
        for vm, cluster in self.existing_placements.items():
            final_placement[cluster].append(vm)
        for vm, cluster in placement_plan.items():
            final_placement[cluster].append(vm)

        return placement_plan, cluster_utilization, final_utilization, final_placement
