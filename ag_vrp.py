"""CLI wrapper for the VRP Genetic Algorithm — delegates to src/ga_engine.py."""

import argparse
from pathlib import Path

from src.config import ScenarioConfig
from src.ga_engine import GeneticAlgorithm, VRPInstance
from src.instance_generator import VRPInstanceGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the GA for VRP.")
    parser.add_argument("--instance", type=str, default="data/instance.json", help="Instance JSON file")
    parser.add_argument("--pop-size", type=int, default=100, help="Population size")
    parser.add_argument("--generations", type=int, default=300, help="Number of generations")
    parser.add_argument("--mutation-rate", type=float, default=0.15, help="Mutation rate")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--capacity", type=int, default=30, help="Vehicle capacity")
    parser.add_argument("--vehicle-cost", type=float, default=300, help="Fixed cost per vehicle")
    parser.add_argument("--distance-cost", type=float, default=2, help="Cost per km")
    parser.add_argument("--empty-cost", type=float, default=10, help="Penalty per empty unit")
    args = parser.parse_args()

    clients = VRPInstanceGenerator.load(Path(args.instance))
    num_clients = len(clients) - 1  # Exclude depot

    config = ScenarioConfig(
        name="CLI Run",
        num_clients=num_clients,
        demand_range=(5, 15),
        value_range=(50, 300),
        vehicle_capacity=args.capacity,
        vehicle_cost=args.vehicle_cost,
        distance_cost=args.distance_cost,
        empty_cost=args.empty_cost,
    )

    instance = VRPInstance(clients, config)
    ga = GeneticAlgorithm(
        instance=instance,
        pop_size=args.pop_size,
        generations=args.generations,
        mutation_rate=args.mutation_rate,
    )

    result = ga.run(seed=args.seed, verbose=True)

    print(f"\nBest Fitness (Z): ${result.best_fitness:,.2f}")
    print(f"Seed used: {result.seed_used}")
    routes = instance.decode_chromosome(result.best_chromosome)
    print(f"Number of routes: {len(routes)}")
    for i, route in enumerate(routes, 1):
        load = sum(clients[cid]["demanda"] for cid in route)
        print(f"  Route {i}: {len(route)} clients, load={load}/{args.capacity}")


if __name__ == "__main__":
    main()
