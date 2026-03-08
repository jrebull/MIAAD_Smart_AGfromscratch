"""Generate fig07 (real convergence curves) and fig08 (route structure comparison).

Run after compute_report_stats.py has produced:
  - results/convergence_history.csv
  - results/report_stats.json
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "Figures"

# UACJ palette
BLUE = "#003CA6"
YELLOW = "#FFD600"
GREEN = "#27AE60"
RED = "#E74C3C"
DARK = "#2C3E50"
GRAY = "#555559"
ORANGE = "#E67E22"


def apply_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "axes.edgecolor": DARK,
        "axes.labelcolor": DARK,
        "text.color": DARK,
        "xtick.color": DARK,
        "ytick.color": DARK,
    })


def fig07_convergence_real():
    """Fig 7: Real convergence curves with shaded CI for Scenarios 1 vs 2."""
    apply_style()

    df = pd.read_csv(RESULTS_DIR / "convergence_history.csv")
    with open(RESULTS_DIR / "report_stats.json") as f:
        stats = json.load(f)

    fig, ax = plt.subplots(figsize=(12, 6))

    for s_id, color, label in [
        (1, BLUE, "Escenario 1 (100 clientes)"),
        (2, ORANGE, "Escenario 2 (200 clientes)"),
    ]:
        subset = df[df["scenario_id"] == s_id]
        grouped = subset.groupby("generation")["best_fitness"]
        mean = grouped.mean()
        std = grouped.std()

        ax.plot(mean.index, mean.values, color=color, linewidth=2.5, label=label)
        ax.fill_between(
            mean.index,
            (mean - std).values,
            (mean + std).values,
            alpha=0.15,
            color=color,
        )

    # Vertical dashed line at median convergence gen of Scenario 1
    conv_gen_1 = stats[0]["convergence_gen_median"]
    ax.axvline(
        x=conv_gen_1, color=GRAY, linestyle="--", linewidth=1.2, alpha=0.7,
        label=f"Convergencia Esc. 1 (gen. {conv_gen_1})"
    )

    ax.set_xlabel("Generación", fontsize=13)
    ax.set_ylabel("Mejor Fitness (Z)", fontsize=13)
    ax.set_title("Curvas de Convergencia: Escalabilidad 100 vs 200 Clientes", fontsize=14)
    ax.legend(fontsize=11, loc="lower right")

    # Format y-axis with thousands
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig07_escalabilidad.png", dpi=300)
    plt.close()
    print("  [7] fig07_escalabilidad.png (regenerated with real data)")


def fig08_route_structure():
    """Fig 8: Grouped horizontal bar chart — vehicles, utilization, distance."""
    apply_style()

    with open(RESULTS_DIR / "report_stats.json") as f:
        stats = json.load(f)

    labels = [f"Esc. {s['scenario_id']}" for s in stats]
    colors = [BLUE, DARK, BLUE, RED, GREEN]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel 1: Average vehicles
    vehicles = [s["avg_num_vehicles"] for s in stats]
    axes[0].barh(labels, vehicles, color=colors, edgecolor="white", linewidth=0.5)
    axes[0].set_xlabel("Número promedio de vehículos", fontsize=11)
    axes[0].set_title("Vehículos Utilizados", fontsize=12, fontweight="bold", color=BLUE)
    for i, v in enumerate(vehicles):
        axes[0].text(v + 0.3, i, f"{v:.1f}", va="center", fontsize=10)

    # Panel 2: Load utilization %
    utils = [s["avg_load_utilization_pct"] for s in stats]
    axes[1].barh(labels, utils, color=colors, edgecolor="white", linewidth=0.5)
    axes[1].axvline(x=100, color=GRAY, linestyle="--", linewidth=1.2, alpha=0.6)
    axes[1].set_xlabel("Utilización de capacidad (%)", fontsize=11)
    axes[1].set_title("Utilización de Carga", fontsize=12, fontweight="bold", color=BLUE)
    for i, v in enumerate(utils):
        axes[1].text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=10)

    # Panel 3: Average total distance
    dists = [s["avg_total_distance"] for s in stats]
    axes[2].barh(labels, dists, color=colors, edgecolor="white", linewidth=0.5)
    axes[2].set_xlabel("Distancia total promedio", fontsize=11)
    axes[2].set_title("Distancia Total", fontsize=12, fontweight="bold", color=BLUE)
    for i, v in enumerate(dists):
        axes[2].text(v + 20, i, f"{v:,.0f}", va="center", fontsize=10)

    for ax in axes:
        ax.invert_yaxis()

    plt.suptitle(
        "Estructura Comparativa de Rutas por Escenario",
        fontsize=14, fontweight="bold", color=BLUE, y=1.02,
    )
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig08_estructura_rutas.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  [8] fig08_estructura_rutas.png (new)")


if __name__ == "__main__":
    print("Generating figures from real data...")
    fig07_convergence_real()
    fig08_route_structure()
    print("Done.")
