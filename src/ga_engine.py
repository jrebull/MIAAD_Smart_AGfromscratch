"""Genetic Algorithm engine for the Capacitated VRP — OOP version of ag_vrp.py."""

import math
import random
from typing import Dict, List, Optional

from .config import GARun, ScenarioConfig


class VRPInstance:
    """Value object holding a VRP instance and its configuration."""

    def __init__(self, clients: Dict, config: ScenarioConfig) -> None:
        self.clients = clients
        self.config = config
        self.client_ids: List[str] = [
            cid for cid in clients.keys() if cid != "0"
        ]

    def euclidean_distance(self, c1: str, c2: str) -> float:
        """Compute Euclidean distance between two client nodes."""
        x1, y1 = self.clients[c1]["x"], self.clients[c1]["y"]
        x2, y2 = self.clients[c2]["x"], self.clients[c2]["y"]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def decode_chromosome(self, chromosome: List[str]) -> List[List[str]]:
        """Decode a permutation chromosome into vehicle routes respecting capacity."""
        routes: List[List[str]] = []
        current_route: List[str] = []
        current_load = 0

        for client_id in chromosome:
            demand = self.clients[client_id]["demanda"]
            if current_load + demand > self.config.vehicle_capacity:
                routes.append(current_route)
                current_route = [client_id]
                current_load = demand
            else:
                current_route.append(client_id)
                current_load += demand

        if current_route:
            routes.append(current_route)

        return routes


class FitnessEvaluator:
    """Evaluates the fitness (net profit Z) of a chromosome."""

    def __init__(self, instance: VRPInstance) -> None:
        self.instance = instance

    def evaluate(self, chromosome: List[str]) -> float:
        """Compute fitness Z = total_revenue - total_costs."""
        inst = self.instance
        cfg = inst.config
        routes = inst.decode_chromosome(chromosome)

        total_revenue = 0.0
        total_distance = 0.0
        total_empty_space = 0.0
        n_vehicles = len(routes)

        for route in routes:
            route_load = 0
            # Distance from depot to first client
            total_distance += inst.euclidean_distance("0", route[0])

            for i in range(len(route)):
                client_id = route[i]
                demand = inst.clients[client_id]["demanda"]
                value = inst.clients[client_id]["valor"]
                route_load += demand
                total_revenue += demand * value

                if i < len(route) - 1:
                    total_distance += inst.euclidean_distance(route[i], route[i + 1])

            # Distance from last client back to depot
            total_distance += inst.euclidean_distance(route[-1], "0")
            total_empty_space += cfg.vehicle_capacity - route_load

        total_costs = (
            (n_vehicles * cfg.vehicle_cost)
            + (total_distance * cfg.distance_cost)
            + (total_empty_space * cfg.empty_cost)
        )

        return total_revenue - total_costs


class GeneticOperators:
    """Static genetic operators: selection, crossover, mutation."""

    @staticmethod
    def tournament_selection(
        population: List[List[str]],
        fitness_values: List[float],
        k: int = 3,
    ) -> List[str]:
        """Select the fittest individual from k random candidates."""
        indices = random.sample(range(len(population)), k)
        best_idx = max(indices, key=lambda i: fitness_values[i])
        return population[best_idx]

    @staticmethod
    def ox1_crossover(parent1: List[str], parent2: List[str]) -> List[str]:
        """Order Crossover (OX1) — Davis 1985."""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[start:end] = parent1[start:end]

        segment_set = set(child[start:end])
        fill_values = [gene for gene in parent2 if gene not in segment_set]

        idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = fill_values[idx]
                idx += 1

        return child

    @staticmethod
    def swap_mutation(chromosome: List[str], mutation_rate: float) -> List[str]:
        """Swap two random positions with given probability."""
        child = chromosome.copy()
        if random.random() < mutation_rate:
            idx1, idx2 = random.sample(range(len(child)), 2)
            child[idx1], child[idx2] = child[idx2], child[idx1]
        return child


class GeneticAlgorithm:
    """Main GA loop with elitism and top-3 tracking."""

    def __init__(
        self,
        instance: VRPInstance,
        pop_size: int = 100,
        generations: int = 300,
        mutation_rate: float = 0.15,
        tournament_k: int = 3,
    ) -> None:
        self.instance = instance
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.tournament_k = tournament_k
        self.evaluator = FitnessEvaluator(instance)

    def run(self, seed: Optional[int] = None, verbose: bool = False) -> GARun:
        """Execute the GA and return results. Deterministic given the same seed."""
        if seed is not None:
            random.seed(seed)

        client_ids = self.instance.client_ids.copy()

        # Initialize population
        population: List[List[str]] = []
        for _ in range(self.pop_size):
            individual = client_ids.copy()
            random.shuffle(individual)
            population.append(individual)

        top_3_historic: List[List[str]] = []
        fitness_history: List[float] = []

        for generation in range(self.generations):
            # Evaluate all fitness values
            fitness_values = [self.evaluator.evaluate(ind) for ind in population]

            # Sort population by fitness (descending)
            paired = list(zip(population, fitness_values))
            paired.sort(key=lambda x: x[1], reverse=True)
            population = [p[0] for p in paired]
            fitness_values = [p[1] for p in paired]

            # Update top-3 historic
            for individual in population:
                if individual not in top_3_historic:
                    top_3_historic.append(individual)
            top_3_historic.sort(
                key=lambda ind: self.evaluator.evaluate(ind), reverse=True
            )
            top_3_historic = top_3_historic[:3]

            # Track best fitness
            best_fitness = self.evaluator.evaluate(top_3_historic[0])
            fitness_history.append(best_fitness)

            if verbose and (generation + 1) % 50 == 0:
                print(
                    f"Generation {generation + 1} | Best Z: ${best_fitness:.2f}"
                )

            # Elitism: keep best individual
            new_population = [population[0]]

            # Generate rest of population
            while len(new_population) < self.pop_size:
                parent1 = GeneticOperators.tournament_selection(
                    population, fitness_values, self.tournament_k
                )
                parent2 = GeneticOperators.tournament_selection(
                    population, fitness_values, self.tournament_k
                )
                child = GeneticOperators.ox1_crossover(parent1, parent2)
                child = GeneticOperators.swap_mutation(child, self.mutation_rate)
                new_population.append(child)

            population = new_population

        return GARun(
            best_fitness=self.evaluator.evaluate(top_3_historic[0]),
            best_chromosome=top_3_historic[0],
            top_3=top_3_historic,
            fitness_history=fitness_history,
            seed_used=seed if seed is not None else -1,
        )
