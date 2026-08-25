"""
Virtual Electrophysiology Module for Mouse Spinal Cord Model.
Replicates BergLab's high-density silicon probe sampling and electrophysiology analysis:
- 3D electrode positioning and channel mapping (matching 02_HelperFunctions/PositionElectrodeAndSample3D.m)
- Multi-unit channel assignment within detection radius (Dist < DistThresh = 50 um)
- Poisson rate-to-spike conversion (matching @Network/ComputeSpikes.m)
- Gaussian kernel smoothing for instantaneous firing rate estimation (matching @Network/ComputeEstimatedRates.m)
- Multi-channel traveling wave phase lag analysis across probe depth
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple, Union
import numpy as np
import scipy.ndimage as ndi
from scipy.signal import find_peaks

from network import Network


@dataclass
class ProbeConfig:
    """Configuration for virtual high-density silicon probe / Neuropixels shank."""
    n_channels: int = 32
    pitch_um: float = 50.0  # inter-electrode spacing along shank
    shank_length_um: float = 1550.0
    detection_radius_um: float = 50.0  # detection radius for units
    tip_x_um: float = -400.0  # mediolateral position (left ventral horn)
    tip_y_um: float = 300.0   # dorsoventral position (ventral layer IX)
    tip_z_um: float = 4000.0  # rostrocaudal position (L2/L3 boundary)
    insertion_angle_deg: float = 0.0  # vertical insertion along Y (dorsoventral)


class VirtualProbe:
    """
    Simulates a high-density silicon probe / Neuropixels electrode shank inserted
    into the 3D mouse spinal cord network matching BergLab's PositionElectrodeAndSample3D.m.
    """

    def __init__(self, config: Optional[ProbeConfig] = None):
        self.config = config or ProbeConfig()
        self.channel_positions_um = self._generate_channel_positions()
        self.detected_neuron_indices: np.ndarray = np.array([], dtype=int)
        self.channel_assignments: np.ndarray = np.array([], dtype=int)
        self.channel_neuron_map: Dict[int, List[int]] = {ch: [] for ch in range(self.config.n_channels)}
        self.detected_cell_types: List[str] = []
        self.n_detected_units: int = 0

    def _generate_channel_positions(self) -> np.ndarray:
        """
        Generates 3D coordinates (X, Y, Z in um) for each recording site on the probe shank.
        Channel 0 is at the tip; channel (n-1) is most dorsal.
        """
        cfg = self.config
        ch_y = cfg.tip_y_um + np.arange(cfg.n_channels) * cfg.pitch_um
        ch_x = np.full(cfg.n_channels, cfg.tip_x_um)
        ch_z = np.full(cfg.n_channels, cfg.tip_z_um)

        if cfg.insertion_angle_deg != 0.0:
            rad = np.radians(cfg.insertion_angle_deg)
            rot_y = (ch_y - cfg.tip_y_um) * np.cos(rad) + cfg.tip_y_um
            rot_x = (ch_y - cfg.tip_y_um) * np.sin(rad) + cfg.tip_x_um
            return np.column_stack([rot_x, rot_y, ch_z])

        return np.column_stack([ch_x, ch_y, ch_z])

    def sample_network(self, network: Network) -> Dict[str, Any]:
        """
        Samples units from the 3D network within detection radius matching PositionElectrodeAndSample3D.m:
          Dist(ii, jj) = sqrt((ElectrodePos(ii) - neuronlocation(jj))^2)
          LogicalDist = (Dist < DistThresh)
          ClusterChan = argmin_ch(Dist)
        """
        soma_pos = np.column_stack([network.pos_x, network.pos_y, network.pos_z]) # (N, 3)
        ch_pos = self.channel_positions_um # (K, 3)

        # Pairwise distance matrix (K, N)
        dx = ch_pos[:, 0, None] - soma_pos[:, 0][None, :]
        dy = ch_pos[:, 1, None] - soma_pos[:, 1][None, :]
        dz = ch_pos[:, 2, None] - soma_pos[:, 2][None, :]
        dist_matrix = np.sqrt(dx**2 + dy**2 + dz**2) # (K, N)

        r_thresh = self.config.detection_radius_um
        in_range = (dist_matrix < r_thresh) # (K, N)

        # Detect neurons that are in range of at least one channel
        detected_mask = np.any(in_range, axis=0) # (N,)
        detected_indices = np.where(detected_mask)[0]

        self.channel_neuron_map = {ch: [] for ch in range(self.config.n_channels)}
        channel_assignments = []

        for neuron_idx in detected_indices:
            # Assign to closest electrode channel
            closest_ch = int(np.argmin(dist_matrix[:, neuron_idx]))
            channel_assignments.append(closest_ch)
            self.channel_neuron_map[closest_ch].append(neuron_idx)

        self.detected_neuron_indices = detected_indices
        self.channel_assignments = np.array(channel_assignments, dtype=int)
        self.detected_cell_types = [str(network.types[idx]) for idx in detected_indices]
        self.n_detected_units = len(detected_indices)

        return {
            'n_detected_units': self.n_detected_units,
            'detected_indices': self.detected_neuron_indices,
            'channel_assignments': self.channel_assignments,
            'channel_neuron_map': self.channel_neuron_map,
            'channel_positions_um': self.channel_positions_um,
            'detected_cell_types': self.detected_cell_types
        }

    def compute_multi_unit_rates(self, rates: np.ndarray) -> np.ndarray:
        """
        Computes aggregate multi-unit firing rates for each channel:
          A_k(t) = mean_{i in Channel k}(R_i(t))
        Returns array of shape (T, n_channels).
        """
        T = rates.shape[0]
        K = self.config.n_channels
        ch_rates = np.zeros((T, K), dtype=np.float64)

        for ch in range(K):
            neuron_indices = self.channel_neuron_map[ch]
            if len(neuron_indices) > 0:
                ch_rates[:, ch] = np.mean(rates[:, neuron_indices], axis=1)

        return ch_rates


def generate_poisson_spikes(
    rates: np.ndarray,
    scale: float = 75.0,
    seed: int = 42
) -> np.ndarray:
    """
    Generates synthetic binary spike trains from continuous firing rates
    matching BergLab's @Network/ComputeSpikes.m:
      RIsp = (RI - min(RI)) / (max(RI) - min(RI))
      Poiss = poissrnd(RIsp / 75) > 0
    Returns boolean array of shape (T, N).
    """
    rng = np.random.default_rng(seed)
    T, N = rates.shape

    min_r = np.min(rates, axis=0, keepdims=True)
    max_r = np.max(rates, axis=0, keepdims=True)
    ptp_r = max_r - min_r
    ptp_r[ptp_r == 0] = 1.0

    r_norm = (rates - min_r) / ptp_r
    lambda_p = r_norm / scale
    spikes = (rng.poisson(lambda_p) > 0)

    return spikes


def estimate_instantaneous_rates(
    spikes: np.ndarray,
    sigma_ms: float = 50.0,
    dt_ms: float = 1.0
) -> np.ndarray:
    """
    Estimates smooth instantaneous firing rates from discrete spike trains
    matching BergLab's GetGaussianFiring.m and @Network/ComputeEstimatedRates.m:
      EstimatedRates = GetGaussianFiring(Spikes, 50, 1000)
    """
    sigma_samples = sigma_ms / dt_ms
    # 1D Gaussian filter along time axis (axis 0)
    smoothed = ndi.gaussian_filter1d(spikes.astype(np.float64), sigma=sigma_samples, axis=0) * (1000.0 / dt_ms)
    return smoothed


def compute_channel_phase_lags(
    channel_rates: np.ndarray,
    dt_ms: float = 1.0,
    t_start_ms: int = 0
) -> Dict[str, Any]:
    """
    Computes cross-channel phase progression and phase lags along the probe shank,
    demonstrating sequential traveling wave activation.
    """
    start_idx = int(t_start_ms / dt_ms)
    if start_idx >= channel_rates.shape[0] - 100:
        start_idx = 0
    steady_rates = channel_rates[start_idx:, :]
    T, K = steady_rates.shape

    # Find active channels
    ch_stds = np.std(steady_rates, axis=0)
    active_channels = np.where(ch_stds > 0.01 * np.max(ch_stds))[0]

    if len(active_channels) == 0:
        return {
            'phase_lags_deg': np.zeros(K),
            'phase_lags_rad': np.zeros(K),
            'active_channels': active_channels,
            'cycle_period_ms': 500.0
        }

    # Reference channel (most active channel)
    ref_ch = active_channels[np.argmax(ch_stds[active_channels])]
    ref_signal = steady_rates[:, ref_ch] - np.mean(steady_rates[:, ref_ch])

    # Find cycle period from autocorrelation of reference signal
    autocorr = np.correlate(ref_signal, ref_signal, mode='full')
    lags = np.arange(-T + 1, T) * dt_ms
    center_idx = len(lags) // 2
    pos_autocorr = autocorr[center_idx:]

    peaks, _ = find_peaks(pos_autocorr, distance=int(150 / dt_ms))
    if len(peaks) > 1:
        cycle_period_ms = float(np.mean(np.diff(peaks)) * dt_ms)
    else:
        cycle_period_ms = 400.0

    phase_lags_rad = np.zeros(K)
    for ch in range(K):
        sig = steady_rates[:, ch] - np.mean(steady_rates[:, ch])
        if np.std(sig) > 1e-6:
            xcorr = np.correlate(ref_signal, sig, mode='full')
            best_lag_idx = np.argmax(xcorr)
            best_lag_ms = (best_lag_idx - (T - 1)) * dt_ms
            phase = (best_lag_ms / cycle_period_ms) * 2.0 * np.pi
            phase_lags_rad[ch] = phase % (2.0 * np.pi)
        else:
            phase_lags_rad[ch] = 0.0

    phase_lags_deg = np.degrees(phase_lags_rad)

    return {
        'phase_lags_deg': phase_lags_deg,
        'phase_lags_rad': phase_lags_rad,
        'active_channels': active_channels,
        'ref_channel': int(ref_ch),
        'cycle_period_ms': float(cycle_period_ms)
    }
