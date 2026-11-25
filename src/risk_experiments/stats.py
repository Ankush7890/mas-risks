"""Small statistics helpers for per-condition rates."""

import math


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial rate k/n (default 95%).

    Chosen over the normal approximation because it stays inside [0, 1] and is
    sensible at k = 0 or k = n, which the paper's 0/10 and 10/10 results hit.
    """
    assert n > 0 and 0 <= k <= n, (k, n)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)
