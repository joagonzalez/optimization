import pytest

from src.services.sequential_placement import SequentialPlacementSimulation


def test_simulation_initialization(basic_config, output_manager):
    simulation = SequentialPlacementSimulation(basic_config, output_manager)
    assert simulation.clusters == basic_config.clusters
    assert simulation.optimizer_model == basic_config.optimizer_model
    assert len(simulation.metrics_history) == 0


def test_vm_demand_generation(basic_config, output_manager):
    simulation = SequentialPlacementSimulation(basic_config, output_manager)
    demand = simulation.generate_vm_demand()

    assert "cpu" in demand
    assert "mem" in demand
    assert "disk" in demand
    assert (
        basic_config.vm_demand_ranges["cpu"][0]
        <= demand["cpu"]
        <= basic_config.vm_demand_ranges["cpu"][1]
    )


def test_cluster_usage_update(basic_config, output_manager):
    simulation = SequentialPlacementSimulation(basic_config, output_manager)
    initial_usage = simulation.current_usage["c1"]["cpu"]

    vm_demand = {"cpu": 10.0, "mem": 20.0, "disk": 15.0}
    simulation.update_cluster_usage("vm1", "c1", vm_demand)

    assert simulation.current_usage["c1"]["cpu"] > initial_usage


@pytest.mark.integration
def test_full_simulation_run(basic_config, output_manager):
    simulation = SequentialPlacementSimulation(basic_config, output_manager)
    simulation.run_simulation()

    assert len(simulation.metrics_history) > 0
    assert len(simulation.placement_history) > 0
    assert simulation.total_time > 0
