"""Configuration dataclasses for VRP Genetic Algorithm scenarios."""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class ScenarioConfig:
    """Immutable configuration for a single experimental scenario."""

    name: str
    num_clients: int
    demand_range: Tuple[int, int]
    value_range: Tuple[int, int]
    vehicle_capacity: int = 30
    vehicle_cost: float = 300.0
    distance_cost: float = 2.0
    empty_cost: float = 10.0
    max_coord: int = 100


@dataclass(frozen=True)
class GAConfig:
    """Immutable configuration for GA hyperparameters."""

    pop_size: int = 100
    generations: int = 300
    mutation_rate: float = 0.15
    tournament_k: int = 3
    runs: int = 30


@dataclass
class GARun:
    """Result of a single GA execution."""

    best_fitness: float
    best_chromosome: list
    top_3: list
    fitness_history: list
    seed_used: int


# UACJ institutional color palette
UACJ_COLORS = {
    "blue": "#003CA6",
    "yellow": "#FFD600",
    "dark_gray": "#2C3E50",
    "light_gray": "#ECF0F1",
    "white": "#FFFFFF",
    "red": "#E74C3C",
    "green": "#27AE60",
}


# Pre-defined experimental scenarios
SCENARIOS = [
    ScenarioConfig(
        name="Escenario 1 — Escalabilidad Media",
        num_clients=100,
        demand_range=(5, 15),
        value_range=(50, 300),
        vehicle_capacity=30,
        vehicle_cost=300,
        distance_cost=2,
        empty_cost=10,
    ),
    ScenarioConfig(
        name="Escenario 2 — Alta Escalabilidad",
        num_clients=200,
        demand_range=(5, 15),
        value_range=(50, 300),
        vehicle_capacity=30,
        vehicle_cost=300,
        distance_cost=2,
        empty_cost=10,
    ),
    ScenarioConfig(
        name="Escenario 3 — Variabilidad Económica",
        num_clients=100,
        demand_range=(1, 8),
        value_range=(150, 600),
        vehicle_capacity=30,
        vehicle_cost=300,
        distance_cost=2,
        empty_cost=10,
    ),
    ScenarioConfig(
        name="Escenario 4 — Estrés Operativo: Penalizaciones Altas",
        num_clients=100,
        demand_range=(5, 15),
        value_range=(50, 300),
        vehicle_capacity=20,
        vehicle_cost=500,
        distance_cost=5,
        empty_cost=15,
    ),
    ScenarioConfig(
        name="Escenario 5 — Estrés Operativo: Capacidad Ampliada",
        num_clients=100,
        demand_range=(5, 15),
        value_range=(50, 300),
        vehicle_capacity=50,
        vehicle_cost=150,
        distance_cost=1,
        empty_cost=5,
    ),
]
