"""Weight algebra in PyTorch's [out_features, in_features] convention.

No inference or training is performed here. Magnitude parameters scale rows
in this convention; papers using [in, out] describe the same operation as
column scaling.
"""
import numpy as np


def dora_components(base, low_rank_update, magnitude):
    """Return W', radial update, and scaled low-rank update, in float64."""
    base = np.asarray(base, dtype=np.float64)
    update = np.asarray(low_rank_update, dtype=np.float64)
    magnitude = np.asarray(magnitude, dtype=np.float64)
    if base.ndim != 2 or update.shape != base.shape:
        raise ValueError("Base and update must have the same matrix shape")
    if magnitude.shape != (base.shape[0],):
        raise ValueError("One magnitude is required per output row")
    direction = base + update
    norms = np.linalg.norm(direction, axis=1)
    if np.any(norms == 0) or not np.all(np.isfinite(norms)):
        raise ValueError("Direction has a zero or nonfinite row norm")
    if not np.all(np.isfinite(magnitude)):
        raise ValueError("Nonfinite magnitude")
    scale = magnitude / norms
    radial = (scale - 1)[:, None] * base
    scaled_low_rank = scale[:, None] * update
    return scale[:, None] * direction, radial, scaled_low_rank


def best_rank_approximation(matrix, rank):
    """Best rank-r approximation in the Frobenius metric, not task loss."""
    matrix = np.asarray(matrix, dtype=np.float64)
    if matrix.ndim != 2 or not 0 <= rank <= min(matrix.shape):
        raise ValueError("Invalid matrix or rank")
    left, singular, right = np.linalg.svd(matrix, full_matrices=False)
    return (left[:, :rank] * singular[:rank]) @ right[:rank]


def relative_output_error(reference_update, approximation, inputs):
    """Relative squared error of the linear update on rows of input X."""
    exact = np.asarray(inputs) @ np.asarray(reference_update).T
    difference = np.asarray(inputs) @ (np.asarray(reference_update) - approximation).T
    denominator = np.sum(exact ** 2)
    if denominator == 0:
        raise ValueError("Reference update has zero energy on these inputs")
    return float(np.sum(difference ** 2) / denominator)
