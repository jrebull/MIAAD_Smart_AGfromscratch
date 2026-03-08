"""CLI wrapper for VRP instance generation — delegates to src/instance_generator.py."""

import argparse
from pathlib import Path

from src.instance_generator import VRPInstanceGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a VRP instance.")
    parser.add_argument("--clients", type=int, default=100, help="Number of clients")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--demand-min", type=int, default=5, help="Min demand")
    parser.add_argument("--demand-max", type=int, default=15, help="Max demand")
    parser.add_argument("--value-min", type=int, default=50, help="Min value per unit")
    parser.add_argument("--value-max", type=int, default=300, help="Max value per unit")
    parser.add_argument("--output", type=str, default="data/instance.json", help="Output file path")
    args = parser.parse_args()

    generator = VRPInstanceGenerator(
        num_clients=args.clients,
        demand_range=(args.demand_min, args.demand_max),
        value_range=(args.value_min, args.value_max),
        seed=args.seed,
    )
    filepath = Path(args.output)
    generator.save(filepath)
    print(f"Instance generated: {filepath} ({args.clients} clients, seed={args.seed})")


if __name__ == "__main__":
    main()
