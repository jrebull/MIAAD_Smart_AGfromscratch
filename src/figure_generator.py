"""Generate all matplotlib/seaborn figures for the LaTeX report."""

import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .config import UACJ_COLORS, SCENARIOS
from .instance_generator import VRPInstanceGenerator
from .ga_engine import VRPInstance


class FigureGenerator:
    """Generates all 7 required figures using UACJ color palette."""

    def __init__(
        self,
        results_dir: Path = Path("results"),
        figures_dir: Path = Path("Figures"),
        data_dir: Path = Path("data"),
    ) -> None:
        self.results_dir = results_dir
        self.figures_dir = figures_dir
        self.data_dir = data_dir
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.colors = UACJ_COLORS

    def _load_metrics(self) -> List[Dict]:
        with open(self.results_dir / "metrics_summary.json") as f:
            return json.load(f)

    def _load_best_run(self, scenario_idx: int) -> Dict:
        with open(self.results_dir / f"best_run_scenario_{scenario_idx}.json") as f:
            return json.load(f)

    def _load_results_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.results_dir / "results_summary.csv")

    def _apply_style(self) -> None:
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({
            "font.family": "sans-serif",
            "axes.edgecolor": self.colors["dark_gray"],
            "axes.labelcolor": self.colors["dark_gray"],
            "text.color": self.colors["dark_gray"],
            "xtick.color": self.colors["dark_gray"],
            "ytick.color": self.colors["dark_gray"],
        })

    def fig01_convergence(self) -> None:
        """Fig 1: Fitness evolution over generations (best run, Scenario 1)."""
        self._apply_style()
        best_run = self._load_best_run(1)
        history = best_run["fitness_history"]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(
            range(1, len(history) + 1),
            history,
            color=self.colors["blue"],
            linewidth=2,
        )
        ax.set_xlabel("Generación", fontsize=12)
        ax.set_ylabel("Mejor Fitness (Z)", fontsize=12)
        ax.set_title("Curva de Convergencia — Escenario 1 (100 clientes)", fontsize=14)
        ax.fill_between(
            range(1, len(history) + 1),
            history,
            alpha=0.15,
            color=self.colors["blue"],
        )
        plt.tight_layout()
        plt.savefig(self.figures_dir / "fig01_convergencia_base.png", dpi=300)
        plt.close()

    def fig02_boxplot(self) -> None:
        """Fig 2: Box plot of best fitness across 5 scenarios."""
        self._apply_style()
        metrics = self._load_metrics()

        data = []
        labels = []
        for i, m in enumerate(metrics):
            short_name = f"Esc. {i + 1}"
            for v in m["all_best_values"]:
                data.append({"Escenario": short_name, "Mejor Fitness": v})
            labels.append(short_name)

        df = pd.DataFrame(data)

        fig, ax = plt.subplots(figsize=(12, 6))
        palette = [
            self.colors["blue"],
            self.colors["dark_gray"],
            self.colors["green"],
            self.colors["red"],
            self.colors["yellow"],
        ]
        sns.boxplot(
            data=df,
            x="Escenario",
            y="Mejor Fitness",
            palette=palette,
            ax=ax,
        )
        ax.set_title("Distribución de Mejor Fitness por Escenario (30 ejecuciones)", fontsize=14)
        ax.set_xlabel("Escenario", fontsize=12)
        ax.set_ylabel("Mejor Fitness (Z)", fontsize=12)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "fig02_boxplot_escenarios.png", dpi=300)
        plt.close()

    def fig03_bar_metrics(self) -> None:
        """Fig 3: Grouped bar chart — BKS vs Avg Best Fitness per scenario."""
        self._apply_style()
        metrics = self._load_metrics()

        labels = [f"Esc. {i + 1}" for i in range(len(metrics))]
        bks_vals = [m["best_fitness"] for m in metrics]
        avg_vals = [m["avg_best_fitness"] for m in metrics]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width / 2, bks_vals, width, label="BKS (Mejor)", color=self.colors["blue"])
        bars2 = ax.bar(x + width / 2, avg_vals, width, label="Promedio", color=self.colors["yellow"], edgecolor=self.colors["dark_gray"])

        ax.set_xlabel("Escenario", fontsize=12)
        ax.set_ylabel("Fitness (Z)", fontsize=12)
        ax.set_title("BKS vs Promedio de Mejor Fitness por Escenario", fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.figures_dir / "fig03_barras_metricas.png", dpi=300)
        plt.close()

    def fig04_gap_success(self) -> None:
        """Fig 4: Dual-axis bar — Gap% and Success Rate%."""
        self._apply_style()
        metrics = self._load_metrics()

        labels = [f"Esc. {i + 1}" for i in range(len(metrics))]
        gaps = [m["gap_pct"] for m in metrics]
        success = [m["success_rate_pct"] for m in metrics]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()

        bars1 = ax1.bar(x - width / 2, gaps, width, label="Gap (%)", color=self.colors["red"], alpha=0.8)
        bars2 = ax2.bar(x + width / 2, success, width, label="Tasa de Éxito (%)", color=self.colors["green"], alpha=0.8)

        ax1.set_xlabel("Escenario", fontsize=12)
        ax1.set_ylabel("Gap (%)", fontsize=12, color=self.colors["red"])
        ax2.set_ylabel("Tasa de Éxito (%)", fontsize=12, color=self.colors["green"])
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels)
        ax1.set_title("Brecha (Gap) y Tasa de Éxito por Escenario", fontsize=14)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

        plt.tight_layout()
        plt.savefig(self.figures_dir / "fig04_gap_success.png", dpi=300)
        plt.close()

    def fig05_route_map(self) -> None:
        """Fig 5: 2D scatter + lines — best route from Scenario 1."""
        self._apply_style()
        best_run = self._load_best_run(1)
        clients = VRPInstanceGenerator.load(self.data_dir / "instance_scenario_1.json")
        config = SCENARIOS[0]
        instance = VRPInstance(clients, config)

        chromosome = best_run["best_chromosome"]
        routes = instance.decode_chromosome(chromosome)

        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot depot
        depot = clients["0"]
        ax.plot(depot["x"], depot["y"], marker="*", color=self.colors["red"],
                markersize=20, zorder=5, label="Depósito")

        # Color palette for routes
        route_colors = plt.cm.tab10(np.linspace(0, 1, len(routes)))

        for r_idx, route in enumerate(routes):
            xs = [depot["x"]]
            ys = [depot["y"]]
            for cid in route:
                xs.append(clients[cid]["x"])
                ys.append(clients[cid]["y"])
            xs.append(depot["x"])
            ys.append(depot["y"])

            ax.plot(xs, ys, "-o", color=route_colors[r_idx], markersize=5,
                    linewidth=1.5, alpha=0.7, label=f"Ruta {r_idx + 1}")

        ax.set_xlabel("Coordenada X", fontsize=12)
        ax.set_ylabel("Coordenada Y", fontsize=12)
        ax.set_title("Mapa de Rutas Óptimas — Escenario 1", fontsize=14)

        if len(routes) <= 15:
            ax.legend(fontsize=8, loc="upper right", ncol=2)

        plt.tight_layout()
        plt.savefig(self.figures_dir / "fig05_ruta_optima.png", dpi=300)
        plt.close()

    def fig06_heatmap(self) -> None:
        """Fig 6: Heatmap — sensitivity of capacity vs vehicle_cost (Scenarios 4 & 5)."""
        self._apply_style()
        metrics = self._load_metrics()

        # Build a simple 2x2+ grid from scenario 1 (base), 4, and 5
        scenarios_data = {
            "Esc. 1\n(Q=30, Cv=$300)": metrics[0]["avg_best_fitness"],
            "Esc. 4\n(Q=20, Cv=$500)": metrics[3]["avg_best_fitness"],
            "Esc. 5\n(Q=50, Cv=$150)": metrics[4]["avg_best_fitness"],
        }

        # Create a comparison matrix
        labels = ["Q=20\nCv=$500\nCd=$5\nCe=$15", "Q=30\nCv=$300\nCd=$2\nCe=$10", "Q=50\nCv=$150\nCd=$1\nCe=$5"]
        values = [metrics[3]["avg_best_fitness"], metrics[0]["avg_best_fitness"], metrics[4]["avg_best_fitness"]]

        fig, ax = plt.subplots(figsize=(10, 6))
        matrix = np.array([[metrics[3]["avg_best_fitness"], metrics[3]["best_fitness"]],
                           [metrics[0]["avg_best_fitness"], metrics[0]["best_fitness"]],
                           [metrics[4]["avg_best_fitness"], metrics[4]["best_fitness"]]])

        sns.heatmap(
            matrix,
            annot=True,
            fmt=",.0f",
            cmap="YlOrRd_r",
            xticklabels=["Promedio", "BKS"],
            yticklabels=["Esc. 4 (Restrictivo)", "Esc. 1 (Base)", "Esc. 5 (Relajado)"],
            ax=ax,
        )
        ax.set_title("Sensibilidad: Configuración de Costos vs Fitness", fontsize=14)
        ax.set_ylabel("Configuración de Parámetros", fontsize=12)
        ax.set_xlabel("Métrica", fontsize=12)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "fig06_heatmap_params.png", dpi=300)
        plt.close()

    def fig07_scalability(self) -> None:
        """Fig 7: Line + shaded CI — Avg fitness ± std dev for Scenarios 1 vs 2."""
        self._apply_style()
        metrics = self._load_metrics()

        scenarios = ["Esc. 1\n(100 clientes)", "Esc. 2\n(200 clientes)"]
        avgs = [metrics[0]["avg_best_fitness"], metrics[1]["avg_best_fitness"]]
        stds = [metrics[0]["std_dev"], metrics[1]["std_dev"]]

        x = np.arange(len(scenarios))

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x, avgs, yerr=stds, capsize=10, color=[self.colors["blue"], self.colors["dark_gray"]],
               edgecolor=self.colors["dark_gray"], linewidth=1.5, alpha=0.85)

        ax.set_xlabel("Escenario", fontsize=12)
        ax.set_ylabel("Fitness Promedio (Z) ± Desv. Estándar", fontsize=12)
        ax.set_title("Escalabilidad: 100 vs 200 Clientes", fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios)

        # Annotate values
        for i, (avg, std) in enumerate(zip(avgs, stds)):
            ax.text(i, avg + std + 50, f"${avg:,.0f}\n±{std:,.0f}",
                    ha="center", fontsize=10, fontweight="bold")

        plt.tight_layout()
        plt.savefig(self.figures_dir / "fig07_escalabilidad.png", dpi=300)
        plt.close()

    def generate_all(self) -> None:
        """Generate all 7 figures."""
        print("Generating figures...")
        self.fig01_convergence()
        print("  [1/7] fig01_convergencia_base.png")
        self.fig02_boxplot()
        print("  [2/7] fig02_boxplot_escenarios.png")
        self.fig03_bar_metrics()
        print("  [3/7] fig03_barras_metricas.png")
        self.fig04_gap_success()
        print("  [4/7] fig04_gap_success.png")
        self.fig05_route_map()
        print("  [5/7] fig05_ruta_optima.png")
        self.fig06_heatmap()
        print("  [6/7] fig06_heatmap_params.png")
        self.fig07_scalability()
        print("  [7/7] fig07_escalabilidad.png")
        print("All figures saved to ./Figures/")
