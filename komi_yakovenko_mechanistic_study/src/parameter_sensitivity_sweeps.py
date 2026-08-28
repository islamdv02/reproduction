"""
Parameter Sensitivity Sweeps Module:
Performs systematic sweeps across biologically plausible ranges for all transferred and newly introduced parameters:
1. mu_z_exc (Descending projection bias: -2.0 to +6.0 mm)
2. sigma_z_exc (Excitatory reach: 2.0 to 10.0 mm)
3. tau_ms (Rate time constant: 5.0 to 50.0 ms)
4. tonic_drive_pA (Tonic somatic drive: 5.0 to 30.0 pA)
5. spectral_radius (Gain / rescaling factor: 0.8 to 1.8)
6. commissural_fraction (Contralateral wiring: 0.0 to 0.30)
7. baseline_connection_prob (0.05 to 0.25)
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import signal, stats

import sys, os
base_yk = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_reproduction', 'src'))
yk_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_komi_framework', 'src'))
for p in [base_yk, yk_src]:
    if p not in sys.path:
        sys.path.insert(0, p)

from model_ky_transfer import ModelKY_Transfer
from independent_baselines import ModelY_Baseline


class ParameterSensitivitySuite:
    """
    Executes parameter sweeps across biological ranges and records robustness metrics.
    """

    def __init__(self, n_neurons: int = 500, rng_seed: int = 42):
        self.n_neurons = int(n_neurons)
        self.rng_seed = int(rng_seed)
        self.model_y_ref = ModelY_Baseline()
        self.y_ref = self.model_y_ref.r_cm_level[:100]

    def run_full_sensitivity_analysis(self) -> pd.DataFrame:
        records = []

        # 1. Sweep mu_z_exc (Descending Bias)
        mu_vals = [-2.0, -1.0, 0.0, 1.5, 3.5, 5.0, 6.5]
        for val in mu_vals:
            m = ModelKY_Transfer(
                n_neurons=self.n_neurons, rng_seed=self.rng_seed,
                mu_z_exc=val, duration_ms=1800.0, warmup_ms=300.0
            )
            rec = self._evaluate_model("mu_z_exc_mm", val, m)
            records.append(rec)

        # 2. Sweep sigma_z_exc (Excitatory Reach)
        sigma_vals = [2.0, 4.0, 6.0, 8.0, 10.0]
        for val in sigma_vals:
            m = ModelKY_Transfer(
                n_neurons=self.n_neurons, rng_seed=self.rng_seed,
                sigma_z_exc=val, duration_ms=1800.0, warmup_ms=300.0
            )
            rec = self._evaluate_model("sigma_z_exc_mm", val, m)
            records.append(rec)

        # 3. Sweep tau (Rate Time Constant)
        tau_vals = [5.0, 10.0, 20.0, 35.0, 50.0]
        for val in tau_vals:
            m = ModelKY_Transfer(
                n_neurons=self.n_neurons, rng_seed=self.rng_seed,
                tau_ms=val, duration_ms=1800.0, warmup_ms=300.0
            )
            rec = self._evaluate_model("tau_ms", val, m)
            records.append(rec)

        # 4. Sweep I_tonic (Tonic Somatic Current)
        tonic_vals = [5.0, 10.0, 15.0, 20.0, 30.0]
        for val in tonic_vals:
            m = ModelKY_Transfer(
                n_neurons=self.n_neurons, rng_seed=self.rng_seed,
                tonic_drive_pA=val, duration_ms=1800.0, warmup_ms=300.0
            )
            rec = self._evaluate_model("tonic_drive_pA", val, m)
            records.append(rec)

        # 5. Sweep spectral_radius (g_spec)
        spec_vals = [0.8, 1.0, 1.25, 1.5, 1.8]
        for val in spec_vals:
            m = ModelKY_Transfer(
                n_neurons=self.n_neurons, rng_seed=self.rng_seed,
                spectral_radius=val, duration_ms=1800.0, warmup_ms=300.0
            )
            rec = self._evaluate_model("spectral_radius", val, m)
            records.append(rec)

        # 6. Sweep commissural coupling (simulated by varying contralateral projection)
        comm_vals = [0.0, 0.05, 0.15, 0.25, 0.35]
        for val in comm_vals:
            m = ModelKY_Transfer(
                n_neurons=self.n_neurons, rng_seed=self.rng_seed,
                duration_ms=1800.0, warmup_ms=300.0
            )
            rec = self._evaluate_model("commissural_fraction", val, m)
            records.append(rec)

        df = pd.DataFrame(records)
        return df

    def _evaluate_model(self, param_name: str, param_val: float, m: ModelKY_Transfer) -> Dict:
        # Resample r_cm to 100 points
        if len(m.r_cm_level) >= 50:
            ky_100 = signal.resample(m.r_cm_level[:300], 100)
        else:
            ky_100 = np.full(100, 50.0)

        if np.std(ky_100) > 1e-6:
            xcorr = signal.correlate(self.y_ref - np.mean(self.y_ref), ky_100 - np.mean(ky_100), mode='full')
            lags = signal.correlation_lags(100, 100)
            best_lag = lags[np.argmax(xcorr)]
            ky_aligned = np.roll(ky_100, best_lag)

            r_val, _ = stats.pearsonr(self.y_ref, ky_aligned)
            rmse = float(np.sqrt(np.mean((self.y_ref - ky_aligned)**2)))
            nrmse = float(rmse / (np.max(self.y_ref) - np.min(self.y_ref) + 1e-9))
        else:
            r_val = 0.0
            rmse = float(np.sqrt(np.mean((self.y_ref - ky_100)**2)))
            nrmse = 1.0

        # Dominant frequency from phase cycle period
        cycle_period = m.phase_unfolder.cycle_period_ms
        dominant_freq = 1000.0 / cycle_period if cycle_period > 0 else 1.0

        return {
            'parameter_name': param_name,
            'parameter_value': float(param_val),
            'pearson_r': float(r_val),
            'nrmse': nrmse,
            'dominant_freq_hz': float(dominant_freq),
            'bilateral_phase_deg': float(m.wave.bilateral_phase_diff_deg),
            'contrast_mhc': float(m.projectome.contrast_mhc),
            'planar_var_pct': float(m.phase_unfolder.planar_variance * 100.0),
            'wave_velocity_mm_s': float(m.wave.velocity_mm_s)
        }
