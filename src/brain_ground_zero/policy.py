from __future__ import annotations

import math
import random
from typing import Dict, List, Tuple

import numpy as np


class RoutePolicy:
    def __init__(self, choices: List[str], lr: float, epsilon: float, seed: int) -> None:
        if not choices:
            raise ValueError("RoutePolicy requires at least one choice")
        self.choices = list(choices)
        self.lr = lr
        self.epsilon = epsilon
        self.rng = random.Random(seed)
        self.weights = np.zeros(len(self.choices), dtype=np.float32)

    def _softmax(self) -> np.ndarray:
        max_w = float(np.max(self.weights))
        exp = np.exp(self.weights - max_w)
        return exp / float(np.sum(exp))

    def select(self) -> Tuple[str, float]:
        probs = self._softmax()
        if self.rng.random() < self.epsilon:
            idx = self.rng.randrange(len(self.choices))
            return self.choices[idx], float(probs[idx])
        idx = int(np.argmax(probs))
        return self.choices[idx], float(probs[idx])

    def update(self, choice: str, reward: float) -> None:
        probs = self._softmax()
        for i, c in enumerate(self.choices):
            grad = (1.0 if c == choice else 0.0) - float(probs[i])
            self.weights[i] += self.lr * reward * grad

