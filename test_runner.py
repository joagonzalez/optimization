import argparse
import json

import matplotlib.pyplot as plt
import numpy as np

from src.services.real_time_viz import run_visualization
from src.services.sequential_placement import SequentialPlacementSimulation
from src.services.test_config import generate_test_scenarios
from src.services.utils import OutputManager


class TestRunner:
    def __init__(self, use_visualization=False):  # Add parameter
        self.scenarios = generate_test_scenarios()
        self.results = {}
        self.use_visualization = use_visualization  # Store preference
        self.output_manager = OutputManager()  # Add output manager

    def run_all_tests(self):
        try:
            print(f"\nStarting test run: {self.output_manager.run_id}")
            for i, scenario in enumerate(self.scenarios):
                print(f"\nRunning scenario: {scenario.name}")
                print("=" * 50)

                simulation = SequentialPlacementSimulation(
                    scenario, self.output_manager
                )

                if self.use_visualization:
                    try:
                        run_visualization(simulation)
                        # Check if this is the last scenario
                        if i == len(self.scenarios) - 1:
                            # For the last scenario, change button text
                            print("Last scenario completed. Click 'Finish' to exit.")
                    except Exception as e:
                        print(f"Visualization error: {e}")
                        continue
                else:
                    print(f"Running without visualization: {scenario.name}")
                    simulation.run_simulation()

                scenario_results = simulation.summarize_results(
                    simulation.total_time, simulation.execution_times
                )

                if scenario_results:
                    print(f"Completed scenario: {scenario.name}")
                    self.results[scenario.name] = scenario_results
                    self._print_scenario_results(scenario.name, scenario_results)
                else:
                    print(f"Failed to get results for scenario: {scenario.name}")

                # Plot results for this scenario
                simulation.plot_results()

            # Create comparative plots after all scenarios are complete
            self.create_comparative_plots()

            self._save_results()
            print(f"\nResults saved in: {self.output_manager.output_dir}")

        finally:
            # Ensure all tkinter windows are closed
            try:
                import tkinter as tk

                root = tk.Tk()
                root.destroy()
            except Exception:
                pass

    def _print_scenario_results(self, scenario_name, results):
        print(f"\nResults for scenario: {scenario_name}")

        if not results["success"]:
            print(f"Simulation failed: {results['error']}")
            return

        print(f"Total time: {results['total_time']:.2f} seconds")
        print(f"VMs successfully placed: {results['vms_placed']}")
        print(f"Average placement time: {results['avg_placement_time']:.3f} seconds")
        print(f"Min placement time: {results['min_placement_time']:.3f} seconds")
        print(f"Max placement time: {results['max_placement_time']:.3f} seconds")

        print("\nFinal Resource Utilization:")
        for cluster, usage in results["final_utilization"].items():
            print(
                f"{cluster}: {', '.join(f'{r}: {v*100:.1f}%' for r, v in usage.items())}"
            )

        print("\nCluster Distribution:")
        for cluster, vms in results["cluster_distribution"].items():
            print(f"{cluster}: {len(vms)} VMs")

    def _save_results(self):
        results_data = {
            scenario_name: {
                "success": results["success"],
                "error": results["error"],
                "total_time": results["total_time"],
                "vms_placed": results["vms_placed"],
                "avg_placement_time": results["avg_placement_time"],
                "min_placement_time": results["min_placement_time"],
                "max_placement_time": results["max_placement_time"],
                "final_utilization": results["final_utilization"],
                "cluster_distribution": {
                    cluster: len(vms)
                    for cluster, vms in results["cluster_distribution"].items()
                },
                # Remove the to_dict() call since metrics are already in dict format
                "metrics_history": results["metrics_history"]
                if results["metrics_history"]
                else [],
                "final_metrics": results["final_metrics"],
            }
            for scenario_name, results in self.results.items()
        }

        output_file = self.output_manager.get_data_path("test_results.json")
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2)

    def create_comparative_plots(self):
        """
        Create comparative plots showing initial and final metrics across all scenarios.
        """
        if not self.results:
            print("No results available for comparison")
            return

        plt.style.use("default")

        # Prepare data
        scenarios = list(self.results.keys())
        n_scenarios = len(scenarios)

        # Define proper color schemes
        colors = {
            "cpu": {"light": "#90EE90", "dark": "#2F4F4F"},
            "mem": {"light": "#FFB6C1", "dark": "#8B0000"},
            "disk": {"light": "#87CEEB", "dark": "#00008B"},
        }

        def extract_resource_metrics(metrics_data, is_initial=True):
            """Helper function to extract resource metrics"""
            try:
                if is_initial:
                    if not metrics_data["metrics_history"]:
                        print("Warning: No metrics history found for scenario")
                        return None
                    metrics = metrics_data["metrics_history"][0]
                else:
                    if not metrics_data["final_metrics"]:
                        print("Warning: No final metrics found for scenario")
                        return None
                    metrics = metrics_data["final_metrics"]

                return {
                    "cpu": metrics["resources"]["cpu"],
                    "mem": metrics["resources"]["mem"],
                    "disk": metrics["resources"]["disk"],
                }
            except (KeyError, IndexError) as e:
                print(f"Error extracting metrics: {e}")
                return None

        # Extract initial and final metrics for each scenario
        initial_metrics = {}
        final_metrics = {}
        imbalance_scores = {"initial": [], "final": []}
        valid_scenarios = []

        for scenario in scenarios:
            result = self.results[scenario]
            if not result["success"]:
                print(f"Skipping failed scenario: {scenario}")
                continue

            initial_metric = extract_resource_metrics(result, True)
            final_metric = extract_resource_metrics(result, False)

            if initial_metric is None or final_metric is None:
                print(f"Skipping scenario {scenario} due to missing metrics")
                continue

            try:
                initial_imbalance = result["metrics_history"][0]["overall_imbalance"]
                final_imbalance = result["final_metrics"]["overall_imbalance"]
            except (KeyError, IndexError):
                print(f"Skipping scenario {scenario} due to missing imbalance scores")
                continue

            initial_metrics[scenario] = initial_metric
            final_metrics[scenario] = final_metric
            imbalance_scores["initial"].append(initial_imbalance)
            imbalance_scores["final"].append(final_imbalance)
            valid_scenarios.append(scenario)

        if not valid_scenarios:
            print("No valid scenarios with complete metrics found")
            return

        # Update n_scenarios to use only valid ones
        scenarios = valid_scenarios
        n_scenarios = len(scenarios)

        # Continue with plotting only if we have valid scenarios
        if n_scenarios > 0:
            # 1. Bar plot comparing initial and final imbalance scores
            plt.figure(figsize=(12, 6))
            x = np.arange(n_scenarios)
            width = 0.35

            plt.bar(
                x - width / 2,
                imbalance_scores["initial"],
                width,
                label="Initial",
                color="#D3D3D3",
            )
            plt.bar(
                x + width / 2,
                imbalance_scores["final"],
                width,
                label="Final",
                color="#4169E1",
            )

            plt.xlabel("Scenarios")
            plt.ylabel("Imbalance Score")
            plt.title("Initial vs Final Imbalance Scores Across Scenarios")
            plt.xticks(x, scenarios, rotation=45)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(
                self.output_manager.get_comparative_plot_path(
                    "comparative_imbalance_scores.png"
                ),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

            # 2. Resource utilization comparison
            fig, axes = plt.subplots(3, 1, figsize=(12, 15))

            for idx, resource in enumerate(["cpu", "mem", "disk"]):
                ax = axes[idx]

                initial_max = [
                    initial_metrics[s][resource]["max_utilization"] * 100
                    for s in scenarios
                ]
                final_max = [
                    final_metrics[s][resource]["max_utilization"] * 100
                    for s in scenarios
                ]
                initial_avg = [
                    initial_metrics[s][resource]["avg_utilization"] * 100
                    for s in scenarios
                ]
                final_avg = [
                    final_metrics[s][resource]["avg_utilization"] * 100
                    for s in scenarios
                ]

                x = np.arange(n_scenarios)
                width = 0.2

                ax.bar(
                    x - width * 1.5,
                    initial_max,
                    width,
                    label="Initial Max",
                    color="#D3D3D3",
                )
                ax.bar(
                    x - width / 2,
                    final_max,
                    width,
                    label="Final Max",
                    color=colors[resource]["light"],
                )
                ax.bar(
                    x + width / 2,
                    initial_avg,
                    width,
                    label="Initial Avg",
                    color="#A9A9A9",
                )
                ax.bar(
                    x + width * 1.5,
                    final_avg,
                    width,
                    label="Final Avg",
                    color=colors[resource]["dark"],
                )

                ax.set_title(f"{resource.upper()} Utilization Comparison")
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45)
                ax.set_ylabel("Utilization (%)")
                ax.grid(True, alpha=0.3)
                ax.legend()

            plt.tight_layout()
            plt.savefig(
                self.output_manager.get_comparative_plot_path(
                    "comparative_resource_utilization.png"
                ),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

            # 3. Heatmap of improvement percentages
            improvements = np.zeros((3, n_scenarios))

            for idx, resource in enumerate(["cpu", "mem", "disk"]):
                for s_idx, scenario in enumerate(scenarios):
                    initial_imbalance = (
                        initial_metrics[scenario][resource]["max_utilization"]
                        - initial_metrics[scenario][resource]["avg_utilization"]
                    )
                    final_imbalance = (
                        final_metrics[scenario][resource]["max_utilization"]
                        - final_metrics[scenario][resource]["avg_utilization"]
                    )
                    if initial_imbalance > 0:
                        improvements[idx, s_idx] = (
                            (initial_imbalance - final_imbalance)
                            / initial_imbalance
                            * 100
                        )
                    else:
                        improvements[idx, s_idx] = 0

            plt.figure(figsize=(12, 6))
            im = plt.imshow(improvements, aspect="auto", cmap="RdYlGn")
            plt.colorbar(im, label="Improvement %")

            plt.yticks(range(3), ["CPU", "Memory", "Disk"])
            plt.xticks(range(n_scenarios), scenarios, rotation=45)
            plt.title("Resource Balance Improvement by Scenario (%)")

            # Add text annotations to the heatmap
            for i in range(3):
                for j in range(n_scenarios):
                    plt.text(
                        j,
                        i,
                        f"{improvements[i, j]:.1f}%",
                        ha="center",
                        va="center",
                        color="black",
                    )

            plt.tight_layout()
            plt.savefig(
                self.output_manager.get_comparative_plot_path(
                    "comparative_improvements_heatmap.png"
                ),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()
        else:
            print("No plots generated due to lack of valid data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run VM placement tests")
    parser.add_argument(
        "--no-viz", action="store_true", help="Run without visualization"
    )
    args = parser.parse_args()

    runner = TestRunner(use_visualization=not args.no_viz)
    print(f"Starting new test run with ID: {runner.output_manager.run_id}")
    runner.run_all_tests()
