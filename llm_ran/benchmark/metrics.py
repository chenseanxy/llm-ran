import numpy as np

def _pass_at_estimator(n: int, c: int, k: int) -> float:
    """Calculates 1 - comb(n - c, k) / comb(n, k)."""
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

def _pass_power_estimator(n: int, c: int, k: int) -> float:
    """Calculates (c / n) ** k."""
    if n == 0:
        return 0.0
    return (c / n) ** k

def pass_at(k):
    def wrapped(series):
        return _pass_at_estimator(len(series), np.sum(series), k)
    return wrapped

def pass_power(k):
    def wrapped(series):
        return _pass_power_estimator(len(series), np.sum(series), k)
    return wrapped
