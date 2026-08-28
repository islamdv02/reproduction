"""
Model K-Y: Komi Recurrent Balanced Projectome Model Applied to Yakovenko Cat Anatomy.
Generates spontaneous rhythmic rate dynamics, spatiotemporal slice activity, and center-of-activity trajectory r_cm,KY(t).
"""

from typing import Tuple, Dict, Optional
import numpy as np
from scipy import signal

# Re-use core mathematical modules from yakovenko_2002_komi_framework
import sys, os
yk_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_komi_framework', 'src'))
if yk_src not in sys.path:
    sys.path.insert(0, yk_src)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics, compound_tanh
from phase_analysis import PhaseUnfolder
from projectome_analysis import ProjectomeAnalyzer
from traveling_wave import TravelingWaveAnalyzer


class ModelKY:
    """
    Implements Komi et al. (2026) generative recurrent network in cat lumbosacral anatomy:
    tau * dR/dt = -R + f(W @ R + I_tonic + noise)
    """

    def __init__(
        self,
        n_neurons: int = 1000,
        rng_seed: int = 42,
        duration_ms: float = 2500.0,
        warmup_ms: float = 500.0,
        balance_ei: bool = True
    ):
        self.n_neurons = int(n_neurons)
        self.rng_seed = int(rng_seed)
        self.duration_ms = float(duration_ms)
        self.warmup_ms = float(warmup_ms)
        self.balance_ei = bool(balance_ei)

        # 1. 3D Spatial Network
        self.network = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        self.n_slices = self.network.n_slices
        self.slice_thickness_mm = self.network.slice_thickness

        # 2. Connectome & Zero-Sum E/I Balancing
        self.connectome = CatSynapticConnectome(self.network, balance_ei=self.balance_ei, rng_seed=self.rng_seed)

        # 3. Recurrent Rate Dynamics
        self.dynamics = RecurrentRateDynamics(self.connectome, rng_seed=self.rng_seed)
        self.times_ms, self.rates, self.currents = self.dynamics.simulate(
            duration_ms=self.duration_ms, warmup_ms=self.warmup_ms
        )

        # 4. Phase Analysis & Limit Cycle
        self.phase_unfolder = PhaseUnfolder(self.rates, self.times_ms)

        # 5. Projectome Analysis
        self.projectome = ProjectomeAnalyzer(self.connectome)

        # 6. Spatiotemporal Traveling Wave & Grid
        self.wave = TravelingWaveAnalyzer(self.network, self.rates, self.times_ms)
        self.grid = self.wave.grid # (30 slices x n_steps)

        # 7. Emergent Center of Activity Trajectory r_cm,KY(t)
        self._compute_center_of_activity()

    def _compute_center_of_activity(self):
        """Computes emergent center of activity in levels (0..100) and in mm (0..28.8)."""
        n_bins = self.grid.shape[1]
        self.r_cm_level = np.zeros(n_bins, dtype=np.float64)
        self.r_cm_mm = np.zeros(n_bins, dtype=np.float64)
        self.velocity_mm_s = np.zeros(n_bins, dtype=np.float64)

        slice_levels = np.linspace(1.67, 98.33, self.n_slices)
        slice_mms = (np.arange(self.n_slices) + 0.5) * self.slice_thickness_mm

        for t in range(n_bins):
            total_act = np.sum(self.grid[:, t])
            if total_act > 1e-9:
                self.r_cm_level[t] = np.sum(self.grid[:, t] * slice_levels) / total_act
                self.r_cm_mm[t] = np.sum(self.grid[:, t] * slice_mms) / total_act
            else:
                self.r_cm_level[t] = 50.0
                self.r_cm_mm[t] = 14.4

        # Migration velocity of center of activity
        dt_s = (self.times_ms[1] - self.times_ms[0]) / 1000.0 if len(self.times_ms) > 1 else 0.001
        dr = np.gradient(self.r_cm_mm, dt_s)
        self.velocity_mm_s = np.abs(dr)
