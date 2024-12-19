import numpy as np

class ResourceMetrics:
    def __init__(self):
        self.max_utilization = 0.0
        self.avg_utilization = 0.0
        self.std_dev = 0.0
        self.cluster_distribution = {}

    def __str__(self):
        return (f"Max: {self.max_utilization:.2%}, "
                f"Avg: {self.avg_utilization:.2%}, "
                f"Std: {self.std_dev:.2%}")

class PlacementMetrics:
    def __init__(self):
        self.resources = {
            'cpu': ResourceMetrics(),
            'mem': ResourceMetrics(),
            'disk': ResourceMetrics()
        }
        self.execution_time = 0.0
        self.successful = False
        self.overall_imbalance = 0.0
        self.resource_weights = {'cpu': 0.4, 'mem': 0.4, 'disk': 0.2}  # Customizable weights

    def to_dict(self):
        """Convert metrics to dictionary format for JSON serialization"""
        metrics_dict = {
            'execution_time': self.execution_time,
            'successful': self.successful,
            'overall_imbalance': self.overall_imbalance,
            'resources': {},
            'overall_metrics': {
                'avg_utilization': np.mean([
                    self.resources[r].avg_utilization
                    for r in self.resources
                ]),
                'max_utilization': max(
                    self.resources[r].max_utilization
                    for r in self.resources
                ),
                'std_dev': np.mean([
                    self.resources[r].std_dev
                    for r in self.resources
                ])
            }
        }

        for resource, metrics in self.resources.items():
            metrics_dict['resources'][resource] = {
                'max_utilization': metrics.max_utilization,
                'avg_utilization': metrics.avg_utilization,
                'std_dev': metrics.std_dev,
                'imbalance_score': metrics.max_utilization - metrics.avg_utilization,
                'cluster_distribution': metrics.cluster_distribution
            }

        return metrics_dict

    def calculate_metrics(self, cluster_utilization, execution_time):
        if not cluster_utilization:
            return

        self.successful = True
        self.execution_time = execution_time

        # Calculate per-resource metrics
        for resource in self.resources.keys():
            resource_utils = [cluster[resource] for cluster in cluster_utilization.values()]

            metrics = self.resources[resource]
            metrics.max_utilization = max(resource_utils)
            metrics.avg_utilization = np.mean(resource_utils)
            metrics.std_dev = np.std(resource_utils)
            metrics.cluster_distribution = {
                cluster: utilization[resource]
                for cluster, utilization in cluster_utilization.items()
            }

        # Calculate overall imbalance score (weighted)
        self.overall_imbalance = self._calculate_weighted_imbalance()

    def _calculate_weighted_imbalance(self):
        """
        Calculates a weighted imbalance score considering all resources.
        Lower score is better (indicates more balanced placement).
        """
        imbalance_score = 0.0

        for resource, weight in self.resource_weights.items():
            metrics = self.resources[resource]
            # Consider both spread (std dev) and peak utilization
            resource_score = (metrics.std_dev +
                            (metrics.max_utilization - metrics.avg_utilization))
            imbalance_score += weight * resource_score

        return imbalance_score

    def get_resource_summary(self):
        """Returns a detailed summary of resource utilization."""
        summary = {}
        for resource in self.resources.keys():
            metrics = self.resources[resource]
            summary[resource] = {
                'max_utilization': metrics.max_utilization,
                'avg_utilization': metrics.avg_utilization,
                'std_dev': metrics.std_dev,
                'cluster_distribution': metrics.cluster_distribution
            }
        return summary

    def __str__(self):
        if not self.successful:
            return "Placement failed"

        output = [
            f"Execution Time: {self.execution_time:.3f}s",
            f"Overall Imbalance Score: {self.overall_imbalance:.4f}",
            "\nPer-Resource Metrics:"
        ]

        for resource, metrics in self.resources.items():
            output.append(f"{resource.upper()}: {metrics}")

        return "\n".join(output)
