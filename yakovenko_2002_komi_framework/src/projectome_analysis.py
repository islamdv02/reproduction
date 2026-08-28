"""
Projectome Analysis Module: Net 1D Spatial Interaction Profile & Mexican-Hat Metrics.
Quantifies local excitation vs surround inhibition and directional asymmetry along the cat spinal cord.
"""

from typing import Tuple, Dict
import numpy as np
from connectivity import CatSynapticConnectome


class ProjectomeAnalyzer:
    """
    Computes 1D net projectome profile Pi(Delta Z) and Mexican-hat metrics from the 3D connectome W.
    """

    def __init__(self, connectome: CatSynapticConnectome, n_bins: int = 51):
        self.connectome = connectome
        self.W = connectome.W
        self.z = connectome.network.z
        self.N = connectome.network.n_neurons
        self.n_bins = int(n_bins)

        self._compute_1d_profile()
        self._compute_mexican_hat_metrics()

    def _compute_1d_profile(self):
        """Computes net average synaptic weight as a function of Delta Z = z_post - z_pre."""
        # Delta Z: Post (i) - Pre (j)
        dz_matrix = self.z[:, None] - self.z[None, :] # (N, N)

        # Distance binning from -20 mm (ascending) to +20 mm (descending)
        max_dist = 20.0
        self.bin_edges = np.linspace(-max_dist, max_dist, self.n_bins + 1)
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
            cnt = np.sum(mask)
            self.count_profile[b] = cnt
            if cnt > 0:
                weights = w_flat[mask]
                self.net_profile[b] = np.mean(weights)
                self.exc_profile[b] = np.mean(np.maximum(0.0, weights))
                self.inh_profile[b] = np.mean(np.minimum(0.0, weights))

    def _compute_mexican_hat_metrics(self):
        """Quantifies local excitation peak, surround inhibition trough, and Mexican-hat index."""
        # Central peak (around Delta Z ~ 0)
        center_mask = np.abs(self.bin_centers) <= 2.5
        surround_mask = (np.abs(self.bin_centers) > 2.5) & (np.abs(self.bin_centers) <= 10.0)

        self.peak_excitation = float(np.max(self.net_profile[center_mask])) if np.any(center_mask) else 0.0
        self.trough_inhibition = float(np.min(self.net_profile[surround_mask])) if np.any(surround_mask) else 0.0

        # Mexican Hat Index: (Peak - Trough) / (Peak + |Trough|)
        denom = self.peak_excitation + np.abs(self.trough_inhibition)
        if denom > 1e-9 and self.peak_excitation > 0 and self.trough_inhibition < 0:
            self.mexican_hat_index = float((self.peak_excitation - self.trough_inhibition) / denom)
            self.is_mexican_hat = True
        else:
            self.mexican_hat_index = 0.0
            self.is_mexican_hat = False

        # Directional Asymmetry Index: Descending (>0) vs Ascending (<0) integral
        desc_mask = self.bin_centers > 0.5
        asc_mask = self.bin_centers < -0.5
        sum_desc = np.sum(self.net_profile[desc_mask])
        sum_asc = np.sum(self.net_profile[asc_mask])
        self.asymmetry_index = float((sum_desc - sum_asc) / (np.abs(sum_desc) + np.abs(sum_asc) + 1e-9))
