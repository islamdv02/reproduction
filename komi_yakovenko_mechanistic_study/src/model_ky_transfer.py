"""
Model KY-Transfer Module: Strict Untuned Transfer of Komi et al. (2026) Dynamics to Yakovenko et al. (2002) Cat Anatomy.
Integrates recurrent balanced rate dynamics across 3D cat lumbosacral coordinates (28.8 mm)
and projects active drives to motoneuron pools.
"""

from typing import Tuple, Dict, Optional
import numpy as np
from scipy import signal

import sys, os
base_yk = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_reproduction', 'src'))
yk_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_komi_framework', 'src'))

for p in [base_yk, yk_src]:
    if p not in sys.path:
        sys.path.insert(0, p)

from anatomy import CatLumbosacralAnatomy, MUSCLE_NAMES, MUSCLE_CATEGORIES
from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder
from traveling_wave import TravelingWaveAnalyzer
from projectome_audit import ProjectomeAuditor


class ModelKY_Transfer:
    """
    Model KY-Transfer:
    Applies Komi equations:
      tau * dR/dt = -R + f_max * tanh( max(0, W @ R + I_tonic + noise) / f_max )
    to Cat Lumbosacral Anatomy (L4-S1, 30 slices, 28.8 mm).
    """

    def __init__(
        self,
        n_neurons: int = 800,
        rng_seed: int = 42,
        duration_ms: float = 2400.0,
        warmup_ms: float = 400.0,
        balance_ei: bool = True,
        spectral_radius: float = 1.25,
        mu_z_exc: float = 3.5,
        sigma_z_exc: float = 6.0,
        sigma_z_inh: float = 2.5,
        tau_ms: float = 20.0,
        tonic_drive_pA: float = 15.0
    ):
        self.n_neurons = int(n_neurons)
        self.rng_seed = int(rng_seed)
        self.duration_ms = float(duration_ms)
        self.warmup_ms = float(warmup_ms)
        self.balance_ei = bool(balance_ei)
        self.spectral_radius = float(spectral_radius)
        self.mu_z_exc = float(mu_z_exc)
        self.sigma_z_exc = float(sigma_z_exc)
        self.sigma_z_inh = float(sigma_z_inh)
        self.tau_ms = float(tau_ms)
        self.tonic_drive_pA = float(tonic_drive_pA)

        # 1. 3D Spatial Network in Cat Anatomy
        self.network = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        self.n_slices = self.network.n_slices
        self.slice_thickness_mm = self.network.slice_thickness

        # 2. Custom Connectome with specific parameters
        self._build_custom_connectome()

        # 3. Recurrent Rate Dynamics
        self.dynamics = RecurrentRateDynamics(
            self.connectome,
            tau_ms=self.tau_ms,
            tonic_drive_pA=self.tonic_drive_pA,
            rng_seed=self.rng_seed
        )
        self.times_ms, self.rates, self.currents = self.dynamics.simulate(
            duration_ms=self.duration_ms, warmup_ms=self.warmup_ms
        )

        # 4. Phase Analysis & SVD Limit Cycle
        self.phase_unfolder = PhaseUnfolder(self.rates, self.times_ms)

        # 5. Projectome Audit (Fixed Non-Saturating Metrics & Raw Profile)
        self.projectome = ProjectomeAuditor(self.connectome.W, self.network.z, n_bins=51, max_dist_mm=20.0)

        # 6. Spatiotemporal Traveling Wave Grid across 30 Slices
        self.wave = TravelingWaveAnalyzer(self.network, self.rates, self.times_ms)
        self.grid = self.wave.grid # (30 slices x n_steps)

        # 7. Motor Pool Somatotopic Output Drive
        self.anatomy = CatLumbosacralAnatomy()
        self._compute_motoneuron_output_and_rcm()

    def _build_custom_connectome(self):
        """Constructs connectome with parametric longitudinal kernel reach."""
        self.connectome = CatSynapticConnectome(
            self.network,
            spectral_radius=self.spectral_radius,
            balance_ei=self.balance_ei,
            rng_seed=self.rng_seed
        )
        # Apply custom mu_z and sigma_z if specified
        N = self.network.n_neurons
        x, y, z = self.network.x, self.network.y, self.network.z
        is_exc = self.network.is_excitatory
        is_comm = self.network.is_commissural
        hemicord = self.network.hemicord

        dx = x[:, None] - x[None, :]
        dy = y[:, None] - y[None, :]
        dz = z[:, None] - z[None, :]

        mu_z = np.zeros(N)
        sigma_z = np.zeros(N)
        for j in range(N):
            if is_comm[j]:
                mu_z[j] = 0.0
                sigma_z[j] = 4.5
            elif is_exc[j]:
                mu_z[j] = self.mu_z_exc
                sigma_z[j] = self.sigma_z_exc
            else:
                mu_z[j] = -1.2
                sigma_z[j] = self.sigma_z_inh

        arg_x = (dx ** 2) / (2.0 * 1.0 ** 2)
        arg_y = (dy ** 2) / (2.0 * 1.0 ** 2)
        arg_z = ((dz - mu_z[None, :]) ** 2) / (2.0 * sigma_z[None, :] ** 2)
        P = 0.12 * np.exp(-(arg_x + arg_y + arg_z))

        is_contra_pair = (hemicord[:, None] != hemicord[None, :])
        for j in range(N):
            if is_comm[j]:
                P[:, j] *= np.where(is_contra_pair[:, j], 1.2, 0.05)
            else:
                P[:, j] *= np.where(~is_contra_pair[:, j], 1.0, 0.0)

        np.fill_diagonal(P, 0.0)
        P = np.clip(P, 0.0, 1.0)

        adj = (self.connectome.rng.random((N, N)) < P).astype(np.float64)
        w_raw = np.zeros((N, N), dtype=np.float64)
        for j in range(N):
            if is_exc[j]:
                w_raw[:, j] = adj[:, j] * self.connectome.rng.uniform(0.5, 1.5, N)
            else:
                w_raw[:, j] = -adj[:, j] * self.connectome.rng.uniform(0.5, 1.5, N)

        if self.balance_ei:
            W_bal = np.copy(w_raw)
            for i in range(N):
                row_exc = np.sum(W_bal[i, W_bal[i, :] > 0])
                row_inh = np.sum(np.abs(W_bal[i, W_bal[i, :] < 0]))
                if row_inh > 1e-9 and row_exc > 1e-9:
                    W_bal[i, W_bal[i, :] < 0] *= (row_exc / row_inh)
                elif row_exc > 0 and row_inh == 0:
                    W_bal[i, :] *= 0.1
            self.connectome.W = W_bal
        else:
            self.connectome.W = w_raw

        try:
            eigenvalues = np.linalg.eigvals(self.connectome.W)
            max_eig = np.max(np.abs(eigenvalues))
            if max_eig > 1e-6:
                self.connectome.W = (self.connectome.W / max_eig) * self.spectral_radius
        except Exception:
            pass

    def _compute_motoneuron_output_and_rcm(self):
        """Maps interneuronal rate grid (30 x n_steps) to motor pools and computes r_cm(t)."""
        n_bins = self.grid.shape[1]
        self.r_cm_level = np.zeros(n_bins, dtype=np.float64)
        self.r_cm_mm = np.zeros(n_bins, dtype=np.float64)
        self.velocity_mm_s = np.zeros(n_bins, dtype=np.float64)

        slice_levels = self.anatomy.slice_centers_level
        slice_mms = self.anatomy.slice_centers_mm

        # Weight slice activity by total MN density across slices
        mn_slice_weights = np.sum(self.anatomy.slice_matrix, axis=0) # (30,)
        norm_mn_weights = mn_slice_weights / (np.mean(mn_slice_weights) + 1e-9)

        # Motoneuron weighted grid
        self.mn_weighted_grid = self.grid * norm_mn_weights[:, None]

        for t in range(n_bins):
            total_act = np.sum(self.mn_weighted_grid[:, t])
            if total_act > 1e-9:
                self.r_cm_level[t] = np.sum(self.mn_weighted_grid[:, t] * slice_levels) / total_act
                self.r_cm_mm[t] = np.sum(self.mn_weighted_grid[:, t] * slice_mms) / total_act
            else:
                self.r_cm_level[t] = 50.0
                self.r_cm_mm[t] = 14.4

        dt_s = (self.times_ms[1] - self.times_ms[0]) / 1000.0 if len(self.times_ms) > 1 else 0.001
        dr = np.gradient(self.r_cm_mm, dt_s)
        self.velocity_mm_s = np.abs(dr)
