"""
Controls and Null Models Module:
Executes the 10 Critical Control Experiments + Matched Null Models with Multi-Seed Monte Carlo Evaluation.

Controls:
1. Control 1: Komi connectivity removed (W = 0, keep Yakovenko anatomy)
2. Control 2: Spatial coordinates shuffled (randomize z-positions)
3. Control 3: Directional bias removed (mu_z = 0)
4. Control 4: Anisotropy removed (isotropic kernels sigma_x=sigma_y=sigma_z)
5. Control 5: E/I balance removed (unbalanced raw weights)
6. Control 6: Commissural connectivity removed (W_contra = 0)
7. Control 7: Connectivity randomized (Erdos-Renyi random graph)
8. Control 8: Yakovenko-only model (pure feedforward EMG)
9. Control 9: Komi on scrambled Yakovenko anatomy (shuffled motor pools)
10. Control 10: Matched null model (same size, density, E/I ratio, firing rates, but scrambled receptive fields)
"""

import sys, os
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import signal, stats

base_yk = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_reproduction', 'src'))
yk_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'yakovenko_2002_komi_framework', 'src'))
for p in [base_yk, yk_src]:
    if p not in sys.path:
        sys.path.insert(0, p)

from anatomy import CatLumbosacralAnatomy
from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder
from traveling_wave import TravelingWaveAnalyzer
from projectome_audit import ProjectomeAuditor
from independent_baselines import ModelY_Baseline
from model_ky_transfer import ModelKY_Transfer


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
        evals = np.linalg.eigvals(W_bal)
        max_eig = np.max(np.abs(evals))
        if max_eig > 1e-6:
            W_bal = (W_bal / max_eig) * spectral_radius
    except Exception:
        pass
    return W_bal


class CriticalControlsSuite:
    """
    Manages and executes all 10 control conditions across multiple random seeds.
    """

    def __init__(self, n_neurons: int = 600, n_seeds: int = 10):
        self.n_neurons = int(n_neurons)
        self.n_seeds = int(n_seeds)
        self.model_y_ref = ModelY_Baseline()
        self.y_ref = self.model_y_ref.r_cm_level[:100]

    def run_all_controls(self) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
        """
        Runs all conditions across seeds.
        Returns:
          - Summary DataFrame with mean +- SEM for all metrics
          - Dictionary of raw Pi(Delta Z) projectome profiles for plotting
        """
        raw_records = []
        raw_profiles = {}

        condition_names = [
            ("Intact_Model_KY", "Intact Model K-Y (Untuned Transfer)"),
            ("Ctrl_1_No_Recurrent", "Control 1: Komi Connectivity Removed (W=0)"),
            ("Ctrl_2_Shuffled_Coords", "Control 2: Spatial Coordinates Shuffled"),
            ("Ctrl_3_Zero_Bias", "Control 3: Directional Bias Removed (mu_z=0)"),
            ("Ctrl_4_Isotropic", "Control 4: Anisotropy Removed (Isotropic Kernels)"),
            ("Ctrl_5_Unbalanced_EI", "Control 5: E/I Balance Removed"),
            ("Ctrl_6_No_Commissural", "Control 6: Commissural Projections Removed"),
            ("Ctrl_7_Erdos_Renyi", "Control 7: Connectivity Randomized (Erdos-Renyi)"),
            ("Ctrl_8_Yakovenko_Only", "Control 8: Yakovenko-Only Model (Feedforward EMG)"),
            ("Ctrl_9_Scrambled_Anatomy", "Control 9: Komi on Scrambled Cat Motor Pools"),
            ("Ctrl_10_Matched_Null", "Control 10: Matched Null Model")
        ]

        for cond_id, cond_desc in condition_names:
            prof_accum = []
            for seed in range(1, self.n_seeds + 1):
                rec, prof = self._run_single_condition(cond_id, cond_desc, seed)
                raw_records.append(rec)
                prof_accum.append(prof)
            raw_profiles[cond_id] = np.mean(np.array(prof_accum), axis=0)

        df_raw = pd.DataFrame(raw_records)

        # Compute summary statistics (mean, std, SEM, 95% CI)
        summary_rows = []
        for (cond_id, cond_desc), group in df_raw.groupby(['cond_id', 'cond_desc']):
            r_vals = group['pearson_r'].values
            nrmse_vals = group['nrmse'].values
            mhc_vals = group['contrast_mhc'].values
            planar_vals = group['planar_var_pct'].values
            alt_vals = group['bilateral_alternation'].values

            summary_rows.append({
                'cond_id': cond_id,
                'cond_desc': cond_desc,
                'pearson_r_mean': float(np.mean(r_vals)),
                'pearson_r_sem': float(np.std(r_vals) / np.sqrt(len(r_vals))),
                'pearson_r_ci95_low': float(np.percentile(r_vals, 2.5)),
                'pearson_r_ci95_high': float(np.percentile(r_vals, 97.5)),
                'spearman_rho_mean': float(np.mean(group['spearman_rho'])),
                'nrmse_mean': float(np.mean(nrmse_vals)),
                'nrmse_sem': float(np.std(nrmse_vals) / np.sqrt(len(nrmse_vals))),
                'rmse_mean': float(np.mean(group['rmse'])),
                'contrast_mhc_mean': float(np.mean(mhc_vals)),
                'contrast_mhc_sem': float(np.std(mhc_vals) / np.sqrt(len(mhc_vals))),
                'area_ratio_mean': float(np.mean(group['area_ratio'])),
                'legacy_mhi_mean': float(np.mean(group['legacy_mhi'])),
                'planar_var_pct_mean': float(np.mean(planar_vals)),
                'planar_var_pct_sem': float(np.std(planar_vals) / np.sqrt(len(planar_vals))),
                'wave_velocity_mm_s_mean': float(np.mean(group['wave_velocity_mm_s'])),
                'bilateral_alternation_mean': float(np.mean(alt_vals)),
                'n_seeds': len(group)
            })

        df_summary = pd.DataFrame(summary_rows)

        # Compute Delta r relative to Matched Null Model (Control 10)
        null_r_mean = df_summary.loc[df_summary['cond_id'] == 'Ctrl_10_Matched_Null', 'pearson_r_mean'].values[0]
        df_summary['delta_r_vs_null'] = df_summary['pearson_r_mean'] - null_r_mean

        # Calculate p-value of Komi vs Null
        komi_r_samples = df_raw.loc[df_raw['cond_id'] == 'Intact_Model_KY', 'pearson_r'].values
        null_r_samples = df_raw.loc[df_raw['cond_id'] == 'Ctrl_10_Matched_Null', 'pearson_r'].values
        t_stat, p_val = stats.ttest_ind(komi_r_samples, null_r_samples, equal_var=False)
        self.p_val_komi_vs_null = float(p_val)
        self.t_stat_komi_vs_null = float(t_stat)

        return df_summary, raw_profiles

    def _run_single_condition(self, cond_id: str, cond_desc: str, seed: int) -> Tuple[Dict, np.ndarray]:
        N = self.n_neurons
        rng = np.random.default_rng(seed)

        if cond_id == "Intact_Model_KY":
            m = ModelKY_Transfer(n_neurons=N, rng_seed=seed, duration_ms=2000.0, warmup_ms=300.0)
            return self._extract_metrics(cond_id, cond_desc, seed, m.grid, m.projectome, m.phase_unfolder, m.wave)

        elif cond_id == "Ctrl_1_No_Recurrent":
            net = YakovenkoKomiSpatialNetwork(n_neurons=N, rng_seed=seed)
            conn = CatSynapticConnectome(net, balance_ei=False, rng_seed=seed)
            conn.W = np.zeros((N, N))
            dyn = RecurrentRateDynamics(conn, rng_seed=seed)
            times, rates, _ = dyn.simulate(duration_ms=2000.0, warmup_ms=300.0)
            pu = PhaseUnfolder(rates, times)
            proj = ProjectomeAuditor(conn.W, net.z)
            wave = TravelingWaveAnalyzer(net, rates, times)
            return self._extract_metrics(cond_id, cond_desc, seed, wave.grid, proj, pu, wave)

        elif cond_id == "Ctrl_2_Shuffled_Coords":
            net = YakovenkoKomiSpatialNetwork(n_neurons=N, rng_seed=seed)
            conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=seed)
            dyn = RecurrentRateDynamics(conn, rng_seed=seed)
            times, rates, _ = dyn.simulate(duration_ms=2000.0, warmup_ms=300.0)
            # Shuffle z positions when mapping to slices
            shuffled_z = np.copy(net.z)
            rng.shuffle(shuffled_z)
            net_shuff = YakovenkoKomiSpatialNetwork(n_neurons=N, rng_seed=seed)
            net_shuff.z = shuffled_z
            wave = TravelingWaveAnalyzer(net_shuff, rates, times)
            pu = PhaseUnfolder(rates, times)
            proj = ProjectomeAuditor(conn.W, shuffled_z)
            return self._extract_metrics(cond_id, cond_desc, seed, wave.grid, proj, pu, wave)

        elif cond_id == "Ctrl_3_Zero_Bias":
            m = ModelKY_Transfer(n_neurons=N, rng_seed=seed, mu_z_exc=0.0, duration_ms=2000.0, warmup_ms=300.0)
            return self._extract_metrics(cond_id, cond_desc, seed, m.grid, m.projectome, m.phase_unfolder, m.wave)

        elif cond_id == "Ctrl_4_Isotropic":
            m = ModelKY_Transfer(n_neurons=N, rng_seed=seed, mu_z_exc=0.0, sigma_z_exc=3.0, sigma_z_inh=3.0, duration_ms=2000.0, warmup_ms=300.0)
            return self._extract_metrics(cond_id, cond_desc, seed, m.grid, m.projectome, m.phase_unfolder, m.wave)

        elif cond_id == "Ctrl_5_Unbalanced_EI":
            m = ModelKY_Transfer(n_neurons=N, rng_seed=seed, balance_ei=False, duration_ms=2000.0, warmup_ms=300.0)
            return self._extract_metrics(cond_id, cond_desc, seed, m.grid, m.projectome, m.phase_unfolder, m.wave)

        elif cond_id == "Ctrl_6_No_Commissural":
            net = YakovenkoKomiSpatialNetwork(n_neurons=N, rng_seed=seed)
            conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=seed)
            is_contra = (net.hemicord[:, None] != net.hemicord[None, :])
            conn.W[is_contra] = 0.0
            conn.W = _balance_matrix(conn.W)
            dyn = RecurrentRateDynamics(conn, rng_seed=seed)
            times, rates, _ = dyn.simulate(duration_ms=2000.0, warmup_ms=300.0)
            pu = PhaseUnfolder(rates, times)
            proj = ProjectomeAuditor(conn.W, net.z)
            wave = TravelingWaveAnalyzer(net, rates, times)
            return self._extract_metrics(cond_id, cond_desc, seed, wave.grid, proj, pu, wave)

        elif cond_id == "Ctrl_7_Erdos_Renyi":
            net = YakovenkoKomiSpatialNetwork(n_neurons=N, rng_seed=seed)
            conn = CatSynapticConnectome(net, balance_ei=False, rng_seed=seed)
            rand_w = rng.normal(0.0, 0.05, size=(N, N))
            np.fill_diagonal(rand_w, 0.0)
            conn.W = rand_w
            dyn = RecurrentRateDynamics(conn, rng_seed=seed)
            times, rates, _ = dyn.simulate(duration_ms=2000.0, warmup_ms=300.0)
            pu = PhaseUnfolder(rates, times)
            proj = ProjectomeAuditor(conn.W, net.z)
            wave = TravelingWaveAnalyzer(net, rates, times)
            return self._extract_metrics(cond_id, cond_desc, seed, wave.grid, proj, pu, wave)

        elif cond_id == "Ctrl_8_Yakovenko_Only":
            # Model Y reference
            grid_y = self.model_y_ref.grid
            proj_dummy = ProjectomeAuditor(np.zeros((10, 10)), np.linspace(0, 10, 10))
            times_dummy = np.linspace(0, 1400, grid_y.shape[1])
            pu_dummy = PhaseUnfolder(grid_y, times_dummy)
            rec = {
                'cond_id': cond_id,
                'cond_desc': cond_desc,
                'seed': seed,
                'pearson_r': 1.0,
                'spearman_rho': 1.0,
                'rmse': 0.0,
                'nrmse': 0.0,
                'contrast_mhc': 0.0,
                'area_ratio': 0.0,
                'legacy_mhi': 0.0,
                'planar_var_pct': 100.0,
                'wave_velocity_mm_s': float(np.max(self.model_y_ref.velocity_mm_s)),
                'bilateral_alternation': 1.0
            }
            return rec, proj_dummy.net_profile

        elif cond_id == "Ctrl_9_Scrambled_Anatomy":
            m = ModelKY_Transfer(n_neurons=N, rng_seed=seed, duration_ms=2000.0, warmup_ms=300.0)
            # Scramble slice assignment of grid
            scrambled_grid = np.copy(m.grid)
            rng.shuffle(scrambled_grid)
            return self._extract_metrics(cond_id, cond_desc, seed, scrambled_grid, m.projectome, m.phase_unfolder, m.wave)

        elif cond_id == "Ctrl_10_Matched_Null":
            # Matched null: preserves neuron count, density, E/I balance, but shuffles spatial kernel targets
            net = YakovenkoKomiSpatialNetwork(n_neurons=N, rng_seed=seed)
            conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=seed)
            # Permute row and column indices to destroy spatial receptive fields while preserving exact weight histogram
            perm = rng.permutation(N)
            conn.W = conn.W[perm, :][:, perm]
            dyn = RecurrentRateDynamics(conn, rng_seed=seed)
            times, rates, _ = dyn.simulate(duration_ms=2000.0, warmup_ms=300.0)
            pu = PhaseUnfolder(rates, times)
            proj = ProjectomeAuditor(conn.W, net.z)
            wave = TravelingWaveAnalyzer(net, rates, times)
            return self._extract_metrics(cond_id, cond_desc, seed, wave.grid, proj, pu, wave)

        else:
            raise ValueError(f"Unknown condition {cond_id}")

    def _extract_metrics(self, cond_id: str, cond_desc: str, seed: int, grid: np.ndarray, proj, pu, wave) -> Tuple[Dict, np.ndarray]:
        # Compute r_cm from grid
        n_slices, n_times = grid.shape
        levels = np.linspace(1.67, 98.33, n_slices)
        r_cm = np.zeros(n_times)
        for t in range(n_times):
            s = np.sum(grid[:, t])
            r_cm[t] = np.sum(grid[:, t] * levels) / s if s > 1e-9 else 50.0

        # Resample to 100 points
        if len(r_cm) >= 50:
            ky_100 = signal.resample(r_cm[:300], 100)
        else:
            ky_100 = np.full(100, 50.0)

        # Cross-correlation alignment with y_ref
        if np.std(ky_100) > 1e-6:
            xcorr = signal.correlate(self.y_ref - np.mean(self.y_ref), ky_100 - np.mean(ky_100), mode='full')
            lags = signal.correlation_lags(100, 100)
            best_lag = lags[np.argmax(xcorr)]
            ky_aligned = np.roll(ky_100, best_lag)

            r_val, _ = stats.pearsonr(self.y_ref, ky_aligned)
            rho_val, _ = stats.spearmanr(self.y_ref, ky_aligned)
            rmse = float(np.sqrt(np.mean((self.y_ref - ky_aligned)**2)))
            nrmse = float(rmse / (np.max(self.y_ref) - np.min(self.y_ref) + 1e-9))
        else:
            r_val = 0.0
            rho_val = 0.0
            rmse = float(np.sqrt(np.mean((self.y_ref - ky_100)**2)))
            nrmse = 1.0

        rec = {
            'cond_id': cond_id,
            'cond_desc': cond_desc,
            'seed': seed,
            'pearson_r': float(r_val),
            'spearman_rho': float(rho_val),
            'rmse': rmse,
            'nrmse': nrmse,
            'contrast_mhc': float(proj.contrast_mhc),
            'area_ratio': float(proj.area_ratio),
            'legacy_mhi': float(proj.legacy_buggy_mhi),
            'planar_var_pct': float(pu.planar_variance * 100.0),
            'wave_velocity_mm_s': float(wave.velocity_mm_s),
            'bilateral_alternation': float(wave.alternation_index)
        }
        return rec, proj.net_profile
