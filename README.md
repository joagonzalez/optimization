# VM Placement Optimization

This project implements optimization strategies for placing virtual machines (VMs) across multiple clusters while balancing resource utilization and maintaining performance constraints.

<img src="doc/img/strategies.png" width="800" alt="Optimization">

## Problem Description

Given:
- Multiple clusters with defined resource capacities (CPU, Memory, Disk)
- Existing VMs already placed in clusters
- New VMs that need to be placed
- Resource demands for each VM
- Current resource utilization of each cluster

## Optimization Strategies

The project implements multiple optimization approaches:

1. **MinUtilizationOptimizer**: Minimizes maximum resource utilization across all clusters
2. **MinMaxPerClusterOptimizer**: Optimizes resource balance within each cluster independently
3. **BaselineOptimizer**: Simple strategy prioritizing clusters with lowest CPU utilization
4. **BaselineOptimizerInv**: Variant of baseline strategy with different selection criteria

## Features

- Real-time visualization of placement progress
- Comprehensive metrics tracking:
  - Resource utilization per cluster
  - Standard deviation of resource usage
  - Imbalance scores
  - Execution time
  - Placement success rate
- Multiple test scenarios:
  - Balanced clusters
  - Unbalanced initial usage
  - Varying cluster capacities
  - Different VM sizes
- Extensive visualization and reporting:
  - Resource utilization plots
  - Comparative analysis
  - Performance metrics evolution
  - Heatmaps of improvements

## Project Structure

```
optimization/
├── src/
│   ├── models/              # Optimization strategies
│   │   ├── base_optimizer.py
│   │   ├── min_max_optimizer.py
│   │   ├── baseline_optimizer.py
│   │   └── min_max_per_cluster_optimizer.py
│   └── services/           # Core services
│       ├── metrics.py      # Performance metrics
│       ├── optimization.py # Optimization logic
│       ├── real_time_viz.py # Visualization
│       └── utils.py        # Utilities
├── test_runner.py         # Main test execution
└── Makefile              # Build and test automation
```

## Usage

1. Run tests with visualization:
```bash
make run
```

2. Run tests without visualization:
```bash
make run-no-viz
```

3. Clean models results:
```bash
make clean
```

4. Clean app tests results and folders:
```bash
make clean-all
```

3. Run unit test and integration:
```bash
make test
```

3. Run unit test and integration with coverage report:
```bash
make test-coverage
```

## Output

The system generates comprehensive output including:
- JSON results file with detailed metrics
- Resource utilization plots
- Comparative analysis visualizations
- Performance evolution graphs
- Resource balance heatmaps

All output is organized by test run in the `test_results` directory.

## Key Metrics

- Resource utilization per cluster
- Overall imbalance score
- Standard deviation of resource usage
- Execution time per placement
- Success rate of placements
- Resource balance improvements

## Development

To set up the development environment:

1. Install dependencies:
```bash
make install
```

2. Format code:
```bash
make format
```

3. Run linting:
```bash
make lint
```

## Future Improvements

1. Integration of host-level constraints
2. Dynamic resource demand handling
3. Machine learning-based prediction
4. Additional optimization strategies
5. Enhanced visualization capabilities

## Test Scenarios

The project includes several test scenarios:
- Balanced clusters
- Unbalanced initial usage
- Varying cluster capacities
- Large VM placements
- Different optimizer comparisons
