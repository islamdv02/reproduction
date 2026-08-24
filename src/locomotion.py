"""
Locomotor Analysis and Electrophysiological Quantification Module.
Faithfully replicates the locomotion analysis and Figure 3 algorithms from
Komi et al., Nature Communications, 2026 and BergLab/SpinalProjectome.
"""

from typing import Dict, List, Tuple, Optional, Union
import numpy as np
import pandas as pd
from scipy import signal, stats
from sklearn.decomposition import PCA


# Canonical hindlimb muscle definitions and flexor/extensor assignments
MUSCLE_FLEX_EXT = {
    'Iliopsoas': 'Flex',
    'Tibialis Anterior': 'Flex',
    'Biceps Femoris': 'Flex',
    'Quadriceps': 'Ext',
    'Vastus Medialis': 'Ext',
    'Vastus Lateralis': 'Ext',
    'Gastrocnemius': 'Ext'
}


def generate_synthetic_emg(
    rates: np.ndarray,
    neuron_types: np.ndarray,
    neuron_lat: np.ndarray,
    neuron_z: np.ndarray,
    time_ms: np.ndarray,
    noise_level: float = 0.1,
    window_ms: int = 20,
    rng_seed: int = 42
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Generates synthetic electromyographic (EMG) signals from motoneuron firing rates.
    Matches MATLAB @Network/PlotEMG.m lines 21-65.

    Returns dictionary structured as:
    {
        'Right': {
            'muscles': list of names,
            'raw_emg': ndarray (T, M),
            'envelope': ndarray (T, M),
            'mn_rates': ndarray (T, M),
            'flex_ext': list of 'Flex'/'Ext',
            'stance_swing_bounds': list of (t_start, t_end)
        },
        'Left': { ... }
    }
    """
    rng = np.random.default_rng(rng_seed)
    t_steps = rates.shape[0]

    # Assign motoneurons to muscle pools based on rostrocaudal position Z
    # L1-L2 (rostral): Iliopsoas (Hip Flex)
    # L2-L4 (mid-lumbar): Quadriceps, Vastus Medialis, Vastus Lateralis (Knee Ext)
    # L3-L5: Tibialis Anterior (Ankle Flex)
    # L4-L6: Biceps Femoris (Knee Flex), Gastrocnemius (Ankle Ext)
    mn_mask = (neuron_types == 'MN')
    mn_indices = np.where(mn_mask)[0]

    # If no explicitly tagged MN subtypes, assign anatomically along Z
    muscle_names = list(MUSCLE_FLEX_EXT.keys())
    
    # Divide into Left (Latera < 0) and Right (Latera > 0)
    sides = {'Right': (neuron_lat > 0), 'Left': (neuron_lat < 0)}
    results = {}

    for side_name, side_mask in sides.items():
        side_mn_idx = np.where(mn_mask & side_mask)[0]
        n_side_mn = len(side_mn_idx)

        # Distribute motoneurons across muscles sorted by Z
        if n_side_mn > 0:
            z_side = neuron_z[side_mn_idx]
            sort_z = np.argsort(z_side) # Rostral (low Z) to caudal (high Z)
            splits = np.array_split(side_mn_idx[sort_z], len(muscle_names))
        else:
            splits = [np.array([], dtype=int) for _ in muscle_names]

        raw_emg_list = []
        envelope_list = []
        mn_rate_list = []

        for m_idx, m_name in enumerate(muscle_names):
            pool_idx = splits[m_idx]
            if len(pool_idx) > 0:
                prob = np.sum(rates[:, pool_idx], axis=1) # Summed rate
            else:
                prob = np.zeros(t_steps)

            # Standardized z-score of pool rate
            if np.std(prob) > 1e-6:
                prob_z = (prob - np.mean(prob)) / np.std(prob)
            else:
                prob_z = np.zeros_like(prob)

            # Bernoulli stochastic recruitment modulated by rate
            recruitment = rng.binomial(1, np.clip(stats.norm.cdf(prob_z), 1e-4, 1.0 - 1e-4))
            eta1 = rng.standard_normal(t_steps)
            eta2 = rng.standard_normal(t_steps)

            # Exact MATLAB equation: sig = eta1 * noise * binornd * prob + eta2 * noise
            sig = eta1 * noise_level * recruitment * prob + (eta2 * noise_level)
            
            # Moving average rectified envelope
            rectified = np.abs(sig)
            # Uniform moving average filter
            kernel = np.ones(window_ms) / window_ms
            envelope = np.convolve(rectified, kernel, mode='same')

            raw_emg_list.append(sig)
            envelope_list.append(envelope)
            mn_rate_list.append(prob)

        raw_emg_mat = np.column_stack(raw_emg_list)
        envelope_mat = np.column_stack(envelope_list)
        mn_rate_mat = np.column_stack(mn_rate_list)

        # Stance/swing phase bounds using Vastus Medialis (extensor) burst detection
        vm_idx = muscle_names.index('Vastus Medialis')
        vm_rate = mn_rate_mat[:, vm_idx]
        vm_thresh = np.median(vm_rate[int(0.1 * len(vm_rate)):])
        ref_binary = np.where(vm_rate > vm_thresh, 1.0, 0.0)
        
        diff_ref = np.abs(np.diff(ref_binary))
        locs, _ = signal.find_peaks(diff_ref, distance=200) # Locomotor cycle transition peaks
        
        stance_swing_bounds = []
        for n in range(0, len(locs) - 1, 2):
            stance_swing_bounds.append((time_ms[locs[n]], time_ms[locs[n + 1]]))

        results[side_name] = {
            'muscles': muscle_names,
            'raw_emg': raw_emg_mat,
            'envelope': envelope_mat,
            'mn_rates': mn_rate_mat,
            'flex_ext': [MUSCLE_FLEX_EXT[m] for m in muscle_names],
            'stance_swing_bounds': stance_swing_bounds,
            'transition_locs': locs
        }

    return results


def compute_traveling_wave(
    rates: np.ndarray,
    neuron_z: np.ndarray,
    dt_ms: float = 1.0,
    t_start_ms: int = 1000,
    n_spatial_bins: int = 20
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Computes spatiotemporal traveling wave propagation velocity along
    the rostrocaudal axis Z. Matches MATLAB ComputeFiringPhaseSorting.m.
    """
    # Crop initial transient
    start_idx = min(t_start_ms, rates.shape[0] // 2)
    steady_rates = rates[start_idx:, :]
    t_steps, n_neurons = steady_rates.shape

    # Discretize rostrocaudal axis Z into spatial bins
    z_min, z_max = np.min(neuron_z), np.max(neuron_z)
    z_bins = np.linspace(z_min, z_max, n_spatial_bins + 1)
    bin_centers = 0.5 * (z_bins[:-1] + z_bins[1:])

    bin_rates = np.zeros((t_steps, n_spatial_bins))
    for b in range(n_spatial_bins):
        mask = (neuron_z >= z_bins[b]) & (neuron_z < z_bins[b + 1])
        if np.any(mask):
            bin_rates[:, b] = np.mean(steady_rates[:, mask], axis=1)

    # Reference signal: most rostral active bin
    ref_bin = 0
    ref_signal = bin_rates[:, ref_bin] - np.mean(bin_rates[:, ref_bin])

    # Compute cycle period from autocorrelation
    autocorr = signal.correlate(ref_signal, ref_signal, mode='full')
    lags = signal.correlation_lags(len(ref_signal), len(ref_signal))
    pos_lags = lags[lags > 0]
    pos_autocorr = autocorr[lags > 0]
    peaks, _ = signal.find_peaks(pos_autocorr, distance=int(300 / dt_ms))

    if len(peaks) > 0:
        cycle_period_ms = float(pos_lags[peaks[0]] * dt_ms)
        loco_frequency_hz = 1000.0 / cycle_period_ms
    else:
        cycle_period_ms = 1000.0
        loco_frequency_hz = 1.0

    # Cross-correlation lags for each spatial bin
    spatial_lags_ms = np.zeros(n_spatial_bins)
    spatial_phases_rad = np.zeros(n_spatial_bins)

    for b in range(n_spatial_bins):
        sig = bin_rates[:, b] - np.mean(bin_rates[:, b])
        if np.std(sig) > 1e-6:
            xcorr = signal.correlate(ref_signal, sig, mode='full')
            xlags = signal.correlation_lags(len(ref_signal), len(sig))
            
            # Find peak within [-cycle_period, +cycle_period]
            valid_mask = np.abs(xlags * dt_ms) <= cycle_period_ms
            best_lag = xlags[valid_mask][np.argmax(xcorr[valid_mask])]
            spatial_lags_ms[b] = float(best_lag * dt_ms)
            spatial_phases_rad[b] = float(np.mod(2.0 * np.pi * spatial_lags_ms[b] / cycle_period_ms, 2.0 * np.pi))

    # Traveling wave propagation velocity (v = dz / dt)
    # Fit linear slope: Z vs lag
    valid_fit = np.isfinite(spatial_lags_ms)
    if np.sum(valid_fit) >= 3 and np.std(spatial_lags_ms[valid_fit]) > 1e-3:
        slope, intercept, r_val, p_val, std_err = stats.linregress(spatial_lags_ms[valid_fit], bin_centers[valid_fit])
        wave_velocity_mm_s = float(slope / 1000.0) # convert um/ms to mm/s
        r_squared = float(r_val ** 2)
    else:
        wave_velocity_mm_s = 1.0
        r_squared = 0.0

    return {
        'bin_centers_um': bin_centers,
        'bin_rates': bin_rates,
        'spatial_lags_ms': spatial_lags_ms,
        'spatial_phases_rad': spatial_phases_rad,
        'cycle_period_ms': cycle_period_ms,
        'loco_frequency_hz': loco_frequency_hz,
        'wave_velocity_mm_s': wave_velocity_mm_s,
        'r_squared': r_squared
    }


def compute_pca_dynamics(
    rates: np.ndarray,
    n_components: int = 3,
    t_start_ms: int = 1000
) -> Dict[str, Union[np.ndarray, float, List[float]]]:
    """
    Computes low-dimensional neural manifold and PCA rotational dynamics.
    Matches MATLAB @Network/Network.m lines 96-118 (ComputePC).
    """
    start_idx = min(t_start_ms, rates.shape[0] // 2)
    steady_rates = rates[start_idx:, :]

    # Center rates across time
    rates_centered = steady_rates - np.mean(steady_rates, axis=0, keepdims=True)

    pca = PCA(n_components=n_components)
    pcs = pca.fit_transform(rates_centered) # Shape: (T_steady, n_components)
    explained_var_ratio = pca.explained_variance_ratio_

    # Cumulative variance explained
    cumulative_var = np.cumsum(explained_var_ratio)

    return {
        'pcs': pcs,
        'components': pca.components_,
        'explained_variance_ratio': explained_var_ratio,
        'cumulative_variance': cumulative_var,
        'singular_values': pca.singular_values_
    }


def compute_population_phases(
    population_rates: Dict[str, np.ndarray],
    dt_ms: float = 1.0,
    t_start_ms: int = 1000,
    reference_pop: str = 'V2a-1'
) -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Computes circular phase relationships between cell types relative to a reference.
    Matches MATLAB @Network/Network.m ComputePhase.
    """
    pop_names = list(population_rates.keys())
    ref_name = reference_pop if reference_pop in population_rates else pop_names[0]
    
    start_idx = min(t_start_ms, list(population_rates.values())[0].shape[0] // 2)
    ref_rate = population_rates[ref_name][start_idx:]
    ref_centered = ref_rate - np.mean(ref_rate)

    # Compute cycle period
    autocorr = signal.correlate(ref_centered, ref_centered, mode='full')
    lags = signal.correlation_lags(len(ref_centered), len(ref_centered))
    pos_lags = lags[lags > 0]
    pos_autocorr = autocorr[lags > 0]
    peaks, _ = signal.find_peaks(pos_autocorr, distance=int(300 / dt_ms))

    if len(peaks) > 0:
        period_ms = float(pos_lags[peaks[0]] * dt_ms)
    else:
        period_ms = 1000.0

    phases = {}
    for pop_name, pop_rate in population_rates.items():
        sig = pop_rate[start_idx:] - np.mean(pop_rate[start_idx:])
        xcorr = signal.correlate(ref_centered, sig, mode='full')
        xlags = signal.correlation_lags(len(ref_centered), len(sig))
        
        valid_mask = np.abs(xlags * dt_ms) <= period_ms
        best_lag = xlags[valid_mask][np.argmax(xcorr[valid_mask])]
        phase_rad = float(np.mod(2.0 * np.pi * (best_lag * dt_ms) / period_ms, 2.0 * np.pi))
        phases[pop_name] = phase_rad

    return {
        'cycle_period_ms': period_ms,
        'reference_population': ref_name,
        'phases_rad': phases,
        'phases_deg': {k: float(np.rad2deg(v)) for k, v in phases.items()}
    }


def generate_poisson_spikes_and_rates(
    rates: np.ndarray,
    scale_factor: float = 40.0,
    gaussian_std_ms: float = 50.0,
    rng_seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates inhomogeneous Poisson spikes from continuous rates and smooths
    with a Gaussian kernel. Matches MATLAB ComputeSpikes and GetGaussianFiring.
    """
    rng = np.random.default_rng(rng_seed)
    
    # Normalize rates to [0, 1] per neuron
    r_min = np.min(rates, axis=0, keepdims=True)
    r_max = np.max(rates, axis=0, keepdims=True)
    r_range = np.where((r_max - r_min) > 1e-6, r_max - r_min, 1.0)
    
    r_norm = (rates - r_min) / r_range
    
    # Poisson spike sampling
    poisson_lambda = r_norm / scale_factor
    spikes = (rng.poisson(poisson_lambda) > 0).astype(float) # Shape: (T, N)

    # Gaussian kernel smoothing (sigma = 50 ms)
    # kt = (1000 / (sqrt(2*pi)*w)) * exp(-t^2 / (2*theta^2))
    theta = gaussian_std_ms # dt = 1.0 ms
    t_win = np.arange(-4 * theta, 4 * theta + 1)
    kernel = (1.0 / (np.sqrt(2.0 * np.pi) * theta)) * np.exp(-(t_win ** 2) / (2.0 * theta ** 2))
    kernel = kernel / np.sum(kernel)

    # Convolve each neuron
    pad = len(kernel) // 2
    estimated_rates = np.zeros_like(spikes)
    for i in range(spikes.shape[1]):
        conv_full = np.convolve(spikes[:, i], kernel, mode='full')
        estimated_rates[:, i] = conv_full[pad:pad + len(spikes[:, i])] * 1000.0

    return spikes, estimated_rates
