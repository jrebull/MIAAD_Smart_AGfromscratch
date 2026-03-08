"""Statistical metrics for GA experiment evaluation."""

from dataclasses import dataclass, field
from typing import List

import numpy as np


@dataclass
class ScenarioMetrics:
    """Aggregated metrics for one scenario across all runs."""

    scenario_name: str
    num_clients: int
    best_fitness: float         # BKS: max across 30 runs
    avg_best_fitness: float     # Mean of best-per-run
    gap_pct: float              # ((BKS - avg) / BKS) * 100
    success_rate_pct: float     # % runs within 2% of BKS
    std_dev: float              # Standard deviation
    all_best_values: List[float] = field(default_factory=list)

    @classmethod
    def compute(
        cls,
        scenario_name: str,
        num_clients: int,
        best_fitness_per_run: List[float],
        tolerance: float = 0.02,
    ) -> "ScenarioMetrics":
        """Compute all metrics from the raw best-fitness-per-run vector."""
        values = np.array(best_fitness_per_run)
        bks = float(np.max(values))
        avg = float(np.mean(values))
        std = float(np.std(values))

        gap = ((bks - avg) / bks) * 100 if bks != 0 else 0.0

        threshold = bks * (1 - tolerance)
        successes = int(np.sum(values >= threshold))
        success_rate = (successes / len(values)) * 100

        return cls(
            scenario_name=scenario_name,
            num_clients=num_clients,
            best_fitness=bks,
            avg_best_fitness=avg,
            gap_pct=gap,
            success_rate_pct=success_rate,
            std_dev=std,
            all_best_values=best_fitness_per_run,
        )
