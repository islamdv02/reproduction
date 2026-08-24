"""
Spinal Projectome Connectivity Module
Implements spatial distance metrics, directional projection biases, joint probability synthesis,
Bernoulli graph sparsification, Dale's principle sign assignment, row-wise E/I balancing,
and spectral rescaling from Komi et al., Nature Communications, 2026.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


def compute_pairwise_distances(
    pos_x: np.ndarray,
    pos_y: np.ndarray,
    pos_z: np.ndarray,
    latera: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes pairwise spatial distance matrices for all neuron pairs (target i, source j):
      - DistRC(i, j) = pos_z[i] - pos_z[j] (rostrocaudal)
      - DistML(i, j) = |pos_x[i]| - |pos_x[j]| (mediolateral)
      - DistDV(i, j) = pos_y[i] - pos_y[j] (dorsoventral)
      - DistCI(i, j) = latera[i] * latera[j] (+1 for ipsilateral, -1 for contralateral)
    """
    pos_x = np.asarray(pos_x, dtype=np.float64)
    pos_y = np.asarray(pos_y, dtype=np.float64)
    pos_z = np.asarray(pos_z, dtype=np.float64)
    latera = np.asarray(latera, dtype=np.float64)

    # In MATLAB: DistRC = -(pos_z - pos_z') = pos_z' - pos_z
    # where target i is rows and source j is columns
    dist_rc = pos_z[:, np.newaxis] - pos_z[np.newaxis, :]
    dist_ml = np.abs(pos_x[:, np.newaxis]) - np.abs(pos_x[np.newaxis, :])
    dist_dv = pos_y[:, np.newaxis] - pos_y[np.newaxis, :]
    dist_ci = np.outer(latera, latera)

    return dist_rc, dist_ml, dist_dv, dist_ci


def compute_directional_biases(
    dist_rc: np.ndarray,
    dist_ml: np.ndarray,
    dist_dv: np.ndarray,
    dist_ci: np.ndarray,
    neuron_types: np.ndarray,
    type_names: List[str],
    bias_rc: Dict[str, str],
    bias_ml: Dict[str, str],
    bias_dv: Dict[str, str],
    bias_ci: Dict[str, str],
    length_scales: Dict[str, float],
    projwidth: float = 500.0,
    rng: Optional[np.random.Generator] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes directional projection bias tensors (RC, ML, DV, Contra/Ipsi) for each neuron pair.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    n_neurons = len(neuron_types)
    b_rc = np.full((n_neurons, n_neurons), np.nan, dtype=np.float64)
    b_ml = np.full((n_neurons, n_neurons), np.nan, dtype=np.float64)
    b_dv = np.full((n_neurons, n_neurons), np.nan, dtype=np.float64)
    b_ci = np.ones((n_neurons, n_neurons), dtype=np.float64)

    neuron_types = np.asarray(neuron_types)

    # --- Rostrocaudal Bias ---
    for t_name in type_names:
        ioi = (neuron_types == t_name) # presynaptic source mask (columns)
        if not np.any(ioi):
            continue
        rc_mode = bias_rc.get(t_name, 'loc')
        l_scale = length_scales.get(t_name, 500.0)

        # Add Gaussian jitter to length scale (std = 0.1 * l_scale)
        divider = l_scale + rng.normal(0, 0.1 * l_scale, size=(n_neurons, np.sum(ioi)))

        sub_dist = dist_rc[:, ioi]
        sub_b_rc = np.zeros_like(sub_dist)

        if rc_mode == 'cau':
            # Caudal projecting: peak at +divider
            sub_b_rc = (sub_dist - divider) / projwidth
        elif rc_mode == 'ro':
            # Rostral projecting: peak at -divider
            sub_b_rc = (sub_dist + divider) / projwidth
        elif rc_mode == 'bi':
            # Bilateral projecting
            sub_b_rc = (np.abs(sub_dist) - divider) / projwidth
        elif rc_mode == 'loc':
            # Local projecting
            sub_b_rc = sub_dist / (divider + 1e-6)

        # Zero distance bias is zero
        sub_b_rc[sub_dist == 0] = 0.0
        b_rc[:, ioi] = sub_b_rc

    # --- Mediolateral Bias ---
    for t_name in type_names:
        ioi = (neuron_types == t_name)
        if not np.any(ioi):
            continue
        ml_mode = bias_ml.get(t_name, 'loc')
        sub_dist = dist_ml[:, ioi]
        sub_b_ml = np.zeros_like(sub_dist)

        if ml_mode == 'lat':
            sub_b_ml[sub_dist > 0] = np.abs(sub_dist[sub_dist > 0]) / (2.0 * projwidth)
            sub_b_ml[sub_dist < 0] = np.abs(sub_dist[sub_dist < 0]) / (projwidth / 5.0)
        elif ml_mode == 'med':
            sub_b_ml[sub_dist > 0] = np.abs(sub_dist[sub_dist > 0]) / (projwidth / 5.0)
            sub_b_ml[sub_dist < 0] = np.abs(sub_dist[sub_dist < 0]) / (2.0 * projwidth)
        else: # 'loc' or ''
            sub_b_ml = np.abs(sub_dist) / (projwidth / 5.0)

        sub_b_ml[sub_dist == 0] = 0.0
        b_ml[:, ioi] = sub_b_ml

    # --- Dorsoventral Bias ---
    for t_name in type_names:
        ioi = (neuron_types == t_name)
        if not np.any(ioi):
            continue
        dv_mode = bias_dv.get(t_name, 'loc')
        sub_dist = dist_dv[:, ioi]
        sub_b_dv = np.zeros_like(sub_dist)

        if dv_mode == 'dor':
            sub_b_dv[sub_dist > 0] = np.abs(sub_dist[sub_dist > 0]) / (2.0 * projwidth)
            sub_b_dv[sub_dist < 0] = np.abs(sub_dist[sub_dist < 0]) / (projwidth / 5.0)
        elif dv_mode == 'ven':
            sub_b_dv[sub_dist > 0] = np.abs(sub_dist[sub_dist > 0]) / (projwidth / 5.0)
            sub_b_dv[sub_dist < 0] = np.abs(sub_dist[sub_dist < 0]) / (2.0 * projwidth)
        else: # 'loc' or ''
            sub_b_dv = np.abs(sub_dist) / (projwidth / 5.0)

        sub_b_dv[sub_dist == 0] = 0.0
        b_dv[:, ioi] = sub_b_dv

    # --- Contra/Ipsilateral Bias ---
    for t_name in type_names:
        ioi = (neuron_types == t_name)
        if not np.any(ioi):
            continue
        ci_mode = bias_ci.get(t_name, 'ipsi')
        sub_dist_ci = dist_ci[:, ioi]
        sub_b_ci = np.ones_like(sub_dist_ci)

        if ci_mode == 'contra':
            sub_b_ci[sub_dist_ci < 0] = 1.0
            sub_b_ci[sub_dist_ci > 0] = 0.0
        elif ci_mode == 'ipsi':
            sub_b_ci[sub_dist_ci > 0] = 1.0
            sub_b_ci[sub_dist_ci < 0] = 0.0
        elif ci_mode == 'bi':
            sub_b_ci[sub_dist_ci > 0] = 0.2
            sub_b_ci[sub_dist_ci < 0] = 1.0

        b_ci[:, ioi] = sub_b_ci

    return b_rc, b_ml, b_dv, b_ci


def compute_connection_probabilities(
    b_rc: np.ndarray,
    b_ml: np.ndarray,
    b_dv: np.ndarray,
    b_ci: np.ndarray,
    b_pop: Optional[np.ndarray] = None,
    b_lay: Optional[np.ndarray] = None,
    b_seg: Optional[np.ndarray] = None,
    b_mn: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Computes joint synaptic connection probability matrix P(i, j) in [0, 1]
    by taking the geometric mean of the Gaussian directional densities.
    """
    # Normalized Gaussian: exp(-bias^2 / 2)
    # Geometric mean: exp(-(b_ml^2 + b_dv^2 + b_rc^2) / 6)
    b_ml_clean = np.nan_to_num(b_ml, nan=0.0)
    b_dv_clean = np.nan_to_num(b_dv, nan=0.0)
    b_rc_clean = np.nan_to_num(b_rc, nan=0.0)

    # Geometric mean over the 3 spatial dimensions
    spatial_prob = np.exp(-(b_ml_clean**2 + b_dv_clean**2 + b_rc_clean**2) / 6.0)

    prob = spatial_prob * b_ci

    if b_pop is not None:
        prob *= b_pop
    if b_lay is not None:
        prob *= b_lay
    if b_seg is not None:
        prob *= b_seg
    if b_mn is not None:
        prob *= b_mn

    prob = np.clip(prob, 0.0, 1.0)
    prob = np.nan_to_num(prob, nan=0.0)
    return prob


def sample_connectivity_matrix(
    prob: np.ndarray,
    cell_transmitters: np.ndarray,
    syn_strengths: np.ndarray,
    var: float = 0.1,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Samples synaptic connectivity matrix W from connection probabilities P(i, j),
    enforces Dale's principle, applies synaptic strengths, and removes self-connections.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    n_neurons = len(cell_transmitters)

    # Bernoulli sparsifier
    sparsifier = rng.binomial(1, prob)

    # Base random synaptic weight: N(1, var^2)
    w_raw = rng.normal(1.0, var, size=(n_neurons, n_neurons))

    # Apply Dale's principle and synaptic strengths
    w = np.zeros((n_neurons, n_neurons), dtype=np.float64)
    for j in range(n_neurons):
        strength = syn_strengths[j]
        if cell_transmitters[j] > 0: # Excitatory
            w[:, j] = np.abs(w_raw[:, j]) * strength
        else: # Inhibitory
            w[:, j] = -np.abs(w_raw[:, j]) * strength

    # Apply graph sparsifier
    w = w * sparsifier

    # Remove self-connections (autapses)
    np.fill_diagonal(w, 0.0)

    return w


def balance_connectivity(
    w: np.ndarray,
    latera: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Balances excitatory and inhibitory synaptic inputs for each neuron row,
    faithfully replicating BalanceConnectivity.m from BergLab.
    """
    w_balanced = w.copy()

    if latera is not None:
        # Balance left (latera > 0) and right (latera < 0) hemichords independently
        mask_l = latera > 0
        mask_r = latera < 0
        if np.any(mask_l):
            w_balanced[mask_l, :] = _balance_submatrix(w_balanced[mask_l, :])
        if np.any(mask_r):
            w_balanced[mask_r, :] = _balance_submatrix(w_balanced[mask_r, :])
    else:
        w_balanced = _balance_submatrix(w_balanced)

    return w_balanced


def _balance_submatrix(w_sub: np.ndarray) -> np.ndarray:
    """Helper implementing vectorized row-wise balance scaling."""
    w_pos = np.maximum(w_sub, 0.0)
    w_neg = np.minimum(w_sub, 0.0)

    sum_pos = np.sum(w_pos, axis=1, keepdims=True)
    sum_neg = np.sum(w_neg, axis=1, keepdims=True)
    balance = sum_pos + sum_neg

    bp = sum_pos - (balance / 2.0)
    bn = sum_neg - (balance / 2.0)

    facp = np.where(sum_pos > 0, bp / np.maximum(sum_pos, 1e-15), 1.0)
    facn = np.where(sum_neg < 0, bn / np.minimum(sum_neg, -1e-15), 1.0)

    # Only apply scaling to rows that contain both positive and negative weights
    has_both = (sum_pos > 0) & (sum_neg < 0)
    facp = np.where(has_both, facp, 1.0)
    facn = np.where(has_both, facn, 1.0)

    w_out = w_pos * facp + w_neg * facn
    return w_out


def rescale_connectivity(
    w: np.ndarray,
    latera: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, float]:
    """
    Rescales the connectivity matrix to normalize synaptic variance and spectral radius,
    faithfully replicating RescaleConnectivity.m from BergLab.
    """
    w_rescaled = w.copy()

    if latera is not None:
        mask_l = latera > 0
        mask_r = latera < 0
        if np.any(mask_l):
            w_rescaled[mask_l, :], sp_l = _rescale_submatrix(w_rescaled[mask_l, :])
        if np.any(mask_r):
            w_rescaled[mask_r, :], sp_r = _rescale_submatrix(w_rescaled[mask_r, :])
        total_zero = np.count_nonzero(w_rescaled == 0)
        sparsity = total_zero / w_rescaled.size
    else:
        w_rescaled, sparsity = _rescale_submatrix(w_rescaled)

    return w_rescaled, sparsity


def _rescale_submatrix(w_sub: np.ndarray) -> Tuple[np.ndarray, float]:
    """Helper implementing spectral rescaling."""
    n_pos = np.count_nonzero(w_sub > 0)
    n_neg = np.count_nonzero(w_sub < 0)

    if n_neg == 0:
        r = 1.0
    else:
        r = n_pos / n_neg

    n_elem = w_sub.size
    n_zero = np.count_nonzero(w_sub == 0)
    sparsity = n_zero / n_elem

    # Rescaling denominator from BergLab RescaleConnectivity.m
    denom = np.sqrt(sparsity * (1.0 - sparsity) * (1.0 + r**2) / 2.0) * np.sqrt(w_sub.shape[1])

    if denom > 0:
        w_out = w_sub / denom
    else:
        w_out = w_sub.copy()

    return w_out, sparsity
