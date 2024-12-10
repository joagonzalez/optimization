class TestCase:
    def __init__(self, name, clusters, existing_placements, new_vms,
                 current_usage, cluster_capacity, vm_demand):
        self.name = name
        self.clusters = clusters
        self.existing_placements = existing_placements
        self.new_vms = new_vms
        self.current_usage = current_usage
        self.cluster_capacity = cluster_capacity
        self.vm_demand = vm_demand

def generate_test_cases():
    test_cases = []

    # Test Case 1: Balanced clusters
    test_cases.append(TestCase(
        name="balanced_clusters",
        clusters=['c1', 'c2'],
        existing_placements={'vm1': 'c1', 'vm2': 'c2'},
        new_vms=['vm3'],
        current_usage={
            'c1': {'cpu': 0.5, 'mem': 0.5, 'disk': 0.5},
            'c2': {'cpu': 0.5, 'mem': 0.5, 'disk': 0.5}
        },
        cluster_capacity={
            'c1': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0}
        },
        vm_demand={
            'vm3': {'cpu': 10.0, 'mem': 10.0, 'disk': 10.0}
        }
    ))

    # Test Case 2: Highly utilized clusters
    test_cases.append(TestCase(
        name="high_utilization",
        clusters=['c1', 'c2'],
        existing_placements={'vm1': 'c1', 'vm2': 'c2'},
        new_vms=['vm3'],
        current_usage={
            'c1': {'cpu': 0.8, 'mem': 0.9, 'disk': 0.85},
            'c2': {'cpu': 0.85, 'mem': 0.8, 'disk': 0.9}
        },
        cluster_capacity={
            'c1': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0}
        },
        vm_demand={
            'vm3': {'cpu': 15.0, 'mem': 15.0, 'disk': 15.0}
        }
    ))

    # Test Case 3: Multiple clusters with varying capacities
    test_cases.append(TestCase(
        name="varying_capacities",
        clusters=['c1', 'c2', 'c3'],
        existing_placements={'vm1': 'c1', 'vm2': 'c2'},
        new_vms=['vm3', 'vm4'],
        current_usage={
            'c1': {'cpu': 0.3, 'mem': 0.4, 'disk': 0.3},
            'c2': {'cpu': 0.5, 'mem': 0.5, 'disk': 0.5},
            'c3': {'cpu': 0.2, 'mem': 0.3, 'disk': 0.4}
        },
        cluster_capacity={
            'c1': {'cpu': 150.0, 'mem': 120.0, 'disk': 100.0},
            'c2': {'cpu': 100.0, 'mem': 100.0, 'disk': 100.0},
            'c3': {'cpu': 80.0, 'mem': 90.0, 'disk': 110.0}
        },
        vm_demand={
            'vm3': {'cpu': 20.0, 'mem': 15.0, 'disk': 10.0},
            'vm4': {'cpu': 15.0, 'mem': 20.0, 'disk': 15.0}
        }
    ))

    return test_cases
