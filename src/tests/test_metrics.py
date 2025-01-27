from src.services.metrics import PlacementMetrics, ResourceMetrics


def test_resource_metrics_initialization():
    metrics = ResourceMetrics()
    assert metrics.max_utilization == 0.0
    assert metrics.avg_utilization == 0.0
    assert metrics.std_dev == 0.0
    assert isinstance(metrics.cluster_distribution, dict)


def test_placement_metrics_initialization():
    metrics = PlacementMetrics()
    assert "cpu" in metrics.resources
    assert "mem" in metrics.resources
    assert "disk" in metrics.resources
    assert metrics.execution_time == 0.0
    assert not metrics.successful
    assert metrics.overall_imbalance == 0.0


def test_metrics_calculation():
    metrics = PlacementMetrics()
    cluster_utilization = {
        "c1": {"cpu": 0.5, "mem": 0.6, "disk": 0.4},
        "c2": {"cpu": 0.3, "mem": 0.4, "disk": 0.5},
    }
    execution_time = 1.0

    metrics.calculate_metrics(cluster_utilization, execution_time)

    assert metrics.execution_time == 1.0
    assert metrics.successful
    assert metrics.resources["cpu"].max_utilization == 0.5
    assert 0.3 < metrics.resources["cpu"].avg_utilization < 0.5


def test_metrics_to_dict():
    metrics = PlacementMetrics()
    cluster_utilization = {
        "c1": {"cpu": 0.5, "mem": 0.6, "disk": 0.4},
        "c2": {"cpu": 0.3, "mem": 0.4, "disk": 0.5},
    }
    metrics.calculate_metrics(cluster_utilization, 1.0)

    result = metrics.to_dict()
    assert isinstance(result, dict)
    assert "resources" in result
    assert "execution_time" in result
    assert "successful" in result
