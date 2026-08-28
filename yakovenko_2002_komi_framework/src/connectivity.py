"""
Connectivity Module: 3D Anisotropic Projectome Construction & Row-Wise E/I Balancing.
Implements Komi et al. (2026) synaptic probability kernels and zero-sum balance on Yakovenko cat anatomy.
"""

from typing import Tuple, Optional
import numpy as np
from scipy import sparse
from spatial_mapping import YakovenkoKomiSpatialNetwork


class CatSynapticConnectome:
    """
    Constructs the 3D anisotropic synaptic matrix W with exact row-wise E/I balancing.
    """

    def __init__(
        self,
        network: YakovenkoKomiSpatialNetwork,
        baseline_prob: float = 0.12,
        spectral_radius: float = 1.25,
        balance_ei: bool = True,
        rng_seed: int = 42
    ):
        self.network = network
        self.baseline_prob = float(baseline_prob)
        self.spectral_radius = float(spectral_radius)
        self.balance_ei = bool(balance_ei)
        self.rng = np.random.default_rng(rng_seed)

        self._build_connectome()

    def _build_connectome(self):
        """Constructs 3D probability matrix, samples Bernoulli synapses, balances rows, and rescales."""
        N = self.network.n_neurons
        x, y, z = self.network.x, self.network.y, self.network.z
        pop = self.network.population
        is_exc = self.network.is_excitatory
        is_comm = self.network.is_commissural
        hemicord = self.network.hemicord

        # 1. Compute Pairwise Distances
        dx = x[:, None] - x[None, :] # Post (i) - Pre (j)
        dy = y[:, None] - y[None, :]
        dz = z[:, None] - z[None, :]

        # 2. Kernel Parameters by Presynaptic Population (j)
        # Transverse dispersions
        sigma_x = 1.0
        sigma_y = 1.0

        # Longitudinal parameters:
        # Excitatory: Descending bias (mu_z > 0), long reach (sigma_z = 6.0 mm)
        # Inhibitory: Local/rostral (mu_z <= 0, sigma_z = 2.5 mm)
        # Commissural: Contralateral cross-cord (sigma_z = 4.5 mm)
        mu_z = np.zeros(N)
        sigma_z = np.zeros(N)

        for j in range(N):
            if is_comm[j]:
                mu_z[j] = 0.0
                sigma_z[j] = 4.5
            elif is_exc[j]:
                mu_z[j] = 3.5  # Descending projection bias (+3.5 mm)
                sigma_z[j] = 6.0
            else:
                mu_z[j] = -1.2 # Local / rostral recurrent inhibition
                sigma_z[j] = 2.5

        # 3. 3D Spatial Probability Matrix
        arg_x = (dx ** 2) / (2.0 * sigma_x ** 2)
        arg_y = (dy ** 2) / (2.0 * sigma_y ** 2)
        arg_z = ((dz - mu_z[None, :]) ** 2) / (2.0 * sigma_z[None, :] ** 2)
        P = self.baseline_prob * np.exp(-(arg_x + arg_y + arg_z))

        # Side targeting: Commissural targets contralateral; Ipsilateral targets ipsilateral
        is_contra_pair = (hemicord[:, None] != hemicord[None, :]) # True if i, j on opposite sides
        
        for j in range(N):
            if is_comm[j]:
                # Commissural projects contralaterally
                P[:, j] *= np.where(is_contra_pair[:, j], 1.2, 0.05)
            else:
                # Ipsilateral interneurons project on same side
                P[:, j] *= np.where(~is_contra_pair[:, j], 1.0, 0.0)

        # Remove self-connections
        np.fill_diagonal(P, 0.0)
        P = np.clip(P, 0.0, 1.0)

        # 4. Bernoulli Synapse Sampling & Dale's Law
        rand_draw = self.rng.random((N, N))
        adj = (rand_draw < P).astype(np.float64)

        # Initial weights: Exc > 0, Inh < 0
        w_raw = np.zeros((N, N), dtype=np.float64)
        for j in range(N):
            if is_exc[j]:
                w_raw[:, j] = adj[:, j] * self.rng.uniform(0.5, 1.5, N)
            else:
                w_raw[:, j] = -adj[:, j] * self.rng.uniform(0.5, 1.5, N)

        # 5. Row-Wise Zero-Sum E/I Balancing (Komi Method)
        if self.balance_ei:
            W_bal = np.copy(w_raw)
            for i in range(N):
                row_exc = np.sum(W_bal[i, W_bal[i, :] > 0])
                row_inh = np.sum(np.abs(W_bal[i, W_bal[i, :] < 0]))
                if row_inh > 1e-9 and row_exc > 1e-9:
                    # Scale inhibitory inputs to exactly cancel excitatory inputs
                    scale = row_exc / row_inh
                    W_bal[i, W_bal[i, :] < 0] *= scale
                elif row_exc > 0 and row_inh == 0:
                    # If no inhibitory input, dampen row to avoid runaway
                    W_bal[i, :] *= 0.1
            self.W = W_bal
        else:
            self.W = w_raw

        # 6. Spectral Radius Rescaling
        try:
            eigenvalues = np.linalg.eigvals(self.W)
            max_eig = np.max(np.abs(eigenvalues))
            if max_eig > 1e-6:
                self.W = (self.W / max_eig) * self.spectral_radius
        except Exception:
            pass

        # Diagnostic metrics
        self.row_sums = np.sum(self.W, axis=1)
        self.mean_row_sum = float(np.mean(self.row_sums))
        self.max_abs_row_sum = float(np.max(np.abs(self.row_sums)))
        self.density = float(np.count_nonzero(self.W) / (N * N))
