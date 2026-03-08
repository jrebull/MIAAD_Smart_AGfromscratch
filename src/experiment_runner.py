"""Orchestrates 30 independent GA runs per scenario and saves results."""

import json
from pathlib import Path
from typing import List, Optional

import pandas as pd
from tqdm import tqdm

from .config import GAConfig, GARun, ScenarioConfig, SCENARIOS
from .ga_engine import GeneticAlgorithm, VRPInstance
from .instance_generator import VRPInstanceGenerator
from .metrics import ScenarioMetrics


class ExperimentRunner:
    """Runs the full experimental design: generate instances, execute GA, collect metrics."""

    def __init__(
        self,
        scenarios: Optional[List[ScenarioConfig]] = None,
        ga_config: Optional[GAConfig] = None,
        data_dir: Path = Path("data"),
        results_dir: Path = Path("results"),
    ) -> None:
        self.scenarios = scenarios or SCENARIOS
        self.ga_config = ga_config or GAConfig()
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def generate_instances(self) -> None:
        """Generate and save one VRP instance per scenario."""
        for i, scenario in enumerate(self.scenarios, 1):
            generator = VRPInstanceGenerator(
                num_clients=scenario.num_clients,
                demand_range=scenario.demand_range,
                value_range=scenario.value_range,
                max_coord=scenario.max_coord,
                seed=42,
            )
            filepath = self.data_dir / f"instance_scenario_{i}.json"
            generator.save(filepath)
            print(f"Generated instance: {filepath} ({scenario.num_clients} clients)")

    def run_scenario(
        self, scenario_idx: int, scenario: ScenarioConfig
    ) -> List[GARun]:
        """Execute the GA `runs` times for a single scenario."""
        filepath = self.data_dir / f"instance_scenario_{scenario_idx}.json"
        clients = VRPInstanceGenerator.load(filepath)
        instance = VRPInstance(clients, scenario)

        ga = GeneticAlgorithm(
            instance=instance,
            pop_size=self.ga_config.pop_size,
            generations=self.ga_config.generations,
            mutation_rate=self.ga_config.mutation_rate,
            tournament_k=self.ga_config.tournament_k,
        )

        results: List[GARun] = []
        for seed in tqdm(
            range(self.ga_config.runs),
            desc=f"  Scenario {scenario_idx}",
            leave=False,
        ):
            result = ga.run(seed=seed)
            results.append(result)

        return results

    def run_all(self) -> List[ScenarioMetrics]:
        """Run all scenarios, save CSV, and return metrics."""
        all_rows = []
        all_metrics: List[ScenarioMetrics] = []
        all_run_results: dict = {}

        for i, scenario in enumerate(self.scenarios, 1):
            print(f"\nRunning: {scenario.name}")
            run_results = self.run_scenario(i, scenario)
            all_run_results[i] = run_results

            best_values = [r.best_fitness for r in run_results]
            metrics = ScenarioMetrics.compute(
                scenario_name=scenario.name,
                num_clients=scenario.num_clients,
                best_fitness_per_run=best_values,
            )
            all_metrics.append(metrics)

            for run_result in run_results:
                all_rows.append({
                    "scenario": scenario.name,
                    "run": run_result.seed_used,
                    "best_fitness": run_result.best_fitness,
                    "generations": self.ga_config.generations,
                    "num_clients": scenario.num_clients,
                    "seed": run_result.seed_used,
                })

            # Save intermediate results after each scenario
            df = pd.DataFrame(all_rows)
            df.to_csv(self.results_dir / "results_summary.csv", index=False)

            print(f"  BKS: {metrics.best_fitness:.2f}")
            print(f"  Avg: {metrics.avg_best_fitness:.2f}")
            print(f"  Gap: {metrics.gap_pct:.2f}%")
            print(f"  Success Rate: {metrics.success_rate_pct:.1f}%")

        # Save best chromosomes and fitness histories for figure generation
        self._save_best_runs(all_run_results)
        self._save_metrics(all_metrics)

        return all_metrics

    def _save_best_runs(self, all_run_results: dict) -> None:
        """Save best chromosome and fitness history per scenario for figures."""
        for scenario_idx, runs in all_run_results.items():
            best_run = max(runs, key=lambda r: r.best_fitness)
            data = {
                "best_fitness": best_run.best_fitness,
                "best_chromosome": best_run.best_chromosome,
                "fitness_history": best_run.fitness_history,
                "seed_used": best_run.seed_used,
            }
            filepath = self.results_dir / f"best_run_scenario_{scenario_idx}.json"
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

    def _save_metrics(self, all_metrics: List[ScenarioMetrics]) -> None:
        """Save computed metrics to a JSON file."""
        metrics_data = []
        for m in all_metrics:
            metrics_data.append({
                "scenario_name": m.scenario_name,
                "num_clients": m.num_clients,
                "best_fitness": m.best_fitness,
                "avg_best_fitness": m.avg_best_fitness,
                "gap_pct": m.gap_pct,
                "success_rate_pct": m.success_rate_pct,
                "std_dev": m.std_dev,
                "all_best_values": m.all_best_values,
            })
        filepath = self.results_dir / "metrics_summary.json"
        with open(filepath, "w") as f:
            json.dump(metrics_data, f, indent=2)
