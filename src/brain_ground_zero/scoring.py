from __future__ import annotations

from typing import Dict


def compute_rates(correct: int, total: int, stale: int, false: int, unknown: int) -> Dict[str, float]:
    incorrect = total - correct
    return {
        "accuracy": correct / total if total else 0.0,
        "stale_rate": stale / incorrect if incorrect else 0.0,
        "false_rate": false / incorrect if incorrect else 0.0,
        "unknown_rate": unknown / incorrect if incorrect else 0.0,
    }

