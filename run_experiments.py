"""Entry point: runs all 5 experimental scenarios (30 runs each)."""

import argparse
import sys
import time

from src.experiment_runner import ExperimentRunner
from src.figure_generator import FigureGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run VRP GA experiments.")
    parser.add_argument("--generate-only", action="store_true", help="Only generate instances")
    parser.add_argument("--full", action="store_true", help="Run full experiment (30 x 5 = 150 runs)")
    parser.add_argument("--figures-only", action="store_true", help="Only generate figures from existing results")
    args = parser.parse_args()

    if args.figures_only:
        fg = FigureGenerator()
        fg.generate_all()
        return

    runner = ExperimentRunner()

    if args.generate_only:
        runner.generate_instances()
        print("\nInstances generated. Run with --full to execute experiments.")
        return

    if args.full:
        runner.generate_instances()
        print("\n" + "=" * 60)
        print("Starting full experiment: 5 scenarios x 30 runs = 150 GA executions")
        print("=" * 60)

        start = time.time()
        metrics = runner.run_all()
        elapsed = time.time() - start

        print("\n" + "=" * 60)
        print("EXPERIMENT COMPLETE")
        print(f"Total time: {elapsed:.1f}s ({elapsed / 60:.1f} min)")
        print("=" * 60)

        print(f"\n{'Scenario':<50} {'BKS':>10} {'Avg':>10} {'Gap%':>8} {'SR%':>8}")
        print("-" * 86)
        for m in metrics:
            print(f"{m.scenario_name:<50} {m.best_fitness:>10,.0f} {m.avg_best_fitness:>10,.0f} {m.gap_pct:>7.2f}% {m.success_rate_pct:>7.1f}%")

        # Generate figures
        print()
        fg = FigureGenerator()
        fg.generate_all()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
