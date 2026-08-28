"""
Spatiotemporal Model of Lumbosacral Motoneuron Activation.
Calculates 3D and 30-slice spatiotemporal activity landscapes,
center of activity trajectories r_cm(t), and migration velocities across the step cycle.
Faithfully reproduces Yakovenko et al. (J Neurophysiol 2002).
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from anatomy import CatLumbosacralAnatomy, MUSCLE_NAMES, MUSCLE_CATEGORIES
from emg_profiles import CatHindlimbEMG


class SpatiotemporalModel:
    """
    Computes active motoneuron recruitment across the 30 spinal slices and 100-step cycle intervals.
    """

    def __init__(
        self,
        anatomy: Optional[CatLumbosacralAnatomy] = None,
        emg: Optional[CatHindlimbEMG] = None,
        recruitment_mode: str = 'graded', # 'graded', 'step', 'phys_40_15', 'inv_15_40'
        fdl_as_retractor: bool = True,
        cycle_period_ms: float = 700.0,
        n_cycles: int = 2
    ):
        self.anatomy = anatomy if anatomy is not None else CatLumbosacralAnatomy()
        self.emg = emg if emg is not None else CatHindlimbEMG(fdl_as_retractor=fdl_as_retractor)
        self.recruitment_mode = recruitment_mode
        self.fdl_as_retractor = bool(fdl_as_retractor)
        self.cycle_period_ms = float(cycle_period_ms)
        self.dt_ms = self.cycle_period_ms / 100.0 # ~7 ms per 1% bin
        self.n_cycles = int(n_cycles)

        self._compute_activity_grid()
        self._compute_center_of_mass_trajectory()

    def _compute_activity_grid(self):
        """
        Computes the (30 slices x (100 * n_cycles) time bins) motoneuron activity matrix.
        """
        n_bins = 100 * self.n_cycles
        self.activity_grid = np.zeros((self.anatomy.n_slices, n_bins), dtype=np.float64)
        self.active_mns_by_muscle = np.zeros((len(MUSCLE_NAMES), n_bins), dtype=np.float64)

        # Determine recruitment cap per muscle
        max_recruit = {}
        for m in MUSCLE_NAMES:
            cat = MUSCLE_CATEGORIES[m]
            if not self.fdl_as_retractor and m == 'FDL':
                cat = 'extensor'

            if self.recruitment_mode == 'graded':
                max_recruit[m] = 1.0
            elif self.recruitment_mode == 'step':
                max_recruit[m] = 1.0 # will binarize EMG
            elif self.recruitment_mode == 'phys_40_15':
                max_recruit[m] = 0.40 if cat == 'extensor' else 0.15
            elif self.recruitment_mode == 'inv_15_40':
                max_recruit[m] = 0.15 if cat == 'extensor' else 0.40
            else:
                max_recruit[m] = 1.0

        for t in range(n_bins):
            step_pct = t % 100
            for i, m in enumerate(MUSCLE_NAMES):
                raw_emg = self.emg.get_emg(m, step_pct)
                if self.recruitment_mode == 'step':
                    emg_val = 1.0 if raw_emg > 0.0 else 0.0
                else:
                    emg_val = raw_emg / 100.0

                # Active motoneurons for muscle m
                pool_counts = self.anatomy.slice_matrix[i, :]
                tot_pool_mn = np.sum(pool_counts)
                n_act = tot_pool_mn * emg_val * max_recruit[m]
                self.active_mns_by_muscle[i, t] = n_act

                # Distribute across slices proportionally
                if tot_pool_mn > 0:
                    self.activity_grid[:, t] += pool_counts * (n_act / tot_pool_mn)

    def _compute_center_of_mass_trajectory(self):
        """
        Calculates center of mass r_cm(t) in normalized levels (0-100) and physical millimeters (0-28.8 mm),
        along with instantaneous migration velocity (mm/s).
        """
        n_bins = 100 * self.n_cycles
        self.r_cm_level = np.zeros(n_bins, dtype=np.float64)
        self.r_cm_mm = np.zeros(n_bins, dtype=np.float64)
        self.total_active_mn = np.sum(self.activity_grid, axis=0)

        for t in range(n_bins):
            tot = self.total_active_mn[t]
            if tot > 0:
                self.r_cm_level[t] = np.sum(self.activity_grid[:, t] * self.anatomy.slice_centers_level) / tot
                self.r_cm_mm[t] = np.sum(self.activity_grid[:, t] * self.anatomy.slice_centers_mm) / tot
            else:
                self.r_cm_level[t] = 50.0
                self.r_cm_mm[t] = 14.4

        # Compute velocity using central differences (accounting for circular boundary over cycles)
        self.velocity_mm_s = np.zeros(n_bins, dtype=np.float64)
        dt_sec = self.dt_ms / 1000.0

        for t in range(n_bins):
            t_prev = (t - 1) % n_bins
            t_next = (t + 1) % n_bins
            self.velocity_mm_s[t] = (self.r_cm_mm[t_next] - self.r_cm_mm[t_prev]) / (2.0 * dt_sec)

        # Single cycle metrics (0 to 99)
        r_single_lvl = self.r_cm_level[:100]
        r_single_mm = self.r_cm_mm[:100]
        v_single = self.velocity_mm_s[:100]

        self.min_level = float(np.min(r_single_lvl))
        self.max_level = float(np.max(r_single_lvl))
        self.displacement_levels = float(self.max_level - self.min_level)
        self.displacement_mm = float(np.max(r_single_mm) - np.min(r_single_mm))

        # Peak migration velocities at transitions
        # Swing-to-Stance: around bins 25-35
        # Retraction-to-Swing: around bins 85-98 / 0-5
        self.peak_velocity_swing_stance = float(np.max(np.abs(v_single[20:40])))
        self.peak_velocity_retract_swing = float(np.max(np.abs(np.concatenate([v_single[85:], v_single[:10]]))))
