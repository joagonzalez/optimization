# test_config.py

class TestConfig:
    def __init__(self,
                 name,
                 num_vms,
                 clusters,
                 cluster_capacity,
                 initial_usage=None,
                 vm_demand_ranges=None):
        self.name = name
        self.num_vms = num_vms
        self.clusters = clusters
        self.cluster_capacity = cluster_capacity
        # Default initial usage if not provided
        self.initial_usage = initial_usage or {
            c: {'cpu': 0.0, 'mem': 0.0, 'disk': 0.0}
            for c in clusters
        }
        # Default VM demand ranges if not provided
        self.vm_demand_ranges = vm_demand_ranges or {
            'cpu': (5.0, 15.0),
            'mem': (10.0, 25.0),
            'disk': (8.0, 20.0)
        }

def generate_test_scenarios():
    scenarios = []

    # Scenario 1: Balanced clusters
    scenarios.append(TestConfig(
        name="balanced_clusters",
        num_vms=100,
        clusters=['c1', 'c2', 'c3'],
        cluster_capacity={
            'c1': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c3': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0}
        },
        vm_demand_ranges={
            'cpu': (0.01, 1),
            'mem': (0.05, 2),
            'disk': (0.1, 3)
        }
    ))

    # Scenario 2: Unbalanced initial usage
    scenarios.append(TestConfig(
        name="unbalanced_initial",
        num_vms=100,
        clusters=['c1', 'c2', 'c3'],
        cluster_capacity={
            'c1': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c3': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0}
        },
        initial_usage={
            'c1': {'cpu': 0.4, 'mem': 0.3, 'disk': 0.2},
            'c2': {'cpu': 0.2, 'mem': 0.5, 'disk': 0.3},
            'c3': {'cpu': 0.1, 'mem': 0.2, 'disk': 0.4}
        },
        vm_demand_ranges={
            'cpu': (0.01, 1),
            'mem': (0.05, 2),
            'disk': (0.1, 3)
        }
    ))

    # Scenario 3: Different cluster capacities
    scenarios.append(TestConfig(
        name="varying_capacity",
        num_vms=100,
        clusters=['c1', 'c2', 'c3'],
        cluster_capacity={
            'c1': {'cpu': 150.0, 'mem': 120.0, 'disk': 100.0},
            'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c3': {'cpu': 80.0, 'mem': 90.0, 'disk': 110.0}
        },
        vm_demand_ranges={
            'cpu': (0.01, 1),
            'mem': (0.05, 2),
            'disk': (0.1, 3)
        }
    ))

    # Scenario 4: Different VM sizes
    scenarios.append(TestConfig(
        name="large_vms",
        num_vms=50,  # Fewer VMs but larger
        clusters=['c1', 'c2', 'c3'],
        cluster_capacity={
            'c1': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c3': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0}
        },
        vm_demand_ranges={
            'cpu': (10.0, 30.0),
            'mem': (20.0, 40.0),
            'disk': (15.0, 35.0)
        }
    ))

    scenarios[-1].is_last = True
    for scenario in scenarios[:-1]:
        scenario.is_last = False

    return scenarios
