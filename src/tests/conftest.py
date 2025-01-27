import pytest

from src.models.min_max_optimizer import MinUtilizationOptimizer
from src.services.test_config import TestConfig
from src.services.utils import OutputManager


@pytest.fixture
def output_manager():
    return OutputManager()


@pytest.fixture
def basic_config():
    return TestConfig(
        name="test_scenario",
        num_vms=10,
        clusters=["c1", "c2"],
        cluster_capacity={
            "c1": {"cpu": 100.0, "mem": 100.0, "disk": 100.0},
            "c2": {"cpu": 100.0, "mem": 100.0, "disk": 100.0},
        },
        initial_usage={
            "c1": {"cpu": 0.2, "mem": 0.3, "disk": 0.2},
            "c2": {"cpu": 0.3, "mem": 0.2, "disk": 0.3},
        },
        vm_demand_ranges={"cpu": (5.0, 10.0), "mem": (8.0, 16.0), "disk": (10.0, 20.0)},
        optimizer_model=MinUtilizationOptimizer,
    )
