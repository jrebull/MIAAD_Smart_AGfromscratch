"""VRP instance generator — OOP version of generador_instancias.py."""

import json
import random
from pathlib import Path
from typing import Dict, Optional, Tuple


class VRPInstanceGenerator:
    """Generates random VRP instances with a depot and n clients."""

    def __init__(
        self,
        num_clients: int,
        demand_range: Tuple[int, int] = (5, 15),
        value_range: Tuple[int, int] = (50, 300),
        max_coord: int = 100,
        seed: Optional[int] = None,
    ) -> None:
        self.num_clients = num_clients
        self.demand_range = demand_range
        self.value_range = value_range
        self.max_coord = max_coord
        self.seed = seed

    def generate(self) -> Dict:
        """Generate a VRP instance dict with depot at center and random clients."""
        if self.seed is not None:
            random.seed(self.seed)

        clients: Dict = {
            "0": {
                "x": self.max_coord // 2,
                "y": self.max_coord // 2,
                "demanda": 0,
                "valor": 0,
            }
        }

        for i in range(1, self.num_clients + 1):
            clients[str(i)] = {
                "x": random.randint(0, self.max_coord),
                "y": random.randint(0, self.max_coord),
                "demanda": random.randint(self.demand_range[0], self.demand_range[1]),
                "valor": random.randint(self.value_range[0], self.value_range[1]),
            }

        return clients

    def save(self, filepath: Path) -> None:
        """Serialize the generated instance to a JSON file."""
        instance = self.generate()
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(instance, f, indent=4)

    @classmethod
    def load(cls, filepath: Path) -> Dict:
        """Load a VRP instance from a JSON file."""
        with open(filepath, "r") as f:
            return json.load(f)
