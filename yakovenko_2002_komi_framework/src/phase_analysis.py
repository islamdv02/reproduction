"""
Phase Analysis Module: PCA Decomposition, Cross-Correlation Phase Sorting & Limit Cycle Metrics.
Implements Komi et al. (2026) functional phase unfolding on simulated cat neural activity.
"""

from typing import Tuple, Dict
import numpy as np
from scipy import signal


class PhaseUnfolder:
    """
    Computes PCA projection, cross-correlation peak lags, and functional phase angles theta_i.
    """

    def __init__(self, rates: np.ndarray, times_ms: np.ndarray, dt_ms: float = 1.0):
        self.rates = rates # (N, n_steps)
        self.times_ms = times_ms
        self.dt_ms = float(dt_ms)
        self.N, self.n_steps = rates.shape

        self._compute_pca()
        self._compute_phases()

    def _compute_pca(self):
        """Performs PCA via SVD on centered rate timeseries."""
        # Mean center rates
        self.rates_mean = np.mean(self.rates, axis=1, keepdims=True)
        R_centered = self.rates - self.rates_mean

        # SVD on (N x n_steps)
        U, S, Vt = np.linalg.svd(R_centered, full_matrices=False)
        self.components = U[:, :3] # Top 3 spatial components
        self.projections = np.diag(S[:3]) @ Vt[:3, :] # (3, n_steps) time trajectories

        # Variance explained
        var_total = np.sum(S ** 2)
        self.explained_var = (S[:3] ** 2) / var_total
        self.planar_variance = float(self.explained_var[0] + self.explained_var[1])

        # PC1, PC2 trajectories
        self.pc1 = self.projections[0, :]
        self.pc2 = self.projections[1, :]

        # Limit cycle orbit radius
        self.orbit_radius = float(np.mean(np.sqrt(self.pc1 ** 2 + self.pc2 ** 2)))

        # Estimate dominant cycle period T_cycle from PC1 autocorrelation
        autocorr = signal.correlate(self.pc1, self.pc1, mode='full')
        lags = signal.correlation_lags(len(self.pc1), len(self.pc1))
        mid = len(autocorr) // 2
        peaks, _ = signal.find_peaks(autocorr[mid:], distance=int(100 / self.dt_ms))
        if len(peaks) > 0:
            self.cycle_period_ms = float(peaks[0] * self.dt_ms)
            self.frequency_hz = float(1000.0 / self.cycle_period_ms)
        else:
            self.cycle_period_ms = 400.0
            self.frequency_hz = 2.5

    def _compute_phases(self):
        """Derives functional firing phase theta_i in [0, 2*pi) via cross-correlation with PC1."""
        self.phase_angles = np.zeros(self.N, dtype=np.float64)
        self.peak_lags_ms = np.zeros(self.N, dtype=np.float64)

        max_lag_steps = int(np.round(self.cycle_period_ms / self.dt_ms))

        for i in range(self.N):
            r_i = self.rates[i, :] - np.mean(self.rates[i, :])
            if np.std(r_i) > 1e-6:
                xcorr = signal.correlate(self.pc1, r_i, mode='full')
                lags = signal.correlation_lags(len(self.pc1), len(r_i))
                valid_mask = np.abs(lags) <= max_lag_steps
                sub_corr = xcorr[valid_mask]
                sub_lags = lags[valid_mask]
                best_lag = sub_lags[np.argmax(sub_corr)] * self.dt_ms
                self.peak_lags_ms[i] = best_lag

                # Convert to circular phase [0, 2*pi)
                phi = (best_lag / self.cycle_period_ms) * 2.0 * np.pi
                self.phase_angles[i] = phi % (2.0 * np.pi)
            else:
                self.phase_angles[i] = 0.0

        # Phase sorting permutation
        self.phase_sorted_indices = np.argsort(self.phase_angles)
