"""
Projectome Audit Module: Mathematically Rigorous Net 1D Spatial Interaction Profile & Mexican-Hat Metrics.

Audits the previous MHI bug and implements corrected, non-saturating metrics:
1. Raw 1D net synaptic interaction profile Pi(Delta Z)
2. Normalized Peak-to-Trough Contrast (MHC)
3. Excitatory-to-Inhibitory Area Ratio (MHR_area)
4. Full distance binning across -20 mm to +20 mm with count tracking
"""

from typing import Tuple, Dict, Optional
import numpy as np


class ProjectomeAuditor:
    """
    Computes 1D net projectome profile Pi(Delta Z) and corrected Mexican-hat metrics.
    Avoids mathematical trivialities and tracks raw profiles.
    """

    def __init__(self, W: np.ndarray, z_coords: np.ndarray, n_bins: int = 51, max_dist_mm: float = 20.0):
        self.W = np.asarray(W, dtype=np.float64)
        self.z = np.asarray(z_coords, dtype=np.float64)
        self.N = len(self.z)
        self.n_bins = int(n_bins)
        self.max_dist_mm = float(max_dist_mm)

        self._compute_1d_profile()
        self._compute_corrected_metrics()

    def _compute_1d_profile(self):
        """Computes average synaptic weight as a function of Delta Z = z_post - z_pre."""
        dz_matrix = self.z[:, None] - self.z[None, :] # (N, N): Post (i) - Pre (j)

        self.bin_edges = np.linspace(-self.max_dist_mm, self.max_dist_mm, self.n_bins + 1)
        self.bin_centers = 0.5 * (self.bin_edges[:-1] + self.bin_edges[1:])

        self.net_profile = np.zeros(self.n_bins, dtype=np.float64)
        self.exc_profile = np.zeros(self.n_bins, dtype=np.float64)
        self.inh_profile = np.zeros(self.n_bins, dtype=np.float64)
        self.count_profile = np.zeros(self.n_bins, dtype=np.int64)

        dz_flat = dz_matrix.ravel()
        w_flat = self.W.ravel()

        bin_indices = np.digitize(dz_flat, self.bin_edges) - 1

        for b in range(self.n_bins):
            mask = (bin_indices == b)
            cnt = int(np.sum(mask))
            self.count_profile[b] = cnt
            if cnt > 0:
                weights = w_flat[mask]
                self.net_profile[b] = np.mean(weights)
                self.exc_profile[b] = np.mean(np.maximum(0.0, weights))
                self.inh_profile[b] = np.mean(np.minimum(0.0, weights))

    def _compute_corrected_metrics(self):
        """
        Computes non-saturating metrics:
        1. Peak excitation in central zone (|Delta Z| <= 2.5 mm)
        2. Trough inhibition in surround zone (2.5 < |Delta Z| <= 10.0 mm)
        3. Peak-to-Trough Contrast (MHC) normalized by profile std
        4. Excitatory/Inhibitory Area Ratio (MHR_area)
        5. Directional Asymmetry Index
        """
        center_mask = np.abs(self.bin_centers) <= 2.5
        surround_mask = (np.abs(self.bin_centers) > 2.5) & (np.abs(self.bin_centers) <= 10.0)

        self.peak_excitation = float(np.max(self.net_profile[center_mask])) if np.any(center_mask) else 0.0
        self.trough_inhibition = float(np.min(self.net_profile[surround_mask])) if np.any(surround_mask) else 0.0

        prof_std = float(np.std(self.net_profile))
        self.contrast_mhc = float((self.peak_excitation - self.trough_inhibition) / (prof_std + 1e-9))

        # Area ratio
        bin_width = self.bin_edges[1] - self.bin_edges[0]
        exc_area = float(np.sum(np.maximum(0.0, self.net_profile[center_mask])) * bin_width)
        inh_area = float(np.sum(np.abs(np.minimum(0.0, self.net_profile[surround_mask]))) * bin_width)
        self.area_ratio = float(exc_area / (inh_area + 1e-9))

        # Directional asymmetry: Descending (> 0.5 mm) vs Ascending (< -0.5 mm)
        desc_mask = self.bin_centers > 0.5
        asc_mask = self.bin_centers < -0.5
        sum_desc = float(np.sum(self.net_profile[desc_mask]))
        sum_asc = float(np.sum(self.net_profile[asc_mask]))
        self.asymmetry_index = float((sum_desc - sum_asc) / (np.abs(sum_desc) + np.abs(sum_asc) + 1e-9))

        # Legacy buggy metric for audit comparison
        denom_legacy = self.peak_excitation + np.abs(self.trough_inhibition)
        if denom_legacy > 1e-9 and self.peak_excitation > 0 and self.trough_inhibition < 0:
            self.legacy_buggy_mhi = float((self.peak_excitation - self.trough_inhibition) / denom_legacy)
        else:
            self.legacy_buggy_mhi = 0.0
