"""
Model Y: Yakovenko Feedforward Kinematic Reconstruction Model.
Reconstructs 30-slice motoneuron activity A_Y(s, t) and center of activity r_cm,Y(t) from empirical EMG.
"""

import sys, os
from typing import Dict, Tuple
import numpy as np

# Import raw anatomical slice matrix and empirical EMG from baseline reproduction
base_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_reproduction', 'src'))
if base_src not in sys.path:
    sys.path.insert(0, base_src)

from anatomy import CatLumbosacralAnatomy, RAW_SLICE_PROFILES, MUSCLE_NAMES, MUSCLE_CATEGORIES
from emg_profiles import build_all_emg_profiles


class ModelY:
    """
    Implements Yakovenko et al. (2002) algebraic model:
    A(s, t) = sum_{m=1}^{27} N_{m,s} * (EMG_m(t) / 100) * gamma_m
    """

    def __init__(self, recruitment_mode: str = 'graded', fdl_as_retractor: bool = True, n_cycles: int = 2):
        self.recruitment_mode = recruitment_mode
        self.fdl_as_retractor = fdl_as_retractor
        self.n_cycles = int(n_cycles)

        self.anatomy = CatLumbosacralAnatomy()
        self.emg_dict = build_all_emg_profiles(fdl_as_retractor=fdl_as_retractor)
        self.n_slices = 30
        self.slice_thickness_mm = self.anatomy.length_mm / self.n_slices # 0.96 mm

        self._compute_activity_grid()
        self._compute_center_of_activity()

    def _compute_activity_grid(self):
        """Computes the (30 slices x 100*n_cycles time bins) activity grid."""
        n_bins = 100 * self.n_cycles
        self.grid = np.zeros((self.n_slices, n_bins), dtype=np.float64)

        # Recruitment ceilings gamma_m
        gamma = {}
        for m in MUSCLE_NAMES:
            cat = MUSCLE_CATEGORIES.get(m, 'extensor')
            if self.recruitment_mode == 'graded':
                gamma[m] = 1.0
            elif self.recruitment_mode == 'step':
                gamma[m] = 1.0
            elif self.recruitment_mode == 'phys_40_15':
                gamma[m] = 0.40 if cat == 'extensor' else 0.15
            elif self.recruitment_mode == 'inv_15_40':
                gamma[m] = 0.15 if cat == 'extensor' else 0.40
            else:
                gamma[m] = 1.0

        for t in range(n_bins):
            t_pct = t % 100
            for s in range(self.n_slices):
                act_s_t = 0.0
                for m_idx, m in enumerate(MUSCLE_NAMES):
                    n_ms = self.anatomy.slice_matrix[m_idx, s]
                    emg_val = self.emg_dict[m][t_pct]
                    if self.recruitment_mode == 'step':
                        emg_val = 100.0 if emg_val > 0.0 else 0.0
                    act_s_t += n_ms * (emg_val / 100.0) * gamma[m]
                self.grid[s, t] = act_s_t

    def _compute_center_of_activity(self):
        """Computes center of activity in levels (0..100) and in mm (0..28.8)."""
        n_bins = self.grid.shape[1]
        self.r_cm_level = np.zeros(n_bins, dtype=np.float64)
        self.r_cm_mm = np.zeros(n_bins, dtype=np.float64)
        self.velocity_mm_s = np.zeros(n_bins, dtype=np.float64)

        slice_levels = self.anatomy.slice_centers_level
        slice_mms = self.anatomy.slice_centers_mm

        for t in range(n_bins):
            total_act = np.sum(self.grid[:, t])
            if total_act > 1e-9:
                self.r_cm_level[t] = np.sum(self.grid[:, t] * slice_levels) / total_act
                self.r_cm_mm[t] = np.sum(self.grid[:, t] * slice_mms) / total_act
            else:
                self.r_cm_level[t] = 50.0
                self.r_cm_mm[t] = 14.4

        # Center of activity migration velocity
        dt_s = 0.007 # 7 ms per 1% interval for 700 ms cycle
        dr = np.gradient(self.r_cm_mm, dt_s)
        self.velocity_mm_s = np.abs(dr)
