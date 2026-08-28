"""
Motor Output Mapping Module: Coupling Recurrent Neural Dynamics to 27 Yakovenko Motor Pools.
Synthesizes simulated multi-muscle EMG envelopes and evaluates cross-correlation/RMSE against empirical profiles.
"""

from typing import Dict, Tuple
import numpy as np
from scipy import signal
from spatial_mapping import YakovenkoKomiSpatialNetwork, MUSCLE_NAMES
from traveling_wave import TravelingWaveAnalyzer

# Import anatomical matrix and EMG profiles from baseline reproduction
import sys, os
base_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_reproduction', 'src'))
if base_src not in sys.path:
    sys.path.insert(0, base_src)
from anatomy import RAW_SLICE_PROFILES
from emg_profiles import build_all_emg_profiles


class MotorOutputMapper:
    """
    Drives 27 Yakovenko hindlimb motor pools from the spatiotemporal activity grid A(s, t).
    """

    def __init__(self, wave_analyzer: TravelingWaveAnalyzer):
        self.wave_analyzer = wave_analyzer
        self.grid = wave_analyzer.grid # (30 slices, n_steps)
        self.times_ms = wave_analyzer.times_ms
        self.empirical_emg = build_all_emg_profiles(fdl_as_retractor=True)

        self._synthesize_motor_outputs()
        self._compare_with_empirical_emg()

    def _synthesize_motor_outputs(self):
        """Projects 30-slice neural activity onto the 27 motor pools using anatomical slice weights."""
        n_muscles = len(MUSCLE_NAMES)
        n_steps = self.grid.shape[1]

        self.simulated_emg = np.zeros((n_muscles, n_steps), dtype=np.float64)

        for m_idx, m in enumerate(MUSCLE_NAMES):
            weights = np.array(RAW_SLICE_PROFILES[m], dtype=np.float64)
            tot_w = np.sum(weights)
            if tot_w > 0:
                norm_w = weights / tot_w
                # Linear dot product of slice activity with muscle spatial distribution
                raw_pool_drive = norm_w @ self.grid
                # Normalize simulated EMG envelope to 0-100% peak
                p_max = np.max(raw_pool_drive)
                p_min = np.min(raw_pool_drive)
                if p_max > p_min:
                    self.simulated_emg[m_idx, :] = ((raw_pool_drive - p_min) / (p_max - p_min)) * 100.0
                else:
                    self.simulated_emg[m_idx, :] = 50.0

    def _compare_with_empirical_emg(self):
        """Computes cross-correlation and RMSE between simulated and empirical EMG for all 27 muscles."""
        self.correlations = {}
        self.nrmse = {}

        # Interpolate empirical EMG across full simulation duration
        n_steps = self.grid.shape[1]
        t_cycle = np.linspace(0, 100, 100, endpoint=False)

        # Map simulation times to step cycle percentage [0, 100)
        # Period derived from traveling wave
        period_ms = 400.0
        cycle_pcts = (self.times_ms % period_ms) / period_ms * 100.0

        for m_idx, m in enumerate(MUSCLE_NAMES):
            emp_100 = self.empirical_emg[m]
            emp_interp = np.interp(cycle_pcts, t_cycle, emp_100)
            sim = self.simulated_emg[m_idx, :]

            # Pearson correlation
            s_std = np.std(sim)
            e_std = np.std(emp_interp)
            if s_std > 1e-4 and e_std > 1e-4:
                corr = np.corrcoef(sim, emp_interp)[0, 1]
            else:
                corr = 0.0

            # Normalized RMSE (RMSE / Range)
            rmse = np.sqrt(np.mean((sim - emp_interp) ** 2))
            norm_rmse = rmse / 100.0

            self.correlations[m] = float(corr)
            self.nrmse[m] = float(norm_rmse)

        self.mean_correlation = float(np.mean(list(self.correlations.values())))
        self.mean_nrmse = float(np.mean(list(self.nrmse.values())))
