from test_cases import generate_test_cases
from metrics import PlacementMetrics
from optimization import optimize_vm_placement, create_combined_utilization_plot
import time
import os

def run_tests():
    test_cases = generate_test_cases()
    results = {}

    for test_case in test_cases:
        print(f"\nRunning test case: {test_case.name}")
        print("=" * 50)

        start_time = time.time()

        result = optimize_vm_placement(
            test_case.clusters,
            test_case.existing_placements,
            test_case.new_vms,
            test_case.current_usage,
            test_case.cluster_capacity,
            test_case.vm_demand
        )

        execution_time = time.time() - start_time

        metrics = PlacementMetrics()
        if result[0] is not None:
            placement_plan, cluster_utilization, final_utilization, final_placement = result
            metrics.calculate_metrics(cluster_utilization, execution_time)

            # Create visualization
            output_dir = "test_results"
            os.makedirs(output_dir, exist_ok=True)
            create_combined_utilization_plot(
                test_case.current_usage,
                cluster_utilization,
                cluster_utilization,  # You might want to modify this for allocated utilization
                test_case.clusters,
                f"{output_dir}/{test_case.name}_utilization.png",
                placement_plan,
                test_case.vm_demand
            )

        results[test_case.name] = metrics
        print(f"\nResults for {test_case.name}:")
        print(metrics)

    return results

if __name__ == "__main__":
    results = run_tests()
