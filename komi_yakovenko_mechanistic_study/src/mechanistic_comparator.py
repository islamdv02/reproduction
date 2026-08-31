"""
Mechanistic Comparator: multi-seed Monte Carlo comparison of the Yakovenko (Y)
and Komi-Yakovenko (KY) locomotor models. Uses >= 5 seeds; reports Pearson r,
RMSE, NRMSE, phase-lag, and wave velocity against a >= 400-surrogate random-walk
null distribution.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import signal
from model_y import ModelY
from model_ky import ModelKY


def compute_random_walk_null_distribution(
    y_ref: np.ndarray,
    n_surrogates: int = 400,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Generates >= 400 random-walk surrogates, runs identical lag-optimization alignment
    against y_ref, and returns null distribution metrics (median, 95th percentile).
    """
    rng = np.random.default_rng(seed)
    n_pts = len(y_ref)
    null_corrs = np.zeros(n_surrogates)
    y_ref_centered = y_ref - np.mean(y_ref)

    for s in range(n_surrogates):
        steps = rng.normal(0.0, 1.0, size=n_pts * 4)
        rw_raw = np.cumsum(steps)
        rw_segment = rw_raw[:n_pts * 2]
        rw_resampled = signal.resample(rw_segment, n_pts)

        rw_centered = rw_resampled - np.mean(rw_resampled)
        if np.std(rw_centered) > 1e-9:
            xcorr = signal.correlate(y_ref_centered, rw_centered, mode='full')
            lags = signal.correlation_lags(n_pts, n_pts)
            best_lag = lags[np.argmax(xcorr)]
            rw_aligned = np.roll(rw_resampled, best_lag)
            r_val = float(np.corrcoef(y_ref, rw_aligned)[0, 1])
        else:
            r_val = 0.0
        null_corrs[s] = r_val

    return {
        'null_median_r': float(np.median(null_corrs)),
        'null_95th_pct_r': float(np.percentile(null_corrs, 95)),
        'null_mean_r': float(np.mean(null_corrs)),
        'null_std_r': float(np.std(null_corrs)),
        'null_corrs': null_corrs
    }


class MechanisticComparator:
    """
    Multi-seed comparative benchmarking of the Y vs. KY locomotor models,
    scored against an empirical random-walk surrogate null distribution.
    """

    def __init__(self, seeds: List[int] = [42, 101, 2024, 7, 99]):
        self.seeds = list(seeds)

    def run_multi_seed_comparison(self, n_surrogates: int = 400) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
        """Simulates all seeds and compiles quantitative comparative statistics."""
        records = []

        # Model Y reference (deterministic empirical baseline)
        model_y = ModelY(recruitment_mode='graded', n_cycles=2)
        y_traj_100 = model_y.r_cm_level[:100]

        # Compute empirical random-walk null baseline
        null_stats = compute_random_walk_null_distribution(y_traj_100, n_surrogates=n_surrogates, seed=42)
        null_median_r = null_stats['null_median_r']
        null_95th_r = null_stats['null_95th_pct_r']
        null_corrs = null_stats['null_corrs']

        for s_idx, seed in enumerate(self.seeds):
            m_ky = ModelKY(n_neurons=500, rng_seed=seed, duration_ms=2500.0, warmup_ms=500.0)

            # Resample Model K-Y trajectory to 100 step cycle points
            T_period = m_ky.phase_unfolder.cycle_period_ms
            dt = m_ky.dynamics.dt_ms
            steps_per_cycle = int(np.round(T_period / dt))

            if steps_per_cycle > 20 and steps_per_cycle < len(m_ky.r_cm_level):
                ky_cycle = m_ky.r_cm_level[:steps_per_cycle]
                ky_resampled = signal.resample(ky_cycle, 100)
            else:
                ky_resampled = signal.resample(m_ky.r_cm_level[:400], 100)

            # Alignment / Cross-correlation to find best phase alignment
            xcorr = signal.correlate(y_traj_100 - np.mean(y_traj_100),
                                     ky_resampled - np.mean(ky_resampled), mode='full')
            lags = signal.correlation_lags(100, 100)
            best_lag = lags[np.argmax(xcorr)]

            ky_aligned = np.roll(ky_resampled, best_lag)

            # Metrics
            corr = float(np.corrcoef(y_traj_100, ky_aligned)[0, 1])
            rmse = float(np.sqrt(np.mean((y_traj_100 - ky_aligned) ** 2)))
            nrmse = float(rmse / (np.max(y_traj_100) - np.min(y_traj_100)))

            # Empirical p-value against null distribution
            p_val = float(np.mean(null_corrs >= corr))

            rec = {
                'seed': seed,
                'correlation_r': corr,
                'null_median_r': null_median_r,
                'null_95th_pct_r': null_95th_r,
                'p_value_vs_null': p_val,
                'rmse_levels': rmse,
                'nrmse': nrmse,
                'phase_lag_pct': abs(best_lag),
                'wave_velocity_mm_s': m_ky.wave.velocity_mm_s,
                'mexican_hat_index': m_ky.projectome.mexican_hat_index,
                'projectome_asymmetry': m_ky.projectome.asymmetry_index,
                'planar_variance_pct': m_ky.phase_unfolder.planar_variance * 100.0,
                'dominant_freq_hz': m_ky.phase_unfolder.frequency_hz,
                'bilateral_phase_deg': m_ky.wave.bilateral_phase_diff_deg
            }
            records.append(rec)

        df = pd.DataFrame(records)

        # Summary statistics (mean +- SD)
        stats = {}
        for col in df.columns:
            if col != 'seed':
                stats[col] = {
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }

        return df, stats
