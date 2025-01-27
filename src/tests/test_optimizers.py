from src.models.baseline_optimizer import BaselineOptimizer
from src.models.min_max_optimizer import MinUtilizationOptimizer


def test_optimizer_initialization(basic_config):
    optimizer = MinUtilizationOptimizer(
        basic_config.clusters,
        {},  # empty existing placements
        ["vm1"],
        basic_config.initial_usage,
        basic_config.cluster_capacity,
        {"vm1": {"cpu": 10.0, "mem": 20.0, "disk": 15.0}},
    )

    assert optimizer.clusters == basic_config.clusters
    assert isinstance(optimizer.existing_placements, dict)
    assert len(optimizer.new_vms) == 1


def test_baseline_optimizer_can_place_vm(basic_config):
    optimizer = BaselineOptimizer(
        basic_config.clusters,
        {},
        ["vm1"],
        basic_config.initial_usage,
        basic_config.cluster_capacity,
        {"vm1": {"cpu": 10.0, "mem": 20.0, "disk": 15.0}},
    )

    assert optimizer.can_place_vm("vm1", "c1")


def test_optimizer_placement_success(basic_config):
    optimizer = MinUtilizationOptimizer(
        basic_config.clusters,
        {},
        ["vm1"],
        basic_config.initial_usage,
        basic_config.cluster_capacity,
        {"vm1": {"cpu": 10.0, "mem": 20.0, "disk": 15.0}},
    )

    result = optimizer.optimize()
    assert result is not None
    assert len(result) == 4
    placement_plan, cluster_utilization, final_utilization, final_placement = result
    assert isinstance(placement_plan, dict)
    assert "vm1" in placement_plan
