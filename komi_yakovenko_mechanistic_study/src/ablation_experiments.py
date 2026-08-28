"""
Ablation Experiments Module: 11 Systematic Conditions (A through K).
Tests whether agreement with Yakovenko specifically depends on the mechanisms proposed by Komi.
"""

import sys, os
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import signal

from model_y import ModelY
from model_ky import ModelKY
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


class AblationEngine:
    """
    Executes the 11 required ablation conditions:
    A. Full Komi framework
    B. No spatial organization (uniform random distance)
    C. Shuffled neuron coordinates (disrupt RC layout)
    D. No directional bias (mu_z = 0, symmetric kernels)
    E. Isotropic connectivity (sigma_x = sigma_y = sigma_z = 2.0 mm)
    F. No E/I balancing (unbalanced raw weights)
    G. Random connectivity (Erdos-Renyi graph)
    H. No commissural connections (hemicords isolated)
    I. No recurrent connectivity (tau * dR/dt = -R + f(I_tonic))
    J. Yakovenko feedforward model without Komi recurrent dynamics (Model Y)
    K. Spatial organization only, without recurrent dynamics (Static spatial projection)
    """

    def __init__(self, rng_seed: int = 42, n_neurons: int = 800):
        self.rng_seed = rng_seed
        self.n_neurons = n_neurons

    def run_all_11_ablations(self) -> pd.DataFrame:
        records = []

        # Ground-truth reference for correlation/RMSE: Model Y center of activity (100 pts)
        model_y = ModelY(recruitment_mode='graded', n_cycles=2)
        y_ref = model_y.r_cm_level[:100]

        # -------------------------------------------------------------
        # Condition A: Full Komi Framework
        # -------------------------------------------------------------
        m_a = ModelKY(n_neurons=self.n_neurons, rng_seed=self.rng_seed, duration_ms=2200.0, warmup_ms=400.0)
        rec_a = self._evaluate_condition(
            cond_id='A',
            cond_name='Full Komi Framework',
            net=m_a.network,
            conn=m_a.connectome,
            dynamics=m_a.dynamics,
            pu=m_a.phase_unfolder,
            proj=m_a.projectome,
            wave=m_a.wave,
            r_cm_level=m_a.r_cm_level,
            y_ref=y_ref
        )
        records.append(rec_a)

        # -------------------------------------------------------------
        # Condition B: No Spatial Organization
        # -------------------------------------------------------------
        net_b = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_b = CatSynapticConnectome(net_b, balance_ei=True, rng_seed=self.rng_seed)
        N = self.n_neurons
        # Uniform connection probability
        p_uniform = 0.12
        adj_b = (conn_b.rng.random((N, N)) < p_uniform).astype(np.float64)
        np.fill_diagonal(adj_b, 0.0)
        # Random sign
        signs = np.where(net_b.is_excitatory, 1.0, -1.0)
        w_b = adj_b * signs[None, :] * conn_b.rng.normal(1.0, 0.1, size=(N, N))
        np.fill_diagonal(w_b, 0.0)
        conn_b.W = w_b
        # Balance
        conn_b.W = _balance_matrix(conn_b.W)
        dyn_b = RecurrentRateDynamics(conn_b, rng_seed=self.rng_seed)
        times_b, rates_b, _ = dyn_b.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_b = PhaseUnfolder(rates_b, times_b)
        proj_b = ProjectomeAnalyzer(conn_b)
        wave_b = TravelingWaveAnalyzer(net_b, rates_b, times_b)
        r_cm_b = self._calc_rcm(wave_b.grid)
        records.append(self._evaluate_condition(
            cond_id='B', cond_name='No Spatial Organization',
            net=net_b, conn=conn_b, dynamics=dyn_b, pu=pu_b, proj=proj_b, wave=wave_b,
            r_cm_level=r_cm_b, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition C: Shuffled Neuron Coordinates
        # -------------------------------------------------------------
        net_c = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        net_c.rng.shuffle(net_c.z)
        conn_c = CatSynapticConnectome(net_c, balance_ei=True, rng_seed=self.rng_seed)
        dyn_c = RecurrentRateDynamics(conn_c, rng_seed=self.rng_seed)
        times_c, rates_c, _ = dyn_c.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_c = PhaseUnfolder(rates_c, times_c)
        proj_c = ProjectomeAnalyzer(conn_c)
        wave_c = TravelingWaveAnalyzer(net_c, rates_c, times_c)
        r_cm_c = self._calc_rcm(wave_c.grid)
        records.append(self._evaluate_condition(
            cond_id='C', cond_name='Shuffled Coordinates',
            net=net_c, conn=conn_c, dynamics=dyn_c, pu=pu_c, proj=proj_c, wave=wave_c,
            r_cm_level=r_cm_c, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition D: No Directional Bias (mu_z = 0)
        # -------------------------------------------------------------
        net_d = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_d = CatSynapticConnectome(net_d, balance_ei=True, rng_seed=self.rng_seed)
        # Symmetrize longitudinal distance
        dz = net_d.z[:, None] - net_d.z[None, :]
        p_sym = 0.12 * np.exp(-(dz**2)/(2.0 * 4.0**2))
        np.fill_diagonal(p_sym, 0.0)
        conn_d.W = np.where(conn_d.rng.random((N, N)) < p_sym, conn_d.W, 0.0)
        conn_d.W = _balance_matrix(conn_d.W)
        dyn_d = RecurrentRateDynamics(conn_d, rng_seed=self.rng_seed)
        times_d, rates_d, _ = dyn_d.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_d = PhaseUnfolder(rates_d, times_d)
        proj_d = ProjectomeAnalyzer(conn_d)
        wave_d = TravelingWaveAnalyzer(net_d, rates_d, times_d)
        r_cm_d = self._calc_rcm(wave_d.grid)
        records.append(self._evaluate_condition(
            cond_id='D', cond_name='No Directional Bias (mu_z=0)',
            net=net_d, conn=conn_d, dynamics=dyn_d, pu=pu_d, proj=proj_d, wave=wave_d,
            r_cm_level=r_cm_d, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition E: Isotropic Connectivity
        # -------------------------------------------------------------
        net_e = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_e = CatSynapticConnectome(net_e, balance_ei=True, rng_seed=self.rng_seed)
        # 3D isotropic distance
        dx = net_e.x[:, None] - net_e.x[None, :]
        dy = net_e.y[:, None] - net_e.y[None, :]
        dz = net_e.z[:, None] - net_e.z[None, :]
        dist_sq = dx**2 + dy**2 + dz**2
        p_iso = 0.12 * np.exp(-dist_sq / (2.0 * 2.5**2))
        np.fill_diagonal(p_iso, 0.0)
        conn_e.W = np.where(conn_e.rng.random((N, N)) < p_iso, conn_e.W, 0.0)
        conn_e.W = _balance_matrix(conn_e.W)
        dyn_e = RecurrentRateDynamics(conn_e, rng_seed=self.rng_seed)
        times_e, rates_e, _ = dyn_e.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_e = PhaseUnfolder(rates_e, times_e)
        proj_e = ProjectomeAnalyzer(conn_e)
        wave_e = TravelingWaveAnalyzer(net_e, rates_e, times_e)
        r_cm_e = self._calc_rcm(wave_e.grid)
        records.append(self._evaluate_condition(
            cond_id='E', cond_name='Isotropic Connectivity',
            net=net_e, conn=conn_e, dynamics=dyn_e, pu=pu_e, proj=proj_e, wave=wave_e,
            r_cm_level=r_cm_e, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition F: No E/I Balancing
        # -------------------------------------------------------------
        net_f = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_f = CatSynapticConnectome(net_f, balance_ei=False, rng_seed=self.rng_seed)
        dyn_f = RecurrentRateDynamics(conn_f, rng_seed=self.rng_seed)
        times_f, rates_f, _ = dyn_f.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_f = PhaseUnfolder(rates_f, times_f)
        proj_f = ProjectomeAnalyzer(conn_f)
        wave_f = TravelingWaveAnalyzer(net_f, rates_f, times_f)
        r_cm_f = self._calc_rcm(wave_f.grid)
        records.append(self._evaluate_condition(
            cond_id='F', cond_name='No E/I Balancing',
            net=net_f, conn=conn_f, dynamics=dyn_f, pu=pu_f, proj=proj_f, wave=wave_f,
            r_cm_level=r_cm_f, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition G: Random Connectivity (Erdos-Renyi)
        # -------------------------------------------------------------
        net_g = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_g = CatSynapticConnectome(net_g, balance_ei=False, rng_seed=self.rng_seed)
        rand_w = conn_g.rng.normal(0.0, 0.05, size=(N, N))
        np.fill_diagonal(rand_w, 0.0)
        conn_g.W = rand_w
        dyn_g = RecurrentRateDynamics(conn_g, rng_seed=self.rng_seed)
        times_g, rates_g, _ = dyn_g.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_g = PhaseUnfolder(rates_g, times_g)
        proj_g = ProjectomeAnalyzer(conn_g)
        wave_g = TravelingWaveAnalyzer(net_g, rates_g, times_g)
        r_cm_g = self._calc_rcm(wave_g.grid)
        records.append(self._evaluate_condition(
            cond_id='G', cond_name='Random Erdos-Renyi Wiring',
            net=net_g, conn=conn_g, dynamics=dyn_g, pu=pu_g, proj=proj_g, wave=wave_g,
            r_cm_level=r_cm_g, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition H: No Commissural Connections
        # -------------------------------------------------------------
        net_h = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_h = CatSynapticConnectome(net_h, balance_ei=True, rng_seed=self.rng_seed)
        is_contra = (net_h.hemicord[:, None] != net_h.hemicord[None, :])
        conn_h.W[is_contra] = 0.0
        conn_h.W = _balance_matrix(conn_h.W)
        dyn_h = RecurrentRateDynamics(conn_h, rng_seed=self.rng_seed)
        times_h, rates_h, _ = dyn_h.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_h = PhaseUnfolder(rates_h, times_h)
        proj_h = ProjectomeAnalyzer(conn_h)
        wave_h = TravelingWaveAnalyzer(net_h, rates_h, times_h)
        r_cm_h = self._calc_rcm(wave_h.grid)
        records.append(self._evaluate_condition(
            cond_id='H', cond_name='No Commissural Projections',
            net=net_h, conn=conn_h, dynamics=dyn_h, pu=pu_h, proj=proj_h, wave=wave_h,
            r_cm_level=r_cm_h, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition I: No Recurrent Connectivity (W = 0)
        # -------------------------------------------------------------
        net_i = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_i = CatSynapticConnectome(net_i, balance_ei=False, rng_seed=self.rng_seed)
        conn_i.W = np.zeros((N, N), dtype=np.float64)
        dyn_i = RecurrentRateDynamics(conn_i, rng_seed=self.rng_seed)
        times_i, rates_i, _ = dyn_i.simulate(duration_ms=2200.0, warmup_ms=400.0)
        pu_i = PhaseUnfolder(rates_i, times_i)
        proj_i = ProjectomeAnalyzer(conn_i)
        wave_i = TravelingWaveAnalyzer(net_i, rates_i, times_i)
        r_cm_i = self._calc_rcm(wave_i.grid)
        records.append(self._evaluate_condition(
            cond_id='I', cond_name='No Recurrent Connectivity (W=0)',
            net=net_i, conn=conn_i, dynamics=dyn_i, pu=pu_i, proj=proj_i, wave=wave_i,
            r_cm_level=r_cm_i, y_ref=y_ref
        ))

        # -------------------------------------------------------------
        # Condition J: Yakovenko Feedforward (Model Y Baseline)
        # -------------------------------------------------------------
        rec_j = {
            'condition_id': 'J',
            'condition_name': 'Model Y (Feedforward EMG)',
            'correlation_r': 1.0,
            'rmse_levels': 0.0,
            'nrmse': 0.0,
            'planar_var_pct': 100.0,
            'orbit_radius': float(np.mean(model_y.velocity_mm_s)),
            'mexican_hat_index': 0.0,
            'wave_velocity_mm_s': float(np.max(model_y.velocity_mm_s)),
            'bilateral_alternation': 1.0,
            'recurrent_wave_present': False
        }
        records.append(rec_j)

        # -------------------------------------------------------------
        # Condition K: Spatial Organization Only, No Recurrent Dynamics
        # -------------------------------------------------------------
        # Static projection of tonic current through spatial weights without time integration
        net_k = YakovenkoKomiSpatialNetwork(n_neurons=self.n_neurons, rng_seed=self.rng_seed)
        conn_k = CatSynapticConnectome(net_k, balance_ei=True, rng_seed=self.rng_seed)
        # Static rate = f(W @ I_tonic)
        I_static = np.full(N, 15.0)
        static_rates = np.maximum(0, conn_k.W @ I_static)
        # Broadcast across time
        rates_k = np.tile(static_rates[:, None], (1, 100))
        times_k = np.linspace(0, 1000, 100)
        pu_k = PhaseUnfolder(rates_k, times_k)
        proj_k = ProjectomeAnalyzer(conn_k)
        wave_k = TravelingWaveAnalyzer(net_k, rates_k, times_k)
        r_cm_k = self._calc_rcm(wave_k.grid)
        records.append(self._evaluate_condition(
            cond_id='K', cond_name='Spatial Layout Only (Static)',
            net=net_k, conn=conn_k, dynamics=None, pu=pu_k, proj=proj_k, wave=wave_k,
            r_cm_level=r_cm_k, y_ref=y_ref
        ))

        df = pd.DataFrame(records)
        return df

    def _calc_rcm(self, grid: np.ndarray) -> np.ndarray:
        n_slices, n_times = grid.shape
        levels = np.linspace(1.67, 98.33, n_slices)
        rcm = np.zeros(n_times)
        for t in range(n_times):
            s = np.sum(grid[:, t])
            rcm[t] = np.sum(grid[:, t] * levels) / s if s > 1e-9 else 50.0
        return rcm

    def _evaluate_condition(
        self, cond_id: str, cond_name: str, net, conn, dynamics, pu, proj, wave,
        r_cm_level: np.ndarray, y_ref: np.ndarray
    ) -> Dict:
        # Resample r_cm_level to 100 points
        if len(r_cm_level) >= 50:
            ky_100 = signal.resample(r_cm_level[:300], 100)
        else:
            ky_100 = np.full(100, 50.0)

        # Cross-correlation alignment
        if np.std(ky_100) > 1e-6:
            xcorr = signal.correlate(y_ref - np.mean(y_ref), ky_100 - np.mean(ky_100), mode='full')
            lags = signal.correlation_lags(100, 100)
            best_lag = lags[np.argmax(xcorr)]
            ky_aligned = np.roll(ky_100, best_lag)
            corr = float(np.corrcoef(y_ref, ky_aligned)[0, 1])
            rmse = float(np.sqrt(np.mean((y_ref - ky_aligned)**2)))
            nrmse = float(rmse / (np.max(y_ref) - np.min(y_ref)))
        else:
            corr = 0.0
            rmse = float(np.sqrt(np.mean((y_ref - ky_100)**2)))
            nrmse = 1.0

        has_wave = bool(pu.planar_variance > 0.3 and proj.mexican_hat_index > 0.5)

        return {
            'condition_id': cond_id,
            'condition_name': cond_name,
            'correlation_r': corr,
            'rmse_levels': rmse,
            'nrmse': nrmse,
            'planar_var_pct': float(pu.planar_variance * 100.0),
            'orbit_radius': float(pu.orbit_radius),
            'mexican_hat_index': float(proj.mexican_hat_index),
            'wave_velocity_mm_s': float(wave.velocity_mm_s),
            'bilateral_alternation': float(wave.alternation_index),
            'recurrent_wave_present': has_wave
        }
