import os
import uuid
from datetime import datetime


class OutputManager:
    def __init__(self):
        self.base_dir = "test_results"
        self.run_id = self._generate_run_id()
        self.output_dir = self._create_output_dir()

    def _generate_run_id(self):
        """Generate a unique run ID using timestamp and UUID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
        return f"{timestamp}_{short_uuid}"

    def _create_output_dir(self):
        """Create and return the path to the output directory for this run"""
        # Create base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)

        # Create run-specific directory
        run_dir = os.path.join(self.base_dir, self.run_id)
        os.makedirs(run_dir, exist_ok=True)

        # Create subdirectories for different types of output
        plot_dirs = [
            "utilization",  # For combined utilization plots
            "metrics",  # For metrics evolution plots
            "comparative",  # For comparative analysis plots
            "heatmaps",  # For heatmap visualizations
            "imbalance",  # For imbalance score plots
            "resource_evolution",  # For resource-specific evolution plots
        ]

        for dir_name in plot_dirs:
            os.makedirs(os.path.join(run_dir, "plots", dir_name), exist_ok=True)

        os.makedirs(os.path.join(run_dir, "data"), exist_ok=True)

        return run_dir

    def get_utilization_plot_path(self, filename):
        """Path for utilization plots"""
        return os.path.join(self.output_dir, "plots", "utilization", filename)

    def get_metrics_plot_path(self, filename):
        """Path for metrics evolution plots"""
        return os.path.join(self.output_dir, "plots", "metrics", filename)

    def get_comparative_plot_path(self, filename):
        """Path for comparative analysis plots"""
        return os.path.join(self.output_dir, "plots", "comparative", filename)

    def get_heatmap_plot_path(self, filename):
        """Path for heatmap plots"""
        return os.path.join(self.output_dir, "plots", "heatmaps", filename)

    def get_imbalance_plot_path(self, filename):
        """Path for imbalance score plots"""
        return os.path.join(self.output_dir, "plots", "imbalance", filename)

    def get_resource_evolution_plot_path(self, filename):
        """Path for resource evolution plots"""
        return os.path.join(self.output_dir, "plots", "resource_evolution", filename)

    def get_data_path(self, filename):
        """Path for data files (JSON, etc.)"""
        return os.path.join(self.output_dir, "data", filename)
