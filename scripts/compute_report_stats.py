"""Compute all statistics needed for the LaTeX report.

Reads actual experiment results and produces:
  - results/report_stats.json   (all metrics, route stats, convergence)
  - results/route_stats.csv     (per-run route structure)

Must be run from project root: python scripts/compute_report_stats.py
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import SCENARIOS, GAConfig
from src.ga_engine import GeneticAlgorithm, VRPInstance, FitnessEvaluator
from src.instance_generator import VRPInstanceGenerator

RESULTS_DIR = PROJECT_ROOT / "results"
DATA_DIR = PROJECT_ROOT / "data"


def load_instance(scenario_idx: int) -> dict:
    path = DATA_DIR / f"instance_scenario_{scenario_idx}.json"
    with open(path) as f:
        return json.load(f)


def decode_and_analyze(chromosome, clients, config):
    """Decode a chromosome and compute route structure metrics."""
    instance = VRPInstance(clients, config)
    routes = instance.decode_chromosome(chromosome)

    n_vehicles = len(routes)
    loads = []
    total_distance = 0.0
    route_lengths = []

    for route in routes:
        route_load = sum(clients[cid]["demanda"] for cid in route)
        loads.append(route_load)
        route_lengths.append(len(route))

        # Distance: depot -> first client
        total_distance += instance.euclidean_distance("0", route[0])
        for i in range(len(route) - 1):
            total_distance += instance.euclidean_distance(route[i], route[i + 1])
        # Distance: last client -> depot
        total_distance += instance.euclidean_distance(route[-1], "0")

    avg_load = np.mean(loads)
    load_utilization = (avg_load / config.vehicle_capacity) * 100
    empty_capacity = sum(config.vehicle_capacity - ld for ld in loads)

    return {
        "num_vehicles": n_vehicles,
        "avg_load_per_vehicle": float(avg_load),
        "load_utilization_pct": float(load_utilization),
        "total_distance": float(total_distance),
        "avg_route_length": float(np.mean(route_lengths)),
        "max_route_length": int(max(route_lengths)),
        "min_route_length": int(min(route_lengths)),
        "empty_capacity_total": float(empty_capacity),
    }


def run_ga_and_collect(scenario_idx, config, clients, ga_config):
    """Re-run the GA for all 30 seeds, collecting chromosomes and histories."""
    instance = VRPInstance(clients, config)
    ga = GeneticAlgorithm(
        instance=instance,
        pop_size=ga_config.pop_size,
        generations=ga_config.generations,
        mutation_rate=ga_config.mutation_rate,
        tournament_k=ga_config.tournament_k,
    )

    runs_data = []
    for seed in range(ga_config.runs):
        result = ga.run(seed=seed)
        runs_data.append({
            "seed": seed,
            "best_fitness": result.best_fitness,
            "best_chromosome": result.best_chromosome,
            "fitness_history": result.fitness_history,
        })
        if (seed + 1) % 10 == 0:
            print(f"    Seed {seed + 1}/30 done")

    return runs_data


def compute_convergence_stats(runs_data):
    """Compute convergence statistics from fitness histories."""
    convergence_gens = []
    fitness_at_50 = []
    fitness_at_100 = []
    fitness_at_300 = []

    for run in runs_data:
        history = run["fitness_history"]
        final_fitness = history[-1]

        # Generation where 99% of final fitness is reached
        threshold = final_fitness * 0.99
        conv_gen = len(history)  # default: never
        for g, f in enumerate(history):
            if f >= threshold:
                conv_gen = g + 1  # 1-indexed
                break
        convergence_gens.append(conv_gen)

        fitness_at_50.append(history[min(49, len(history) - 1)])
        fitness_at_100.append(history[min(99, len(history) - 1)])
        fitness_at_300.append(history[-1])

    avg_f50 = np.mean(fitness_at_50)
    avg_f300 = np.mean(fitness_at_300)
    improvement = ((avg_f300 - avg_f50) / avg_f50) * 100 if avg_f50 != 0 else 0

    return {
        "convergence_gen_median": int(np.median(convergence_gens)),
        "convergence_gen_p25": int(np.percentile(convergence_gens, 25)),
        "convergence_gen_p75": int(np.percentile(convergence_gens, 75)),
        "fitness_at_gen50_avg": float(avg_f50),
        "fitness_at_gen100_avg": float(np.mean(fitness_at_100)),
        "fitness_at_gen300_avg": float(avg_f300),
        "improvement_50_to_300_pct": float(improvement),
    }


def main():
    ga_config = GAConfig()
    all_stats = []
    all_route_rows = []
    all_convergence_histories = []  # For fig07

    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\nScenario {i}: {scenario.name}")
        clients = load_instance(i)

        # Re-run GA to get all chromosomes and histories
        print("  Re-running GA (30 seeds)...")
        runs_data = run_ga_and_collect(i, scenario, clients, ga_config)

        # 1A: Per-scenario metrics
        fitnesses = [r["best_fitness"] for r in runs_data]
        bks = float(np.max(fitnesses))
        avg = float(np.mean(fitnesses))
        std = float(np.std(fitnesses))
        gap = ((bks - avg) / bks) * 100 if bks != 0 else 0
        success = sum(1 for f in fitnesses if f >= bks * 0.98) / 30 * 100

        # 1B: Route structure for each run
        print("  Computing route structures...")
        route_stats_list = []
        for run in runs_data:
            rs = decode_and_analyze(run["best_chromosome"], clients, scenario)
            rs["scenario_id"] = i
            rs["run"] = run["seed"]
            route_stats_list.append(rs)
            all_route_rows.append(rs)

        # Aggregate route stats
        avg_vehicles = np.mean([r["num_vehicles"] for r in route_stats_list])
        std_vehicles = np.std([r["num_vehicles"] for r in route_stats_list])
        avg_util = np.mean([r["load_utilization_pct"] for r in route_stats_list])
        avg_dist = np.mean([r["total_distance"] for r in route_stats_list])
        std_dist = np.std([r["total_distance"] for r in route_stats_list])
        avg_rl = np.mean([r["avg_route_length"] for r in route_stats_list])
        avg_empty = np.mean([r["empty_capacity_total"] for r in route_stats_list])

        # 1C: Convergence
        print("  Computing convergence stats...")
        conv_stats = compute_convergence_stats(runs_data)

        # Save convergence histories for fig07
        for run in runs_data:
            for g, f in enumerate(run["fitness_history"]):
                all_convergence_histories.append({
                    "scenario_id": i,
                    "run": run["seed"],
                    "generation": g + 1,
                    "best_fitness": f,
                })

        scenario_stats = {
            "scenario_id": i,
            "scenario_name": scenario.name,
            "num_clients": scenario.num_clients,
            # Metrics
            "bks": bks,
            "avg_best_fitness": avg,
            "gap_pct": gap,
            "success_rate_pct": success,
            "std_dev": std,
            "min_fitness": float(np.min(fitnesses)),
            "median_fitness": float(np.median(fitnesses)),
            # Route structure (aggregated)
            "avg_num_vehicles": float(avg_vehicles),
            "std_num_vehicles": float(std_vehicles),
            "avg_load_utilization_pct": float(avg_util),
            "avg_total_distance": float(avg_dist),
            "std_total_distance": float(std_dist),
            "avg_route_length": float(avg_rl),
            "avg_empty_capacity": float(avg_empty),
            # Convergence
            **conv_stats,
        }
        all_stats.append(scenario_stats)

        print(f"  BKS: {bks:,.2f} | Avg: {avg:,.2f} | Std: {std:,.2f}")
        print(f"  Gap: {gap:.2f}% | Success: {success:.1f}%")
        print(f"  Vehicles: {avg_vehicles:.1f} | Util: {avg_util:.1f}% | Dist: {avg_dist:,.1f}")
        print(f"  Conv gen (median): {conv_stats['convergence_gen_median']}")

    # Save outputs
    with open(RESULTS_DIR / "report_stats.json", "w") as f:
        json.dump(all_stats, f, indent=2)
    print(f"\nSaved: results/report_stats.json")

    pd.DataFrame(all_route_rows).to_csv(RESULTS_DIR / "route_stats.csv", index=False)
    print(f"Saved: results/route_stats.csv")

    pd.DataFrame(all_convergence_histories).to_csv(
        RESULTS_DIR / "convergence_history.csv", index=False
    )
    print(f"Saved: results/convergence_history.csv")

    # Print summary table for verification
    print("\n" + "=" * 100)
    print(f"{'Scenario':<50} {'BKS':>10} {'Avg':>10} {'Std':>8} {'Gap%':>7} {'SR%':>7} {'Veh':>5} {'Util%':>6}")
    print("-" * 100)
    for s in all_stats:
        print(f"{s['scenario_name']:<50} {s['bks']:>10,.0f} {s['avg_best_fitness']:>10,.0f} "
              f"{s['std_dev']:>8,.0f} {s['gap_pct']:>6.2f}% {s['success_rate_pct']:>6.1f}% "
              f"{s['avg_num_vehicles']:>5.1f} {s['avg_load_utilization_pct']:>5.1f}%")


if __name__ == "__main__":
    main()
