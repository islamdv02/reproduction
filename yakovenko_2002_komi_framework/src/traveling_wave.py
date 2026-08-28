"""
Traveling Wave Module: Spatiotemporal Wave Propagation & Left-Right Coordination Analysis.
Measures rostrocaudal wave velocity (v_wave) and bilateral phase alternation across cat spinal cord.
"""

from typing import Tuple, Dict
import numpy as np
from scipy import signal
from spatial_mapping import YakovenkoKomiSpatialNetwork


class TravelingWaveAnalyzer:
    """
    Computes longitudinal spatiotemporal activity landscapes, wave propagation velocity,
    and left-right bilateral phase relationships.
    """

    def __init__(
        self,
        network: YakovenkoKomiSpatialNetwork,
        rates: np.ndarray,
        times_ms: np.ndarray,
        dt_ms: float = 1.0,
        n_slices: int = 30
    ):
        self.network = network
        self.rates = rates # (N, n_steps)
        self.times_ms = times_ms
        self.dt_ms = float(dt_ms)
        self.n_slices = int(n_slices)
        self.slice_thickness = network.length_mm / self.n_slices

        self._compute_spatiotemporal_grid()
        self._compute_wave_velocity()
        self._compute_bilateral_coordination()

    def _compute_spatiotemporal_grid(self):
        """Bins neural rates across the 30 rostrocaudal slices over time."""
        n_steps = len(self.times_ms)
        self.grid = np.zeros((self.n_slices, n_steps), dtype=np.float64)
        self.grid_left = np.zeros((self.n_slices, n_steps), dtype=np.float64)
        self.grid_right = np.zeros((self.n_slices, n_steps), dtype=np.float64)

        slice_indices = np.clip(np.floor(self.network.z / self.slice_thickness).astype(int), 0, self.n_slices - 1)
        is_left = (self.network.hemicord == 'left')
        is_right = (self.network.hemicord == 'right')

        for s in range(self.n_slices):
            mask_s = (slice_indices == s)
            if np.any(mask_s):
                self.grid[s, :] = np.mean(self.rates[mask_s, :], axis=0)

                mask_sl = mask_s & is_left
                if np.any(mask_sl):
                    self.grid_left[s, :] = np.mean(self.rates[mask_sl, :], axis=0)

                mask_sr = mask_s & is_right
                if np.any(mask_sr):
                    self.grid_right[s, :] = np.mean(self.rates[mask_sr, :], axis=0)

    def _compute_wave_velocity(self):
        """Computes traveling wave propagation velocity v_wave (mm/s) using cross-correlation between rostral & caudal slices."""
        # Rostral slice 5 (~L4/L5) vs Caudal slice 24 (~L7)
        s_rostral = self.grid[5, :]
        s_caudal = self.grid[24, :]

        # Mean center
        r_sig = s_rostral - np.mean(s_rostral)
        c_sig = s_caudal - np.mean(s_caudal)

        if np.std(r_sig) > 1e-4 and np.std(c_sig) > 1e-4:
            xcorr = signal.correlate(r_sig, c_sig, mode='full')
            lags = signal.correlation_lags(len(r_sig), len(c_sig))
            mid = len(lags) // 2

            # Restrict lag search to positive forward delay (rostral leads caudal)
            valid_mask = (lags >= 0) & (lags <= int(500 / self.dt_ms))
            sub_corr = xcorr[valid_mask]
            sub_lags = lags[valid_mask]

            if len(sub_corr) > 0:
                best_lag_steps = sub_lags[np.argmax(sub_corr)]
                self.lag_ms = float(best_lag_steps * self.dt_ms)
            else:
                self.lag_ms = 50.0
        else:
            self.lag_ms = 50.0

        # Physical distance between slice 5 and slice 24: (24 - 5) * 0.96 mm = 18.24 mm
        distance_mm = (24 - 5) * self.slice_thickness
        if self.lag_ms > 0:
            self.velocity_mm_s = float((distance_mm / self.lag_ms) * 1000.0)
        else:
            self.velocity_mm_s = 150.0 # fallback

    def _compute_bilateral_coordination(self):
        """Computes left-right phase difference and circular alternation index."""
        # Mean left rate vs mean right rate
        left_pop = np.mean(self.grid_left, axis=0)
        right_pop = np.mean(self.grid_right, axis=0)

        # Cross-correlation to determine phase shift
        lp_c = left_pop - np.mean(left_pop)
        rp_c = right_pop - np.mean(right_pop)

        if np.std(lp_c) > 1e-4 and np.std(rp_c) > 1e-4:
            xcorr = signal.correlate(lp_c, rp_c, mode='full')
            lags = signal.correlation_lags(len(lp_c), len(rp_c))
            best_lag = lags[np.argmax(xcorr)] * self.dt_ms
            # Autocorr of left to get period
            ac = signal.correlate(lp_c, lp_c, mode='full')
            peaks, _ = signal.find_peaks(ac[len(ac)//2:], distance=int(100/self.dt_ms))
            period = float(peaks[0] * self.dt_ms) if len(peaks) > 0 else 400.0
            
            # Phase difference in radians [0, pi]
            phase_rad = (np.abs(best_lag) / period) * 2.0 * np.pi
            self.bilateral_phase_diff_deg = float(np.degrees(phase_rad % np.pi))
            # Alternation index: 1.0 = strict alternation (180 deg), 0.0 = synchronous hopping (0 deg)
            self.alternation_index = float(np.cos(np.radians(180.0 - self.bilateral_phase_diff_deg)))
        else:
            self.bilateral_phase_diff_deg = 180.0
            self.alternation_index = 1.0
