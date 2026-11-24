# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Uncertainty helpers (protocol section 6): percentile bootstrap over instances."""

from __future__ import annotations

import numpy as np

from .network import FlowError

BOOTSTRAP_SEED = 20261124
BOOTSTRAP_RESAMPLES = 10_000


def bootstrap_median(values, resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED) -> np.ndarray:
    """Bootstrap distribution of the median, resampling the independent units."""
    v = np.asarray(values, dtype=float)
    if v.ndim != 1 or v.size == 0 or not np.all(np.isfinite(v)):
        raise FlowError("bootstrap needs a nonempty finite 1-D sample")
    if resamples < 1:
        raise FlowError("resamples must be >= 1")
    rng = np.random.Generator(np.random.PCG64(seed))
    idx = rng.integers(0, v.size, size=(resamples, v.size))
    return np.median(v[idx], axis=1)


def percentile_interval(values, level: float = 0.95, one_sided_lower: bool = False, **kw) -> tuple[float, float]:
    """Two-sided percentile interval, or (lower bound, +inf) for a one-sided interval."""
    if not 0 < level < 1:
        raise FlowError("level must lie in (0, 1)")
    boots = bootstrap_median(values, **kw)
    if one_sided_lower:
        return float(np.quantile(boots, 1 - level)), float("inf")
    a = (1 - level) / 2
    return float(np.quantile(boots, a)), float(np.quantile(boots, 1 - a))


def paired_differences(a: dict, b: dict) -> np.ndarray:
    """Per-instance differences a - b over the common instance keys (sorted)."""
    keys = sorted(set(a) & set(b))
    if not keys:
        raise FlowError("no common instances for a paired comparison")
    return np.array([a[k] - b[k] for k in keys], dtype=float)
