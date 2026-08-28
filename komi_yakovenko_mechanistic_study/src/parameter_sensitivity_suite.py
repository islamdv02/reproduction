"""
Parameter Sensitivity Suite: Systematic Sweeps Over Core Model Parameters.
Evaluates sensitivity to mu_z, sigma_z, tau, I_tonic, and commissural fraction.
"""

import sys, os
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import signal

from model_y import ModelY
from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder
from projectome_analysis import ProjectomeAnalyzer
from traveling_wave import TravelingWaveAnalyzer


def _balance_matrix(W: np.ndarray, spectral_radius: float = 1.25) -> np.ndarray:
    W_bal = np.copy(W)
    N = W.shape[0]
    for i in range(N):
        row_exc = np.sum(W_bal[i, W_bal[i, :] > 0])
        row_inh = np.sum(np.abs(W_bal[i, W_bal[i, :] < 0]))
        if row_inh > 1e-9 and row_exc > 1e-9:
            scale = row_exc / row_inh
            W_bal[i, W_bal[i, :] < 0] *= scale
        elif row_exc > 0 and row_inh == 0:
            W_bal[i, :] *= 0.1
    try:
        eigenvalues = np.linalg.eigvals(W_bal)
        max_eig = np.max(np.abs(eigenvalues))
        if max_eig > 1e-6:
            W_bal = (W_bal / max_eig) * spectral_radius
    except Exception:
        pass
    return W_bal


class ParameterSensitivitySuite:
    """
    Executes systematic sweeps over major transferred parameters:
    - mu_z (descending bias): [0.0, 1.5, 3.5, 5.0, 7.0] mm
    - sigma_z (axonal reach): [2.0, 4.0, 6.0, 8.0, 10.0] mm
    - tau (time constant): [5.0, 10.0, 20.0, 40.0, 60.0] ms
    - I_tonic (somatic drive): [5.0, 10.0, 15.0, 25.0, 35.0] pA
    - commissural_frac: [0.0, 0.05, 0.15, 0.30, 0.50]
    """

    def __init__(self, rng_seed: int = 42, n_neurons: int = 600):
        self.rng_seed = rng_seed
        self.n_neurons = n_neurons

    def run_all_sweeps(self) -> pd.DataFrame:
        records = []
        model_y = ModelY(recruitment_mode='graded', n_cycles=2)
        y_ref = model_y.r_cm_level[:100]

        # 1. Sweep mu_z
        for val in [0.0, 1.5, 3.5, 5.0, 7.0]:
            rec = self._evaluate_param(
                param_name='mu_z_exc_mm', param_val=val,
                mu_z_exc=val, sigma_z_exc=6.0, tau=20.0, i_tonic=15.0, comm_frac=0.15,
                y_ref=y_ref
            )
            records.append(rec)

        # 2. Sweep sigma_z
        for val in [2.0, 4.0, 6.0, 8.0, 10.0]:
            rec = self._evaluate_param(
                param_name='sigma_z_exc_mm', param_val=val,
                mu_z_exc=3.5, sigma_z_exc=val, tau=20.0, i_tonic=15.0, comm_frac=0.15,
                y_ref=y_ref
            )
            records.append(rec)

        # 3. Sweep tau
        for val in [5.0, 10.0, 20.0, 40.0, 60.0]:
            rec = self._evaluate_param(
                param_name='tau_ms', param_val=val,
                mu_z_exc=3.5, sigma_z_exc=6.0, tau=val, i_tonic=15.0, comm_frac=0.15,
                y_ref=y_ref
            )
            records.append(rec)

        # 4. Sweep I_tonic
        for val in [5.0, 10.0, 15.0, 25.0, 35.0]:
            rec = self._evaluate_param(
                param_name='i_tonic_pA', param_val=val,
                mu_z_exc=3.5, sigma_z_exc=6.0, tau=20.0, i_tonic=val, comm_frac=0.15,
                y_ref=y_ref
            )
            records.append(rec)

        # 5. Sweep commissural fraction
        for val in [0.0, 0.05, 0.15, 0.30, 0.50]:
            rec = self._evaluate_param(
                param_name='commissural_fraction', param_val=val,
                mu_z_exc=3.5, sigma_z_exc=6.0, tau=20.0, i_tonic=15.0, comm_frac=val,
                y_ref=y_ref
            )
            records.append(rec)

        df = pd.DataFrame(records)
        return df

    def _evaluate_param(
        self, param_name: str, param_val: float,
        mu_z_exc: float, sigma_z_exc: float, tau: float, i_tonic: float, comm_frac: float,
        y_ref: np.ndarray
    ) -> Dict:
        net = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=self.rng_seed)
        # Adapt kernel parameters
        # Rebuild W with custom mu_z and sigma_z
        N = self.n_neurons
        dz = net.z[:, None] - net.z[None, :]
        p_exc = 0.15 * np.exp(-((dz - mu_z_exc)**2) / (2.0 * sigma_z_exc**2))
        np.fill_diagonal(p_exc, 0.0)
        # Apply commissural scaling
        if comm_frac != 0.15:
            is_contra = (net.hemicord[:, None] != net.hemicord[None, :])
            p_exc[is_contra] *= (comm_frac / 0.15)

        conn.W = np.where(conn.rng.random((N, N)) < p_exc, conn.W, 0.0)
        conn.W = _balance_matrix(conn.W)

        dyn = RecurrentRateDynamics(conn, tau_ms=tau, tonic_drive_pA=i_tonic, rng_seed=self.rng_seed)
        times, rates, _ = dyn.simulate(duration_ms=1800.0, warmup_ms=300.0)
        pu = PhaseUnfolder(rates, times)
        proj = ProjectomeAnalyzer(conn)
        wave = TravelingWaveAnalyzer(net, rates, times)

        # R_cm
        levels = np.linspace(1.67, 98.33, wave.grid.shape[0])
        rcm = np.zeros(wave.grid.shape[1])
        for t in range(len(rcm)):
            s = np.sum(wave.grid[:, t])
            rcm[t] = np.sum(wave.grid[:, t] * levels) / s if s > 1e-9 else 50.0

        ky_100 = signal.resample(rcm[:300], 100) if len(rcm) >= 50 else np.full(100, 50.0)
        if np.std(ky_100) > 1e-6:
            xcorr = signal.correlate(y_ref - np.mean(y_ref), ky_100 - np.mean(ky_100), mode='full')
            lags = signal.correlation_lags(100, 100)
            best_lag = lags[np.argmax(xcorr)]
            ky_aligned = np.roll(ky_100, best_lag)
            corr = float(np.corrcoef(y_ref, ky_aligned)[0, 1])
            rmse = float(np.sqrt(np.mean((y_ref - ky_aligned)**2)))
        else:
            corr = 0.0
            rmse = float(np.sqrt(np.mean((y_ref - ky_100)**2)))

        return {
            'parameter_name': param_name,
            'parameter_value': param_val,
            'correlation_r': corr,
            'rmse_levels': rmse,
            'planar_var_pct': float(pu.planar_variance * 100.0),
            'dominant_freq_hz': float(pu.frequency_hz),
            'wave_velocity_mm_s': float(wave.velocity_mm_s),
            'mexican_hat_index': float(proj.mexican_hat_index),
            'bilateral_phase_deg': float(wave.bilateral_phase_diff_deg)
        }
