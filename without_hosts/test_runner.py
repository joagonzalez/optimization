# test_runner.py
import os
import json
from datetime import datetime
from real_time_viz import run_visualization
from test_config import generate_test_scenarios
from sequential_placement import SequentialPlacementSimulation


class TestRunner:
    def __init__(self, use_visualization=False):  # Add parameter
            self.scenarios = generate_test_scenarios()
            self.results = {}
            self.use_visualization = use_visualization  # Store preference

    def run_all_tests(self):
        try:
            for i, scenario in enumerate(self.scenarios):
                print(f"\nRunning scenario: {scenario.name}")
                print("=" * 50)

                simulation = SequentialPlacementSimulation(scenario)

                if self.use_visualization:
                    try:
                        run_visualization(simulation)
                        # Check if this is the last scenario
                        if i == len(self.scenarios) - 1:
                            # For the last scenario, change button text
                            print("Last scenario completed. Click 'Finish' to exit.")
                        scenario_results = simulation.summarize_results(
                            simulation.total_time,
                            simulation.execution_times
                        )
                    except Exception as e:
                        print(f"Visualization error: {e}")
                        continue
                else:
                    scenario_results = simulation.run_simulation()

                simulation.plot_results()
                self.results[scenario.name] = scenario_results
                self._print_scenario_results(scenario.name, scenario_results)

            self._save_results()

        finally:
            # Ensure all tkinter windows are closed
            try:
                import tkinter as tk
                root = tk.Tk()
                root.destroy()
            except:
                pass

    def _print_scenario_results(self, scenario_name, results):
            print(f"\nResults for scenario: {scenario_name}")

            if not results['success']:
                print(f"Simulation failed: {results['error']}")
                return

            print(f"Total time: {results['total_time']:.2f} seconds")
            print(f"VMs successfully placed: {results['vms_placed']}")
            print(f"Average placement time: {results['avg_placement_time']:.3f} seconds")
            print(f"Min placement time: {results['min_placement_time']:.3f} seconds")
            print(f"Max placement time: {results['max_placement_time']:.3f} seconds")

            print("\nFinal Resource Utilization:")
            for cluster, usage in results['final_utilization'].items():
                print(f"{cluster}: {', '.join(f'{r}: {v*100:.1f}%' for r, v in usage.items())}")

            print("\nCluster Distribution:")
            for cluster, vms in results['cluster_distribution'].items():
                print(f"{cluster}: {len(vms)} VMs")

    def _save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            scenario_name: {
                'success': results['success'],
                'error': results['error'],
                'total_time': results['total_time'],
                'vms_placed': results['vms_placed'],
                'avg_placement_time': results['avg_placement_time'],
                'min_placement_time': results['min_placement_time'],
                'max_placement_time': results['max_placement_time'],
                'final_utilization': results['final_utilization'],
                'cluster_distribution': {
                    cluster: len(vms)
                    for cluster, vms in results['cluster_distribution'].items()
                },
                # Remove the to_dict() call since metrics are already in dict format
                'metrics_history': results['metrics_history'] if results['metrics_history'] else [],
                'final_metrics': results['final_metrics']
            }
            for scenario_name, results in self.results.items()
        }

        # Create test_results directory if it doesn't exist
        os.makedirs('test_results', exist_ok=True)

        output_file = f'test_results/test_results_{timestamp}.json'
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)

if __name__ == "__main__":
    runner = TestRunner(use_visualization=True)
    runner.run_all_tests()
