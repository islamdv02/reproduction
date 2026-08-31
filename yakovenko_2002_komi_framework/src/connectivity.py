"""
Connectivity Module: 3D Anisotropic Projectome Construction & Row-Wise E/I Balancing.
Implements Komi et al. (2026) multi-subpopulation Mexican-hat spatial kernels,
symmetric row-wise zero-sum balance, and real-part spectral rescaling on Yakovenko cat anatomy.
"""

from typing import Tuple, Optional, List, Dict
import numpy as np
from spatial_mapping import YakovenkoKomiSpatialNetwork
from oscillation_gate import print_eigenvalue_diagnostics


class CatSynapticConnectome:
    """
    Constructs the 3D anisotropic synaptic matrix W with Mexican-hat spatial kernels,
    exact symmetric row-wise zero-sum E/I balancing, and real-part spectral rescaling.
    """

    def __init__(
        self,
        network: YakovenkoKomiSpatialNetwork,
        baseline_prob: float = 0.25,
        spectral_radius: float = 2.0,
        balance_ei: bool = True,
        rng_seed: int = 42,
        periodic_z: bool = True
    ):
        self.network = network
        self.baseline_prob = float(baseline_prob)
        # spectral_radius parameter acts as target max Re(lambda)
        self.spectral_radius = float(spectral_radius)
        self.balance_ei = bool(balance_ei)
        self.periodic_z = bool(periodic_z)
        self.rng_seed = int(rng_seed)
        self.rng = np.random.default_rng(rng_seed)

        self._build_connectome()

    def _build_connectome(self):
        """Constructs 3D probability matrix, samples Bernoulli synapses, balances rows, and rescales."""
        N = self.network.n_neurons
        x, y, z = self.network.x, self.network.y, self.network.z

        # 1. Pairwise Distances
        dx = x[:, None] - x[None, :] # Post (i) - Pre (j)
        dy = y[:, None] - y[None, :]
        dz = z[:, None] - z[None, :]

        # Cord length
        L_z = float(np.max(z) - np.min(z)) if (np.max(z) - np.min(z)) > 1.0 else 28.8
        if self.periodic_z:
            dz_eff = (dz + L_z / 2.0) % L_z - L_z / 2.0
        else:
            dz_eff = dz

        # 2. 5-Subpopulation Mexican-Hat Kernel Parameters (scaled from Komi Fig 1 to cat cord length)
        scale = L_z / 5.0
        pop_defs = [
            {'name': 'sp1', 'is_exc': True,  'mu': 0.20 * scale * 1.8, 'sigma': 0.15 * scale},
            {'name': 'sp2', 'is_exc': False, 'mu': 0.60 * scale * 1.8, 'sigma': 0.25 * scale},
            {'name': 'sp3', 'is_exc': True,  'mu': 1.20 * scale * 1.8, 'sigma': 0.35 * scale},
            {'name': 'sp4', 'is_exc': False, 'mu': 2.00 * scale * 1.8, 'sigma': 0.45 * scale},
            {'name': 'sp5', 'is_exc': True,  'mu': 3.00 * scale * 1.8, 'sigma': 0.60 * scale},
        ]
        n_pops = len(pop_defs)
        pop_idx = np.arange(N) % n_pops
        self.neuron_pops = [pop_defs[idx] for idx in pop_idx]
        self.is_excitatory = np.array([p['is_exc'] for p in self.neuron_pops])
        self.transmitter = np.where(self.is_excitatory, 1.0, -1.0)
        self.network.is_excitatory = self.is_excitatory
        self.network.transmitter = self.transmitter

        # Transverse spatial dispersions
        sigma_xy = 3.0

        # 3. Construct Synaptic Matrix W
        mus = np.array([p['mu'] for p in pop_defs])
        sigs = np.array([p['sigma'] for p in pop_defs])
        mu_j = mus[pop_idx]
        sig_j = sigs[pop_idx]

        arg_z = ((dz_eff - mu_j[None, :]) ** 2) / (2.0 * sig_j[None, :] ** 2)
        arg_xy = (dx ** 2 + dy ** 2) / (2.0 * sigma_xy ** 2)
        P = self.baseline_prob * np.exp(-(arg_xy + arg_z))
        np.fill_diagonal(P, 0.0)
        P = np.clip(P, 0.0, 1.0)

        adj = (self.rng.random((N, N)) < P).astype(np.float64)
        weights = self.rng.normal(1.0, 0.1, size=(N, N))
        weights = np.clip(weights, 0.05, None)

        W = np.zeros((N, N), dtype=np.float64)
        for j in range(N):
            W[:, j] = adj[:, j] * weights[:, j] * self.transmitter[j]

        np.fill_diagonal(W, 0.0)

        # 4. Row-Wise Zero-Sum E/I Balancing (BergLab BalanceConnectivity.m)
        if self.balance_ei:
            W_bal = np.copy(W)
            for i in range(N):
                row = W_bal[i, :]
                pos_mask = row > 0
                neg_mask = row < 0
                sum_pos = np.sum(row[pos_mask])
                sum_neg = np.sum(row[neg_mask])
                total_sum = sum_pos + sum_neg
                if sum_pos > 0 and sum_neg < 0:
                    f_pos = (sum_pos - total_sum / 2.0) / sum_pos
                    f_neg = (sum_neg - total_sum / 2.0) / sum_neg
                    W_bal[i, pos_mask] *= f_pos
                    W_bal[i, neg_mask] *= f_neg
                else:
                    W_bal[i, :] = 0.0
            self.W = W_bal
        else:
            self.W = W

        # 5. Spectral Rescaling by Dominant Real Part max Re(lambda)
        try:
            eigenvalues = np.linalg.eigvals(self.W)
            dom_idx = np.argmax(eigenvalues.real)
            max_re = eigenvalues[dom_idx].real
            if max_re > 1e-6:
                self.W = (self.W / max_re) * self.spectral_radius
        except Exception:
            pass

        # Clean near-zero numerical noise and negative zeros
        self.W[np.abs(self.W) < 1e-15] = 0.0

        # Diagnostic metrics and logging
        self.row_sums = np.sum(self.W, axis=1)
        self.mean_row_sum = float(np.mean(self.row_sums))
        self.max_abs_row_sum = float(np.max(np.abs(self.row_sums)))
        self.density = float(np.count_nonzero(self.W) / (N * N))

        self.max_re, self.im_dom, self.spectral_radius_actual = print_eigenvalue_diagnostics(
            self.W, name=f"CatSynapticConnectome(N={N}, seed={self.rng_seed})"
        )
