from abc import ABC, abstractmethod


class BaseVMOptimizer(ABC):
    def __init__(
        self,
        clusters,
        existing_placements,
        new_vms,
        current_usage,
        cluster_capacity,
        vm_demand,
    ):
        self.clusters = clusters
        self.existing_placements = existing_placements
        self.new_vms = new_vms
        self.current_usage = current_usage
        self.cluster_capacity = cluster_capacity
        self.vm_demand = vm_demand
        self.resources = ["cpu", "mem", "disk"]

    def print_initial_state(self):
        """Print initial state information"""
        print("\nInitial State:")
        for vm, cluster in self.existing_placements.items():
            print(f"VM {vm} is already placed in cluster {cluster}")

        print("\nCurrent Cluster State:")
        for c in self.clusters:
            print(
                f"Cluster {c}:",
                {r: f"{v:.1%}" for r, v in self.current_usage[c].items()},
            )

        print("\nVM Resource Demands:")
        for vm, demands in self.vm_demand.items():
            print(f"{vm}:", {r: f"{v:.1f} units" for r, v in demands.items()})

    def print_decision_variables(self):
        """Print decision variables information"""
        print("\nDecision Variables Generated:")
        print("Binary variables x[v,c]:")
        for v in self.new_vms:
            for c in self.clusters:
                print(f"x[{v},{c}] ∈ {{0,1}}")
        print("\nContinuous variable z:")
        print("z ∈ ℝ")

    def print_constraints(self, constraint, description):
        """Print constraint information"""
        print(f"{description}: {constraint}")

    def print_optimization_results(self, final_utilization):
        """Print optimization results"""
        print("\nOptimization Results:")
        print(
            f"z = {final_utilization:.2%} (max minimum utilization across all resources and clusters)"
        )

    @abstractmethod
    def create_model(self):
        """Create the optimization model with variables and constraints"""
        pass

    @abstractmethod
    def add_objective(self):
        """Define the objective function"""
        pass

    @abstractmethod
    def solve(self):
        """Solve the optimization model and return results"""
        pass

    def optimize(self):
        """Main optimization workflow"""
        self.print_initial_state()
        model = self.create_model()
        if model is None:
            return None, None, None, None

        self.add_objective()
        return self.solve()

    def calculate_utilization(self, solution, placement_plan):
        """Calculate cluster utilization based on solution"""
        cluster_utilization = {
            c: {r: 0.0 for r in self.resources} for c in self.clusters
        }

        # Start with current usage
        for c in self.clusters:
            for r in self.resources:
                cluster_utilization[c][r] = self.current_usage[c][r]

        # Add new VM placements
        for v, c in placement_plan.items():
            for r in self.resources:
                cluster_utilization[c][r] += (
                    self.vm_demand[v][r] / self.cluster_capacity[c][r]
                )

        return cluster_utilization
