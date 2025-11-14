from __future__ import annotations

import numpy as np


def gini_coefficient(values: list[float]) -> float:
    """Laske Gini-kerroin arvolistasta.

    Palauttaa 0.0 jos kaikki arvot ovat samat tai lista on tyhjä,
    muuten arvon välillä [0, 1], jossa 0 = täydellinen tasa-arvo.
    """

    if not values or len(values) < 2:
        return 0.0

    sorted_values = np.sort(values)
    n = len(sorted_values)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (
        n + 1
    ) / n
