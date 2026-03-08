# Genetic Algorithm from Scratch for the Vehicle Routing Problem (VRP)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-Academic-green)

A complete implementation of a Genetic Algorithm (GA) to solve the Capacitated Vehicle Routing Problem (CVRP), built from scratch without optimization libraries. The project includes experimental evaluation across 5 scenarios, statistical metrics, automated figure generation, and an interactive Streamlit dashboard.

## Problem Description

The **Capacitated Vehicle Routing Problem (CVRP)** seeks to design optimal delivery routes from a single depot to *n* geographically dispersed customers using a homogeneous fleet of vehicles with capacity *Q*. This implementation maximizes **net profit Z**:

```
Z = Sum(Di x Vi) - [(N_veh x C_veh) + (Dist_total x C_dist) + (Empty_total x C_empty)]
```

The GA uses **permutation-based chromosomes**, **OX1 crossover** (Davis, 1985), **swap mutation**, **tournament selection** (k=3), and **elitism**.

## Project Structure

```
AGfromscratch/
├── data/                         # Generated VRP instance JSON files
├── results/                      # CSV outputs from experiments
├── Figures/                      # Matplotlib/seaborn figures (300 DPI)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Dataclasses for scenario configuration
│   ├── instance_generator.py     # VRP instance generator (OOP)
│   ├── ga_engine.py              # Genetic Algorithm engine (OOP)
│   ├── experiment_runner.py      # Orchestrates 30 runs per scenario
│   ├── metrics.py                # BKS, Avg, Gap, SuccessRate computations
│   └── figure_generator.py       # All matplotlib figures for LaTeX
├── app/
│   └── streamlit_app.py          # Interactive Streamlit dashboard
├── generador_instancias.py       # CLI wrapper for instance generation
├── ag_vrp.py                     # CLI wrapper for GA execution
├── run_experiments.py            # Entry point: runs all 5 scenarios
├── requirements.txt
├── README.md
└── report/
    └── reporte_vrp_ag.tex        # LaTeX technical report (Spanish)
```

## Installation

```bash
git clone https://github.com/jrebull/MIAAD_Smart_AGfromscratch
cd AGfromscratch
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Usage

```bash
# Generate a single instance
python generador_instancias.py --clients 100 --seed 42

# Run a single GA execution
python ag_vrp.py --instance data/instance.json --generations 300

# Generate instances only
python run_experiments.py --generate-only

# Run full experiment (5 scenarios x 30 runs = 150 GA executions)
python run_experiments.py --full

# Generate figures only (requires results)
python run_experiments.py --figures-only

# Launch Streamlit dashboard
streamlit run app/streamlit_app.py
```

## Experimental Scenarios

| Scenario | Clients | Capacity | Vehicle Cost | Distance Cost | Empty Cost |
|----------|---------|----------|-------------|---------------|------------|
| 1 — Medium Scale | 100 | 30 | $300 | $2 | $10 |
| 2 — High Scale | 200 | 30 | $300 | $2 | $10 |
| 3 — Economic Variability | 100 | 30 | $300 | $2 | $10 |
| 4 — High Penalties | 100 | 20 | $500 | $5 | $15 |
| 5 — Expanded Capacity | 100 | 50 | $150 | $1 | $5 |

## Results

Results are saved to `./results/results_summary.csv` with columns: `scenario, run, best_fitness, generations, num_clients, seed`.

Metrics computed per scenario:
- **BKS** (Best Known Solution): Maximum fitness across 30 runs
- **Average Best Fitness**: Mean of best-per-run values
- **Gap (%)**: Percentage difference from BKS
- **Success Rate (%)**: Percentage of runs within 2% of BKS

## Academic Context

- **Program:** Maestria en Inteligencia Artificial y Analitica de Datos (MIAAD)
- **University:** Universidad Autonoma de Ciudad Juarez (UACJ)
- **Course:** Optimizacion Inteligente
- **Professor:** Mtro. Raul Gibran Porras Alaniz

## Author

**Javier Augusto Rebull Saucedo** — Matricula 263483
